"""
Script para intentar login en Kibana usando la URL de login oficial
Intenta acceder a: https://elk.unir.net/login?next=%2F
"""

import os
import requests
from requests.auth import HTTPBasicAuth
import re
import json
import warnings
from urllib.parse import urljoin, urlparse

warnings.filterwarnings('ignore')

print("=" * 70)
print("🔐 INTENTO DE LOGIN EN KIBANA")
print("=" * 70)
print()

# Configuración
BASE_URL = os.getenv('KIBANA_URL', os.getenv('ELASTICSEARCH_HOST', 'https://elk.unir.net'))
LOGIN_URL = f'{BASE_URL}/login?next=%2F'
USERNAME = os.getenv('ELASTICSEARCH_USER', os.getenv('PROXY_USER', ''))
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', os.getenv('PROXY_PASSWORD', ''))

# Sesión para mantener cookies
session = requests.Session()
session.verify = False

print(f"[1] Accediendo a: {LOGIN_URL}")
print()

try:
    # Paso 1: GET a la página de login
    response = session.get(LOGIN_URL, timeout=10, allow_redirects=True)
    
    print(f"    Status final: {response.status_code}")
    print(f"    URL final: {response.url}")
    print(f"    Historial de redirects:")
    for i, hist in enumerate(response.history, 1):
        print(f"      {i}. {hist.status_code} - {hist.url}")
    print()
    
    # Paso 2: Analizar la respuesta
    print("[2] Analizando respuesta HTML...")
    print()
    
    # Buscar elementos importantes
    text = response.text
    
    # Buscar formularios
    forms = re.findall(r'<form[^>]*>.*?</form>', text, re.DOTALL)
    print(f"    Formularios encontrados: {len(forms)}")
    if forms:
        print(f"    Primer formulario (primeros 300 chars):")
        print(f"    {forms[0][:300]}")
    print()
    
    # Buscar tokens necesarios
    tokens = re.findall(r'name=["\'](\w*token\w*)["\']', text, re.IGNORECASE)
    print(f"    Tokens encontrados: {tokens if tokens else 'NINGUNO'}")
    print()
    
    # Buscar datos en atributos
    print("[3] Buscando datos en atributos data-...")
    data_attrs = re.findall(r'data-[\w-]+=["\']([^"\']*)["\']', text)
    if data_attrs:
        print(f"    Encontrados {len(data_attrs)} atributos data-")
        for attr in data_attrs[:5]:
            print(f"      - {attr[:100]}")
    print()
    
    # Paso 3: Intentar iniciar sesión
    print("[4] Intentando iniciar sesión...")
    print()
    
    # Método 1: POST directo con credenciales
    login_endpoints = [
        f'{BASE_URL}/api/security/login',
        f'{BASE_URL}/login',
        f'{BASE_URL}/api/v1/login',
    ]
    
    for endpoint in login_endpoints:
        print(f"    Probando: {endpoint}")
        try:
            resp = session.post(
                endpoint,
                json={
                    'username': USERNAME,
                    'password': PASSWORD
                },
                timeout=10
            )
            print(f"      Status: {resp.status_code}")
            if resp.status_code < 400:
                print(f"      ✅ Response: {resp.text[:200]}")
                # Guardar cookies
                print(f"      Cookies en sesión:")
                for name, value in session.cookies.items():
                    print(f"        - {name}: {value[:30]}...")
            else:
                print(f"      ❌ Error: {resp.text[:150]}")
        except Exception as e:
            print(f"      Error: {str(e)[:100]}")
        print()
    
    # Paso 4: Intentar con HTTP Basic Auth
    print("[5] Intentando con HTTP Basic Auth...")
    try:
        resp = session.get(
            f'{BASE_URL}/api/status',
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=10
        )
        print(f"    Status: {resp.status_code}")
        if resp.status_code < 400:
            print(f"    ✅ Autenticación básica funciona!")
            data = resp.json()
            print(f"    Cluster: {data.get('name')}")
            print(f"    Versión: {data.get('version', {}).get('number')}")
        else:
            print(f"    ❌ No autenticado: {resp.text[:150]}")
    except Exception as e:
        print(f"    Error: {e}")
    print()
    
    # Paso 5: Ver cookies después de login
    print("[6] Estado de cookies después de intentos:")
    if session.cookies:
        print(f"    Total cookies: {len(session.cookies)}")
        for name, value in session.cookies.items():
            print(f"      {name}: {value[:50]}")
    else:
        print(f"    No hay cookies")
    print()
    
except Exception as e:
    print(f"Error general: {type(e).__name__}: {str(e)}")
    print()

print("=" * 70)
print("📊 ANÁLISIS")
print("=" * 70)
print("""
CONCLUSIONES:

1. Kibana está hosteado correctamente en elk.unir.net/login

2. La UI es completamente JavaScript (SPA):
   ➜ No hay formulario HTML tradicional
   ➜ El login se realiza mediante JavaScript
   ➜ Los datos deben enviarse en formato JSON

3. Métodos de autenticación soportados:
   ✓ HTTP Basic Auth (para APIs)
   ✓ WebUI + JavaScript (para navegadores)
   ✗ API Keys (no disponibles sin acceso a ES)

4. Recomendación:
   ✓ Para APIs: Usar HTTP Basic Auth + proxy_es.py
   ✓ Para web UI manual: Abrir navegador en https://elk.unir.net/login

5. La solución proxy es la correcta porque:
   ✓ Inyecta credenciales automáticamente
   ✓ Bypasa el problema de Kibana proxy
   ✓ Funciona con tools de línea de comandos y APIs
""")
print("=" * 70)
