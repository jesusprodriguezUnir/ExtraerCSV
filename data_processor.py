#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Procesador de datos para extraer información de logs
Funciones comunes para procesar mensajes y extraer valores no nulos
"""

import json
import re
from typing import Iterator, Dict, List, Set, Tuple, Optional, Any


def normalizar_json(text: str) -> Optional[str]:
    """
    Extrae el JSON del campo Body del mensaje.
    
    Args:
        text: Texto del mensaje que contiene el JSON
        
    Returns:
        JSON como string, o None si no se encuentra
    """
    # Buscar el patrón Body: {"where":[...]}
    # El CSV ya des-escapa las comillas automáticamente
    match = re.search(r'Body:\s*(\{"where":\[.*?\]\})', text)
    
    if not match:
        return None
    
    json_str = match.group(1)
    
    return json_str


def extraer_valores_no_nulos(json_data: Dict) -> List[Dict[str, Any]]:
    """
    Extrae los campos con valores no nulos del JSON.
    
    Args:
        json_data: Diccionario con estructura {"where": [{"field": "...", "value": ...}, ...]}
        
    Returns:
        Lista de diccionarios {"field": str, "value": valor} para valores no nulos
    """
    valores = []
    
    if "where" not in json_data:
        return valores
    
    for item in json_data["where"]:
        if item.get("value") is not None:
            valores.append({
                "field": item["field"],
                "value": item["value"]
            })
    
    return valores


def procesar_mensaje(message: str) -> List[Dict[str, Any]]:
    """
    Procesa un mensaje completo: extrae JSON y filtra valores no nulos
    
    Args:
        message: Texto del mensaje de log
        
    Returns:
        Lista de diccionarios con valores no nulos
    """
    try:
        # Normalizar JSON
        json_str = normalizar_json(message)
        
        if not json_str:
            return []
        
        # Parsear JSON
        json_data = json.loads(json_str)
        
        # Extraer valores no nulos
        valores = extraer_valores_no_nulos(json_data)
        
        return valores
        
    except json.JSONDecodeError:
        return []
    except Exception:
        return []


def procesar_registros_iterable(
    registros: Iterator[Dict],
    output_json: str,
    show_progress: bool = True
) -> Dict[str, int]:
    """
    Procesa un iterador de registros y extrae valores únicos a JSON
    
    Args:
        registros: Iterador que produce diccionarios con campo 'message'
        output_json: Ruta del archivo JSON de salida
        show_progress: Mostrar progreso durante el procesamiento
        
    Returns:
        dict: Estadísticas del procesamiento
    """
    # Usar set con tuplas para eliminar duplicados
    valores_unicos: Set[Tuple[str, Any]] = set()
    registros_procesados = 0
    registros_con_valores = 0
    
    if show_progress:
        print("⏳ Procesando registros...")
    
    for registro in registros:
        registros_procesados += 1
        
        try:
            message = registro.get('message', '')
            
            if not message:
                continue
            
            # Procesar mensaje
            valores = procesar_mensaje(message)
            
            if valores:
                registros_con_valores += 1
                
                # Agregar al set (como tuplas para que sean hashables)
                for valor in valores:
                    valores_unicos.add((valor["field"], valor["value"]))
            
        except Exception:
            # Continuar con el siguiente registro si hay error
            continue
        
        # Mostrar progreso cada 1000 registros
        if show_progress and registros_procesados % 1000 == 0:
            print(f"  ✓ Procesados {registros_procesados:,} registros...")
    
    if show_progress:
        print(f"✓ Total de registros procesados: {registros_procesados:,}")
        print(f"📊 Registros con valores: {registros_con_valores:,}")
    
    # Convertir set de tuplas a lista de diccionarios ordenada
    resultado = [
        {"field": field, "value": value}
        for field, value in sorted(valores_unicos)
    ]
    
    if show_progress:
        print(f"📊 Valores únicos encontrados: {len(resultado):,}")
    
    # Escribir resultado a JSON
    with open(output_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(resultado, jsonfile, indent=2, ensure_ascii=False)
    
    if show_progress:
        print(f"💾 Archivo generado: {output_json}")
    
    return {
        "registros_procesados": registros_procesados,
        "registros_con_valores": registros_con_valores,
        "valores_unicos": len(resultado)
    }


def contar_valores_por_campo(valores: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Cuenta cuántos valores hay por cada campo
    
    Args:
        valores: Lista de diccionarios {"field": str, "value": valor}
        
    Returns:
        dict: Conteo por campo
    """
    conteo = {}
    for item in valores:
        field = item["field"]
        conteo[field] = conteo.get(field, 0) + 1
    return conteo


if __name__ == "__main__":
    # Test de las funciones
    mensaje_ejemplo = (
        'Body: {"where":[{"field":"idAsignaturaOfertada","value":294859},'
        '{"field":"idAsignaturaPlan","value":null},'
        '{"field":"idEstudio","value":null},'
        '{"field":"idPlanEstudio","value":5109}]} , Mensaje del error'
    )
    
    print("🧪 Probando procesamiento de mensaje...")
    print(f"Mensaje: {mensaje_ejemplo[:100]}...")
    
    valores = procesar_mensaje(mensaje_ejemplo)
    print(f"\n✓ Valores extraídos: {len(valores)}")
    for v in valores:
        print(f"  - {v['field']}: {v['value']}")
