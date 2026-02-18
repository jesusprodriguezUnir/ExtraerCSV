"""
Aplicación web Flask para conectar y consultar Elasticsearch
Proporciona interfaz web para:
- Login con credenciales de Elasticsearch o API Key
- Listar índices disponibles
- Ejecutar queries personalizadas
- Exportar resultados a JSON
"""

import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch
import warnings

warnings.filterwarnings('ignore')

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)


@app.route('/')
def index():
    """Página de login"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Página del dashboard"""
    return render_template('dashboard.html')


@app.route('/api/connect', methods=['POST'])
def api_connect():
    """
    Conectar con Elasticsearch con usuario/contraseña o API Key
    
    Con usuario/contraseña:
    {
        "host": "http://localhost:9200",
        "username": "usuario",
        "password": "contraseña",
        "index": "logs-*"
    }
    
    Con API Key:
    {
        "host": "https://elasticsearch.example.com",
        "apiKeyId": "K1234...",
        "apiKeySecret": "abcDEF...",
        "authType": "apikey",
        "index": "logs-*"
    }
    """
    try:
        data = request.get_json()
        host = data.get('host', '').rstrip('/')
        auth_type = data.get('authType', 'basic')
        
        if not host:
            return jsonify({'error': 'Host es requerido'}), 400
        
        print(f"\n[DEBUG] Conectando a: {host} con {auth_type}")
        
        try:
            # Crear cliente según tipo de autenticación
            if auth_type == 'apikey':
                # Autenticación con API Key
                api_key_id = data.get('apiKeyId')
                api_key_secret = data.get('apiKeySecret')
                
                if not api_key_id or not api_key_secret:
                    return jsonify({'error': 'API Key ID y Secret son requeridos'}), 400
                
                print(f"[DEBUG] Usando API Key: {api_key_id[:10]}...")
                
                es_client = Elasticsearch(
                    hosts=[host],
                    api_key=(api_key_id, api_key_secret),
                    verify_certs=False,
                    request_timeout=15
                )
            else:
                # Autenticación con usuario/contraseña
                username = data.get('username')
                password = data.get('password')
                
                if not username or not password:
                    return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
                
                print(f"[DEBUG] Usando usuario: {username}")
                
                es_client = Elasticsearch(
                    hosts=[host],
                    basic_auth=(username, password),
                    verify_certs=False,
                    request_timeout=15
                )
            
            # Probar conexión
            print(f"[DEBUG] Intentando obtener info del cluster...")
            info = es_client.info()
            
            cluster_name = info.get('cluster_name', 'desconocido')
            version = info.get('version', {}).get('number', 'desconocido')
            
            print(f"[DEBUG] ✅ Conectado a cluster: {cluster_name} v{version}")
            
            return jsonify({
                'status': 'connected',
                'cluster_name': cluster_name,
                'version': version,
                'auth_type': auth_type
            }), 200
            
        except Exception as inner_e:
            error_str = str(inner_e)
            print(f"[DEBUG] Error: {type(inner_e).__name__}: {error_str[:200]}")
            
            # Mensajes de error específicos
            if '401' in error_str or 'Unauthorized' in error_str or 'authentication' in error_str.lower():
                return jsonify({'error': f'❌ Error de autenticación: Verifica credenciales o API Key'}), 401
            elif '302' in error_str:
                return jsonify({'error': f'❌ Kibana interceptando: Usa proxy_es.py o contacta admin'}), 403
            elif 'Connection refused' in error_str or 'refused' in error_str.lower():
                return jsonify({'error': f'❌ No se puede conectar al servidor: Verifica host y puerto'}), 500
            else:
                return jsonify({'error': f'❌ Error: {error_str[:100]}'}), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Aplicación: {error_msg}")
        return jsonify({'error': f'Error: {error_msg[:100]}'}), 500


@app.route('/api/indices', methods=['POST'])
def api_indices():
    """
    Obtener lista de índices disponibles
    """
    try:
        data = request.get_json()
        auth_type = data.get('authType', 'basic')
        
        # Crear cliente
        if auth_type == 'apikey':
            es_client = Elasticsearch(
                hosts=[data['host']],
                api_key=(data['apiKeyId'], data['apiKeySecret']),
                verify_certs=False,
                request_timeout=10
            )
        else:
            es_client = Elasticsearch(
                hosts=[data['host']],
                basic_auth=(data['username'], data['password']),
                verify_certs=False,
                request_timeout=10
            )
        
        # Obtener índices
        try:
            indices_response = es_client.cat.indices(format='json')
        except:
            indices_response = []
        
        indices = sorted([idx['index'] for idx in indices_response])
        
        return jsonify({
            'indices': indices,
            'total': len(indices)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al cargar índices: {str(e)[:100]}'}), 500


@app.route('/api/search', methods=['POST'])
def api_search():
    """
    Ejecutar una query de Elasticsearch
    """
    try:
        data = request.get_json()
        auth_type = data.get('authType', 'basic')
        
        if not data.get('query'):
            return jsonify({'error': 'Query requerida'}), 400
        
        # Crear cliente
        if auth_type == 'apikey':
            es_client = Elasticsearch(
                hosts=[data['host']],
                api_key=(data['apiKeyId'], data['apiKeySecret']),
                verify_certs=False,
                request_timeout=30
            )
        else:
            es_client = Elasticsearch(
                hosts=[data['host']],
                basic_auth=(data['username'], data['password']),
                verify_certs=False,
                request_timeout=30
            )
        
        # Ejecutar query
        index = data.get('index', '*')
        response = es_client.search(
            index=index,
            body=data['query']
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en la query: {str(e)[:100]}'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Manejar rutas no encontradas"""
    return jsonify({'error': 'Ruta no encontrada'}), 404


@app.errorhandler(500)
def server_error(error):
    """Manejar errores del servidor"""
    return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   🌐 Servidor web - Extractor Elasticsearch           ║
    ║                                                        ║
    ║   📂 Acceder a: http://localhost:5000                 ║
    ║                                                        ║
    ║   💡 Usa proxy_es.py si Kibana bloquea               ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )
