#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cliente de Elasticsearch para descarga de logs
Maneja conexión, queries y descarga de datos desde Elasticsearch/Kibana
"""

import csv
import json
from typing import Iterator, Dict, List, Optional, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import (
    ConnectionError, 
    AuthenticationException,
    NotFoundError,
    RequestError
)


class ElasticsearchClient:
    """Cliente para interactuar con Elasticsearch"""
    
    def __init__(self, config):
        """
        Inicializa el cliente de Elasticsearch
        
        Args:
            config: Objeto Config con credenciales y configuración
        """
        self.config = config
        self.es = None
        self._connect()
    
    def _connect(self):
        """Establece conexión con Elasticsearch"""
        try:
            self.es = Elasticsearch(
                [self.config.es_host],
                basic_auth=(self.config.es_user, self.config.es_password),
                verify_certs=self.config.verify_ssl,
                ssl_show_warn=self.config.verify_ssl,
                timeout=self.config.timeout,
                max_retries=3,
                retry_on_timeout=True
            )
        except Exception as e:
            raise ConnectionError(f"Error al conectar con Elasticsearch: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Verifica la conexión con Elasticsearch
        
        Returns:
            dict: Información del cluster si la conexión es exitosa
            
        Raises:
            Exception: Si no se puede conectar o hay error de autenticación
        """
        try:
            if not self.es.ping():
                raise Exception(
                    f"❌ Error de conexión: No se pudo establecer conexión con Elasticsearch\n"
                    f"Verifica:\n"
                    f"  - URL correcta: {self.config.es_host}\n"
                    f"  - Red/Firewall\n"
                    f"  - Si hay problemas SSL, configura ELASTICSEARCH_VERIFY_SSL=false en .env"
                )
            
            info = self.es.info()
            return {
                'connected': True,
                'cluster_name': info['cluster_name'],
                'version': info['version']['number'],
                'host': self.config.es_host
            }
        except Exception as e:
            # Si ya es nuestra Exception personalizada, re-lanzarla
            if "❌" in str(e):
                raise
            
            # Procesar otros errores
            error_msg = str(e).lower()
            if 'auth' in error_msg or 'unauthorized' in error_msg:
                raise Exception(
                    f"❌ Error de autenticación: {e}\n"
                    f"Verifica usuario y contraseña en .env"
                )
            else:
                raise Exception(
                    f"❌ Error de conexión: {e}\n"
                    f"Verifica:\n"
                    f"  - URL correcta: {self.config.es_host}\n"
                    f"  - Red/Firewall\n"
                    f"  - Si hay problemas SSL, configura ELASTICSEARCH_VERIFY_SSL=false en .env"
                )
    
    def get_available_indices(self, pattern: Optional[str] = None) -> List[str]:
        """
        Obtiene lista de índices disponibles
        
        Args:
            pattern: Patrón para filtrar índices (opcional)
            
        Returns:
            list: Lista de nombres de índices
        """
        try:
            if pattern:
                indices = self.es.cat.indices(index=pattern, format='json')
            else:
                indices = self.es.cat.indices(format='json')
            
            return sorted([idx['index'] for idx in indices])
        except NotFoundError:
            return []
        except Exception as e:
            print(f"⚠ Advertencia: No se pudieron listar índices: {e}")
            return []
    
    def get_total_estimate(self, query_dict: Dict, index_pattern: str) -> int:
        """
        Obtiene estimación del total de documentos que coinciden con la query
        
        Args:
            query_dict: Query de Elasticsearch en formato dict
            index_pattern: Patrón de índices a consultar
            
        Returns:
            int: Número estimado de documentos
        """
        try:
            result = self.es.count(index=index_pattern, body=query_dict)
            return result['count']
        except Exception:
            return 0
    
    def search_logs(
        self, 
        query_dict: Dict, 
        index_pattern: Optional[str] = None
    ) -> Iterator[Dict]:
        """
        Busca logs en Elasticsearch usando Scroll API
        
        Args:
            query_dict: Query de Elasticsearch en formato dict
            index_pattern: Patrón de índices (override del config)
            
        Yields:
            dict: Documentos encontrados uno por uno
            
        Raises:
            ValueError: Si no se encuentra el índice
            Exception: Para errores de query o conexión
        """
        index = index_pattern or self.config.es_index
        
        try:
            # Verificar que el índice existe
            if not self.es.indices.exists(index=index):
                available = self.get_available_indices()
                error_msg = (
                    f"❌ Índice no encontrado: {index}\n"
                    f"Índices disponibles: {', '.join(available[:10])}"
                )
                raise ValueError(error_msg)
            
            # Usar scan helper para manejar paginación automáticamente
            for doc in scan(
                self.es,
                index=index,
                query=query_dict,
                scroll=self.config.scroll_timeout,
                size=self.config.scroll_size,
                raise_on_error=True
            ):
                yield doc
        except ValueError:
            # Re-raise ValueError como está (índice no encontrado)
            raise
        except Exception as e:
            # Cualquier otro error se envuelve en Exception genérica
            raise Exception(f"Error durante la búsqueda: {str(e)}")
    
    def download_to_csv(
        self,
        query_dict: Dict,
        output_csv: str,
        fields: Optional[List[str]] = None,
        index_pattern: Optional[str] = None
    ) -> int:
        """
        Descarga resultados de búsqueda a archivo CSV
        
        Args:
            query_dict: Query de Elasticsearch
            output_csv: Ruta del archivo CSV de salida
            fields: Lista de campos a incluir (None = todos los de _source)
            index_pattern: Patrón de índices (override del config)
            
        Returns:
            int: Número de documentos descargados
        """
        print(f"📥 Descargando logs a CSV: {output_csv}")
        
        count = 0
        writer = None
        csv_file = None
        
        try:
            csv_file = open(output_csv, 'w', newline='', encoding='utf-8')
            
            for doc in self.search_logs(query_dict, index_pattern):
                source = doc['_source']
                
                # Filtrar campos si se especificaron
                if fields:
                    source = {k: v for k, v in source.items() if k in fields}
                
                # Inicializar writer con los campos del primer documento
                if writer is None:
                    fieldnames = list(source.keys())
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                
                writer.writerow(source)
                count += 1
                
                # Mostrar progreso cada 1000 documentos
                if count % 1000 == 0:
                    print(f"  ✓ Descargados {count:,} documentos...")
            
            print(f"✅ Descarga completa: {count:,} documentos guardados en {output_csv}")
            return count
            
        finally:
            if csv_file:
                csv_file.close()
    
    def get_documents_generator(
        self,
        query_dict: Dict,
        index_pattern: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Obtiene generador de documentos para procesamiento directo
        
        Args:
            query_dict: Query de Elasticsearch
            index_pattern: Patrón de índices
            
        Yields:
            dict: Documento con estructura compatible con procesador
        """
        for doc in self.search_logs(query_dict, index_pattern):
            # Retornar en formato compatible con el procesador CSV
            yield {
                'message': doc['_source'].get('message', ''),
                '@timestamp': doc['_source'].get('@timestamp', ''),
                '_id': doc['_id']
            }


if __name__ == "__main__":
    # Test del cliente
    from config import load_config
    
    try:
        config = load_config()
        client = ElasticsearchClient(config)
        
        print("🔍 Probando conexión...")
        info = client.test_connection()
        print(f"✅ Conectado a: {info['cluster_name']} (v{info['version']})")
        
        print(f"\n📊 Índices disponibles con patrón '{config.es_index}':")
        indices = client.get_available_indices(config.es_index)
        for idx in indices[:5]:
            print(f"  - {idx}")
        if len(indices) > 5:
            print(f"  ... y {len(indices) - 5} más")
            
    except Exception as e:
        print(f"❌ Error: {e}")
