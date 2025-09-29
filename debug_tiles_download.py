#!/usr/bin/env python3
"""
Script para diagnosticar por qué no se descargan los tiles
"""

import requests
import os
from pathlib import Path

def test_tile_download():
    """Probar descarga de tiles individuales"""
    
    year = "2026"
    view_type = "interior"
    quality_level = 0
    
    # URL base
    base_url = f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360"
    
    print(f"🔍 Probando descarga de tiles desde: {base_url}")
    
    # Generar algunas URLs de prueba
    test_files = []
    
    if view_type == "interior":
        # Probar algunos tiles del interior
        for cf in range(3):  # Solo primeras 3 caras
            for l in [1, 2]:  # l_1 y l_2
                for c in range(2):  # c_0 y c_1
                    for tile in range(2):  # tile_0.jpg y tile_1.jpg
                        file_path = f"tiles/node1/cf_{cf}/l_{l}/c_{c}/tile_{tile}.jpg"
                        test_files.append(file_path)
    
    print(f"📋 Probando {len(test_files)} tiles...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(test_files[:6]):  # Solo probar primeros 6
        url = f"{base_url}/{file_path}"
        print(f"\n🔗 Probando {i+1}/6: {file_path}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200 and len(response.content) > 500:
                print(f"   ✅ ÉXITO - Archivo válido")
                successful += 1
                
                # Guardar archivo de prueba
                test_dir = Path("test_tiles")
                test_dir.mkdir(exist_ok=True)
                test_file = test_dir / f"test_tile_{i}.jpg"
                with open(test_file, 'wb') as f:
                    f.write(response.content)
                print(f"   💾 Guardado: {test_file}")
                
            elif response.status_code == 404:
                print(f"   ❌ 404 - No encontrado")
                failed += 1
            else:
                print(f"   ⚠️ Error {response.status_code}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    print(f"\n📊 RESULTADO:")
    print(f"   ✅ Exitosos: {successful}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"   📁 Archivos de prueba guardados en: test_tiles/")

if __name__ == "__main__":
    test_tile_download()





