#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extractor de Datos JSON desde CSV o Elasticsearch
Punto de entrada principal con interfaz CLI
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any


def comando_csv(args):
    """Procesa archivo CSV local"""
    from extractor_csv import procesar_csv
    
    try:
        print("=" * 60)
        print("  PROCESADOR DE CSV LOCAL")
        print("=" * 60)
        print()
        
        stats = procesar_csv(args.input, args.output)
        
        print()
        print("=" * 60)
        print("  ✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"  📋 Registros procesados: {stats['registros_procesados']:,}")
        print(f"  📊 Valores únicos extraídos: {stats['valores_unicos']}")
        if stats.get('registros_con_error', 0) > 0:
            print(f"  ⚠  Registros con errores: {stats['registros_con_error']:,}")
        print(f"  📁 Archivo de salida: {args.output}")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def comando_elasticsearch(args):
    """Descarga y procesa logs desde Elasticsearch"""
    from config import load_config
    from elasticsearch_client import ElasticsearchClient
    from data_processor import procesar_registros_iterable
    
    try:
        print("=" * 60)
        print("  EXTRACTOR DESDE ELASTICSEARCH")
        print("=" * 60)
        print()
        
        # Cargar configuración
        print("⚙️  Cargando configuración...")
        config = load_config()
        print(f"✓ Configuración cargada: {config.es_host}")
        
        # Cargar query
        query_dict = cargar_query(args.query_file)
        
        # Mostrar query si está en modo verbose
        if args.verbose:
            print("\n📋 Query a ejecutar:")
            print(json.dumps(query_dict, indent=2))
            print()
        
        # Conectar a Elasticsearch
        print("🔌 Conectando a Elasticsearch...")
        client = ElasticsearchClient(config)
        
        # Test de conexión
        info = client.test_connection()
        print(f"✅ Conectado a: {info['cluster_name']} (v{info['version']})")
        
        # Obtener estimación de documentos
        index = args.index or config.es_index
        print(f"📊 Índice: {index}")
        
        total_est = client.get_total_estimate(query_dict, index)
        if total_est > 0:
            print(f"📊 Documentos estimados: {total_est:,}")
        
        print()
        
        # Decisión: CSV intermedio o directo a JSON
        if args.output_csv:
            # Opción A: Descargar a CSV, luego procesar
            print(f"📥 Descargando a CSV intermedio: {args.output_csv}")
            count = client.download_to_csv(query_dict, args.output_csv, index_pattern=index)
            
            if count == 0:
                print("⚠️  No se encontraron documentos que coincidan con la query")
                return
            
            # Procesar el CSV descargado
            print(f"\n📊 Procesando CSV a JSON: {args.output_json}")
            from extractor_csv import procesar_csv
            stats = procesar_csv(args.output_csv, args.output_json)
            
        else:
            # Opción B: Procesamiento directo sin CSV intermedio
            print("📥 Descargando y procesando directamente a JSON...")
            docs_generator = client.get_documents_generator(query_dict, index)
            stats = procesar_registros_iterable(docs_generator, args.output_json, show_progress=True)
        
        # Resumen final
        print()
        print("=" * 60)
        print("  ✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"  📋 Registros procesados: {stats['registros_procesados']:,}")
        print(f"  📊 Registros con valores: {stats.get('registros_con_valores', 'N/A'):,}")
        print(f"  📊 Valores únicos extraídos: {stats['valores_unicos']}")
        print(f"  📁 Archivo de salida JSON: {args.output_json}")
        if args.output_csv:
            print(f"  📁 Archivo CSV intermedio: {args.output_csv}")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def comando_test_connection(args):
    """Prueba la conexión con Elasticsearch"""
    from config import load_config
    from elasticsearch_client import ElasticsearchClient
    
    try:
        print("=" * 60)
        print("  TEST DE CONEXIÓN ELASTICSEARCH")
        print("=" * 60)
        print()
        
        # Cargar configuración
        print("⚙️  Cargando configuración...")
        config = load_config()
        
        print(f"📋 Host: {config.es_host}")
        print(f"📋 Usuario: {config.es_user}")
        print(f"📋 Índice: {config.es_index}")
        print(f"📋 SSL Verify: {config.verify_ssl}")
        print()
        
        # Conectar
        print("🔌 Probando conexión...")
        client = ElasticsearchClient(config)
        info = client.test_connection()
        
        print("✅ ¡Conexión exitosa!")
        print()
        print(f"  Cluster: {info['cluster_name']}")
        print(f"  Versión: {info['version']}")
        print(f"  Host: {info['host']}")
        print()
        
        # Listar índices disponibles
        print(f"📊 Índices disponibles con patrón '{config.es_index}':")
        indices = client.get_available_indices(config.es_index)
        
        if indices:
            for idx in indices[:10]:
                print(f"  ✓ {idx}")
            if len(indices) > 10:
                print(f"  ... y {len(indices) - 10} índices más")
        else:
            print("  ⚠️  No se encontraron índices con ese patrón")
        
        print()
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def cargar_query(query_file: str = None) -> Dict[str, Any]:
    """
    Carga query desde archivo JSON o retorna query por defecto
    
    Args:
        query_file: Ruta al archivo JSON con la query (opcional)
        
    Returns:
        dict: Query de Elasticsearch
    """
    if query_file:
        query_path = Path(query_file)
        if not query_path.exists():
            raise FileNotFoundError(f"Archivo de query no encontrado: {query_file}")
        
        with open(query_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Query por defecto: últimos 7 días, mensajes con "Body"
        return {
            "query": {
                "bool": {
                    "must": [
                        {"wildcard": {"message": "*Body:*"}},
                        {"exists": {"field": "message"}}
                    ],
                    "filter": [
                        {"range": {"@timestamp": {"gte": "now-7d"}}}
                    ]
                }
            },
            "_source": ["message", "@timestamp"]
        }


def main():
    """Función principal con argumentos CLI"""
    parser = argparse.ArgumentParser(
        description='Extractor de datos JSON desde CSV o Elasticsearch',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Procesar CSV local
  python main.py csv --input datos.csv --output salida.json

  # Descargar desde Elasticsearch directamente a JSON
  python main.py elasticsearch --output-json salida.json

  # Descargar desde Elasticsearch con CSV intermedio
  python main.py elasticsearch --output-csv logs.csv --output-json salida.json

  # Usar query personalizada
  python main.py elasticsearch --query-file queries/custom.json --output-json salida.json

  # Probar conexión
  python main.py test-connection
        """
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Comando a ejecutar')
    subparsers.required = True
    
    # Subcomando: csv
    parser_csv = subparsers.add_parser('csv', help='Procesar archivo CSV local')
    parser_csv.add_argument('--input', '-i', required=True, 
                           help='Archivo CSV de entrada')
    parser_csv.add_argument('--output', '-o', required=True,
                           help='Archivo JSON de salida')
    parser_csv.set_defaults(func=comando_csv)
    
    # Subcomando: elasticsearch
    parser_es = subparsers.add_parser('elasticsearch', help='Descargar desde Elasticsearch')
    parser_es.add_argument('--query-file', '-q',
                          help='Archivo JSON con query personalizada (opcional)')
    parser_es.add_argument('--output-json', '-o', required=True,
                          help='Archivo JSON de salida')
    parser_es.add_argument('--output-csv', '-c',
                          help='Guardar CSV intermedio (opcional)')
    parser_es.add_argument('--index', '-idx',
                          help='Patrón de índices (override de .env)')
    parser_es.add_argument('--verbose', '-v', action='store_true',
                          help='Mostrar query y detalles adicionales')
    parser_es.set_defaults(func=comando_elasticsearch)
    
    # Subcomando: test-connection
    parser_test = subparsers.add_parser('test-connection', help='Probar conexión con Elasticsearch')
    parser_test.set_defaults(func=comando_test_connection)
    
    # Parsear argumentos y ejecutar comando
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
