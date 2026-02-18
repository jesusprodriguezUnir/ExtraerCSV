# Extractor de Datos JSON desde CSV de Logs y Elasticsearch

Herramienta Python para extraer y procesar datos JSON embebidos en archivos CSV de logs o directamente desde Elasticsearch/Kibana. Filtra automáticamente valores no nulos, elimina duplicados y exporta los resultados a JSON limpio.

## 🚀 Características

- ✅ **Múltiples fuentes de datos** - CSV local o Elasticsearch/Kibana API
- ✅ **Extracción automática** de datos JSON desde columnas de mensajes
- 🔍 **Filtrado inteligente** - solo valores diferentes de `null`
- 🎯 **Eliminación de duplicados** - resultados únicos basados en campo + valor
- 📊 **Progreso en tiempo real** - visualización del procesamiento cada 1000 registros
- 🛡️ **Manejo robusto de errores** - continúa procesando aunque algún registro falle
- ⚙️ **Configuración flexible** - queries personalizables de Elasticsearch
- 📝 **Estadísticas detalladas** - resumen completo al finalizar
- 🔒 **Seguro** - credenciales en archivo `.env` no commiteado
- 🌐 **Interfaz web** - GUI moderna para visualizar y configurar conexiones

## 📋 Requisitos

- Python 3.6 o superior
- Librerías:
  - `elasticsearch>=8.11.0` (para conexión a Elasticsearch/Kibana)
  - `python-dotenv>=1.0.0` (para gestión de variables de entorno)

## 🔧 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/extractor-csv-json.git
cd extractor-csv-json

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales (solo si usarás Elasticsearch)
cp .env.example .env
# Edita .env con tus credenciales reales
```

## 💻 Uso

### 🌐 Opción recomendada: Interfaz Web (con GUI)

La forma más fácil y visual de usar la aplicación:

```bash
# Windows
start_web.bat

# Linux/Mac
bash start_web.sh

# O manualmente
python app_web.py
```

Accede a **http://localhost:5000** en tu navegador.

**Características:**
- ✅ Login visual con credenciales
- ✅ Explorador de índices interactivo
- ✅ Editor de queries con sintaxis JSON
- ✅ Visor de resultados con formato
- ✅ Exportación a JSON
- ✅ Interfaz responsive (mobile-friendly)

[📖 Ver documentación completa de la interfaz web](WEB_README.md)

---

### Opción 1: Procesar CSV local

#### Método directo (script original)

1. Edita las rutas en `extractor_csv.py` (líneas 16-17):

```python
INPUT_CSV = "tu_archivo.csv"
OUTPUT_JSON = "salida.json"
```

2. Ejecuta el script:

```bash
python extractor_csv.py
```

#### Método CLI (recomendado)

```bash
python main.py csv --input archivo.csv --output salida.json
```

### Opción 2: Descargar desde Elasticsearch/Kibana

#### Configuración inicial

1. Copia el archivo de ejemplo de configuración:
```bash
cp .env.example .env
```

2. Edita `.env` con tus credenciales:
```env
ELASTICSEARCH_HOST=https://elk.unir.net
ELASTICSEARCH_USER=tu_usuario
ELASTICSEARCH_PASSWORD=tu_contraseña
ELASTICSEARCH_INDEX=logs-*
```

3. Prueba la conexión:
```bash
python main.py test-connection
```

#### Descarga y procesamiento

**Directo a JSON (más eficiente):**
```bash
python main.py elasticsearch --output-json datos.json
```

**Con CSV intermedio (para auditoría):**
```bash
python main.py elasticsearch --output-csv logs.csv --output-json datos.json
```

**Con query personalizada:**
```bash
python main.py elasticsearch --query-file queries/error_logs_ejemplo.json --output-json datos.json
```

**Con índice específico:**
```bash
python main.py elasticsearch --index "logs-2026.02.*" --output-json datos.json
```

**Modo verbose (ver query y detalles):**
```bash
python main.py elasticsearch --output-json datos.json --verbose
```

### Opción 3: Uso como módulo

```python
# Desde CSV
from extractor_csv import procesar_csv
stats = procesar_csv("entrada.csv", "salida.json")

# Desde Elasticsearch
from config import load_config
from elasticsearch_client import ElasticsearchClient
from data_processor import procesar_registros_iterable

config = load_config()
client = ElasticsearchClient(config)

query = {"query": {"match_all": {}}}
docs = client.get_documents_generator(query)
stats = procesar_registros_iterable(docs, "salida.json")
```

## 📊 Formato de datos

### Entrada esperada (CSV)

El script espera un archivo CSV con una columna llamada `message` que contenga JSON con esta estructura:

```
Body: {"where":[{"field":"idAsignaturaOfertada","value":294859},{"field":"idAsignaturaPlan","value":null},{"field":"idEstudio","value":null},{"field":"idPlanEstudio","value":5109}]}
```

### Salida generada (JSON)

```json
[
  {
    "field": "idAsignaturaOfertada",
    "value": 294859
  },
  {
    "field": "idPlanEstudio",
    "value": 5109
  }
]
```

**Nota:** Solo se incluyen campos con valores diferentes de `null` y se eliminan duplicados.

## 📖 Ejemplo de ejecución

### Desde CSV local

```
============================================================
  PROCESADOR DE CSV LOCAL
============================================================

📂 Procesando archivo: Error Evaluacion Niveles Escala.csv
⏳ Procesando registros...
  ✓ Procesados 1,000 registros...
  ✓ Procesados 2,000 registros...
  ✓ Procesados 3,000 registros...
  ✓ Procesados 4,000 registros...
✓ Total de registros procesados: 4,524
📊 Registros con valores: 498
📊 Valores únicos encontrados: 17
💾 Archivo generado: datos_extraidos.json

============================================================
  ✅ PROCESO COMPLETADO EXITOSAMENTE
============================================================
  📋 Registros procesados: 4,524
  📊 Valores únicos extraídos: 17
  📁 Archivo de salida: datos_extraidos.json
============================================================
```

### Desde Elasticsearch

```
============================================================
  EXTRACTOR DESDE ELASTICSEARCH
============================================================

⚙️  Cargando configuración...
✓ Configuración cargada: https://elk.unir.net
🔌 Conectando a Elasticsearch...
✅ Conectado a: production-cluster (v8.11.0)
📊 Índice: logs-*
📊 Documentos estimados: 15,234

📥 Descargando y procesando directamente a JSON...
⏳ Procesando registros...
  ✓ Procesados 1,000 registros...
  ✓ Procesados 2,000 registros...
  ...
✓ Total de registros procesados: 15,234
📊 Registros con valores: 892
📊 Valores únicos encontrados: 45
💾 Archivo generado: datos_extraidos.json

============================================================
  ✅ PROCESO COMPLETADO EXITOSAMENTE
============================================================
  📋 Registros procesados: 15,234
  📊 Registros con valores: 892
  📊 Valores únicos extraídos: 45
  📁 Archivo de salida JSON: datos_extraidos.json
============================================================
```

## 🔍 Funciones principales

### Módulo `data_processor.py`
- **`normalizar_json(text)`** - Extrae JSON del campo Body del mensaje
- **`extraer_valores_no_nulos(json_data)`** - Filtra valores diferentes de null
- **`procesar_mensaje(message)`** - Procesa mensaje completo
- **`procesar_registros_iterable(registros, output)`** - Procesa cualquier fuente de datos

### Módulo `elasticsearch_client.py`
- **`ElasticsearchClient(config)`** - Cliente para conectar a Elasticsearch
- **`test_connection()`** - Verifica conectividad
- **`search_logs(query, index)`** - Busca logs con Scroll API
- **`download_to_csv(query, output)`** - Descarga resultados a CSV
- **`get_documents_generator(query)`** - Generador para procesamiento directo

### Módulo `config.py`
- **`load_config()`** - Carga y valida configuración desde .env
- **`Config`** - Clase con toda la configuración de la aplicación

## ⚙️ Configuración avanzada

### Variables de entorno (.env)

```env
# Requeridas
ELASTICSEARCH_HOST=https://elk.unir.net
ELASTICSEARCH_USER=tu_usuario
ELASTICSEARCH_PASSWORD=tu_contraseña
ELASTICSEARCH_INDEX=logs-*

# Opcionales
ELASTICSEARCH_VERIFY_SSL=true         # Verificar certificados SSL
ELASTICSEARCH_TIMEOUT=300             # Timeout en segundos
ELASTICSEARCH_SCROLL_SIZE=1000        # Documentos por batch
ELASTICSEARCH_SCROLL_TIMEOUT=5m       # Tiempo de vida del scroll
```

### Queries personalizadas

Crea archivos JSON en el directorio `queries/` con tu query de Elasticsearch:

```json
{
  "query": {
    "bool": {
      "must": [
        {"wildcard": {"message": "*Body:*"}},
        {"term": {"level": "ERROR"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "2026-02-01", "lte": "2026-02-17"}}}
      ]
    }
  },
  "_source": ["message", "@timestamp", "level"]
}
```

Ver más ejemplos en [queries/README.md](queries/README.md).

### Encoding del archivo CSV

Si tu CSV tiene encoding especial, modifica en `extractor_csv.py`:

```python
with open(input_file, 'r', encoding='utf-8-sig') as csvfile:
```

### Frecuencia de progreso

Para cambiar cada cuántos registros se muestra el progreso, edita en `data_processor.py`:

```python
if registros_procesados % 1000 == 0:  # Cambiar 1000 por el valor deseado
```

## 🐛 Troubleshooting

### Error: "Faltan variables de entorno requeridas"

**Solución:** Asegúrate de haber creado el archivo `.env` con las credenciales:
```bash
cp .env.example .env
# Edita .env con tus credenciales reales
```

### Error: SSL certificate verification failed

**Síntoma:** Error de certificado SSL al conectar a Elasticsearch

**Soluciones:**
1. Si es entorno de desarrollo con certificados autofirmados:
   ```env
   ELASTICSEARCH_VERIFY_SSL=false
   ```
2. Si es producción, obtén el certificado correcto y configúralo

### Error: Authentication failed

**Síntoma:** Error 401 o mensaje de autenticación fallida

**Solución:** Verifica usuario y contraseña en `.env`:
```bash
python main.py test-connection  # Para probar credenciales
```

### Error: Index not found

**Síntoma:** Índice no encontrado o sin resultados

**Solución:**
1. Lista los índices disponibles:
   ```bash
   python main.py test-connection
   ```
2. Ajusta el patrón en `.env`:
   ```env
   ELASTICSEARCH_INDEX=logs-2026.*
   ```

### Error: Request timeout

**Síntoma:** Timeout después de unos minutos

**Solución:** Aumenta el timeout en `.env`:
```env
ELASTICSEARCH_TIMEOUT=600  # 10 minutos
```

### Error: Too many results / Memory error

**Síntoma:** Se queda sin memoria con millones de registros

**Soluciones:**
1. Usa CSV intermedio en lugar de procesamiento directo
2. Divide por rangos de fechas pequeños
3. Reduce scroll_size:
   ```env
   ELASTICSEARCH_SCROLL_SIZE=500
   ```

### No se encuentra el .env

**Síntoma:** Variables de entorno no se cargan

**Solución:** El archivo `.env` debe estar en el mismo directorio donde ejecutas el script:
```bash
ls -la .env  # Verificar que existe
cat .env     # Verificar contenido (¡cuidado con la contraseña en pantalla!)
```

## 📝 Casos de uso

Este extractor es ideal para:

- 📋 **Análisis de logs de aplicaciones** - Extrae configuraciones desde logs de error
- 🔍 **Auditoría de sistemas** - Identifica valores únicos en grandes volúmenes de logs
- 📊 **Generación de datasets** - Prepara datos únicos para análisis o machine learning
- 🧹 **Limpieza de datos** - Normaliza y filtra información de logs estructurados
- 📈 **Dashboards y reportes** - Exporta datos listos para visualización
- 🔄 **ETL de logs** - Transforma logs no estructurados en JSON estructurado
- 🚨 **Análisis de incidentes** - Extrae rapidamente información específica de periodos de error

### Ejemplos prácticos

#### 1. Analizar errores de la última semana
```bash
python main.py elasticsearch --output-json errores_semana.json
# Query por defecto usa últimos 7 días
```

#### 2. Extraer configuraciones de un día específico
```bash
# Crea queries/dia_especifico.json con el rango deseado
python main.py elasticsearch --query-file queries/dia_especifico.json --output-json configs.json
```

#### 3. Procesar CSV descargado manualmente de Kibana
```bash
python main.py csv --input export_kibana.csv --output datos.json
```

#### 4. Pipeline automatizado
```bash
# Descarga, procesa y guarda CSV para auditoría
python main.py elasticsearch \
  --output-csv backup_$(date +%Y%m%d).csv \
  --output-json datos_$(date +%Y%m%d).json
```

## 🏗️ Arquitectura

```
ExtraerCSV/
├── main.py                      # 🎯 Punto de entrada CLI principal
├── config.py                    # ⚙️ Gestión de configuración desde .env
├── elasticsearch_client.py      # 🔌 Cliente para conectar a Elasticsearch
├── data_processor.py            # 🔄 Lógica de procesamiento común
├── extractor_csv.py             # 📄 Procesador específico de CSV (legacy)
├── requirements.txt             # 📦 Dependencias Python
├── .env.example                 # 📋 Template de configuración
├── .env                         # 🔒 Credenciales (NO COMMITEAR)
├── .gitignore                   # 🚫 Archivos ignorados por git
├── README.md                    # 📖 Esta documentación
│
├── queries/                     # 📁 Directorio de queries
│   ├── README.md               # Guía de queries
│   ├── default_query.json      # Query por defecto
│   └── error_logs_ejemplo.json # Ejemplo de query personalizada
│
└── datos_extraidos.json         # 📊 Archivo de salida generado
```

### Flujo de datos

#### Desde CSV local
```
CSV local → extractor_csv.py → data_processor.py → JSON
```

#### Desde Elasticsearch (directo)
```
Elasticsearch → elasticsearch_client.py → data_processor.py → JSON
```

#### Desde Elasticsearch (con CSV intermedio)
```
Elasticsearch → elasticsearch_client.py → CSV temporal → data_processor.py → JSON
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## � Troubleshooting

### Problema: No puedo conectar a Elasticsearch

**Síntomas:**
- Error 302 o redirección a `/login`
- Error 401 (Unauthorized)
- Error de certificado SSL

**Soluciones:**

📖 [Ver guía completa de troubleshooting →](TROUBLESHOOTING.md)

**Verificación rápida:**
```bash
# Ejecutar script de depuración
python debug_es.py

# Probar conexión manual
curl -k -u usuario:contraseña https://elasticsearch-host:puerto/
```

⚠️ **Nota importante**: Si Kibana está en frente de Elasticsearch (como proxy), 
necesitarás contactar al administrador para:
- Exponer Elasticsearch en un endpoint sin Kibana
- O crear un API Key para acceso programático
- O configurar un bypass específico

Ver [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) completo para todas las opciones.

## �📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## ✉️ Contacto

Para preguntas, sugerencias o reportar problemas, por favor abre un issue en GitHub.

---

**Desarrollo:** 2026  
**Versión:** 1.0.0
