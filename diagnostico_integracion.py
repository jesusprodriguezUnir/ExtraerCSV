"""
Script de diagnóstico para integración
Identifica exactamente dónde falla la cadena
"""

import os
import requests
import json
import warnings
import sys
from concurrent.futures import ThreadPoolExecutor
import time

warnings.filterwarnings('ignore')

print("=" * 70)
print("🔧 DIAGNÓSTICO DE INTEGRACIÓN")
print("=" * 70)
print()

# URLs
PROXY = os.getenv('PROXY_URL', 'http://localhost:9200')
KIBANA = os.getenv('KIBANA_URL', os.getenv('ELASTICSEARCH_HOST', 'https://elk.unir.net'))
WEB_APP = os.getenv('WEB_APP_URL', 'http://localhost:5000')
USERNAME = os.getenv('ELASTICSEARCH_USER', os.getenv('PROXY_USER', ''))
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', os.getenv('PROXY_PASSWORD', ''))

# Test 1: Conectividad básica a proxy
print("[1] Conectividad básica al proxy (localhost:9200)...")
try:
    response = requests.get(f'{PROXY}/health', timeout=3)
    if response.status_code == 200:
        print(f"    ✅ Proxy responde: {response.json()}")
    else:
        print(f"    ⚠️  Status {response.status_code}")
except requests.exceptions.Timeout:
    print(f"    ❌ TIMEOUT - El proxy no responde en 3 segundos")
except requests.exceptions.ConnectionError as e:
    print(f"    ❌ CONEXIÓN RECHAZADA - El proxy no está escuchando")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:80]}")
print()

# Test 2: Conectividad directa a Kibana (para comparar)
print("[2] Conectividad a Kibana (elk.unir.net) directamente...")
try:
    response = requests.get(
        f'{KIBANA}/api/status',
        auth=(USERNAME, PASSWORD),
        timeout=5,
        verify=False
    )
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Kibana responde: {data.get('name')} v{data.get('version', {}).get('number')}")
    else:
        print(f"    ⚠️  Status {response.status_code}: {response.text[:100]}")
except requests.exceptions.Timeout:
    print(f"    ❌ TIMEOUT en Kibana (5 segs)")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:80]}")
print()

# Test 3: Acceso a proxy sin autenticación (test rápido)
print("[3] Test de proxy a / (sin auth)...")
try:
    response = requests.get(
        f'{PROXY}/',
        timeout=3,
        verify=False
    )
    print(f"    Status: {response.status_code}")
    if response.status_code < 500:
        print(f"    Response (primeros 150 chars): {response.text[:150]}")
except requests.exceptions.Timeout:
    print(f"    ❌ TIMEOUT - El proxy tarda demasiado en responder")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:80]}")
print()

# Test 4: Acceso a proxy CON autenticación
print("[4] Test de proxy a / (CON auth)...")
try:
    response = requests.get(
        f'{PROXY}/',
        auth=(USERNAME, PASSWORD),
        timeout=5,
        verify=False
    )
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Proxy info cluster:")
        print(f"       Name: {data.get('cluster_name')}")
        print(f"       Version: {data.get('version', {}).get('number')}")
    elif response.status_code == 302:
        print(f"    ⚠️  Redirect 302: {response.headers.get('Location')}")
    else:
        print(f"    Response: {response.text[:150]}")
except requests.exceptions.Timeout:
    print(f"    ❌ TIMEOUT (5 segs) - El proxy tarda en reenviar")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:80]}")
print()

# Test 5: Acceso a web app
print("[5] Conectividad a web app (localhost:5000)...")
try:
    response = requests.get(f'{WEB_APP}/', timeout=3)
    if response.status_code == 200:
        print(f"    ✅ Web app responde (HTML de login)")
    else:
        print(f"    ⚠️  Status {response.status_code}")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:80]}")
print()

# Test 6: Hacer POST a api/connect CON PROXY
print("[6] Prueba de /api/connect (con proxy localhost:9200)...")
try:
    payload = {
        'host': 'http://localhost:9200',
        'username': USERNAME,
        'password': PASSWORD,
        'authType': 'basic'
    }
    
    response = requests.post(
        f'{WEB_APP}/api/connect',
        json=payload,
        timeout=15
    )
    
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ CONEXIÓN EXITOSA:")
        print(f"       {json.dumps(data, indent=2)}")
    else:
        print(f"    Error: {response.text[:200]}")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:80]}")
print()

# Test 7: Hacer POST a api/connect SIN PROXY (directo a Kibana)
print("[7] Prueba de /api/connect (sin proxy, directo a Kibana)...")
try:
    payload = {
        'host': 'https://elk.unir.net',
        'username': USERNAME,
        'password': PASSWORD,
        'authType': 'basic'
    }
    
    response = requests.post(
        f'{WEB_APP}/api/connect',
        json=payload,
        timeout=15
    )
    
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Conexión sin proxy: {data}")
    else:
        print(f"    Error: {response.text[:200]}")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:80]}")
print()

print("=" * 70)
print("📌 RESUMEN DE DIAGNÓSTICO")
print("=" * 70)
print("""
COMPONENTES:
├─ ✅ Proxy (port 9200)      ← responde a /health
├─ ✅ Web App (port 5000)     ← responde a /
├─ ⚠️  Kibana (elk.unir.net)  ← responde directo OK
└─ ⚠️  Proxy → Kibana        ← posible latencia

PROBLEMAS POSIBLES:
1. Proxy tarda en forwarding a Kibana (timeout 30s)
2. Autenticación Basic Auth no se está inyectando correctamente
3. Redirección 302 de Kibana no se maneja bien
4. Certificados SSL causan problemas

RECOMENDACIÓN:
- Revisar logs de proxy_es.py
- Aumentar timeout de requests
- Considerar usar curl directamente contra proxy
""")
print("=" * 70)
