#!/usr/bin/env python3
"""
Script de depuración para encontrar el endpoint correcto de Elasticsearch

Prueba múltiples combinaciones de host, puerto y autenticación
"""

from elasticsearch import Elasticsearch
import os
import warnings
import sys

warnings.filterwarnings('ignore')

# Credenciales desde entorno
USER = os.getenv('ELASTICSEARCH_USER', os.getenv('PROXY_USER', ''))
PWD = os.getenv('ELASTICSEARCH_PASSWORD', os.getenv('PROXY_PASSWORD', ''))

# Hosts a probar
HOSTS_TO_TEST = [
    # Puerto 9200 (Elasticsearch directo)
    'https://elk.unir.net:9200',
    'http://elk.unir.net:9200',
    
    # Puerto 443 (HTTPS estándar)
    'https://elk.unir.net:443',
    'https://elk.unir.net',
    
    # Puerto 9300 (node communication - poco probable)
    'https://elk.unir.net:9300',
    
    # API gateway de Kibana
    'https://elk.unir.net/api/elasticsearch',
    'https://elk.unir.net/elasticsearch',
    
    # Alternativas HTTP
    'http://elk.unir.net:9200',
    'http://elk.unir.net:5601',
]

def test_connection(host):
    """Prueba conexión a un host específico"""
    print(f"\n{'='*60}")
    print(f"🧪 Probando: {host}")
    print(f"{'='*60}")
    
    try:
        # Crear cliente
        es = Elasticsearch(
            hosts=[host],
            basic_auth=(USER, PWD),
            verify_certs=False,
            request_timeout=10
        )
        
        print("   ✓ Cliente creado")
        
        # Intentar obtener info
        try:
            print("   ⏳ Intentando es.info()...")
            info = es.info()
            print(f"\n   ✅ ¡ÉXITO!")
            print(f"   Cluster: {info.get('cluster_name')}")
            print(f"   Version: {info.get('version', {}).get('number')}")
            return True, info
        except Exception as e:
            error_str = str(e)
            status = None
            
            # Extraer código HTTP si está disponible
            if '302' in error_str:
                status = '302 (REDIRECT a /login)'
            elif '401' in error_str:
                status = '401 (UNAUTHORIZED - credenciales incorrectas)'
            elif '403' in error_str:
                status = '403 (FORBIDDEN - sin permisos)'
            elif '404' in error_str:
                status = '404 (NOT FOUND)'
            elif 'Connection' in error_str or 'refused' in error_str.lower():
                status = 'CONNECTION REFUSED (puerto no disponible)'
            
            print(f"   ✗ Error: {status or error_str[:100]}")
            return False, None
            
    except Exception as e:
        print(f"   ✗ Error al crear cliente: {str(e)[:80]}")
        return False, None


def main():
    print("\n" + "="*60)
    print("🔍 DEPURADOR DE ELASTICSEARCH")
    print("="*60)
    print(f"Usuario: {USER}")
    print(f"Contraseña: {PWD[:5]}...***")
    print(f"Hosts a probar: {len(HOSTS_TO_TEST)}")
    
    success_hosts = []
    failed_hosts = []
    
    for host in HOSTS_TO_TEST:
        success, info = test_connection(host)
        if success:
            success_hosts.append((host, info))
        else:
            failed_hosts.append(host)
    
    # Resumen
    print("\n\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    if success_hosts:
        print(f"\n✅ {len(success_hosts)} endpoint(s) exitoso(s):\n")
        for i, (host, info) in enumerate(success_hosts, 1):
            print(f"{i}. {host}")
            print(f"   Cluster: {info.get('cluster_name')}")
            print(f"   Version: {info.get('version', {}).get('number')}")
            print()
        
        # Guardar host exitoso
        with open('elasticsearch_host.txt', 'w') as f:
            f.write(success_hosts[0][0])
        print(f"✅ Host guardado en: elasticsearch_host.txt\n")
        
    else:
        print(f"\n❌ Ningún endpoint funcionó.\n")
        print("Opciones:\n")
        print("1. Verifica que el servidor está disponible")
        print("2. Verifica que las credenciales son correctas")
        print("3. Pregunta al administrador dónde está Elasticsearch")
        print("4. Verifica si hay firewall bloqueando puertos")
        print("\nServidores probados:")
        for host in failed_hosts:
            print(f"   - {host}")


if __name__ == '__main__':
    main()
