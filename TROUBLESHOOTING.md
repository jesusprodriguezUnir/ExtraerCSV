# 🔧 Guía de Troubleshooting - Conexión a Elasticsearch

## 🔴 Problema Detectado

Sistema: `elk.unir.net`
- **Kibana** está actuando como proxy reverso en el puerto 443
- Fuerza redirección a `/login` para todas las requests
- Incluso con credenciales correctas, Kibana intercepta

**Estado de puertos:**
- ✓ Puerto 9200: ABIERTO (Elasticsearch)
- ✓ Puerto 443: ABIERTO (Kibana)
- ✓ Puerto 9300: ABIERTO (cluster communication)

````markdown
# 🔧 Guía de Troubleshooting - Conexión a Elasticsearch

## 🔴 Problema Detectado

Sistema: `elk.unir.net`
- **Kibana** está actuando como proxy reverso en el puerto 443
- Fuerza redirección a `/login` para todas las requests
- Incluso con credenciales correctas, Kibana intercepta

**Estado de puertos:**
- ✓ Puerto 9200: ABIERTO (Elasticsearch)
- ✓ Puerto 443: ABIERTO (Kibana)
- ✓ Puerto 9300: ABIERTO (cluster communication)

---

## ✅ Soluciones posibles (en orden de facilidad)

### 🥇 Opción 1: Habla con el administrador (RECOMENDADO)

El administrador de Elasticsearch/Kibana debe hacer uno de esto:

**A) Exponer Elasticsearch sin Kibana en frente**
```
https://elasticsearch.unir.net:9200
```
O en un puerto diferente:
```
https://elk.unir.net:19200
```

**B) Crear un API Token/Key**
En Kibana > Stack Management > API Keys
- Más seguro que usuario/contraseña
- No requiere Kibana proxy

**C) Configurar endpoint específico en Kibana**
```
https://elk.unir.net/api/elasticsearch
```
Con autenticación integrada

---

### 🥈 Opción 2: Usar interfaz web de Kibana (Workaround temporal)

Mientras se resuelve con el admin, puedes:

1. **Acceder a Kibana normalmente en navegador:**
   ```
   https://elk.unir.net/
   ```
   (Te pedirá login)

2. **Ir a Dev Tools → Console**

3. **Ejecutar queries directamente ahí:**
   ```json
   GET /
   GET _cat/indices
   GET logs-*/_search
   ```

---

### 🥉 Opción 3: SSL Bypass avanzado

Si el servidor tiene certificado autofirmado mal configurado:

```bash
# En Windows PowerShell
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
```

Pero primero vamos a intentar un acceso más directo...

---

## 🛠️ Script mejorado de depuración

Voy a crear un script que intente acceso directo sin ir por HTTPS:

```python
python debug_es_advanced.py
```

Este probará:
- Directivas HTTP/HTTPS
- Con/sin SSL
- Diferentes parámetros de conexión

---

## 📋 Información para el administrador

Si envías esto al admin puede usar el template de request:

```bash
# Test directo a Elasticsearch (sin Kibana)
curl -k -u <USER>:<PASSWORD> https://elk.unir.net:9200/

# Debería responder con JSON del cluster, no con HTML de login
```

Si devuelve HTML con `<base href="/login/">`, confirma que Kibana está bloqueando.

---

## 🚀 Mientras tanto...

**Para la aplicación web, puedes:**

1. Guardar la conexión funcional cuando la tengas:
   ```
   python -c "HOST='https://...:9200' > .env"
   ```

2. Usar la aplicación CLI mientras se resuelve:
   ```bash
   python main.py csv -i datos.csv -o salida.json
   ```

3. Si algún día tienes acceso SSH a un servidor interno, hacer port forwarding:
   ```bash
   ssh user@servidor -L 9200:localhost:9200
   # Luego conectar a: http://localhost:9200
   ```

---

## 💡 Próximos pasos

**Recomendado:**

1. Contacta al administrador de elk.unir.net
2. Pide que exponga Elasticsearch en un endpoint sin Kibana proxy
3. O que cree un API Key para tu usuario
4. Prueba con la URL nueva cuando la obtengas

**Mientras tanto:**
1. Usa Kibana web manualmente accediendo a `https://elk.unir.net`
2. Continúa usando el procesador CSV local

---

## 📞 Plantilla de email para admin

```
Asunto: Necesito acceso API a Elasticsearch sin proxy de Kibana

Hola,

Estoy trabajando en herramientas de extracción de datos desde los logs.
Necesito acceso directo a la API de Elasticsearch.

Actualmente, todas las requests a:
- https://elk.unir.net:9200
- https://elk.unir.net/api/elasticsearch
- https://elk.unir.net

Se redirigen a la página de login de Kibana.

¿Podrías hacer uno de esto?

A) Exponer Elasticsearch en un endpoint sin Kibana proxy
B) Crear un API Key para autenticación
C) Configurar bypass de Kibana para acceso programático

Credenciales: <USER>

Gracias
```

---

## 🔍 Para seguir debuggeando

```bash
# Ver exactamente qué devuelve el servidor
curl -v -k -u <USER>:<PASSWORD> https://elk.unir.net:9200/

# Probar con headers específicos
curl -k -u <USER>:<PASSWORD> \
  -H "Content-Type: application/json" \
  https://elk.unir.net:9200/

# Ver certificado SSL
openssl s_client -connect elk.unir.net:443 -showcerts
```

---

**¿Qué opción vas a intentar primero?** 🚀
````
