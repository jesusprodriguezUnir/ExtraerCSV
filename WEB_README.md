# 🌐 Interfaz Web - Extractor Elasticsearch

Interfaz web moderna y amigable para conectar con Elasticsearch, explorar índices y ejecutar queries sin necesidad de herramientas externas.

## 🚀 Características

✅ **Autenticación segura** - Login con usuario y contraseña  
✅ **Explorador de índices** - Visualiza todos los índices disponibles  
✅ **Editor de queries** - Escribe queries JSON con autocompletado  
✅ **Visor de resultados** - Visualiza respuestas formateadas  
✅ **Exportación** - Descarga resultados a JSON  
✅ **Responsive** - Funciona en mobile, tablet y desktop  
✅ **Interfaz moderna** - Diseño limpio y profesional  

---

## 📋 Requisitos

```bash
python >= 3.9
flask >= 2.3.0
flask-cors >= 4.0.0
elasticsearch >= 8.11.0
python-dotenv >= 1.0.0
```

Instalar dependencias:
```bash
pip install -r requirements.txt
```

---

## 🔧 Configuración

### Opción 1: Variables de entorno (.env)

Crear archivo `.env` en la raíz del proyecto (copiar de `.env.example`):

```ini
ELASTICSEARCH_HOST=https://elk.unir.net
ELASTICSEARCH_USER=<USER>
ELASTICSEARCH_PASSWORD=<PASSWORD>
ELASTICSEARCH_INDEX=logs-*
```

### Opción 2: Credenciales en la interfaz

Simplemente ingresa las credenciales en el formulario de login.

---

## ▶️ Ejecución

### Opción 1: Servidor web completo

```bash
python app_web.py
```

Luego accede a: **http://localhost:5000**

### Opción 2: Con Gunicorn (producción)

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app_web:app
```

### Opción 3: Con variables de entorno

```bash
python app_web.py
```

La aplicación cargará automáticamente las credenciales de `.env`.

---

## 🖥️ Interfaz de usuario

### Pantalla de Login

Al iniciar, se muestra un formulario con campos:
- **Servidor Elasticsearch** - URL completa (ej: https://elk.unir.net)
- **Usuario** - Nombre de usuario con permisos
- **Contraseña** - Contraseña del usuario
- **Patrón de índices** - Patrón para filtrar (ej: logs-*, logs-app-*)

Botones:
- **Conectar** - Establece conexión y valida credenciales
- **ℹ️ Credenciales de ejemplo** - Carga los datos de prueba

### Panel de Control (Dashboard)

Una vez conectado, verás:

#### Sección Izquierda: Índices
```
📑 Índices disponibles
├─ logs-2024.02.15
├─ logs-2024.02.16
├─ logs-2024.02.17
└─ logs-aplicacion
```

Haz clic en un índice para precargar una query de ejemplo.

#### Sección Central: Editor de Query
```json
{
  "query": {
    "bool": {
      "must": [
        { "match_all": {} }
      ]
    }
  },
  "size": 100,
  "_source": ["@timestamp", "message"]
}
```

Atajos:
- **Ctrl + Enter** - Ejecuta la query rápidamente
- **VerQuery ejemplo** - Carga una query base

#### Sección Inferior: Resultados
- Número total de documentos encontrados
- Tiempo de ejecución en ms
- Vista de árbol de resultados

---

## 📚 Ejemplos de uso

### Query simple - Buscar todos

```json
{
  "query": {
    "match_all": {}
  },
  "size": 50
}
```

### Query con filtro por timestamp

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "range": {
            "@timestamp": {
              "gte": "2024-02-15T00:00:00Z",
              "lte": "2024-02-16T23:59:59Z"
            }
          }
        }
      ]
    }
  },
  "size": 100
}
```

### Query de búsqueda en mensaje

```json
{
  "query": {
    "match": {
      "message": "error"
    }
  },
  "size": 100,
  "_source": ["@timestamp", "message", "level"]
}
```

### Query agregada

```json
{
  "aggs": {
    "logs_por_nivel": {
      "terms": {
        "field": "level.keyword",
        "size": 10
      }
    }
  },
  "size": 0
}
```

---

## 🔐 Seguridad

### Consideraciones de seguridad

⚠️ **IMPORTANTE**: Esta es una interfaz de desarrollo/testing.

Para producción:
- ✅ Usar HTTPS obligatoriamente
- ✅ Implementar autenticación robusta
- ✅ No guardar credenciales en sesiones del cliente
- ✅ Usar variables de entorno (no hardcodear)
- ✅ Validar todas las queries en el servidor
- ✅ Limitar tamaño de respuestas
- ✅ Implementar rate limiting

### Credenciales

- Las credenciales se envían **solo a través de sessionStorage** (solo en la sesión actual)
- No se guardan en localStorage ni cookies
- Se pierde al cerrar la pestaña

---

## 🛠️ Estructura de archivos

```
├── app_web.py                 # Servidor Flask (puntoentrada)
├── templates/
│   ├── index.html             # Página de login
│   └── dashboard.html         # Panel principal
├── static/
│   └── style.css              # Estilos CSS
├── config.py                  # Gestión de configuración
├── elasticsearch_client.py    # Cliente de Elasticsearch
├── requirements.txt           # Dependencias
└── .env.example              # Template de .env
```

---

## 🐛 Troubleshooting

### "No se puede conectar a Elasticsearch"

Verifica:
- ✓ URL correcta (incluye https://)
- ✓ Firewall permite conexión
- ✓ Credenciales correctas
- ✓ Red accesible desde tu máquina

### "Credenciales incorrectas"

- Verifica usuario y contraseña
- Comprueba que el usuario tiene permisos de lectura
- Si usas LDAP, valida contra el servidor LDAP

### "Índices no se cargan"

- Verifica que el usuario tenga permisos en `_cat/indices`
- Comprueba el patrón de índices (usar * para todas)
- Revisa que hay índices disponibles en Elasticsearch

### Slow performance

- Reduce el tamaño de la query (parámetro `size`)
- Usa filtros más específicos
- Agrega `_source` para limitar campos devueltos

---

## 📝 API REST

La aplicación expone endpoints REST internos:

### POST `/api/connect`
Conecta con Elasticsearch y valida credenciales

```bash
curl -X POST http://localhost:5000/api/connect \
  -H "Content-Type: application/json" \
  -d '{
    "host": "https://elk.unir.net",
    "username": "usuario",
    "password": "contraseña",
    "index": "logs-*"
  }'
```

### POST `/api/indices`
Obtiene lista de índices disponibles

```bash
curl -X POST http://localhost:5000/api/indices \
  -H "Content-Type: application/json" \
  -d '{
    "host": "...",
    "username": "...",
    "password": "...",
    "index": "logs-*"
  }'
```

### POST `/api/search`
Ejecuta una query

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "host": "...",
    "username": "...",
    "password": "...",
    "index": "logs-*",
    "query": {
      "match_all": {}
    }
  }'
```

---

## 📊 Exportación

Los resultados se pueden exportar a JSON:

1. Ejecuta una query
2. Haz clic en **💾 Exportar JSON**
3. Se descargará un archivo `elasticsearch_results_TIMESTAMP.json`

---

## 🤝 Contribuciones

Para mejorar la interfaz:
1. Modifica `static/style.css` para estilos
2. Actualiza `templates/` para UI
3. Edita `app_web.py` para endpoints

---

## 📞 Soporte

Si encuentras problemas:
1. Verifica los requisitos de sistema
2. Revisa logs del servidor Flask
3. Activa modo debug en `app_web.py`

---

**Versión:** 1.0.0  
**Última actualización:** 17 de febrero de 2026  
**Autor:** Extractor CSV - Elasticsearch Integration
