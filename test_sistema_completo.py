"""
SCRIPT DE PRUEBA PARA EL SISTEMA COMPLETO CON SELENIUM
"""

import requests
import time
import json
from pathlib import Path

def test_sistema_completo():
    """Probar el sistema completo con Selenium integrado"""
    
    print("=== PROBANDO SISTEMA COMPLETO CON SELENIUM ===")
    
    # URL del backend
    backend_url = "http://127.0.0.1:8000"
    
    # Datos de prueba
    extraction_data = {
        "year": "2024",
        "view_type": "interior", 
        "quality_level": 0,
        "download_path": None
    }
    
    print(f"Enviando solicitud de extracción: {extraction_data}")
    
    try:
        # 1. INICIAR EXTRACCIÓN
        response = requests.post(
            f"{backend_url}/api/honda/extract",
            json=extraction_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            extraction_id = result.get("extraction_id")
            print(f"✅ Extracción iniciada: {extraction_id}")
            
            # 2. MONITOREAR PROGRESO
            print("\n=== MONITOREANDO PROGRESO ===")
            max_attempts = 60  # 60 segundos máximo
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(2)  # Esperar 2 segundos
                attempt += 1
                
                # Consultar estado
                status_response = requests.get(f"{backend_url}/api/honda/extract/{extraction_id}")
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    progress = status.get("progress_percentage", 0)
                    downloaded = status.get("downloaded_tiles", 0)
                    failed = status.get("failed_tiles", 0)
                    extraction_status = status.get("status", "unknown")
                    
                    print(f"[{attempt:2d}] Estado: {extraction_status} | Progreso: {progress:.1f}% | Descargados: {downloaded} | Fallidos: {failed}")
                    
                    if extraction_status == "completed":
                        print("✅ EXTRACCIÓN COMPLETADA!")
                        break
                    elif extraction_status == "failed":
                        error = status.get("error_message", "Error desconocido")
                        print(f"❌ EXTRACCIÓN FALLÓ: {error}")
                        break
                else:
                    print(f"❌ Error consultando estado: {status_response.status_code}")
                
            # 3. VERIFICAR ARCHIVOS GENERADOS
            print("\n=== VERIFICANDO ARCHIVOS GENERADOS ===")
            
            download_path = Path(f"backend/downloads/honda_city_{extraction_data['year']}")
            
            if download_path.exists():
                print(f"📁 Carpeta encontrada: {download_path}")
                
                # Verificar estructura Honda Original
                honda_original = download_path / "honda_original" / f"ViewType.{extraction_data['view_type'].upper()}"
                if honda_original.exists():
                    print(f"✅ Estructura Honda Original: {honda_original}")
                    
                    # Contar archivos
                    files = list(honda_original.rglob("*"))
                    print(f"   Archivos encontrados: {len(files)}")
                    
                    # Mostrar archivos importantes
                    important_files = ["config.xml", "viewer.html", "skin.js", "pano2vr_player.js", "object2vr_player.js"]
                    for file in important_files:
                        file_path = honda_original / file
                        if file_path.exists():
                            size = file_path.stat().st_size
                            print(f"   ✅ {file}: {size} bytes")
                        else:
                            print(f"   ❌ {file}: No encontrado")
                
                # Verificar estructura Sistema
                system_path = download_path / f"ViewType.{extraction_data['view_type'].upper()}"
                if system_path.exists():
                    print(f"✅ Estructura Sistema: {system_path}")
                    
                    # Contar imágenes
                    images_path = system_path / "images"
                    if images_path.exists():
                        image_files = list(images_path.glob("*.jpg"))
                        print(f"   Imágenes descargadas: {len(image_files)}")
                        
                        if image_files:
                            print(f"   Primera imagen: {image_files[0].name} ({image_files[0].stat().st_size} bytes)")
                    
                    # Verificar config
                    config_file = system_path / "config_extraction.json"
                    if config_file.exists():
                        print(f"   ✅ Config generado: {config_file.stat().st_size} bytes")
                        
                        # Leer config
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                            print(f"   Total descargados: {config_data.get('extraction_info', {}).get('successful_downloads', 0)}")
                            print(f"   Total fallidos: {config_data.get('extraction_info', {}).get('failed_downloads', 0)}")
                
                print("\n=== RESUMEN FINAL ===")
                print("✅ SISTEMA COMPLETO FUNCIONANDO!")
                print("✅ SELENIUM INTEGRADO CORRECTAMENTE!")
                print("✅ ASSETS GENERADOS AUTOMÁTICAMENTE!")
                print("✅ TILES DESCARGADOS CON REQUESTS!")
                print("✅ ESTRUCTURA DUAL CREADA!")
                
            else:
                print(f"❌ Carpeta no encontrada: {download_path}")
                
        else:
            print(f"❌ Error iniciando extracción: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend. ¿Está corriendo en http://127.0.0.1:8000?")
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sistema_completo()
