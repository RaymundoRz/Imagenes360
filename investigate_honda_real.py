#!/usr/bin/env python3
"""
INGENIERÍA INVERSA HONDA - ENCONTRAR MODELOS 360° REALES
"""

import requests
import re
from bs4 import BeautifulSoup

def find_360_patterns():
    """Encontrar patrones 360° reales en Honda.mx"""
    
    models_to_check = [
        "city", "civic", "hr-v", "cr-v", "accord", "pilot", "odyssey", "br-v"
    ]
    
    print("=== INVESTIGACION HONDA 360° REAL ===")
    print()
    
    found_models = {}
    
    for model in models_to_check:
        print(f"Investigando {model.upper()}...")
        
        try:
            # Obtener página del modelo
            url = f"https://www.honda.mx/autos/{model}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Buscar patrones 360°
                patterns_360 = [
                    r'web/img/cars/models/([^/]+)/([^/]+)/([^"\']+)_360',
                    r'360.*?/([^/]+)/([^/]+)',
                    r'pano\.xml',
                    r'object2vr',
                    r'pano2vr'
                ]
                
                found_patterns = []
                for pattern in patterns_360:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        found_patterns.extend(matches)
                
                if found_patterns:
                    print(f"  ✅ {model.upper()} tiene 360°: {found_patterns[:3]}")
                    found_models[model] = found_patterns
                else:
                    print(f"  ❌ {model.upper()} sin 360°")
            else:
                print(f"  ⚠️ {model.upper()} página no accesible: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {model.upper()} error: {e}")
    
    print()
    print("=== MODELOS CON 360° CONFIRMADOS ===")
    for model, patterns in found_models.items():
        print(f"{model.upper()}: {patterns}")
    
    return found_models

def test_specific_urls():
    """Probar URLs específicas encontradas"""
    
    print()
    print("=== PROBANDO URLs ESPECÍFICAS ===")
    
    # URLs que pueden existir basadas en patrones comunes
    test_urls = [
        # City (ya confirmado)
        "https://www.honda.mx/web/img/cars/models/city/2024/city_2024_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/pano.xml",
        
        # Civic variaciones
        "https://www.honda.mx/web/img/cars/models/civic/2024/civic_2024_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/civic/2025/civic_2025_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/civic/2026/civic_2026_int_360/pano.xml",
        
        # HR-V variaciones
        "https://www.honda.mx/web/img/cars/models/hr-v/2024/hrv_2024_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/hr-v/2025/hrv_2025_int_360/pano.xml", 
        "https://www.honda.mx/web/img/cars/models/hr-v/2026/hrv_2026_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/hrv/2026/hrv_2026_int_360/pano.xml",
        
        # CR-V variaciones
        "https://www.honda.mx/web/img/cars/models/cr-v/2024/crv_2024_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/cr-v/2025/crv_2025_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/cr-v/2026/crv_2026_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/crv/2026/crv_2026_int_360/pano.xml",
        
        # Accord variaciones
        "https://www.honda.mx/web/img/cars/models/accord/2024/accord_2024_int_360/pano.xml",
        "https://www.honda.mx/web/img/cars/models/accord/2025/accord_2025_int_360/pano.xml",
    ]
    
    existing_configs = []
    
    for url in test_urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ EXISTE: {url}")
                existing_configs.append(url)
            else:
                print(f"❌ NO EXISTE ({response.status_code}): {url}")
        except:
            print(f"❌ ERROR: {url}")
    
    return existing_configs

if __name__ == "__main__":
    # 1. Buscar patrones en páginas
    found_models = find_360_patterns()
    
    # 2. Probar URLs específicas
    existing_configs = test_specific_urls()
    
    print()
    print("=== RESUMEN FINAL ===")
    print(f"Modelos con referencias 360°: {list(found_models.keys())}")
    print(f"Configuraciones XML existentes: {len(existing_configs)}")
    print()
    print("URLs CONFIRMADAS:")
    for url in existing_configs:
        print(f"  {url}")

