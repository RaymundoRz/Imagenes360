#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROBADOR DE URLs REALES DE HONDA
===============================
Encuentra las URLs que realmente funcionan
"""

import requests
import time

def test_url(url, description):
    """Probar una URL específica"""
    try:
        print(f"Probando: {description}")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"OK FUNCIONA - Tamaño: {len(response.content)} bytes")
            return True
        else:
            print(f"ERROR FALLA - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR ERROR: {e}")
        return False
    finally:
        print("-" * 60)

def main():
    print("PROBANDO URLs REALES DE HONDA CITY 2026")
    print("=" * 60)
    
    # URLs base a probar
    bases_a_probar = [
        # Honda México
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360",
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_ext_360",
        
        # Honda Global
        "https://automobiles.honda.com/images/2026/city/360",
        "https://automobiles.honda.com/images/2026/city/360/ViewType.INTERIOR",
        "https://automobiles.honda.com/images/2026/city/360/ViewType.EXTERIOR",
        
        # Honda CDN
        "https://cdn.honda.com/images/city/2026/360/interior",
        "https://cdn.honda.com/images/city/2026/360/exterior",
        
        # Honda Assets
        "https://assets.honda.com/city/2026/360",
        
        # Variaciones de año
        "https://www.honda.mx/web/img/cars/models/city/2025/city_2025_int_360",
        "https://www.honda.mx/web/img/cars/models/city/2024/city_2024_int_360",
    ]
    
    archivos_a_probar = [
        "config.xml",
        "pano.xml", 
        "tour.xml",
        "index.html",
        "viewer.html",
        "tiles/node1/cf_0/l_0/c_0/tile_0.jpg",
        "tiles/c0_l0_0_0.jpg"
    ]
    
    urls_funcionando = []
    
    for base in bases_a_probar:
        print(f"\nPROBANDO BASE: {base}")
        print("=" * 80)
        
        for archivo in archivos_a_probar:
            url_completa = f"{base}/{archivo}"
            descripcion = f"{base.split('/')[-1]} - {archivo}"
            
            if test_url(url_completa, descripcion):
                urls_funcionando.append(url_completa)
            
            time.sleep(0.5)  # No sobrecargar
    
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    
    if urls_funcionando:
        print(f"OK URLs QUE FUNCIONAN ({len(urls_funcionando)}):")
        for url in urls_funcionando:
            print(f"  - {url}")
    else:
        print("ERROR NO SE ENCONTRARON URLs QUE FUNCIONEN")
        print("\nPROBANDO URLS ALTERNATIVAS...")
        
        # URLs alternativas conocidas
        urls_alternativas = [
            "https://httpbin.org/get",  # Test que siempre funciona
            "https://jsonplaceholder.typicode.com/posts/1",  # API de prueba
        ]
        
        for url in urls_alternativas:
            test_url(url, "URL de prueba")

if __name__ == "__main__":
    main()
