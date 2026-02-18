#!/usr/bin/env python3
"""
Proxy reverso local para acceder a Elasticsearch
Bypassea el proxy de Kibana

Uso:
  python proxy_es.py
  
Luego conectar a:
  http://localhost:9200  (en lugar de https://elk.unir.net)
"""

from flask import Flask, request, Response
import requests
from requests.auth import HTTPBasicAuth
import warnings
from urllib.parse import urljoin
import os
import sys

warnings.filterwarnings('ignore')

# Leer configuración desde variables de entorno (usar .env al arrancar)
TARGET_HOST = os.getenv('PROXY_TARGET_HOST', os.getenv('ELASTICSEARCH_HOST', 'https://elk.unir.net'))
TARGET_PORT = int(os.getenv('PROXY_TARGET_PORT', os.getenv('ELASTICSEARCH_PORT', '443')))
PROXY_PORT = int(os.getenv('PROXY_LISTEN_PORT', '9200'))
PROXY_HOST = os.getenv('PROXY_LISTEN_HOST', '127.0.0.1')

# Credenciales (mover a .env; evitar hardcode en el repo)
USERNAME = os.getenv('PROXY_USER', os.getenv('ELASTICSEARCH_USER', ''))
PASSWORD = os.getenv('PROXY_PASSWORD', os.getenv('ELASTICSEARCH_PASSWORD', ''))

# Opciones
VERIFY_SSL = os.getenv('PROXY_VERIFY_SSL', os.getenv('ELASTICSEARCH_VERIFY_SSL', 'false')).lower() == 'true'
TIMEOUT = int(os.getenv('PROXY_TIMEOUT', '30'))

app = Flask(__name__)

# Headers a pasar
PASS_HEADERS = [
    'Content-Type',
    'Accept',
    'User-Agent',
    'Accept-Encoding',
    'Accept-Language',
]


def log_request(method, path, status):
    """Log de requests"""
    print(f"[{method:6}] {path:50} → {status}")


@app.before_request
def check_auth():
    """Verificar autenticación básica"""
    auth = request.authorization
    if auth and auth.username == USERNAME and auth.password == PASSWORD:
        return None
    elif not request.path.startswith('/health'):
        # Si la solicitud no es /health y no tiene auth, permitir paso
        # porque iremos con las credenciales del proxy
        pass
    return None


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'])
def proxy(path):
    """Proxy todas las requests"""
    
    # Construir URL destino
    url = urljoin(f'{TARGET_HOST}:{TARGET_PORT}/', path)
    
    # Agregar query string
    if request.query_string:
        url = f"{url}?{request.query_string.decode()}"
    
    # Preparar headers
    headers = {}
    for header in PASS_HEADERS:
        if header in request.headers:
            headers[header] = request.headers[header]
    
    # Agregar headers adicionales
    headers['Host'] = 'elk.unir.net'
    
    try:
        # Hacer request forwarded
        session = requests.Session()
        session.verify = VERIFY_SSL
        # Session respetará variables de entorno si trust_env=True (por defecto True)
        if request.method == 'GET':
            resp = session.get(
                url,
                headers=headers,
                auth=HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME else None,
                timeout=TIMEOUT,
                allow_redirects=False
            )
        elif request.method == 'POST':
            resp = session.post(
                url,
                data=request.get_data(),
                headers=headers,
                auth=HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME else None,
                timeout=TIMEOUT,
                allow_redirects=False
            )
        elif request.method == 'PUT':
            resp = session.put(
                url,
                data=request.get_data(),
                headers=headers,
                auth=HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME else None,
                timeout=TIMEOUT,
                allow_redirects=False
            )
        elif request.method == 'DELETE':
            resp = session.delete(
                url,
                headers=headers,
                auth=HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME else None,
                timeout=TIMEOUT,
                allow_redirects=False
            )
        elif request.method == 'PATCH':
            resp = session.patch(
                url,
                data=request.get_data(),
                headers=headers,
                auth=HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME else None,
                timeout=TIMEOUT,
                allow_redirects=False
            )
        elif request.method == 'HEAD':
            resp = session.head(
                url,
                headers=headers,
                auth=HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME else None,
                timeout=TIMEOUT,
                allow_redirects=False
            )
        
        # Log
        log_request(request.method, f"/{path}", resp.status_code)
        
        # Retornar respuesta
        return Response(
            resp.content,
            status=resp.status_code,
            headers=dict(resp.headers),
            mimetype=resp.headers.get('Content-Type', 'application/json')
        )
        
    except requests.exceptions.RequestException as e:
        log_request(request.method, f"/{path}", "ERROR")
        print(f"  Error: {str(e)[:100]}")
        return Response(
            f'{{"error": "Proxy error: {str(e)}"}}',
            status=502,
            mimetype='application/json'
        )
    except Exception as e:
        log_request(request.method, f"/{path}", "ERROR")
        print(f"  Error: {str(e)[:100]}")
        return Response(
            f'{{"error": "Internal error: {str(e)}"}}',
            status=500,
            mimetype='application/json'
        )


@app.route('/health', methods=['GET'])
def health():
    """Health check del proxy"""
    return {'status': 'proxy_ok', 'target': TARGET_HOST}, 200


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════╗
║          🔗 PROXY REVERSO - ELASTICSEARCH                      ║
╚════════════════════════════════════════════════════════════════╝

📍 Servidor origen : {target}
🖥️  Puerto proxy    : {proxy_port}
🔐 Usuario         : {user}

Acceso:
  http://127.0.0.1:{proxy_port}/
  
Ejemplos:
  curl http://127.0.0.1:{proxy_port}/
  curl http://127.0.0.1:{proxy_port}/_cat/indices
  curl -X GET http://127.0.0.1:{proxy_port}/logs-*/_search -H 'Content-Type: application/json'

¡El proxy maneja automáticamente la autenticación!

═══════════════════════════════════════════════════════════════════
""".format(
        target=TARGET_HOST,
        proxy_port=PROXY_PORT,
        user=USERNAME
    ))
    
    app.run(
        host=PROXY_HOST,
        port=PROXY_PORT,
        debug=False,
        use_reloader=False
    )
