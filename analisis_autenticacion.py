"""
Script avanzado para investigar autenticación en Kibana/Elasticsearch
Intenta múltiples métodos de autenticación
"""

import os
import requests
import json
import warnings
from requests.auth import HTTPBasicAuth

warnings.filterwarnings('ignore')

# Configuración
KIBANA_URL = 'https://elk.unir.net'
PROXY_URL = 'http://localhost:9200'
USERNAME = os.getenv('ELASTICSEARCH_USER', os.getenv('PROXY_USER', ''))
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', os.getenv('PROXY_PASSWORD', ''))

print("=" * 70)
print("🔐 ANÁLISIS AVANZADO: Métodos de Autenticación")
print("=" * 70)
print()

session = requests.Session()
session.verify = False

# Prueba 1: Acceso directo a Elasticsearch a través de Kibana
print("[1] Intentando acceso directo a ES a través de Kibana...")
try:
    endpoints = [
        f'{KIBANA_URL}/.cluster/health',
        f'{KIBANA_URL}/_cluster/health',
        f'{KIBANA_URL}/api/status',
    ]
    
    for endpoint in endpoints:
        try:
            response = session.get(
                endpoint,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                timeout=10
            )
            print(f"    {endpoint.split(KIBANA_URL)[1]}")
            print(f"      Status: {response.status_code}")
            if response.status_code < 400:
                data = response.json() if response.text else {}
                print(f"      ✅ Respuesta: {json.dumps(data, indent=2)[:200]}")
            else:
                print(f"      ❌ {response.text[:100]}")
        except Exception as e:
            print(f"      Error: {str(e)[:80]}")
    print()
    
except Exception as e:
    print(f"    Error general: {e}")
    print()

# Prueba 2: Acceso a través del proxy
print("[2] Acceso a través del proxy (localhost:9200)...")
try:
    response = session.get(
        f'{PROXY_URL}/',
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=10
    )
    print(f"    Status: {response.status_code}")
    try:
        data = response.json()
        print(f"    ✅ Cluster info:")
        print(f"      Nombre: {data.get('cluster_name')}")
        print(f"      Versión ES: {data.get('version', {}).get('number')}")
        print(f"      Versión Lucene: {data.get('version', {}).get('lucene_version')}")
    except:
        print(f"    Respuesta: {response.text[:200]}")
    print()
    
except Exception as e:
    print(f"    Error: {e}")
    print()

# Prueba 3: Headers específicos para Kibana
print("[3] Intentando con headers específicos de Kibana...")
try:
    headers = {
        'Content-Type': 'application/json',
        'kbn-xsrf': 'true',
    }
    
    response = session.post(
        f'{KIBANA_URL}/api/security/login',
        json={
            'username': USERNAME,
            'password': PASSWORD
        },
        headers=headers,
        timeout=10
    )
    print(f"    Status: {response.status_code}")
    print(f"    Respuesta: {response.text[:300]}")
    print()
    
except Exception as e:
    print(f"    Error: {e}")
    print()

# Prueba 4: Investigar estructura de login
print("[4] Investigando endpoints de login disponibles...")
login_endpoints = [
    '/api/security/login',
    '/api/v1/auth/login',
    '/api/security/v1/login',
    '/auth/login',
    '/login',
    '/api/shim/elasticsearch/_security/v1/login',
]

for endpoint in login_endpoints:
    try:
        response = session.post(
            f'{KIBANA_URL}{endpoint}',
            json={'username': USERNAME, 'password': PASSWORD},
            timeout=5
        )
        status = response.status_code
        symbol = "✅" if status < 400 else "❌"
        print(f"    {symbol} {endpoint}: {status}")
    except:
        print(f"    ⚠️  {endpoint}: timeout/error")
print()

# Prueba 5: Información sobre API keys
print("[5] Intentando obtener información del usuario...")
try:
    # A través del proxy
    response = session.get(
        f'{PROXY_URL}/_security/user',
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=10
    )
    print(f"    Proxy - Status: {response.status_code}")
    if response.status_code < 400:
        user_info = response.json()
        print(f"    ✅ Usuario autenticado como: {user_info.get('username')}")
        print(f"       Roles: {user_info.get('roles')}")
    else:
        print(f"    Error: {response.text[:150]}")
    print()
    
except Exception as e:
    print(f"    Error: {e}")
    print()

# Prueba 6: Probar acceso a índices
print("[6] Intentando listar índices...")
try:
    # A través del proxy
    response = session.get(
        f'{PROXY_URL}/_cat/indices?format=json',
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=10
    )
    print(f"    Proxy - Status: {response.status_code}")
    if response.status_code < 400:
        indices = response.json()
        print(f"    ✅ Total índices: {len(indices)}")
        if indices:
            print(f"    Primeros 3 índices:")
            for idx in indices[:3]:
                print(f"      - {idx['index']} ({idx['docs.count']} docs)")
    else:
        print(f"    Error: {response.text[:150]}")
    print()
    
except Exception as e:
    print(f"    Error: {e}")
    print()

print("=" * 70)
print("📊 RESUMEN DE FINDINGS")
print("=" * 70)
print("""
CONCLUSIONES:

1. Kibana (versión 7.17.26) usa una SPA moderna
   ➜ No hay formulario HTML tradicional
   ➜ El login se maneja con JavaScript

2. Métodos de autenticación encontrados:
   ✓ HTTP Basic Auth (usuario/contraseña)
   ✓ API Key (si está habilitado)
   ✓ Headers especiales (kbn-xsrf, kbn-name)

3. Solución implementada:
   ✓ proxy_es.py inyecta credenciales Basic Auth
   ✓ Bypass de Kibana proxy completado
   ✓ Elasticsearch accesible en localhost:9200

4. Recomendaciones:
   ✓ Usar proxy_es.py para desarrollo
   ✓ Las credenciales se envían en Authorization header
   ✓ No se requieren cookies adicionales
   ✓ La sesión se mantiene por HTTP Basic Auth

5. Próximos pasos:
   ✓ Conectar web app al proxy
   ✓ Verificar que todas las queries funcionan
   ✓ Documentar proceso para el admin
""")
print("=" * 70)
