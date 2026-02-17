# Tests y Validación de Calidad

Este directorio contiene tests automatizados para el extractor de datos JSON.

## 🧪 Ejecutar tests

### Instalar dependencias de testing

```bash
pip install -r requirements-dev.txt
```

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con cobertura

```bash
pytest --cov=. --cov-report=html
```

Esto generará un reporte HTML en `htmlcov/index.html`.

### Ejecutar tests específicos

```bash
# Un archivo específico
pytest tests/test_data_processor.py

# Una clase específica
pytest tests/test_data_processor.py::TestNormalizarJson

# Un test específico
pytest tests/test_data_processor.py::TestNormalizarJson::test_extrae_json_correctamente

# Con verbose
pytest -v

# Con output de print
pytest -s
```

### Ejecutar tests en modo watch (desarrollo)

```bash
pytest-watch
```

## 📁 Estructura de tests

```
tests/
├── __init__.py                      # Inicialización del paquete
├── test_data_processor.py           # Tests para data_processor.py
├── test_config.py                   # Tests para config.py
├── test_elasticsearch_client.py     # Tests para elasticsearch_client.py (con mocks)
└── README.md                        # Esta documentación
```

## 🧩 Tipos de tests

### Unit Tests
Tests aislados de funciones individuales sin dependencias externas.

**Ejemplo:**
- `test_normalizar_json` - Prueba la extracción de JSON
- `test_extraer_valores_no_nulos` - Prueba el filtrado de valores

### Integration Tests
Tests que verifican la interacción entre múltiples componentes.

**Ejemplo:**
- `test_flujo_completo_csv_simulado` - Simula el flujo completo de procesamiento
- `test_procesa_registros_correctamente` - Verifica el pipeline completo

### Mocked Tests
Tests con mocks para componentes externos (Elasticsearch).

**Ejemplo:**
- `test_conexion_exitosa` - Mock de conexión a Elasticsearch
- `test_busca_logs_correctamente` - Mock de búsquedas con scan API

## 🎯 Cobertura de tests

Los tests cubren:

✅ **data_processor.py**
- Extracción de JSON de mensajes
- Filtrado de valores nulos
- Procesamiento de registros iterables
- Eliminación de duplicados
- Casos edge: mensajes vacíos, JSON malformado

✅ **config.py**
- Carga de variables de entorno
- Validación de configuración
- Valores por defecto
- Conversión de tipos
- Manejo de errores

✅ **elasticsearch_client.py**
- Inicialización del cliente (mock)
- Test de conexión
- Listado de índices
- Búsqueda con Scroll API
- Descarga a CSV
- Manejo de errores (auth, SSL, índices no encontrados)

## 🔧 Escribir nuevos tests

### Template básico

```python
import pytest

def test_mi_nueva_funcionalidad():
    """Test: Descripción de qué se está probando"""
    # Arrange (preparar)
    input_data = "datos de prueba"
    
    # Act (ejecutar)
    result = mi_funcion(input_data)
    
    # Assert (verificar)
    assert result == "resultado esperado"
```

### Usando fixtures

```python
@pytest.fixture
def datos_prueba():
    """Fixture que proporciona datos de prueba reutilizables"""
    return {
        "field": "test",
        "value": 123
    }

def test_con_fixture(datos_prueba):
    """Test que usa el fixture"""
    assert datos_prueba["field"] == "test"
```

### Usando mocks

```python
from unittest.mock import Mock, patch

def test_con_mock():
    """Test usando mock para Elasticsearch"""
    with patch('elasticsearch_client.Elasticsearch') as MockES:
        mock_instance = MockES.return_value
        mock_instance.ping.return_value = True
        
        # Tu código de test aquí
        assert mock_instance.ping() is True
```

### Usando archivos temporales

```python
def test_con_archivo_temporal(tmp_path):
    """Test que crea archivos temporales"""
    archivo = tmp_path / "test.json"
    archivo.write_text('{"test": true}')
    
    assert archivo.exists()
    # El archivo se limpia automáticamente después del test
```

## 📊 Mejores prácticas

### ✅ DO (Hacer)

- Escribe tests descriptivos con nombres claros
- Usa fixtures para datos reutilizables
- Un assert por concepto (pero pueden ser múltiples asserts relacionados)
- Mockea dependencias externas (APIs, bases de datos)
- Prueba casos normales y edge cases
- Mantén los tests independientes entre sí

### ❌ DON'T (No hacer)

- No dependas de orden de ejecución de tests
- No uses sleeps o esperas innecesarias
- No compartas estado entre tests
- No pruebes implementación interna, prueba comportamiento
- No skipees tests sin razón documentada

## 🐛 Debugging tests

### Test fallido - ver output completo

```bash
pytest -vv --tb=long
```

### Entrar en debugger cuando falla

```bash
pytest --pdb
```

### Ver print statements

```bash
pytest -s
```

### Ejecutar solo tests marcados

```python
@pytest.mark.slow
def test_operacion_lenta():
    pass

# Ejecutar solo tests lentos
pytest -m slow

# Ejecutar todos excepto los lentos
pytest -m "not slow"
```

## 📈 CI/CD Integration

### GitHub Actions example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 🎓 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## 📞 Ayuda

Si encuentras problemas con los tests:

1. Verifica que instalaste `requirements-dev.txt`
2. Ejecuta `pytest --version` para confirmar instalación
3. Limpia cache: `pytest --cache-clear`
4. Revisa los logs con `-vv --tb=long`
