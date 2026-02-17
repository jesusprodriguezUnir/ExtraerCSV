# Extractor de Datos JSON desde CSV de Logs

Herramienta Python para extraer y procesar datos JSON embebidos en archivos CSV de logs. Filtra automáticamente valores no nulos, elimina duplicados y exporta los resultados a JSON limpio.

## 🚀 Características

- ✅ **Extracción automática** de datos JSON desde columnas de mensajes CSV
- 🔍 **Filtrado inteligente** - solo valores diferentes de `null`
- 🎯 **Eliminación de duplicados** - resultados únicos basados en campo + valor
- 📊 **Progreso en tiempo real** - visualización del procesamiento cada 1000 registros
- 🛡️ **Manejo robusto de errores** - continúa procesando aunque algún registro falle
- ⚙️ **Fácil configuración** - rutas modificables al inicio del script
- 📝 **Estadísticas detalladas** - resumen completo al finalizar

## 📋 Requisitos

- Python 3.6 o superior
- No requiere librerías externas (solo módulos estándar)

## 🔧 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/extractor-csv-json.git
cd extractor-csv-json

# O simplemente descargar el archivo extractor_csv.py
```

## 💻 Uso

### Método 1: Configuración básica

1. Edita las rutas en `extractor_csv.py` (líneas 16-17):

```python
INPUT_CSV = "tu_archivo.csv"
OUTPUT_JSON = "salida.json"
```

2. Ejecuta el script:

```bash
python extractor_csv.py
```

### Método 2: Uso como módulo

```python
from extractor_csv import procesar_csv

# Procesar archivo
stats = procesar_csv("entrada.csv", "salida.json")

print(f"Registros procesados: {stats['registros_procesados']}")
print(f"Valores únicos: {stats['valores_unicos']}")
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

```
============================================================
  EXTRACTOR DE DATOS JSON DESDE CSV
============================================================

📂 Procesando archivo: Error Evaluacion Niveles Escala.csv
⏳ Leyendo registros...
  ✓ Procesados 1,000 registros...
  ✓ Procesados 2,000 registros...
  ✓ Procesados 3,000 registros...
  ✓ Procesados 4,000 registros...
✓ Total de registros procesados: 4,524
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

## 🔍 Funciones principales

### `normalizar_json(text: str) -> Optional[str]`
Extrae el JSON del campo Body del mensaje de log.

### `extraer_valores_no_nulos(json_data: Dict) -> List[Dict]`
Filtra y extrae solo los campos con valores diferentes de `null`.

### `procesar_csv(input_path: str, output_path: str) -> Dict`
Función principal que procesa el CSV completo y genera el JSON de salida.

## ⚙️ Configuración avanzada

### Encoding del archivo

El script usa `utf-8-sig` por defecto. Si tu archivo tiene otro encoding, modifica la línea:

```python
with open(input_file, 'r', encoding='utf-8-sig') as csvfile:
```

### Frecuencia de progreso

Para cambiar cada cuántos registros se muestra el progreso, modifica:

```python
if idx % 1000 == 0:  # Cambiar 1000 por el valor deseado
```

## 🐛 Manejo de errores

El script incluye manejo robusto de errores:

- ✅ Valida existencia del archivo de entrada
- ✅ Crea directorios de salida si no existen
- ✅ Continúa procesando aunque registros individuales fallen
- ✅ Reporta cantidad de registros con errores al final

## 📝 Casos de uso

Este extractor es ideal para:

- 📋 Análisis de logs de aplicaciones
- 🔍 Extracción de configuraciones desde logs de errores
- 📊 Generación de datasets únicos para análisis
- 🧹 Limpieza y normalización de datos de logs
- 📈 Preparación de datos para dashboards o reportes

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## ✉️ Contacto

Para preguntas, sugerencias o reportar problemas, por favor abre un issue en GitHub.

---

**Desarrollo:** 2026  
**Versión:** 1.0.0
