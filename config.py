#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gestión de configuración desde variables de entorno
Carga credenciales y configuración desde archivo .env
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuración de la aplicación"""
    
    def __init__(self):
        """Carga configuración desde variables de entorno"""
        # Cargar variables desde .env si existe
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)
        
        # Elasticsearch/Kibana
        self.es_host = os.getenv('ELASTICSEARCH_HOST')
        self.es_user = os.getenv('ELASTICSEARCH_USER')
        self.es_password = os.getenv('ELASTICSEARCH_PASSWORD')
        self.es_index = os.getenv('ELASTICSEARCH_INDEX', 'logs-*')
        
        # Configuración opcional con defaults
        self.verify_ssl = os.getenv('ELASTICSEARCH_VERIFY_SSL', 'true').lower() == 'true'
        self.timeout = int(os.getenv('ELASTICSEARCH_TIMEOUT', '300'))
        self.scroll_size = int(os.getenv('ELASTICSEARCH_SCROLL_SIZE', '1000'))
        self.scroll_timeout = os.getenv('ELASTICSEARCH_SCROLL_TIMEOUT', '5m')
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valida que la configuración esté completa
        
        Returns:
            tuple: (es_valido, mensaje_error)
        """
        required_vars = {
            'ELASTICSEARCH_HOST': self.es_host,
            'ELASTICSEARCH_USER': self.es_user,
            'ELASTICSEARCH_PASSWORD': self.es_password
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        
        if missing:
            error_msg = (
                f"❌ Faltan variables de entorno requeridas: {', '.join(missing)}\n\n"
                f"Por favor:\n"
                f"1. Copia .env.example a .env\n"
                f"2. Completa las credenciales en .env\n"
                f"3. Asegúrate de que .env no esté en .gitignore (ya está configurado)\n"
            )
            return False, error_msg
        
        return True, None
    
    def __repr__(self):
        """Representación segura sin exponer la contraseña"""
        return (
            f"Config(host={self.es_host}, "
            f"user={self.es_user}, "
            f"index={self.es_index}, "
            f"verify_ssl={self.verify_ssl}, "
            f"timeout={self.timeout}s)"
        )


def load_config() -> Config:
    """
    Carga y valida la configuración
    
    Returns:
        Config: Objeto de configuración
        
    Raises:
        ValueError: Si la configuración está incompleta
    """
    config = Config()
    is_valid, error_msg = config.validate()
    
    if not is_valid:
        raise ValueError(error_msg)
    
    return config


if __name__ == "__main__":
    # Test de configuración
    try:
        config = load_config()
        print("✅ Configuración cargada correctamente:")
        print(config)
    except ValueError as e:
        print(e)
