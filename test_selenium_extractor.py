"""
SCRIPT DE PRUEBA PARA SELENIUM EXTRACTOR
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio backend al path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.honda_selenium_extractor import extract_honda_assets_with_selenium

async def test_selenium_extractor():
    """Probar el extractor de Selenium"""
    
    print("=== PROBANDO SELENIUM EXTRACTOR ===")
    
    # Crear directorio de prueba
    test_dir = Path("test_selenium_output")
    test_dir.mkdir(exist_ok=True)
    
    # Probar extracción
    year = "2024"
    view_type = "interior"
    
    print(f"Probando extracción para Honda City {year} {view_type}...")
    print(f"Directorio de salida: {test_dir}")
    
    try:
        results = await extract_honda_assets_with_selenium(year, view_type, test_dir)
        
        print("\n=== RESULTADOS ===")
        print(f"config.xml: {'✓' if results['config_xml'] else '✗'}")
        print(f"viewer.html: {'✓' if results['viewer_html'] else '✗'}")
        print(f"skin.js: {'✓' if results['skin_js'] else '✗'}")
        print(f"player.js: {'✓' if results['player_js'] else '✗'}")
        
        if results['error']:
            print(f"Error: {results['error']}")
        
        # Verificar archivos generados
        print("\n=== ARCHIVOS GENERADOS ===")
        for file in test_dir.glob("*"):
            print(f"{file.name} - {file.stat().st_size} bytes")
        
        success_count = sum([
            results['config_xml'],
            results['viewer_html'], 
            results['skin_js'],
            results['player_js']
        ])
        
        print(f"\n=== RESUMEN ===")
        print(f"Assets obtenidos: {success_count}/4")
        
        if success_count > 0:
            print("✓ SELENIUM FUNCIONANDO!")
        else:
            print("✗ SELENIUM NO FUNCIONÓ")
            
    except Exception as e:
        print(f"Error en prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_selenium_extractor())








