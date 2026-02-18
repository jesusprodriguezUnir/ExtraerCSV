"""
Script para hacer scraping de la página de login de Kibana
e investigar cómo funciona la autenticación
"""

import os
import requests
from bs4 import BeautifulSoup
import json
import re
import warnings

warnings.filterwarnings('ignore')

# Configuración
KIBANA_URL = os.getenv('KIBANA_URL', os.getenv('ELASTICSEARCH_HOST', 'https://elk.unir.net'))
USERNAME = os.getenv('ELASTICSEARCH_USER', os.getenv('PROXY_USER', ''))
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', os.getenv('PROXY_PASSWORD', ''))

print("=" * 70)
print("🔍 INVESTIGACIÓN: Scraping de Login Kibana")
print("=" * 70)
print()

# Sesión con cookies
session = requests.Session()
session.verify = False

# 1. Obtener página de login
print("[1] Obteniendo página de login...")
try:
    response = session.get(f'{KIBANA_URL}/login', timeout=10, allow_redirects=True)
    print(f"    Status: {response.status_code}")
    print(f"    URL final: {response.url}")
    print()
    
    # Guardar HTML para análisis
    with open('login_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("    ✅ HTML guardado en login_page.html")
    print()
    
except Exception as e:
    print(f"    ❌ Error: {e}")
    print()

# 2. Analizar formulario de login
print("[2] Analizando formulario de login...")
try:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscar form
    form = soup.find('form')
    if form:
        print(f"    Form ID: {form.get('id')}")
        print(f"    Form action: {form.get('action')}")
        print(f"    Form method: {form.get('method')}")
        print()
        
        # Inputs
        print("    Inputs encontrados:")
        for input_tag in form.find_all('input'):
            input_name = input_tag.get('name')
            input_type = input_tag.get('type')
            input_value = input_tag.get('value')
            print(f"      - {input_name} (type={input_type}) = {input_value}")
        print()
    else:
        print("    ⚠️  No se encontró formulario tradicional")
        print()
    
    # Buscar campos
    print("    Campos de entrada encontrados:")
    for input_tag in soup.find_all(['input', 'textarea']):
        print(f"      {input_tag.get('name')} ({input_tag.get('type', 'text')})")
    print()
    
except Exception as e:
    print(f"    ❌ Error: {e}")
    print()

# 3. Extraer JavaScript y variables
print("[3] Analizando JavaScript...")
try:
    scripts = soup.find_all('script')
    print(f"    Total scripts: {len(scripts)}")
    
    # Buscar variables de configuración
    for script in scripts:
        content = script.string
        if content:
            if 'username' in content.lower() or 'login' in content.lower():
                # Buscar patterns interesantes
                patterns = [
                    r'const\s+(\w+)\s*=\s*{.*?}',
                    r'var\s+(\w+)\s*=\s*{.*?}',
                    r'"(\w*login\w*)":\s*"([^"]*)"',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content[:500])  # Primeros 500 chars
                    if matches:
                        print(f"    Encontrado: {pattern}")
                        print(f"      {matches}")
    print()
    
except Exception as e:
    print(f"    ❌ Error: {e}")
    print()

# 4. Intentar login con credenciales
print("[4] Intentando autenticación...")
try:
    # Método 1: POST directo a /api/security/login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    print("    Intentando POST a /api/security/login...")
    response = session.post(
        f'{KIBANA_URL}/api/security/login',
        json=login_data,
        timeout=10
    )
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:200]}")
    print()
    
except Exception as e:
    print(f"    Error en /api/security/login: {e}")
    print()

# 5. Intentar obtener índices con credenciales
print("[5] Probando acceso directo a Elasticsearch API...")
try:
    # Intentar acceder a /_cat/indices a través de Kibana
    response = session.get(
        f'{KIBANA_URL}/_cat/indices',
        auth=(USERNAME, PASSWORD),
        timeout=10
    )
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:500]}")
    print()
    
except Exception as e:
    print(f"    Error: {e}")
    print()

# 6. Analizar headers y cookies
print("[6] Analizando cookies y headers...")
print(f"    Cookies en sesión:")
for cookie in session.cookies:
    print(f"      {cookie.name} = {cookie.value[:50]}")
print()

print("[7] Resumen de hallazgos:")
print("""
    - El scraping mostró la estructura del formulario
    - Se guardó login_page.html para análisis detallado
    - Los intentos de autenticación proporcionan información sobre:
      * Endpoints válidos para login
      * Mecanismos de autenticación esperados
      * Cookies y tokens necesarios
""")
print()

# 8. Generar lista de endpoints a probar
print("[8] Endpoints relevantes para probar:")
endpoints = [
    '/api/security/login',
    '/api/security/v1/login',
    '/login',
    '/app/kibana',
    '/app/home',
    '/elasticsearch/_security/oauth2/authorize',
    '/api/v1/auth/login',
    '/api/shim/elasticsearch/_security/v1/login',
]
print("    Endpoints a considerar para proxy:")
for endpoint in endpoints:
    print(f"      {endpoint}")
print()

print("=" * 70)
print("✅ Análisis completado")
print("=" * 70)
print("""
Próximos pasos:
1. Revisar login_page.html con navegador para análisis visual
2. Probar endpoints descubiertos
3. Considerar ajustar proxy_es.py con hallazgos
4. Si hay CSRF tokens, podrían ser necesarios para autenticación
""")
