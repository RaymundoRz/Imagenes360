#!/usr/bin/env python3
"""
Script para extraer index.html EN BRUTO del exterior de Honda
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time

def extract_exterior_index_bruto():
    """Extraer index.html EN BRUTO del exterior desde Honda"""
    
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
        
        # URL del index.html real del exterior de Honda
        url = "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_ext_360/index.html"
        
        print(f"🔍 Descargando exterior: {url}")
        
        # Navegar a la URL
        driver.get(url)
        time.sleep(5)  # Esperar más tiempo para que cargue completamente
        
        print(f"✅ Página cargada")
        print(f"   Título: {driver.title}")
        print(f"   URL Final: {driver.current_url}")
        print(f"   Tamaño del contenido: {len(driver.page_source)} bytes")
        
        # Obtener el contenido HTML EN BRUTO
        html_content = driver.page_source
        
        # Crear directorio si no existe
        output_dir = Path("backend/downloads/honda_city_2026/ViewType.EXTERIOR")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar index.html EN BRUTO como viewer.html
        viewer_file = output_dir / "viewer.html"
        with open(viewer_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 INDEX.HTML EXTERIOR GUARDADO EN BRUTO: {viewer_file}")
        print(f"   Tamaño del archivo: {viewer_file.stat().st_size} bytes")
        
        # También guardar como index.html original
        index_file = output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 INDEX.HTML EXTERIOR ORIGINAL GUARDADO: {index_file}")
        
        # Mostrar primeras líneas del contenido
        print(f"\n📄 PRIMERAS LÍNEAS DEL CONTENIDO EXTERIOR:")
        lines = html_content.split('\n')[:10]
        for i, line in enumerate(lines, 1):
            print(f"   {i:2d}: {line[:100]}{'...' if len(line) > 100 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("\n🔚 Chrome cerrado")

if __name__ == "__main__":
    extract_exterior_index_bruto()





