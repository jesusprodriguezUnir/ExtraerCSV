#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests para el módulo config
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch
from config import Config, load_config


class TestConfig:
    """Tests para la clase Config"""
    
    def test_carga_variables_entorno(self):
        """Test: Carga variables de entorno correctamente"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_USER': 'testuser',
            'ELASTICSEARCH_PASSWORD': 'testpass',
            'ELASTICSEARCH_INDEX': 'test-logs-*'
        }):
            config = Config()
            
            assert config.es_host == 'https://test.example.com'
            assert config.es_user == 'testuser'
            assert config.es_password == 'testpass'
            assert config.es_index == 'test-logs-*'
    
    def test_valores_por_defecto(self):
        """Test: Usa valores por defecto cuando no están definidos"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_USER': 'testuser',
            'ELASTICSEARCH_PASSWORD': 'testpass'
        }, clear=True):
            config = Config()
            
            assert config.es_index == 'logs-*'  # Default
            assert config.verify_ssl is True    # Default
            assert config.timeout == 300        # Default
            assert config.scroll_size == 1000   # Default
    
    def test_convierte_tipos_correctamente(self):
        """Test: Convierte tipos de datos correctamente"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_USER': 'testuser',
            'ELASTICSEARCH_PASSWORD': 'testpass',
            'ELASTICSEARCH_TIMEOUT': '600',
            'ELASTICSEARCH_SCROLL_SIZE': '2000',
            'ELASTICSEARCH_VERIFY_SSL': 'false'
        }):
            config = Config()
            
            assert isinstance(config.timeout, int)
            assert config.timeout == 600
            assert isinstance(config.scroll_size, int)
            assert config.scroll_size == 2000
            assert config.verify_ssl is False
    
    def test_validate_con_variables_completas(self):
        """Test: Validación exitosa con todas las variables"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_USER': 'testuser',
            'ELASTICSEARCH_PASSWORD': 'testpass'
        }):
            config = Config()
            is_valid, error_msg = config.validate()
            
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_falla_sin_host(self):
        """Test: Validación falla sin ELASTICSEARCH_HOST"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_USER': 'testuser',
            'ELASTICSEARCH_PASSWORD': 'testpass'
        }, clear=True):
            config = Config()
            is_valid, error_msg = config.validate()
            
            assert is_valid is False
            assert 'ELASTICSEARCH_HOST' in error_msg
    
    def test_validate_falla_sin_usuario(self):
        """Test: Validación falla sin ELASTICSEARCH_USER"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_PASSWORD': 'testpass'
        }, clear=True):
            config = Config()
            is_valid, error_msg = config.validate()
            
            assert is_valid is False
            assert 'ELASTICSEARCH_USER' in error_msg
    
    def test_validate_falla_sin_password(self):
        """Test: Validación falla sin ELASTICSEARCH_PASSWORD"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_USER': 'testuser'
        }, clear=True):
            config = Config()
            is_valid, error_msg = config.validate()
            
            assert is_valid is False
            assert 'ELASTICSEARCH_PASSWORD' in error_msg
    
    def test_repr_no_expone_password(self):
        """Test: __repr__ no expone la contraseña"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_USER': 'testuser',
            'ELASTICSEARCH_PASSWORD': 'supersecret123'
        }):
            config = Config()
            repr_str = repr(config)
            
            assert 'supersecret123' not in repr_str
            assert 'testuser' in repr_str
            assert 'https://test.example.com' in repr_str


class TestLoadConfig:
    """Tests para la función load_config"""
    
    def test_load_config_exitoso(self):
        """Test: load_config retorna configuración válida"""
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'https://test.example.com',
            'ELASTICSEARCH_USER': 'testuser',
            'ELASTICSEARCH_PASSWORD': 'testpass'
        }):
            config = load_config()
            
            assert isinstance(config, Config)
            assert config.es_host == 'https://test.example.com'
    
    def test_load_config_falla_sin_variables(self):
        """Test: load_config lanza ValueError si falta configuración"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as excinfo:
                load_config()
            
            assert 'Faltan variables de entorno' in str(excinfo.value)
    
    def test_load_config_mensaje_error_util(self):
        """Test: load_config proporciona mensaje de error útil"""
        with patch.dict(os.environ, {}, clear=True):
            try:
                load_config()
                assert False, "Debería haber lanzado ValueError"
            except ValueError as e:
                error_msg = str(e)
                assert '.env.example' in error_msg
                assert '.env' in error_msg


class TestConfigIntegracion:
    """Tests de integración con archivo .env"""
    
    def test_carga_desde_archivo_env(self, tmp_path, monkeypatch):
        """Test: Carga configuración desde archivo .env"""
        # Crear archivo .env temporal
        env_file = tmp_path / ".env"
        env_file.write_text(
            "ELASTICSEARCH_HOST=https://test.example.com\n"
            "ELASTICSEARCH_USER=testuser\n"
            "ELASTICSEARCH_PASSWORD=testpass\n"
            "ELASTICSEARCH_INDEX=test-*\n"
        )
        
        # Cambiar directorio de trabajo al temporal
        monkeypatch.chdir(tmp_path)
        
        config = Config()
        
        assert config.es_host == 'https://test.example.com'
        assert config.es_user == 'testuser'
        assert config.es_password == 'testpass'
        assert config.es_index == 'test-*'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
