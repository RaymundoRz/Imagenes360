#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISIS DE PROBLEMAS DETECTADOS
================================
Analiza específicamente los problemas encontrados
"""

from pathlib import Path
import json

def analizar_problemas():
    """Analizar los problemas específicos detectados"""
    
    print("ANÁLISIS DE PROBLEMAS DETECTADOS")
    print("=" * 40)
    
    downloads_path = Path("backend/downloads/honda_city_2026")
    
    # PROBLEMA 1: ViewType.EXTERIOR - Completamente vacío
    print("\n1. PROBLEMA: ViewType.EXTERIOR - Completamente vacío")
    print("-" * 50)
    
    exterior_path = downloads_path / "ViewType.EXTERIOR"
    if exterior_path.exists():
        print(f"OK Carpeta existe: {exterior_path}")
        
        # Contar archivos
        all_files = list(exterior_path.rglob("*"))
        files_only = [f for f in all_files if f.is_file()]
        dirs_only = [f for f in all_files if f.is_dir()]
        
        print(f"  - Archivos totales: {len(files_only)}")
        print(f"  - Carpetas totales: {len(dirs_only)}")
        
        if len(files_only) == 0:
            print("  ERROR CONFIRMADO: No hay archivos")
        else:
            print("  OK Archivos encontrados:")
            for f in files_only:
                print(f"    - {f.name} ({f.stat().st_size} bytes)")
        
        # Verificar subcarpetas
        print("  - Subcarpetas:")
        for subdir in exterior_path.iterdir():
            if subdir.is_dir():
                files_in_subdir = list(subdir.rglob("*"))
                files_count = len([f for f in files_in_subdir if f.is_file()])
                print(f"    - {subdir.name}: {files_count} archivos")
    else:
        print("ERROR Carpeta NO existe")
    
    # PROBLEMA 2: honda_original/ - Completamente vacío
    print("\n2. PROBLEMA: honda_original/ - Completamente vacío")
    print("-" * 50)
    
    honda_original_path = downloads_path / "honda_original"
    if honda_original_path.exists():
        print(f"OK Carpeta existe: {honda_original_path}")
        
        # Contar archivos
        all_files = list(honda_original_path.rglob("*"))
        files_only = [f for f in all_files if f.is_file()]
        dirs_only = [f for f in all_files if f.is_dir()]
        
        print(f"  - Archivos totales: {len(files_only)}")
        print(f"  - Carpetas totales: {len(dirs_only)}")
        
        if len(files_only) == 0:
            print("  ERROR CONFIRMADO: No hay archivos")
        else:
            print("  OK Archivos encontrados:")
            for f in files_only:
                print(f"    - {f.name} ({f.stat().st_size} bytes)")
        
        # Verificar subcarpetas
        print("  - Subcarpetas:")
        for subdir in honda_original_path.iterdir():
            if subdir.is_dir():
                files_in_subdir = list(subdir.rglob("*"))
                files_count = len([f for f in files_in_subdir if f.is_file()])
                print(f"    - {subdir.name}: {files_count} archivos")
    else:
        print("ERROR Carpeta NO existe")
    
    # PROBLEMA 3: Archivos faltantes - HTML, JS, config.xml de EXTERIOR
    print("\n3. PROBLEMA: Archivos faltantes - HTML, JS, config.xml de EXTERIOR")
    print("-" * 70)
    
    exterior_path = downloads_path / "ViewType.EXTERIOR"
    
    # Verificar config.xml
    config_file = exterior_path / "config.xml"
    if config_file.exists():
        print(f"OK config.xml: EXISTE ({config_file.stat().st_size} bytes)")
    else:
        print("ERROR config.xml: NO EXISTE")
    
    # Verificar viewer.html
    viewer_file = exterior_path / "viewer.html"
    if viewer_file.exists():
        print(f"OK viewer.html: EXISTE ({viewer_file.stat().st_size} bytes)")
    else:
        print("ERROR viewer.html: NO EXISTE")
    
    # Verificar index.html
    index_file = exterior_path / "index.html"
    if index_file.exists():
        print(f"OK index.html: EXISTE ({index_file.stat().st_size} bytes)")
    else:
        print("ERROR index.html: NO EXISTE")
    
    # Verificar archivos JS
    js_files = list(exterior_path.rglob("*.js"))
    if js_files:
        print(f"OK Archivos JS: {len(js_files)} encontrados")
        for js in js_files:
            print(f"  - {js.name} ({js.stat().st_size} bytes)")
    else:
        print("ERROR Archivos JS: NINGUNO encontrado")
    
    # Verificar assets/
    assets_path = exterior_path / "assets"
    if assets_path.exists():
        assets_files = list(assets_path.glob("*"))
        if assets_files:
            print(f"OK assets/: {len(assets_files)} archivos")
            for asset in assets_files:
                print(f"  - {asset.name} ({asset.stat().st_size} bytes)")
        else:
            print("ERROR assets/: VACÍO")
    else:
        print("ERROR assets/: NO EXISTE")
    
    # COMPARACIÓN CON INTERIOR (que SÍ tiene archivos)
    print("\n4. COMPARACIÓN CON ViewType.INTERIOR (que SÍ funciona)")
    print("-" * 60)
    
    interior_path = downloads_path / "ViewType.INTERIOR"
    if interior_path.exists():
        print(f"OK ViewType.INTERIOR existe")
        
        # Contar archivos
        all_files = list(interior_path.rglob("*"))
        files_only = [f for f in all_files if f.is_file()]
        
        print(f"  - Archivos totales: {len(files_only)}")
        
        # Mostrar archivos encontrados
        print("  OK Archivos encontrados:")
        for f in files_only:
            print(f"    - {f.name} ({f.stat().st_size} bytes)")
        
        # Verificar config.xml
        config_interior = interior_path / "config.xml"
        if config_interior.exists():
            print(f"  OK config.xml: EXISTE ({config_interior.stat().st_size} bytes)")
        else:
            print("  ERROR config.xml: NO EXISTE")
    
    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    analizar_problemas()
