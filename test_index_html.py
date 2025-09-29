#!/usr/bin/env python3
"""
Script para probar index.html en Honda
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_index_html():
    """Probar index.html en URLs de Honda"""
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    
    try:
        # Inicializar driver
        print("🚀 Iniciando Chrome WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # URLs a probar con index.html
        urls_to_test = [
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/index.html",
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_ext_360/index.html",
            "https://automobiles.honda.com/images/2026/city/360/ViewType.INTERIOR/index.html",
            "https://automobiles.honda.com/images/2026/city/360/ViewType.EXTERIOR/index.html"
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
                    print("   ✅ ¡INDEX.HTML ENCONTRADO!")
                    
                    # Mostrar primeras líneas del contenido
                    content_preview = driver.page_source[:300]
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
    test_index_html()





