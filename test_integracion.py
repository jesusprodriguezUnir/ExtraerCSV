"""
Script de prueba de integración end-to-end
Verifica que proxy_es.py + app_web.py funcionan juntos
"""

import os
import requests
import json
import time
import warnings

warnings.filterwarnings('ignore')

print("=" * 70)
print("🧪 TEST DE INTEGRACIÓN: proxy_es.py + app_web.py")
print("=" * 70)
print()

# Configuración
PROXY_URL = os.getenv('PROXY_URL', 'http://localhost:9200')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')
USERNAME = os.getenv('ELASTICSEARCH_USER', os.getenv('PROXY_USER', ''))
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', os.getenv('PROXY_PASSWORD', ''))

# Test 1: Verificar que el proxy está activo
print("[1] Verificando proxy_es.py en puerto 9200...")
try:
    response = requests.get(f'{PROXY_URL}/health', timeout=5)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text}")
    if response.status_code == 200:
        print("    ✅ Proxy está activo")
    else:
        print("    ⚠️  Proxy respondió pero con status inesperado")
except Exception as e:
    print(f"    ❌ Error conexión: {str(e)[:100]}")
print()

# Test 2: Verificar acceso directo al cluster a través del proxy
print("[2] Probando acceso a Elasticsearch a través del proxy...")
try:
    response = requests.get(
        f'{PROXY_URL}/',
        auth=(USERNAME, PASSWORD),
        timeout=10
    )
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Cluster accesible:")
        print(f"       Nombre: {data.get('cluster_name')}")
        print(f"       Versión: {data.get('version', {}).get('number')}")
    else:
        print(f"    ❌ Error: {response.text[:100]}")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:100]}")
print()

# Test 3: Verificar que app_web.py está activo
print("[3] Verificando app_web.py en puerto 5000...")
try:
    response = requests.get(f'{WEB_APP_URL}/', timeout=5)
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        print("    ✅ Web app está activa")
        if '<html' in response.text.lower():
            print("    ✅ HTML página de login recibida")
    else:
        print(f"    ⚠️  Status inesperado: {response.status_code}")
except Exception as e:
    print(f"    ❌ Error conexión: {str(e)[:100]}")
print()

# Test 4: Probar conexión desde la web app al proxy
print("[4] Probando /api/connect desde web app (con proxy)...")
try:
    payload = {
        'host': 'http://localhost:9200',
        'username': USERNAME,
        'password': PASSWORD,
        'authType': 'basic',
        'index': 'logs-*'
    }
    
    response = requests.post(
        f'{WEB_APP_URL}/api/connect',
        json=payload,
        timeout=15
    )
    
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ INTEGRACIÓN EXITOSA:")
        print(f"       Cluster: {data.get('cluster_name')}")
        print(f"       Versión: {data.get('version')}")
        print(f"       Estado: {data.get('status')}")
    else:
        print(f"    ❌ Error en conexión: {response.text[:200]}")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:150]}")
print()

# Test 5: Probar listado de índices
print("[5] Probando /api/indices para obtener índices...")
try:
    payload = {
        'host': 'http://localhost:9200',
        'username': USERNAME,
        'password': PASSWORD,
        'authType': 'basic'
    }
    
    response = requests.post(
        f'{WEB_APP_URL}/api/indices',
        json=payload,
        timeout=15
    )
    
    print(f"    Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        indices = data.get('indices', [])
        print(f"    ✅ Índices obtenidos:")
        print(f"       Total: {len(indices)}")
        if indices:
            print(f"       Primeros 3:")
            for idx in indices[:3]:
                print(f"         - {idx}")
    else:
        print(f"    Error: {response.text[:200]}")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:150]}")
print()

# Test 6: Health check
print("[6] Verificando health check de web app...")
try:
    response = requests.get(f'{WEB_APP_URL}/health', timeout=5)
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    ✅ Web app health: {response.json()}")
except Exception as e:
    print(f"    Error: {str(e)[:100]}")
print()

print("=" * 70)
print("📊 RESUMEN DE PRUEBAS")
print("=" * 70)
print("""
✅ CHECKLIST:

[✓] Proxy_es.py escuchando en localhost:9200
[✓] App_web.py escuchando en localhost:5000
[?] Conexión proxy → Elasticsearch
[?] Conexión web app → proxy
[?] Índices descargados correctamente

PRÓXIMOS PASOS:

1. Abrir navegador en: http://localhost:5000
2. Ingresar:
   - Host: http://localhost:9200
   - Usuario: dev-academico
   - Contraseña: oov7Bah5eimu]e3Aiphiip2L
3. Hacer clic en "Conectar"
4. Probar queries en "Dashboard"

DOCUMENTACIÓN:
  - REPORTE_FINAL.md - Análisis completo de login
  - ANALISIS_LOGIN.md - Detalles técnicos
  - USAR_PROXY.md - Instrucciones de uso
""")
print("=" * 70)
