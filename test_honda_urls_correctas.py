#!/usr/bin/env python3
"""
🎯 SCRIPT PARA ENCONTRAR LAS URLs CORRECTAS DE HONDA 2026
Basado en que los archivos SÍ EXISTEN (restaurados por el usuario)
"""

import requests
import time

def test_honda_url(base_url, file_path):
    """Probar una URL específica"""
    full_url = f"{base_url}/{file_path}"
    try:
        print(f"🔍 Probando: {full_url}")
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == 200 and len(response.content) > 0:
            print(f"✅ FUNCIONA: {full_url} ({len(response.content)} bytes)")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {full_url}")
            return False
    except Exception as e:
        print(f"💥 ERROR: {full_url} - {str(e)}")
        return False

def main():
    print("🚀 BUSCANDO URLs CORRECTAS HONDA CITY 2026")
    print("=" * 60)
    
    # POSIBLES URLs BASE PARA 2026
    possible_base_urls = [
        # Las que estoy usando ahora (que fallan)
        "https://www.honda.mx/autos/city/2026/city_2026_int_360",
        "https://www.honda.mx/autos/city/2026/city_2026_ext_360",
        
        # Variaciones web/img
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360",
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_ext_360",
        
        # Sin year en la URL
        "https://www.honda.mx/autos/city/city_2026_int_360", 
        "https://www.honda.mx/autos/city/city_2026_ext_360",
        
        # Estructura diferente
        "https://www.honda.mx/city/2026/360/interior",
        "https://www.honda.mx/city/2026/360/exterior",
        
        # Como 2024 que funciona
        "https://www.honda.mx/autos/city/2024/city_2024_int_360",
        "https://www.honda.mx/autos/city/2024/city_2024_ext_360",
    ]
    
    # ARCHIVOS CLAVE PARA PROBAR
    test_files = [
        "config.xml",
        "viewer.html", 
        "assets/pano2vr_player.js",
        "assets/object2vr_player.js",
        "assets/skin.js",
        "tiles/node1/cf_0/l_2/c_0/tile_0.jpg",  # Interior tile
        "tiles/c0_l2_0_0.jpg"  # Exterior tile
    ]
    
    print("\n🔍 PROBANDO URLs...")
    
    working_urls = []
    
    for base_url in possible_base_urls:
        print(f"\n📍 BASE URL: {base_url}")
        success_count = 0
        
        for test_file in test_files:
            if test_honda_url(base_url, test_file):
                success_count += 1
            time.sleep(0.2)  # No saturar el servidor
        
        if success_count > 0:
            working_urls.append({
                "url": base_url,
                "success_count": success_count,
                "total_tests": len(test_files)
            })
            print(f"🎯 ÉXITO PARCIAL: {success_count}/{len(test_files)} archivos encontrados")
        
        print("-" * 50)
    
    print("\n🏆 RESUMEN FINAL:")
    if working_urls:
        for result in sorted(working_urls, key=lambda x: x["success_count"], reverse=True):
            percentage = (result["success_count"] / result["total_tests"]) * 100
            print(f"✅ {result['url']}")
            print(f"   📊 {result['success_count']}/{result['total_tests']} archivos ({percentage:.1f}%)")
    else:
        print("❌ NINGUNA URL FUNCIONA - Revisar estructura manualmente")

if __name__ == "__main__":
    main()








