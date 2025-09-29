#!/usr/bin/env python3
"""
Script para probar la lógica de extracción del backend
"""

import asyncio
import aiohttp
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

async def test_extraction_logic():
    """Probar la lógica de extracción paso a paso"""
    
    year = "2026"
    view_type = "interior"
    quality_level = 0
    
    print(f"🔍 Probando extracción: {year} {view_type} calidad {quality_level}")
    
    # 1. CREAR DIRECTORIOS
    honda_original_base = Path(f"backend/downloads/honda_city_{year}_honda_original")
    system_base = Path(f"backend/downloads/honda_city_{year}/ViewType.{view_type.upper()}/{quality_level}")
    
    print(f"📁 Directorio Honda Original: {honda_original_base}")
    print(f"📁 Directorio Sistema: {system_base}")
    
    # 2. GENERAR LISTA DE ARCHIVOS
    base_url = f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360"
    print(f"🌐 URL Base: {base_url}")
    
    files_to_download = []
    
    if view_type == "interior":
        print("[INTERIOR] Generando lista INTERIOR...")
        for cf in range(6):  # cf_0 a cf_5
            for l in [1, 2]:  # SOLO l_1 y l_2
                for c in range(2):  # c_0 y c_1
                    for tile in range(2):  # tile_0.jpg y tile_1.jpg
                        file_path = f"tiles/node1/cf_{cf}/l_{l}/c_{c}/tile_{tile}.jpg"
                        files_to_download.append(file_path)
    
    print(f"📋 Total archivos a descargar: {len(files_to_download)}")
    
    # 3. FILTRAR SOLO TILES
    tiles_only = [f for f in files_to_download if f.endswith('.jpg')]
    print(f"🖼️ Tiles a descargar: {len(tiles_only)}")
    
    # 4. CREAR DIRECTORIOS
    honda_original_base.mkdir(parents=True, exist_ok=True)
    system_base.mkdir(parents=True, exist_ok=True)
    (system_base / "images").mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")
    
    # 5. FUNCIÓN DE DESCARGA
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    def download_file(file_info):
        file_path, index = file_info
        try:
            url = f"{base_url}/{file_path}"
            print(f"🔗 Descargando {index+1}/{len(tiles_only)}: {file_path}")
            
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
                
                print(f"   ✅ Guardado: {len(response.content)} bytes")
                return {'status': 'success', 'file': file_path, 'size': len(response.content)}
            
            elif response.status_code == 404:
                print(f"   ❌ 404 - No encontrado")
                return {'status': 'skip', 'file': file_path}
            else:
                print(f"   ⚠️ Error {response.status_code}")
                return {'status': 'error', 'file': file_path, 'code': response.status_code}
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {'status': 'error', 'file': file_path, 'error': str(e)}
    
    # 6. DESCARGA PARALELA
    print(f"\n🚀 Iniciando descarga paralela de {len(tiles_only)} tiles...")
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        file_list = [(file, i) for i, file in enumerate(tiles_only)]
        results = executor.map(download_file, file_list)
        
        for result in results:
            if result['status'] == 'success':
                downloaded += 1
                if downloaded % 5 == 0:  # Log cada 5 archivos
                    print(f"📊 Progreso: {downloaded} descargados | {failed} fallidos | {skipped} omitidos")
            elif result['status'] == 'skip':
                skipped += 1
            else:
                failed += 1
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   ✅ Descargados: {downloaded}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"   ⏭️ Omitidos: {skipped}")
    
    # 7. VERIFICAR ARCHIVOS GUARDADOS
    print(f"\n🔍 Verificando archivos guardados...")
    honda_files = list(honda_original_base.rglob("*.jpg"))
    system_files = list((system_base / "images").glob("*.jpg"))
    
    print(f"   📁 Honda Original: {len(honda_files)} archivos")
    print(f"   📁 Sistema: {len(system_files)} archivos")
    
    if honda_files:
        print(f"   📄 Ejemplo Honda: {honda_files[0]}")
    if system_files:
        print(f"   📄 Ejemplo Sistema: {system_files[0]}")

if __name__ == "__main__":
    asyncio.run(test_extraction_logic())





