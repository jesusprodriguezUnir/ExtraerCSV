#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests para el módulo data_processor
"""

import pytest
import json
from pathlib import Path
from data_processor import (
    normalizar_json,
    extraer_valores_no_nulos,
    procesar_mensaje,
    procesar_registros_iterable,
    contar_valores_por_campo
)


class TestNormalizarJson:
    """Tests para la función normalizar_json"""
    
    def test_extrae_json_correctamente(self):
        """Test: Extrae JSON correctamente del mensaje"""
        mensaje = (
            'Error con el Servicio de Evaluaciones, Method: POST, '
            'Body: {"where":[{"field":"idPlanEstudio","value":5109}]} , '
            'Mensaje del error'
        )
        
        resultado = normalizar_json(mensaje)
        
        assert resultado is not None
        assert '{"where":[' in resultado
        assert 'idPlanEstudio' in resultado
    
    def test_retorna_none_si_no_hay_body(self):
        """Test: Retorna None si no encuentra Body en el mensaje"""
        mensaje = "Este es un mensaje sin Body"
        
        resultado = normalizar_json(mensaje)
        
        assert resultado is None
    
    def test_maneja_multiples_campos(self):
        """Test: Maneja múltiples campos en el JSON"""
        mensaje = (
            'Body: {"where":[{"field":"idAsignaturaOfertada","value":294859},'
            '{"field":"idAsignaturaPlan","value":null},'
            '{"field":"idEstudio","value":null},'
            '{"field":"idPlanEstudio","value":5109}]}'
        )
        
        resultado = normalizar_json(mensaje)
        json_data = json.loads(resultado)
        
        assert len(json_data["where"]) == 4


class TestExtraerValoresNoNulos:
    """Tests para la función extraer_valores_no_nulos"""
    
    def test_filtra_valores_null(self):
        """Test: Filtra correctamente valores null"""
        json_data = {
            "where": [
                {"field": "idAsignaturaOfertada", "value": 294859},
                {"field": "idAsignaturaPlan", "value": None},
                {"field": "idEstudio", "value": None},
                {"field": "idPlanEstudio", "value": 5109}
            ]
        }
        
        resultado = extraer_valores_no_nulos(json_data)
        
        assert len(resultado) == 2
        assert resultado[0]["field"] == "idAsignaturaOfertada"
        assert resultado[0]["value"] == 294859
        assert resultado[1]["field"] == "idPlanEstudio"
        assert resultado[1]["value"] == 5109
    
    def test_retorna_vacio_si_todos_null(self):
        """Test: Retorna lista vacía si todos los valores son null"""
        json_data = {
            "where": [
                {"field": "campo1", "value": None},
                {"field": "campo2", "value": None}
            ]
        }
        
        resultado = extraer_valores_no_nulos(json_data)
        
        assert len(resultado) == 0
    
    def test_maneja_json_sin_where(self):
        """Test: Maneja JSON sin campo 'where'"""
        json_data = {"otros": "datos"}
        
        resultado = extraer_valores_no_nulos(json_data)
        
        assert len(resultado) == 0
    
    def test_preserva_diferentes_tipos_de_valores(self):
        """Test: Preserva diferentes tipos de valores"""
        json_data = {
            "where": [
                {"field": "numero", "value": 123},
                {"field": "texto", "value": "abc"},
                {"field": "booleano", "value": True},
                {"field": "nulo", "value": None}
            ]
        }
        
        resultado = extraer_valores_no_nulos(json_data)
        
        assert len(resultado) == 3
        assert resultado[0]["value"] == 123
        assert resultado[1]["value"] == "abc"
        assert resultado[2]["value"] is True


class TestProcesarMensaje:
    """Tests para la función procesar_mensaje"""
    
    def test_procesa_mensaje_completo(self):
        """Test: Procesa mensaje completo correctamente"""
        mensaje = (
            'Body: {"where":[{"field":"idAsignaturaOfertada","value":294859},'
            '{"field":"idAsignaturaPlan","value":null},'
            '{"field":"idPlanEstudio","value":5109}]}'
        )
        
        resultado = procesar_mensaje(mensaje)
        
        assert len(resultado) == 2
        assert any(v["field"] == "idAsignaturaOfertada" for v in resultado)
        assert any(v["field"] == "idPlanEstudio" for v in resultado)
    
    def test_maneja_mensaje_sin_json(self):
        """Test: Maneja mensaje sin JSON válido"""
        mensaje = "Mensaje sin JSON válido"
        
        resultado = procesar_mensaje(mensaje)
        
        assert len(resultado) == 0
    
    def test_maneja_json_malformado(self):
        """Test: Maneja JSON malformado sin lanzar excepción"""
        mensaje = 'Body: {"where":[{"field":"test","value":}]}'  # JSON inválido
        
        resultado = procesar_mensaje(mensaje)
        
        assert len(resultado) == 0


class TestProcesarRegistrosIterable:
    """Tests para la función procesar_registros_iterable"""
    
    def test_procesa_registros_correctamente(self, tmp_path):
        """Test: Procesa múltiples registros correctamente"""
        output_file = tmp_path / "output.json"
        
        registros = [
            {"message": 'Body: {"where":[{"field":"id1","value":100}]}'},
            {"message": 'Body: {"where":[{"field":"id2","value":200}]}'},
            {"message": 'Body: {"where":[{"field":"id1","value":100}]}'},  # Duplicado
        ]
        
        stats = procesar_registros_iterable(
            iter(registros), 
            str(output_file), 
            show_progress=False
        )
        
        assert stats["registros_procesados"] == 3
        assert stats["registros_con_valores"] == 3
        assert stats["valores_unicos"] == 2  # Debe eliminar duplicado
        
        # Verificar archivo generado
        with open(output_file, 'r') as f:
            resultado = json.load(f)
        
        assert len(resultado) == 2
    
    def test_maneja_registros_vacios(self, tmp_path):
        """Test: Maneja registros sin mensaje"""
        output_file = tmp_path / "output.json"
        
        registros = [
            {"message": ""},
            {"otro_campo": "valor"},
            {"message": 'Body: {"where":[{"field":"id","value":1}]}'}
        ]
        
        stats = procesar_registros_iterable(
            iter(registros), 
            str(output_file), 
            show_progress=False
        )
        
        assert stats["valores_unicos"] == 1
    
    def test_elimina_duplicados(self, tmp_path):
        """Test: Elimina correctamente los duplicados"""
        output_file = tmp_path / "output.json"
        
        registros = [
            {"message": 'Body: {"where":[{"field":"id","value":100}]}'},
            {"message": 'Body: {"where":[{"field":"id","value":100}]}'},
            {"message": 'Body: {"where":[{"field":"id","value":100}]}'},
            {"message": 'Body: {"where":[{"field":"id","value":200}]}'},
        ]
        
        stats = procesar_registros_iterable(
            iter(registros), 
            str(output_file), 
            show_progress=False
        )
        
        assert stats["valores_unicos"] == 2
        
        with open(output_file, 'r') as f:
            resultado = json.load(f)
        
        # Verificar que hay exactamente 2 valores únicos
        assert len(resultado) == 2
        valores = {r["value"] for r in resultado}
        assert valores == {100, 200}


class TestContarValoresPorCampo:
    """Tests para la función contar_valores_por_campo"""
    
    def test_cuenta_correctamente(self):
        """Test: Cuenta valores por campo correctamente"""
        valores = [
            {"field": "id1", "value": 100},
            {"field": "id1", "value": 200},
            {"field": "id2", "value": 300},
            {"field": "id1", "value": 400},
        ]
        
        resultado = contar_valores_por_campo(valores)
        
        assert resultado["id1"] == 3
        assert resultado["id2"] == 1
    
    def test_maneja_lista_vacia(self):
        """Test: Maneja lista vacía"""
        resultado = contar_valores_por_campo([])
        
        assert resultado == {}


# Tests de integración
class TestIntegracion:
    """Tests de integración completos"""
    
    def test_flujo_completo_csv_simulado(self, tmp_path):
        """Test: Flujo completo similar al procesamiento de CSV"""
        output_file = tmp_path / "resultado.json"
        
        # Simular datos de un CSV con logs reales
        registros = [
            {
                "message": '[123] Error con Evaluaciones, Body: {"where":[{"field":"idPlanEstudio","value":5109}]}',
                "@timestamp": "2026-02-16"
            },
            {
                "message": '[456] Error con Evaluaciones, Body: {"where":[{"field":"idPlanEstudio","value":5500}]}',
                "@timestamp": "2026-02-16"
            },
            {
                "message": '[789] Error con Evaluaciones, Body: {"where":[{"field":"idAsignaturaOfertada","value":294859}]}',
                "@timestamp": "2026-02-16"
            },
            {
                "message": '[789] Error sin Body',  # Sin Body
                "@timestamp": "2026-02-16"
            },
        ]
        
        stats = procesar_registros_iterable(
            iter(registros),
            str(output_file),
            show_progress=False
        )
        
        # Verificaciones
        assert stats["registros_procesados"] == 4
        assert stats["registros_con_valores"] == 3
        assert stats["valores_unicos"] == 3
        
        # Verificar contenido del archivo
        with open(output_file, 'r', encoding='utf-8') as f:
            resultado = json.load(f)
        
        assert len(resultado) == 3
        
        # Verificar que contiene los campos esperados
        campos = {r["field"] for r in resultado}
        assert "idPlanEstudio" in campos
        assert "idAsignaturaOfertada" in campos


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
