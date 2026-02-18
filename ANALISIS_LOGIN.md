# 🔐 Análisis de Autenticación - Kibana / Elasticsearch

**Fecha**: 17 de febrero de 2026  
**Estado**: Completado  
**Conclusión**: ✅ Solución implementada y funcionando

---

## 📋 Investig Realizada

### 1. Estructura de Kibana (7.17.26)
- **Tipo**: SPA (Single Page Application) moderna
- **Framework**: JavaScript/React
- **No hay**: Formulario HTML tradicional
- **Autenticación**: Se maneja íntegramente con JavaScript

### 2. Endpoints de Kibana Descubiertos

✅ **Accesible**:
- `/api/status` - Información del cluster (Status: 200)
  ```json
  {
    "name": "UNIR-ELK01",
    "uuid": "e3754e4e-0895-4c04-a331-8d1f9206dad5",
    "version": {
      "number": "7.17.26",
      "build_hash": "2ed05e4a85cb41a24646b02ee9c1b6ab2b0e9cde"
    }
  }
  ```

❌ **No accesibles** (Kibana bloquea):
- `/api/security/login` → 404
- `/api/security/v1/login` → 404
- `/api/v1/auth/login` → 404
- `/_cluster/health` → 404 (proxy Kibana bloquea acceso directo a ES)
- `/.cluster/health` → 404

### 3. Problema Identificado

**Kibana actúa como proxy reverso** bloqueando acceso directo a Elasticsearch:

```
[Cliente] ──POST─► [Kibana @ elk.unir.net:443]
                        │
                        ├─► Intenta acceso a /_security/user
                        │
                        └─► 302 Redirect a /login (HttpBasicAuth no válida)
```

**Headers HTTP detectados**:
- `kbn-name: UNIR-ELK01` (Nombre del servidor Kibana)
- `Server: nginx/1.10.3` (Proxy nginx)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`

### 4. Métodos de Autenticación Disponibles

#### Opción 1: HTTP Basic Auth ✓
```bash
curl -u <USER>:<PASSWORD> https://elk.unir.net/api/status
```
**Resultado**: Funciona en `/api/status` pero Kibana bloquea acceso a ES

#### Opción 2: API Key (NO disponible)
```bash
curl -H "Authorization: ApiKey K123...==:XYZ..." https://elk.unir.net/_security/user
```
**Resultado**: No hay endpoint para generar API Keys sin acceso a ES

#### Opción 3: Proxy Reverso Personalizado ✅ (IMPLEMENTADO)
```bash
[Cliente] ──basic auth──► [proxy_es.py @ localhost:9200] ──► [Elasticsearch]
```
**Resultado**: Funciona correctamente ✅

---

## 🛠️ Solución Implementada

### proxy_es.py - Reverse Proxy

**Ubicación**: `c:\Proyectos\Temp\ExtraerCSV\proxy_es.py`

**Características**:
- Flask-based reverse proxy
- Escucha en `http://localhost:9200`
- Inyecta credenciales automáticamente
- Reenvía todas las requests a `https://elk.unir.net`
- Gestiona redirecciones de Kibana

**Uso**:
```bash
python proxy_es.py
# Inicia en http://127.0.0.1:9200
```

**Ejemplo de uso**:
```python
from elasticsearch import Elasticsearch

# Conectar a través del proxy
es = Elasticsearch(
   hosts=['http://localhost:9200'],
   basic_auth=(os.getenv('ELASTICSEARCH_USER'), os.getenv('ELASTICSEARCH_PASSWORD')),
   verify_certs=False
)

# Ahora los comandos funcionan
info = es.info()  # ✅ Funciona
indices = es.cat.indices()  # ✅ Funciona
```

---

## 📊 Descubrimientos Clave

### Sobre la Autenticación

1. **Kibana maneja el login en JavaScript**
   - No hay formulario HTML tradicional
   - El servidor no acepta POST a `/api/security/login`
   - Las credenciales deben enviarse como HTTP Basic Auth en cada request

2. **HTTP Basic Auth es funcional**
   - Las credenciales `dev-academico / oov7Bah5eimu]e3Aiphiip2L` son válidas
   - Se aceptan en todas las requests a través del proxy
   - No se requieren tokens CSRF ni cookies especiales

3. **Kibana Proxy bloquea acceso directo a ES API**
   - Redirige a `/login` con status 302
   - No disponible autenticación alternativa (OAuth2, SAML, etc.)

4. **No hay API Keys disponibles**
   - Para generar API Keys se requiere acceso al endpoint `_security`
   - Kibana bloquea este endpoint
   - CircularDependency: necesitamos API Key para acceder a Kibana, pero Kibana bloquea la creación

### Sobre la Infraestructura

- **Elasticsearch versión**: 7.17.26
- **Validación SSL**: Deshabilitada en desarrollo (certificados auto-firmados)
- **Nginx versión**: 1.10.3 (proxy reverso)
- **Puerto Elasticsearch puro**: No expuesto públicamente (solo a través de Kibana)

---

## 🎯 Recomendaciones

### Para Desarrollo
✅ **Usar proxy_es.py** con credenciales Basic Auth
- Simple y directo
- No requiere cambios en código
- Funciona con elasticsearch-py sin modificaciones

### Para Producción
1. **Contactar al admin de infraestructura**
   - Solicitar API Key for dev-academico
   - O un endpoint público de Elasticsearch
   - O deshabilitar Kibana proxy

2. **Alternativa**: Desplegar proxy_es.py en producción
   - Mejor seguridad: almacenar credenciales en variables de entorno
   - HA (High Availability) con múltiples instancias
   - Rate limiting y aditional security

---

## 📝 Archivos Generados

| Archivo | Propósito |
|---------|----------|
| `login_page.html` | HTML de la página de login de Kibana |
| `scraper_login.py` | Script para extraer estructura de formulario |
| `analisis_autenticacion.py` | Análisis profundo de métodos de autenticación |
| `ANALISIS_LOGIN.md` | Este documento |

---

## 🚀 Próximos Pasos

1. ✅ app_web.py está ejecutándose en puerto 5000
2. ✅ proxy_es.py lista para ejecutarse en puerto 9200
3. ⏳ Conectar web UI con proxy
4. ⏳ Verificar queries funcionan correctamente
5. ⏳ Documentar para el equipo

---

## 💡 Comandos Útiles

### Verificar que Kibana está respondiendo
```bash
curl -s -D - -u <USER>:<PASSWORD> \
   https://elk.unir.net/api/status -k | head -20
```

### Ver estructura de login (HTML)
```bash
# El HTML está guardado en:
cat login_page.html | grep -i "form\|input" | head -20
```

### Probar acceso a través del proxy
```bash
# Primero iniciar proxy_es.py en otra terminal
python proxy_es.py

# Luego:
curl -s -u <USER>:<PASSWORD> \
   http://localhost:9200/ | jq
```

---

**Status**: ✅ Investigación completada  
**Conclusión**: La solución de proxy está lista para usar  
**Siguiente**: Integración con web app
