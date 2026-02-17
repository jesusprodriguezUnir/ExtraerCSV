#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests para el módulo elasticsearch_client con mocks
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from elasticsearch.exceptions import (
    ConnectionError,
    AuthenticationException,
    NotFoundError,
    RequestError
)

# Importar después de configurar el path si es necesario
from config import Config
from elasticsearch_client import ElasticsearchClient


@pytest.fixture
def mock_config():
    """Fixture que proporciona una configuración de prueba"""
    config = Mock(spec=Config)
    config.es_host = 'https://test.example.com'
    config.es_user = 'testuser'
    config.es_password = 'testpass'
    config.es_index = 'test-logs-*'
    config.verify_ssl = True
    config.timeout = 300
    config.scroll_size = 1000
    config.scroll_timeout = '5m'
    return config


@pytest.fixture
def mock_elasticsearch():
    """Fixture que proporciona un mock de Elasticsearch"""
    with patch('elasticsearch_client.Elasticsearch') as mock_es:
        mock_instance = MagicMock()
        mock_es.return_value = mock_instance
        yield mock_instance


class TestElasticsearchClientInit:
    """Tests para la inicialización del cliente"""
    
    def test_inicializa_con_configuracion_correcta(self, mock_config, mock_elasticsearch):
        """Test: Inicializa cliente con configuración correcta"""
        client = ElasticsearchClient(mock_config)
        
        assert client.config == mock_config
        assert client.es is not None
    
    def test_llama_elasticsearch_con_parametros_correctos(self, mock_config):
        """Test: Llama a Elasticsearch con los parámetros correctos"""
        with patch('elasticsearch_client.Elasticsearch') as MockES:
            client = ElasticsearchClient(mock_config)
            
            MockES.assert_called_once()
            call_kwargs = MockES.call_args[1]
            
            assert call_kwargs['basic_auth'] == ('testuser', 'testpass')
            assert call_kwargs['verify_certs'] is True
            assert call_kwargs['timeout'] == 300


class TestTestConnection:
    """Tests para el método test_connection"""
    
    def test_conexion_exitosa(self, mock_config, mock_elasticsearch):
        """Test: Conexión exitosa retorna información correcta"""
        mock_elasticsearch.ping.return_value = True
        mock_elasticsearch.info.return_value = {
            'cluster_name': 'test-cluster',
            'version': {'number': '8.11.0'}
        }
        
        client = ElasticsearchClient(mock_config)
        result = client.test_connection()
        
        assert result['connected'] is True
        assert result['cluster_name'] == 'test-cluster'
        assert result['version'] == '8.11.0'
        assert result['host'] == 'https://test.example.com'
    
    def test_ping_falla(self, mock_config, mock_elasticsearch):
        """Test: Lanza Exception si ping falla"""
        mock_elasticsearch.ping.return_value = False
        
        client = ElasticsearchClient(mock_config)
        
        with pytest.raises(Exception) as excinfo:
            client.test_connection()
        
        assert 'conexión' in str(excinfo.value).lower()
    
    def test_autenticacion_falla(self, mock_config, mock_elasticsearch):
        """Test: Lanza AuthenticationException en error de auth"""
        mock_elasticsearch.ping.side_effect = Exception("Authentication failed")
        
        client = ElasticsearchClient(mock_config)
        
        with pytest.raises(Exception) as excinfo:
            client.test_connection()
        
        # Debería contener mensaje de autenticación o conexión
        assert 'auth' in str(excinfo.value).lower() or 'conexión' in str(excinfo.value).lower()


class TestGetAvailableIndices:
    """Tests para el método get_available_indices"""
    
    def test_lista_indices_sin_patron(self, mock_config, mock_elasticsearch):
        """Test: Lista todos los índices sin patrón"""
        mock_elasticsearch.cat.indices.return_value = [
            {'index': 'logs-2026.01'},
            {'index': 'logs-2026.02'},
            {'index': 'other-index'}
        ]
        
        client = ElasticsearchClient(mock_config)
        indices = client.get_available_indices()
        
        assert len(indices) == 3
        assert 'logs-2026.01' in indices
        assert 'logs-2026.02' in indices
    
    def test_filtra_indices_con_patron(self, mock_config, mock_elasticsearch):
        """Test: Filtra índices por patrón"""
        mock_elasticsearch.cat.indices.return_value = [
            {'index': 'logs-2026.01'},
            {'index': 'logs-2026.02'}
        ]
        
        client = ElasticsearchClient(mock_config)
        indices = client.get_available_indices('logs-*')
        
        assert len(indices) == 2
        mock_elasticsearch.cat.indices.assert_called_with(index='logs-*', format='json')
    
    def test_maneja_indice_no_encontrado(self, mock_config, mock_elasticsearch):
        """Test: Maneja error y retorna lista vacía"""
        mock_elasticsearch.cat.indices.side_effect = Exception("Not found")
        
        client = ElasticsearchClient(mock_config)
        indices = client.get_available_indices('nonexistent-*')
        
        assert indices == []


class TestGetTotalEstimate:
    """Tests para el método get_total_estimate"""
    
    def test_retorna_count_correcto(self, mock_config, mock_elasticsearch):
        """Test: Retorna el count correcto"""
        mock_elasticsearch.count.return_value = {'count': 12500}
        
        client = ElasticsearchClient(mock_config)
        query = {"query": {"match_all": {}}}
        total = client.get_total_estimate(query, 'logs-*')
        
        assert total == 12500
    
    def test_maneja_error_retorna_cero(self, mock_config, mock_elasticsearch):
        """Test: Maneja errores retornando 0"""
        mock_elasticsearch.count.side_effect = Exception("Error")
        
        client = ElasticsearchClient(mock_config)
        query = {"query": {"match_all": {}}}
        total = client.get_total_estimate(query, 'logs-*')
        
        assert total == 0


class TestSearchLogs:
    """Tests para el método search_logs con scroll"""
    
    def test_busca_logs_correctamente(self, mock_config, mock_elasticsearch):
        """Test: Busca logs usando scan correctamente"""
        mock_elasticsearch.indices.exists.return_value = True
        
        # Simular respuesta de scan
        mock_docs = [
            {'_source': {'message': 'log1'}, '_id': '1'},
            {'_source': {'message': 'log2'}, '_id': '2'}
        ]
        
        with patch('elasticsearch_client.scan') as mock_scan:
            mock_scan.return_value = iter(mock_docs)
            
            client = ElasticsearchClient(mock_config)
            query = {"query": {"match_all": {}}}
            
            results = list(client.search_logs(query, 'logs-*'))
            
            assert len(results) == 2
            assert results[0]['_source']['message'] == 'log1'
    
    def test_lanza_error_si_indice_no_existe(self, mock_config, mock_elasticsearch):
        """Test: Lanza ValueError si el índice no existe"""
        mock_elasticsearch.indices.exists.return_value = False
        mock_elasticsearch.cat.indices.return_value = [
            {'index': 'other-index'}
        ]
        
        client = ElasticsearchClient(mock_config)
        query = {"query": {"match_all": {}}}
        
        with pytest.raises(ValueError) as excinfo:
            list(client.search_logs(query, 'nonexistent-*'))
        
        assert 'Índice no encontrado' in str(excinfo.value)
    
    def test_lanza_error_query_invalida(self, mock_config, mock_elasticsearch):
        """Test: Lanza RequestError si la query es inválida"""
        mock_elasticsearch.indices.exists.return_value = True
        
        with patch('elasticsearch_client.scan') as mock_scan:
            # Simular error de request
            mock_scan.side_effect = Exception("Query parsing error")
            
            client = ElasticsearchClient(mock_config)
            query = {"query": {"invalid": {}}}
            
            with pytest.raises(Exception) as excinfo:
                list(client.search_logs(query, 'logs-*'))
            
            assert 'Query parsing error' in str(excinfo.value)


class TestDownloadToCsv:
    """Tests para el método download_to_csv"""
    
    def test_descarga_a_csv_correctamente(self, mock_config, mock_elasticsearch, tmp_path):
        """Test: Descarga documentos a CSV correctamente"""
        mock_elasticsearch.indices.exists.return_value = True
        
        mock_docs = [
            {'_source': {'message': 'log1', 'level': 'ERROR'}, '_id': '1'},
            {'_source': {'message': 'log2', 'level': 'WARN'}, '_id': '2'}
        ]
        
        output_csv = tmp_path / "output.csv"
        
        with patch('elasticsearch_client.scan') as mock_scan:
            mock_scan.return_value = iter(mock_docs)
            
            client = ElasticsearchClient(mock_config)
            query = {"query": {"match_all": {}}}
            
            count = client.download_to_csv(query, str(output_csv))
            
            assert count == 2
            assert output_csv.exists()
            
            # Verificar contenido del CSV
            import csv
            with open(output_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]['message'] == 'log1'
    
    def test_filtra_campos_especificados(self, mock_config, mock_elasticsearch, tmp_path):
        """Test: Filtra solo campos especificados"""
        mock_elasticsearch.indices.exists.return_value = True
        
        mock_docs = [
            {'_source': {'message': 'log1', 'level': 'ERROR', 'extra': 'data'}, '_id': '1'}
        ]
        
        output_csv = tmp_path / "filtered.csv"
        
        with patch('elasticsearch_client.scan') as mock_scan:
            mock_scan.return_value = iter(mock_docs)
            
            client = ElasticsearchClient(mock_config)
            query = {"query": {"match_all": {}}}
            
            count = client.download_to_csv(
                query, 
                str(output_csv), 
                fields=['message', 'level']
            )
            
            # Verificar que solo tiene los campos especificados
            import csv
            with open(output_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert 'extra' not in rows[0]
                assert 'message' in rows[0]
                assert 'level' in rows[0]


class TestGetDocumentsGenerator:
    """Tests para el método get_documents_generator"""
    
    def test_genera_documentos_formato_correcto(self, mock_config, mock_elasticsearch):
        """Test: Genera documentos en formato compatible"""
        mock_elasticsearch.indices.exists.return_value = True
        
        mock_docs = [
            {
                '_source': {'message': 'Body: {...}', '@timestamp': '2026-02-16'},
                '_id': '123'
            },
            {
                '_source': {'message': 'Body: {...}', '@timestamp': '2026-02-17'},
                '_id': '456'
            }
        ]
        
        with patch('elasticsearch_client.scan') as mock_scan:
            mock_scan.return_value = iter(mock_docs)
            
            client = ElasticsearchClient(mock_config)
            query = {"query": {"match_all": {}}}
            
            docs = list(client.get_documents_generator(query))
            
            assert len(docs) == 2
            assert docs[0]['message'] == 'Body: {...}'
            assert docs[0]['@timestamp'] == '2026-02-16'
            assert docs[0]['_id'] == '123'
    
    def test_maneja_campos_faltantes(self, mock_config, mock_elasticsearch):
        """Test: Maneja correctamente documentos sin campos requeridos"""
        mock_elasticsearch.indices.exists.return_value = True
        
        mock_docs = [
            {'_source': {}, '_id': '789'}  # Sin message ni timestamp
        ]
        
        with patch('elasticsearch_client.scan') as mock_scan:
            mock_scan.return_value = iter(mock_docs)
            
            client = ElasticsearchClient(mock_config)
            query = {"query": {"match_all": {}}}
            
            docs = list(client.get_documents_generator(query))
            
            assert len(docs) == 1
            assert docs[0]['message'] == ''
            assert docs[0]['@timestamp'] == ''


# Tests de integración con todo el flujo
class TestIntegracionElasticsearchClient:
    """Tests de integración del cliente completo"""
    
    def test_flujo_completo_busqueda_procesamiento(self, mock_config, mock_elasticsearch, tmp_path):
        """Test: Flujo completo desde búsqueda hasta archivo"""
        mock_elasticsearch.indices.exists.return_value = True
        mock_elasticsearch.ping.return_value = True
        mock_elasticsearch.info.return_value = {
            'cluster_name': 'test',
            'version': {'number': '8.0.0'}
        }
        
        mock_docs = [
            {
                '_source': {
                    'message': 'Body: {"where":[{"field":"id","value":100}]}',
                    '@timestamp': '2026-02-16'
                },
                '_id': '1'
            }
        ]
        
        with patch('elasticsearch_client.scan') as mock_scan:
            mock_scan.return_value = iter(mock_docs)
            
            client = ElasticsearchClient(mock_config)
            
            # Test conexión
            info = client.test_connection()
            assert info['connected'] is True
            
            # Test descarga
            output_csv = tmp_path / "logs.csv"
            count = client.download_to_csv(
                {"query": {"match_all": {}}},
                str(output_csv)
            )
            
            assert count == 1
            assert output_csv.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
