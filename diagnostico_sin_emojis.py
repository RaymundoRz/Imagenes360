#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO COMPLETO HONDA 360° - SIN EMOJIS
===========================================
Ejecuta todos los diagnósticos y genera reportes
"""

import os
import sys
from pathlib import Path
import json
import time

def run_system_monitor():
    """Ejecutar diagnóstico del sistema"""
    print("=== SISTEMA MONITOR ===")
    print("Verificando estado del sistema...")
    
    # Verificar backend
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"Backend API: OK (HTTP {response.status_code})")
    except:
        print("Backend API: ERROR - No disponible")
    
    # Verificar frontend
    try:
        import requests
        response = requests.get("http://127.0.0.1:5174", timeout=5)
        print(f"Frontend: OK (HTTP {response.status_code})")
    except:
        print("Frontend: ERROR - No disponible")
    
    # Verificar file server
    try:
        import requests
        response = requests.get("http://127.0.0.1:8080", timeout=5)
        print(f"File Server: OK (HTTP {response.status_code})")
    except:
        print("File Server: ERROR - No disponible")
    
    print()

def run_quality_fixer():
    """Ejecutar análisis de calidad"""
    print("=== QUALITY FIXER ===")
    
    downloads_path = Path("backend/downloads/honda_city_2026")
    if not downloads_path.exists():
        print("ERROR: Directorio downloads no existe")
        return
    
    # Analizar ViewType.INTERIOR
    interior_path = downloads_path / "ViewType.INTERIOR"
    if interior_path.exists():
        print("ViewType.INTERIOR:")
        
        # Buscar archivos de imagen
        jpg_files = list(interior_path.rglob("*.jpg"))
        print(f"  - Archivos JPG encontrados: {len(jpg_files)}")
        
        # Analizar config.xml
        config_file = interior_path / "config.xml"
        if config_file.exists():
            print(f"  - config.xml: EXISTE ({config_file.stat().st_size} bytes)")
        else:
            print("  - config.xml: NO EXISTE")
        
        # Analizar carpetas de imágenes
        tiles_path = interior_path / "tiles"
        if tiles_path.exists():
            print(f"  - tiles/: EXISTE")
            # Contar archivos en tiles
            tile_files = list(tiles_path.rglob("*.jpg"))
            print(f"    - Archivos en tiles: {len(tile_files)}")
        else:
            print("  - tiles/: NO EXISTE")
    
    # Analizar ViewType.EXTERIOR
    exterior_path = downloads_path / "ViewType.EXTERIOR"
    if exterior_path.exists():
        print("ViewType.EXTERIOR:")
        
        # Buscar archivos de imagen
        jpg_files = list(exterior_path.rglob("*.jpg"))
        print(f"  - Archivos JPG encontrados: {len(jpg_files)}")
        
        # Analizar config.xml
        config_file = exterior_path / "config.xml"
        if config_file.exists():
            print(f"  - config.xml: EXISTE ({config_file.stat().st_size} bytes)")
        else:
            print("  - config.xml: NO EXISTE")
        
        # Analizar carpetas de imágenes
        tiles_path = exterior_path / "tiles"
        if tiles_path.exists():
            print(f"  - tiles/: EXISTE")
            # Contar archivos en tiles
            tile_files = list(tiles_path.rglob("*.jpg"))
            print(f"    - Archivos en tiles: {len(tile_files)}")
        else:
            print("  - tiles/: NO EXISTE")
    
    print()

def run_advanced_quality_fixer():
    """Ejecutar análisis avanzado"""
    print("=== ADVANCED QUALITY FIXER ===")
    
    downloads_path = Path("backend/downloads/honda_city_2026")
    
    # Analizar estructura honda_original
    honda_original_path = downloads_path / "honda_original"
    if honda_original_path.exists():
        print("honda_original/")
        
        # Verificar ViewType.INTERIOR
        interior_orig = honda_original_path / "ViewType.INTERIOR"
        if interior_orig.exists():
            print("  ViewType.INTERIOR:")
            orig_files = list(interior_orig.rglob("*"))
            print(f"    - Archivos totales: {len(orig_files)}")
            
            # Buscar config.xml original
            config_orig = interior_orig / "config.xml"
            if config_orig.exists():
                print(f"    - config.xml original: EXISTE ({config_orig.stat().st_size} bytes)")
            else:
                print("    - config.xml original: NO EXISTE")
        
        # Verificar ViewType.EXTERIOR
        exterior_orig = honda_original_path / "ViewType.EXTERIOR"
        if exterior_orig.exists():
            print("  ViewType.EXTERIOR:")
            orig_files = list(exterior_orig.rglob("*"))
            print(f"    - Archivos totales: {len(orig_files)}")
            
            # Buscar config.xml original
            config_orig = exterior_orig / "config.xml"
            if config_orig.exists():
                print(f"    - config.xml original: EXISTE ({config_orig.stat().st_size} bytes)")
            else:
                print("    - config.xml original: NO EXISTE")
    else:
        print("honda_original/: NO EXISTE")
    
    print()

def run_complete_diagnosis():
    """Ejecutar diagnóstico completo"""
    print("=== DIAGNÓSTICO COMPLETO ===")
    
    downloads_path = Path("backend/downloads/honda_city_2026")
    
    # Análisis general
    print("ESTADO GENERAL:")
    print(f"  - Directorio base: {downloads_path}")
    print(f"  - Existe: {'SÍ' if downloads_path.exists() else 'NO'}")
    
    if downloads_path.exists():
        # Contar archivos totales
        all_files = list(downloads_path.rglob("*"))
        files_only = [f for f in all_files if f.is_file()]
        dirs_only = [f for f in all_files if f.is_dir()]
        
        print(f"  - Archivos totales: {len(files_only)}")
        print(f"  - Carpetas totales: {len(dirs_only)}")
        
        # Analizar archivos JPG
        jpg_files = list(downloads_path.rglob("*.jpg"))
        print(f"  - Archivos JPG: {len(jpg_files)}")
        
        # Analizar archivos XML
        xml_files = list(downloads_path.rglob("*.xml"))
        print(f"  - Archivos XML: {len(xml_files)}")
        
        # Analizar archivos HTML
        html_files = list(downloads_path.rglob("*.html"))
        print(f"  - Archivos HTML: {len(html_files)}")
        
        # Analizar archivos JS
        js_files = list(downloads_path.rglob("*.js"))
        print(f"  - Archivos JS: {len(js_files)}")
    
    print()

def main():
    """Ejecutar todos los diagnósticos"""
    print("DIAGNÓSTICO COMPLETO HONDA 360° EXTRACTOR")
    print("=" * 50)
    print(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    run_system_monitor()
    run_quality_fixer()
    run_advanced_quality_fixer()
    run_complete_diagnosis()
    
    print("DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main()








