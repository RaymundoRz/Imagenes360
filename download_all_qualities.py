#!/usr/bin/env python3
"""
Script para descargar las 3 calidades de Honda City 2026 Interior
"""

import asyncio
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

def download_quality(quality_level: int):
    """Descargar una calidad específica"""
    
    year = "2026"
    view_type = "interior"
    
    print(f"\n🚀 === DESCARGANDO CALIDAD {quality_level} ===")
    
    # URLs base
    base_url = f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360"
    
    # Directorios
    honda_original_base = Path(f"backend/downloads/honda_city_{year}_honda_original_q{quality_level}")
    system_base = Path(f"backend/downloads/honda_city_{year}/ViewType.{view_type.upper()}/{quality_level}")
    
    print(f"📁 Honda Original: {honda_original_base}")
    print(f"📁 Sistema: {system_base}")
    
    # Crear directorios
    honda_original_base.mkdir(parents=True, exist_ok=True)
    system_base.mkdir(parents=True, exist_ok=True)
    (system_base / "images").mkdir(parents=True, exist_ok=True)
    
    # Generar lista de archivos
    files_to_download = []
    
    # Tiles del interior (6 caras x 2 niveles x 2 columnas x 2 tiles = 48 archivos)
    for cf in range(6):  # cf_0 a cf_5
        for l in [1, 2]:  # l_1 y l_2
            for c in range(2):  # c_0 y c_1
                for tile in range(2):  # tile_0.jpg y tile_1.jpg
                    file_path = f"tiles/node1/cf_{cf}/l_{l}/c_{c}/tile_{tile}.jpg"
                    files_to_download.append(file_path)
    
    print(f"📋 Total archivos: {len(files_to_download)}")
    
    # Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    def download_file(file_info):
        file_path, index = file_info
        try:
            url = f"{base_url}/{file_path}"
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200 and len(response.content) > 500:
                # Guardar archivo original Honda
                honda_file = honda_original_base / file_path
                honda_file.parent.mkdir(parents=True, exist_ok=True)
                with open(honda_file, 'wb') as f:
                    f.write(response.content)
                
                # Guardar archivo sistema
                system_filename = f"tile_{index:04d}.jpg"
                system_file = system_base / "images" / system_filename
                with open(system_file, 'wb') as f:
                    f.write(response.content)
                
                return {'status': 'success', 'file': file_path, 'size': len(response.content)}
            
            elif response.status_code == 404:
                return {'status': 'skip', 'file': file_path}
            else:
                return {'status': 'error', 'file': file_path, 'code': response.status_code}
                
        except Exception as e:
            return {'status': 'error', 'file': file_path, 'error': str(e)}
    
    # Descarga paralela
    print(f"🔄 Iniciando descarga paralela...")
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        file_list = [(file, i) for i, file in enumerate(files_to_download)]
        results = executor.map(download_file, file_list)
        
        for result in results:
            if result['status'] == 'success':
                downloaded += 1
                if downloaded % 10 == 0:
                    print(f"   📊 Progreso: {downloaded} descargados")
            elif result['status'] == 'skip':
                skipped += 1
            else:
                failed += 1
    
    print(f"\n📊 CALIDAD {quality_level} COMPLETADA:")
    print(f"   ✅ Descargados: {downloaded}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"   ⏭️ Omitidos: {skipped}")
    
    # Verificar archivos guardados
    honda_files = list(honda_original_base.rglob("*.jpg"))
    system_files = list((system_base / "images").glob("*.jpg"))
    
    print(f"   📁 Honda Original: {len(honda_files)} archivos")
    print(f"   📁 Sistema: {len(system_files)} archivos")
    
    return downloaded, failed, skipped

def main():
    """Descargar las 3 calidades"""
    
    print("🎯 === DESCARGANDO LAS 3 CALIDADES DE HONDA CITY 2026 INTERIOR ===")
    
    total_downloaded = 0
    total_failed = 0
    total_skipped = 0
    
    for quality in [0, 1, 2]:
        downloaded, failed, skipped = download_quality(quality)
        total_downloaded += downloaded
        total_failed += failed
        total_skipped += skipped
    
    print(f"\n🎉 === DESCARGA COMPLETA ===")
    print(f"   ✅ Total descargados: {total_downloaded}")
    print(f"   ❌ Total fallidos: {total_failed}")
    print(f"   ⏭️ Total omitidos: {total_skipped}")
    
    print(f"\n📁 Archivos guardados en:")
    print(f"   backend/downloads/honda_city_2026/ViewType.INTERIOR/0/")
    print(f"   backend/downloads/honda_city_2026/ViewType.INTERIOR/1/")
    print(f"   backend/downloads/honda_city_2026/ViewType.INTERIOR/2/")

if __name__ == "__main__":
    main()





