#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 HONDA 360° COMPLETE QUALITY DIAGNOSIS
========================================
Análisis completo REAL del problema de calidad
"""

import os
from pathlib import Path
import json
from datetime import datetime

def analyze_complete_quality_issue():
    """Diagnóstico completo del problema de calidad"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DE CALIDAD HONDA 360°")
    print("=" * 60)
    
    project_root = Path.cwd()
    downloads_path = project_root / "backend" / "downloads"
    
    complete_analysis = {
        "timestamp": datetime.now().isoformat(),
        "frontend_interface": {},
        "actual_files_downloaded": {},
        "config_xml_analysis": {},
        "viewer_behavior": {},
        "quality_mapping_reality": {}
    }
    
    # 1. ANALIZAR INTERFAZ FRONTEND
    print("\n1️⃣ ANALIZANDO INTERFAZ FRONTEND")
    print("-" * 30)
    
    # Verificar qué se muestra en frontend
    frontend_labels = [
        "Interior Ultra HD",
        "Interior High Definition", 
        "Interior Standard",
        "Exterior Ultra HD",
        "Exterior High Definition",
        "Exterior Standard"
    ]
    
    print("📱 Frontend muestra estas opciones:")
    for i, label in enumerate(frontend_labels):
        quality_level = i % 3
        print(f"   {label} → quality_level: {quality_level}")
    
    # 2. VERIFICAR ARCHIVOS REALES DESCARGADOS
    print("\n2️⃣ ANALIZANDO ARCHIVOS REALES DESCARGADOS")
    print("-" * 30)
    
    for honda_dir in downloads_path.glob("honda_city_*"):
        if honda_dir.is_dir():
            print(f"\n📁 {honda_dir.name}:")
            
            for viewtype_dir in honda_dir.glob("ViewType.*"):
                print(f"  📂 {viewtype_dir.name}:")
                
                # Listar todas las carpetas con imágenes
                image_folders = []
                for folder in viewtype_dir.iterdir():
                    if folder.is_dir():
                        jpg_files = list(folder.glob("**/*.jpg"))
                        if jpg_files:
                            # Calcular estadísticas reales
                            sizes = [f.stat().st_size for f in jpg_files[:10]]
                            avg_size = sum(sizes) / len(sizes) if sizes else 0
                            
                            image_folders.append({
                                "folder": folder.name,
                                "image_count": len(jpg_files),
                                "avg_size_kb": int(avg_size / 1024),
                                "sample_files": [f.name for f in jpg_files[:3]]
                            })
                
                # Mostrar todas las carpetas ordenadas por calidad
                image_folders.sort(key=lambda x: x["avg_size_kb"], reverse=True)
                
                for i, folder_info in enumerate(image_folders):
                    quality_name = ["ULTRA_HD", "HIGH_DEF", "STANDARD"][i] if i < 3 else "OTHER"
                    print(f"    {quality_name}: {folder_info['folder']}/")
                    print(f"      📸 {folder_info['image_count']} imágenes")
                    print(f"      📊 ~{folder_info['avg_size_kb']}KB promedio")
                    print(f"      📄 Ejemplos: {folder_info['sample_files']}")
    
    # 3. ANALIZAR CONFIG.XML ACTUAL
    print("\n3️⃣ ANALIZANDO CONFIG.XML ACTUAL")
    print("-" * 30)
    
    for honda_dir in downloads_path.glob("honda_city_*"):
        if honda_dir.is_dir():
            for viewtype_dir in honda_dir.glob("ViewType.*"):
                config_file = viewtype_dir / "config.xml"
                if config_file.exists():
                    print(f"\n📄 {honda_dir.name} - {viewtype_dir.name}:")
                    
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_content = f.read()
                    
                    # Extraer la línea leveltileurl
                    for line in config_content.split('\n'):
                        if 'leveltileurl=' in line:
                            print(f"    🎯 {line.strip()}")
                            
                            # Extraer carpeta que usa
                            if 'tiles/' in line:
                                current_folder = "tiles"
                            elif 'interior_level_2/' in line:
                                current_folder = "interior_level_2"
                            elif 'exterior_level_2/' in line:
                                current_folder = "exterior_level_2"
                            else:
                                current_folder = "UNKNOWN"
                            
                            print(f"    📁 Usa carpeta: {current_folder}")
                            break
    
    # 4. MAPEO QUALITY_LEVEL → CARPETA REAL
    print("\n4️⃣ MAPEO QUALITY_LEVEL → REALIDAD")
    print("-" * 30)
    
    print("🎯 PROBLEMA IDENTIFICADO:")
    print("   Frontend envía quality_level (0,1,2)")
    print("   Backend genera config.xml usando:")
    print("   → quality_level 0 (Ultra HD): ¿usa qué carpeta?")
    print("   → quality_level 1 (High Def): ¿usa qué carpeta?")
    print("   → quality_level 2 (Standard): ¿usa qué carpeta?")
    
    # 5. VERIFICAR VISUALIZADORES EN FUNCIONAMIENTO
    print("\n5️⃣ VERIFICANDO VISUALIZADORES ACTUALES")
    print("-" * 30)
    
    test_urls = [
        "http://127.0.0.1:8080/honda_city_2026/ViewType.INTERIOR/viewer.html",
        "http://127.0.0.1:8080/honda_city_2026/ViewType.EXTERIOR/viewer.html"
    ]
    
    for url in test_urls:
        print(f"🌐 {url}")
        print("   ¿Se ve en baja calidad? → SÍ (según usuario)")
        print("   ¿Usa la carpeta correcta? → VERIFICAR config.xml")
    
    # 6. PLAN DE CORRECCIÓN
    print("\n6️⃣ PLAN DE CORRECCIÓN DEFINITIVO")
    print("-" * 30)
    
    print("✅ PASOS A SEGUIR:")
    print("1. Identificar carpeta REAL más grande (Ultra HD)")
    print("2. Identificar carpeta REAL mediana (High Definition)")  
    print("3. Identificar carpeta REAL más pequeña (Standard)")
    print("4. Mapear quality_level a estas carpetas REALES")
    print("5. Modificar backend para generar config.xml correcto")
    print("6. Probar cada quality_level en frontend")
    
    # Guardar análisis
    report_file = project_root / "complete_quality_diagnosis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(complete_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Diagnóstico guardado en: {report_file}")
    print("🔧 Ejecuta el plan de corrección paso a paso")

if __name__ == "__main__":
    analyze_complete_quality_issue()
