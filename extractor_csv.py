#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extractor de datos JSON desde CSV de logs
Extrae campos con valores no nulos del JSON embebido en logs CSV
NOTA: Este módulo mantiene retrocompatibilidad. Para nuevo código, usa data_processor.py
"""

import csv
from pathlib import Path
from typing import Dict

# Importar funciones desde el módulo refactorizado
from data_processor import procesar_mensaje

# ===========================================
# CONFIGURACIÓN - Modifica estas rutas según necesites
# ===========================================
INPUT_CSV = "Error Evaluacion Niveles Escala.csv"
OUTPUT_JSON = "datos_extraidos.json"


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
    
    print(f"📂 Procesando archivo: {input_path}")
    
    # Crear generador de registros desde CSV
    def csv_generator():
        with open(input_file, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                yield row
    
    # Usar el procesador común
    from data_processor import procesar_registros_iterable
    stats = procesar_registros_iterable(csv_generator(), output_path, show_progress=True)
    
    return {
        "registros_procesados": stats["registros_procesados"],
        "registros_con_error": stats["registros_procesados"] - stats["registros_con_valores"],
        "valores_unicos": stats["valores_unicos"]
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
