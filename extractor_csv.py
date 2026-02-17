#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extractor de datos JSON desde CSV de logs
Extrae campos con valores no nulos del JSON embebido en logs CSV
"""

import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

# ===========================================
# CONFIGURACIÓN - Modifica estas rutas según necesites
# ===========================================
INPUT_CSV = "Error Evaluacion Niveles Escala.csv"
OUTPUT_JSON = "datos_extraidos.json"


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


def extraer_valores_no_nulos(json_data: Dict) -> List[Dict[str, any]]:
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


def procesar_csv(input_path: str, output_path: str) -> Dict[str, int]:
    """
    Procesa el archivo CSV y extrae valores no nulos únicos a JSON.
    
    Args:
        input_path: Ruta al archivo CSV de entrada
        output_path: Ruta al archivo JSON de salida
        
    Returns:
        Diccionario con estadísticas del procesamiento
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    # Validar existencia del archivo de entrada
    if not input_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {input_path}")
    
    # Crear directorio de salida si no existe
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Usar set con tuplas para eliminar duplicados
    valores_unicos: Set[Tuple[str, any]] = set()
    registros_procesados = 0
    registros_con_error = 0
    
    print(f"📂 Procesando archivo: {input_path}")
    print("⏳ Leyendo registros...")
    
    # Leer el CSV
    with open(input_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for idx, row in enumerate(reader, start=1):
            registros_procesados += 1
            
            try:
                # Extraer el campo message
                message = row.get('message', '')
                
                if not message:
                    continue
                
                # Normalizar JSON
                json_str = normalizar_json(message)
                
                if not json_str:
                    continue
                
                # Parsear JSON
                json_data = json.loads(json_str)
                
                # Extraer valores no nulos
                valores = extraer_valores_no_nulos(json_data)
                
                # Agregar al set (como tuplas para que sean hashables)
                for valor in valores:
                    valores_unicos.add((valor["field"], valor["value"]))
                
            except json.JSONDecodeError as e:
                registros_con_error += 1
                # Continuar con el siguiente registro
                continue
            except Exception as e:
                registros_con_error += 1
                # Continuar con el siguiente registro
                continue
            
            # Mostrar progreso cada 1000 registros
            if idx % 1000 == 0:
                print(f"  ✓ Procesados {idx:,} registros...")
    
    print(f"✓ Total de registros procesados: {registros_procesados:,}")
    
    if registros_con_error > 0:
        print(f"⚠ Registros con errores (omitidos): {registros_con_error:,}")
    
    # Convertir set de tuplas a lista de diccionarios
    resultado = [
        {"field": field, "value": value}
        for field, value in sorted(valores_unicos)
    ]
    
    print(f"📊 Valores únicos encontrados: {len(resultado):,}")
    
    # Escribir resultado a JSON
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(resultado, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"💾 Archivo generado: {output_path}")
    
    return {
        "registros_procesados": registros_procesados,
        "registros_con_error": registros_con_error,
        "valores_unicos": len(resultado)
    }


def main():
    """Función principal"""
    print("=" * 60)
    print("  EXTRACTOR DE DATOS JSON DESDE CSV")
    print("=" * 60)
    print()
    
    try:
        stats = procesar_csv(INPUT_CSV, OUTPUT_JSON)
        
        print()
        print("=" * 60)
        print("  ✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"  📋 Registros procesados: {stats['registros_procesados']:,}")
        print(f"  📊 Valores únicos extraídos: {stats['valores_unicos']}")
        if stats['registros_con_error'] > 0:
            print(f"  ⚠  Registros con errores: {stats['registros_con_error']:,}")
        print(f"  📁 Archivo de salida: {OUTPUT_JSON}")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"   Verifica que el archivo '{INPUT_CSV}' existe en el directorio actual.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
