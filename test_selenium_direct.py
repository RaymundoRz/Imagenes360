#!/usr/bin/env python3
"""
Script de diagnóstico para probar Selenium directamente con Honda
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_honda_urls():
    """Probar URLs de Honda directamente con Selenium"""
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    
    try:
        # Inicializar driver con múltiples métodos de fallback
        print("🚀 Iniciando Chrome WebDriver...")
        
        driver = None
        
        # Método 1: ChromeDriverManager
        try:
            print("   Intentando ChromeDriverManager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("   ✅ ChromeDriverManager funcionó")
        except Exception as e:
            print(f"   ❌ ChromeDriverManager falló: {e}")
            
            # Método 2: Chrome desde PATH
            try:
                print("   Intentando Chrome desde PATH...")
                driver = webdriver.Chrome(options=chrome_options)
                print("   ✅ Chrome desde PATH funcionó")
            except Exception as e:
                print(f"   ❌ Chrome desde PATH falló: {e}")
                
                # Método 3: Edge como fallback
                try:
                    print("   Intentando Edge como fallback...")
                    driver = webdriver.Edge(options=chrome_options)
                    print("   ✅ Edge funcionó")
                except Exception as e:
                    print(f"   ❌ Edge también falló: {e}")
                    return
        
        # URLs a probar
        urls_to_test = [
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/viewer.html",
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/config.xml",
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/skin.js",
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/pano2vr_player.js",
            "https://automobiles.honda.com/images/2026/city/360/ViewType.INTERIOR/viewer.html",
            "https://automobiles.honda.com/images/2026/city/360/ViewType.INTERIOR/config.xml"
        ]
        
        for url in urls_to_test:
            print(f"\n🔍 Probando: {url}")
            
            try:
                driver.get(url)
                time.sleep(3)
                
                print(f"   Status: {driver.title}")
                print(f"   Content Length: {len(driver.page_source)}")
                print(f"   URL Final: {driver.current_url}")
                
                # Verificar si es 404
                if "404" in driver.title or "not found" in driver.title.lower():
                    print("   ❌ 404 - No encontrado")
                else:
                    print("   ✅ ¡ARCHIVO ENCONTRADO!")
                    
                    # Mostrar primeras líneas del contenido
                    content_preview = driver.page_source[:200]
                    print(f"   Preview: {content_preview}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error inicializando Selenium: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("\n🔚 Chrome cerrado")

if __name__ == "__main__":
    test_honda_urls()
