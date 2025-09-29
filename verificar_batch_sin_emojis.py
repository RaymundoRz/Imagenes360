import requests
import json

def verificar_batch_status():
    """Verificar el estado actual de todos los jobs del batch"""
    
    print("VERIFICANDO ESTADO DE BATCH PROCESSING")
    print("="*50)
    
    try:
        # 1. Listar todos los jobs
        print("1. Listando todos los jobs...")
        response = requests.get("http://127.0.0.1:8000/api/honda/batch-list", timeout=10)
        
        if response.status_code == 200:
            batch_data = response.json()
            print(f"Total jobs encontrados: {batch_data['total_jobs']}")
            
            if batch_data['total_jobs'] > 0:
                print("\n2. Estado de cada job:")
                print("-" * 50)
                
                for job_id, job_result in batch_data['jobs'].items():
                    status = job_result.get('status', 'unknown')
                    year = job_result.get('year', 'N/A')
                    view_type = job_result.get('view_type', 'N/A')
                    quality = job_result.get('quality_level', 'N/A')
                    
                    print(f"\nJob: {job_id[:8]}...")
                    print(f"   Tipo: {year} {view_type} calidad {quality}")
                    print(f"   Estado: {status}")
                    
                    if status == 'completed':
                        successful = job_result.get('successful_downloads', 0)
                        total = job_result.get('total_tiles', 0)
                        size = job_result.get('total_size_mb', 0)
                        time_taken = job_result.get('download_time_seconds', 0)
                        success_rate = job_result.get('success_rate', 0)
                        
                        print(f"   COMPLETADO - Tiles: {successful}/{total}")
                        print(f"   Tasa exito: {success_rate}%")
                        print(f"   Tamaño: {size} MB")
                        print(f"   Tiempo: {time_taken}s")
                        
                    elif status == 'processing':
                        print(f"   PROCESANDO...")
                        
                    elif status == 'failed':
                        error = job_result.get('error', 'Desconocido')
                        print(f"   ERROR: {error}")
                        
                    elif status == 'queued':
                        print(f"   EN COLA...")
                        
                    else:
                        print(f"   ESTADO DESCONOCIDO: {status}")
                        
            else:
                print("No hay jobs en el sistema")
                
        else:
            print(f"Error obteniendo lista: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexion: {e}")
        
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    verificar_batch_status()








