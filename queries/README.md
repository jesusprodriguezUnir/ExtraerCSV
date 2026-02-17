# Ejemplos de Queries para Elasticsearch

Este directorio contiene ejemplos de queries que puedes usar con el extractor.

## Uso

```bash
python main.py elasticsearch --query-file queries/nombre_query.json --output-json salida.json
```

## Queries disponibles

### 1. `default_query.json`
Query por defecto que se usa si no especificas ninguna.
- **Rango:** Últimos 7 días
- **Filtro:** Mensajes que contienen "Body:"
- **Campos:** message, @timestamp

### 2. `error_logs_ejemplo.json`
Ejemplo de query para logs de error en fechas específicas.
- **Rango:** Del 10 al 17 de febrero de 2026
- **Filtro:** Solo logs de nivel ERROR con "Body:"
- **Campos:** message, @timestamp, level, applicationName

## Crear tu propia query

### Estructura básica

```json
{
  "query": {
    "bool": {
      "must": [
        {"wildcard": {"message": "*Body:*"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-7d"}}}
      ]
    }
  },
  "_source": ["message", "@timestamp"]
}
```

### Componentes importantes

#### Filtros de tiempo

```json
// Últimos N días
{"range": {"@timestamp": {"gte": "now-7d"}}}

// Fechas específicas
{"range": {"@timestamp": {"gte": "2026-02-01", "lte": "2026-02-28"}}}

// Últimas N horas
{"range": {"@timestamp": {"gte": "now-24h"}}}
```

#### Filtros por campo

```json
// Nivel de log
{"term": {"level": "ERROR"}}

// Aplicación específica
{"term": {"applicationName": "ExpedientesAcademicos"}}

// Contiene texto
{"wildcard": {"message": "*texto*"}}

// Match exacto
{"match": {"message": "texto exacto"}}
```

#### Campos a retornar

```json
"_source": ["message", "@timestamp", "level"]  // Solo estos campos
"_source": true  // Todos los campos (más lento)
"_source": false  // Sin campos, solo metadatos
```

### Ejemplos adicionales

#### Solo logs de una aplicación

```json
{
  "query": {
    "bool": {
      "must": [
        {"wildcard": {"message": "*Body:*"}},
        {"term": {"applicationName": "ExpedientesAcademicos"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-1d"}}}
      ]
    }
  },
  "_source": ["message", "@timestamp"]
}
```

#### Múltiples niveles de log

```json
{
  "query": {
    "bool": {
      "must": [
        {"wildcard": {"message": "*Body:*"}}
      ],
      "should": [
        {"term": {"level": "ERROR"}},
        {"term": {"level": "WARN"}}
      ],
      "minimum_should_match": 1,
      "filter": [
        {"range": {"@timestamp": {"gte": "now-7d"}}}
      ]
    }
  },
  "_source": ["message", "@timestamp", "level"]
}
```

#### Excluir ciertos valores

```json
{
  "query": {
    "bool": {
      "must": [
        {"wildcard": {"message": "*Body:*"}}
      ],
      "must_not": [
        {"term": {"level": "DEBUG"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-7d"}}}
      ]
    }
  },
  "_source": ["message", "@timestamp"]
}
```

## Recursos

- [Documentación oficial de Elasticsearch Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
- [Kibana Dev Tools](https://elk.unir.net/app/dev_tools#/console) - Prueba tus queries aquí primero
