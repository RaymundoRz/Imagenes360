from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from typing import List, Dict, Optional
import uuid
from datetime import datetime
from pathlib import Path
import logging
import os
import asyncio
import aiohttp
import aiofiles
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from app.services.honda_selenium_extractor import extract_honda_assets_with_selenium
from app.utils.patterns import get_all_honda_models, get_confirmed_models  # AGREGAR

router = APIRouter()

# Storage en memoria para extracciones activas 
active_extractions: Dict[str, dict] = {}

# MODELOS ADAPTADOS SIMPLES (sin dependencias externas)
class ExtractionRequest:
    def __init__(self, year: str, view_type: str, quality_level: int = 0, download_path: Optional[str] = None):
        self.year = year
        self.view_type = view_type
        self.quality_level = quality_level
        self.download_path = download_path

class ExtractionResponse:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

async def process_honda_files_for_local_system(honda_original_path: Path, system_local_path: Path, year: str, view_type: str, images_for_system: list):
    """
    PROCESA AUTOMÁTICAMENTE los archivos de Honda para funcionar con el sistema local
    - Toma config.xml y viewer.html originales de Honda
    - Reemplaza URLs de Honda por URLs del sistema local  
    - Genera viewer_local.html y config_local.xml funcionales
    """
    print("[PROCESAMIENTO] Generando archivos locales desde Honda originales...")
    
    try:
        # 1. PROCESAR CONFIG.XML
        honda_config_file = honda_original_path / "config.xml"
        if honda_config_file.exists():
            with open(honda_config_file, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Reemplazar patrones de tiles por URLs del sistema local
            if view_type == "interior":
                # De: tiles/node1/cf_%c/l_%l/c_%x/tile_%y.jpg
                # A: /api/honda/images/2026/interior/tile_%c_%l_%x.jpg  
                config_content = config_content.replace(
                    'tiles/node1/cf_%c/l_%l/c_%x/tile_%y.jpg',
                    f'/api/honda/images/{year}/{view_type.lower()}/tile_%c_%l_%x.jpg'
                )
            else:  # exterior
                # De: tiles/c%c_l%r_%y_%x.jpg
                # A: /api/honda/images/2026/exterior/tile_%c_%r_%y.jpg
                config_content = config_content.replace(
                    'tiles/c%c_l%r_%y_%x.jpg', 
                    f'/api/honda/images/{year}/{view_type.lower()}/tile_%c_%r_%y.jpg'
                )
            
            # Guardar config_local.xml
            local_config_file = system_local_path / "config_local.xml"
            with open(local_config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f"[OK] config_local.xml generado")
        
        # 2. PROCESAR VIEWER.HTML
        honda_viewer_file = honda_original_path / "viewer.html"
        if honda_viewer_file.exists():
            with open(honda_viewer_file, 'r', encoding='utf-8') as f:
                viewer_content = f.read()
            
            # Reemplazar referencias a archivos por URLs del sistema local
            replacements = {
                'config.xml': 'config_local.xml',
                'pano.js': f'http://127.0.0.1:8000/api/honda/honda_city_{year}/ViewType/{view_type.lower()}/assets/pano.js',
                'object2vr.js': f'http://127.0.0.1:8000/api/honda/honda_city_{year}/ViewType/{view_type.lower()}/assets/object2vr.js',
                'skin.js': f'http://127.0.0.1:8000/api/honda/honda_city_{year}/ViewType/{view_type.lower()}/assets/skin.js',
                'style.css': f'http://127.0.0.1:8000/api/honda/honda_city_{year}/ViewType/{view_type.lower()}/assets/style.css'
            }
            
            for old_ref, new_ref in replacements.items():
                viewer_content = viewer_content.replace(old_ref, new_ref)
            
            # Guardar viewer_local.html
            local_viewer_file = system_local_path / "viewer_local.html"
            with open(local_viewer_file, 'w', encoding='utf-8') as f:
                f.write(viewer_content)
            print(f"[OK] viewer_local.html generado")
        
        print("[PROCESAMIENTO] Archivos locales generados correctamente")
        
    except Exception as e:
        print(f"[ERROR] Error procesando archivos Honda: {e}")

# FUNCIÓN DE DESCARGA DUAL (Honda Original + Sistema Funcional)
async def perform_extraction(extraction_id: str, year: str, view_type: str, quality_level: int, download_path: Optional[str]):
    """
    EXTRACCIÓN MASIVA BASADA EN DATOS REALES CONFIRMADOS
    - Interior: 6 caras × 2 niveles × 2 columnas × 2 tiles = 48 archivos exactos
    - Exterior: 32 columnas × 2 tiles + assets = 68 archivos exactos
    - Descarga paralela con 4 hilos
    - Estructura dual: Honda Original + Sistema Optimizado
    """
    
    try:
        print(f"[EXTRACCION] INICIANDO EXTRACCION MASIVA CON DATOS REALES: {extraction_id}")
        active_extractions[extraction_id]["status"] = "in_progress"
        
        # URLs CORRECTAS PROBADAS
        base_url = f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360"
        print(f"[URL] URL Base: {base_url}")
        
        # GENERAR LISTA DE ARCHIVOS BASADA EN DATOS REALES
        files_to_download = []
        
        if view_type == "interior":
            print("[INTERIOR] Generando lista INTERIOR (6 caras x 2 niveles x 2 columnas x 2 tiles = 48 archivos)...")
            # DATOS REALES: 6 caras x 2 niveles x 2 columnas x 2 tiles = 48 archivos
            for cf in range(6):  # cf_0 a cf_5
                for l in [1, 2]:  # SOLO l_1 y l_2 (como en datos reales)
                    for c in range(2):  # c_0 y c_1
                        for tile in range(2):  # tile_0.jpg y tile_1.jpg
                            file_path = f"tiles/node1/cf_{cf}/l_{l}/c_{c}/tile_{tile}.jpg"
                            files_to_download.append(file_path)
        
        else:  # exterior
            print("[EXTERIOR] Generando lista EXTERIOR (32 columnas x 2 tiles + assets = 68 archivos)...")
            # DATOS REALES: 32 columnas x 2 tiles = 64 archivos
            for col in range(32):  # column_00 a column_31
                for tile in range(2):  # tile_0_0.jpg y tile_0_1.jpg
                    file_path = f"exterior_level_2/column_{col:02d}/tile_0_{tile}.jpg"
                    files_to_download.append(file_path)
            
            # Assets que SÍ existen según datos reales
            assets = ["config.xml", "viewer.html", "assets/object2vr_player.js", "assets/skin.js"]
            files_to_download.extend(assets)
        
        total_files = len(files_to_download)
        active_extractions[extraction_id]["total_tiles"] = total_files
        
        print(f"[LISTA] LISTA GENERADA: {total_files} archivos para descargar")
        
        # CREAR ESTRUCTURA DE CARPETAS COMPLETA
        base_path = Path(f"downloads/honda_city_{year}")
        
        # Estructura Honda Original (solo crear cuando se necesite)
        honda_original_base = base_path / "honda_original" / f"ViewType.{view_type.upper()}"
        honda_original_base.mkdir(parents=True, exist_ok=True)
        # Las subcarpetas se crearán automáticamente cuando se guarden archivos
        
        # Estructura Sistema (solo crear cuando se necesite)
        system_base = base_path / f"ViewType.{view_type.upper()}"
        system_base.mkdir(parents=True, exist_ok=True)
        # Las subcarpetas se crearán automáticamente cuando se guarden archivos
        
        # HEADERS OPTIMIZADOS
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'https://www.honda.mx/web/img/cars/models/city/{year}/',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        # PROCESO DE DESCARGA MASIVA CON THREADS
        downloaded = 0
        failed = 0
        skipped = 0
        successful_files = []
        
        import time
        
        def download_file(file_info):
            file_path, index = file_info
            try:
                url = f"{base_url}/{file_path}"
                
                # Hacer request con timeout
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200 and len(response.content) > 500:  # Archivos válidos
                    
                    # Guardar archivo original Honda (estructura exacta)
                    honda_file = honda_original_base / file_path
                    honda_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(honda_file, 'wb') as f:
                        f.write(response.content)
                    
                    # Guardar archivo sistema (optimizado)
                    if file_path.endswith('.jpg'):
                        # Imágenes: numeración secuencial
                        system_filename = f"tile_{len(successful_files):04d}.jpg"
                        system_file = system_base / "images" / system_filename
                    else:
                        # Archivos config/assets: mantener estructura
                        system_file = system_base / file_path
                        system_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(system_file, 'wb') as f:
                        f.write(response.content)
                    
                    return {
                        'status': 'success', 
                        'file': file_path, 
                        'size': len(response.content),
                        'index': index
                    }
                
                elif response.status_code == 404:
                    return {'status': 'skip', 'file': file_path, 'index': index}
                else:
                    return {'status': 'error', 'file': file_path, 'code': response.status_code, 'index': index}
                    
            except Exception as e:
                return {'status': 'error', 'file': file_path, 'error': str(e), 'index': index}
        
        # PRIMERO: USAR SELENIUM PARA OBTENER ASSETS PRINCIPALES
        print(f"[SELENIUM] Iniciando extracción de assets principales con Selenium...")
        selenium_results = await extract_honda_assets_with_selenium(year, view_type, honda_original_base, quality_level)
        
        selenium_success = 0
        if selenium_results["config_xml"]:
            selenium_success += 1
            print("[SELENIUM] config.xml obtenido")
        if selenium_results["viewer_html"]:
            selenium_success += 1
            print("[SELENIUM] viewer.html obtenido")
        if selenium_results["skin_js"]:
            selenium_success += 1
            print("[SELENIUM] skin.js obtenido")
        if selenium_results["player_js"]:
            selenium_success += 1
            print("[SELENIUM] player.js obtenido")
        
        print(f"[SELENIUM] Assets obtenidos: {selenium_success}/4")
        
        # SEGUNDO: DESCARGA PARALELA DE TILES (4 hilos simultaneos)
        print(f"[DESCARGA] Iniciando descarga paralela de tiles con 4 hilos...")
        
        # Filtrar solo tiles (excluir assets que ya obtuvimos con Selenium)
        tiles_only = [f for f in files_to_download if f.endswith('.jpg')]
        print(f"[DESCARGA] Descargando {len(tiles_only)} tiles...")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            file_list = [(file, i) for i, file in enumerate(tiles_only)]
            results = executor.map(download_file, file_list)
            
            for result in results:
                if result['status'] == 'success':
                    downloaded += 1
                    successful_files.append(result['file'])
                    if downloaded % 10 == 0:  # Log cada 10 archivos
                        print(f"[PROGRESO] Descargados: {downloaded} | Fallidos: {failed} | Omitidos: {skipped}")
                elif result['status'] == 'skip':
                    skipped += 1
                else:
                    failed += 1
                
                # Actualizar progreso
                completed = downloaded + failed + skipped
                active_extractions[extraction_id]["progress_percentage"] = (completed / len(tiles_only)) * 100
                active_extractions[extraction_id]["downloaded_tiles"] = downloaded
                active_extractions[extraction_id]["failed_tiles"] = failed
        
        # 📄 GENERAR CONFIGURACIÓN LOCAL COMPLETA
        config_completo = {
            "extraction_info": {
                "date": datetime.now().isoformat(),
                "year": year,
                "view_type": view_type,
                "base_url": base_url,
                "total_attempted": total_files,
                "successful_downloads": downloaded,
                "failed_downloads": failed,
                "skipped_files": skipped
            },
            "file_structure": {
                "honda_original_path": str(honda_original_base),
                "system_optimized_path": str(system_base),
                "successful_files": successful_files[:50]  # Primeros 50 para no sobrecargar
            },
            "viewer_config": {
                "image_base_url": f"http://127.0.0.1:8080/honda_city_{year}/ViewType.{view_type.upper()}/images/",
                "viewer_url": f"http://127.0.0.1:8080/honda_city_{year}/ViewType.{view_type.upper()}/viewer.html",
                "total_images": downloaded,
                "pattern": "tiles/node1/cf_X/l_Y/c_Z/tile_N.jpg" if view_type == "interior" else "exterior_level_2/column_XX/tile_0_N.jpg"
            }
        }
        
        # Guardar configuración
        config_file = system_base / "config_extraction.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_completo, f, indent=2, ensure_ascii=False)
        
        # FINALIZAR EXTRACCION
        extraction = active_extractions[extraction_id]
        extraction["status"] = "completed"
        extraction["downloaded_tiles"] = downloaded
        extraction["failed_tiles"] = failed 
        extraction["progress_percentage"] = 100.0
        extraction["completed_at"] = datetime.now().isoformat()
        
        print(f"[COMPLETADO] EXTRACCION MASIVA COMPLETADA:")
        print(f"   [SELENIUM] Assets principales: {selenium_success}/4")
        print(f"   [TILES] Tiles descargados: {downloaded}")
        print(f"   [ERROR] Archivos fallidos: {failed}")
        print(f"   [SKIP] Archivos omitidos (404): {skipped}")
        print(f"   [FOLDER] Honda Original: {honda_original_base}")
        print(f"   [FOLDER] Sistema Optimizado: {system_base}")
        print(f"   [CONFIG] Config generado: {config_file}")
        
        # SI DESCARGAMOS ALGO, ES EXITO
        if downloaded > 0 or selenium_success > 0:
            print(f"[EXITO] EXTRACCION COMPLETADA CON {downloaded} TILES + {selenium_success} ASSETS!")
        else:
            print(f"[WARNING] Sin archivos descargados. Revisar URLs o conectividad.")
            
    except Exception as e:
        extraction = active_extractions[extraction_id]
        extraction["status"] = "failed"
        extraction["error_message"] = str(e)
        extraction["completed_at"] = datetime.now().isoformat()
        print(f"[ERROR] ERROR CRITICO EN EXTRACCION MASIVA: {e}")

@router.post("/extract")
async def start_extraction(request: dict, background_tasks: BackgroundTasks):
    """Iniciar extracción de imágenes Honda City - ENDPOINT ORIGINAL"""
    
    # Generar ID único para la extracción
    extraction_id = str(uuid.uuid4())
    
    # Crear response inicial
    response = {
        "extraction_id": extraction_id,
        "status": "pending",
        "year": request.get("year", "2026"),
        "view_type": request.get("view_type", "interior"),
        "total_tiles": 0,  # Se calculará en background
        "downloaded_tiles": 0,
        "failed_tiles": 0,
        "progress_percentage": 0.0,
        "estimated_time_remaining": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "error_message": None
    }
    
    # Guardar en storage
    active_extractions[extraction_id] = response
    
    # Iniciar extracción en background
    background_tasks.add_task(
        perform_extraction, 
        extraction_id, 
        request.get("year", "2026"),
        request.get("view_type", "interior"),
        request.get("quality_level", 0),
        request.get("download_path")
    )
    
    return response

@router.get("/extract/{extraction_id}")
async def get_extraction_status(extraction_id: str):
    """Obtener estado de una extracción específica"""
    
    if extraction_id not in active_extractions:
        raise HTTPException(status_code=404, detail="Extracción no encontrada")
    
    return active_extractions[extraction_id]

@router.get("/extractions")
async def list_all_extractions():
    """Listar todas las extracciones (activas y completadas)"""
    return list(active_extractions.values())

@router.delete("/extract/{extraction_id}")
async def delete_extraction(extraction_id: str):
    """Eliminar registro de extracción"""
    
    if extraction_id not in active_extractions:
        raise HTTPException(status_code=404, detail="Extracción no encontrada")
    
    del active_extractions[extraction_id]
    return {"message": f"Extracción {extraction_id} eliminada"}

@router.get("/images/{year}/{view_type}/{quality_level}")
async def get_images_list(year: str, view_type: str, quality_level: int):
    base_path = Path(f"downloads/honda_city_{year}/ViewType.{view_type.upper()}")
    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Images not found")
    
    images = []
    # NUEVA RUTA: busca en /images/ en vez de /tiles/
    images_path = base_path / "images"
    if images_path.exists():
        for jpg_file in images_path.glob("*.jpg"):
            images.append({
                "filename": jpg_file.name,
                "url": f"http://127.0.0.1:8000/api/honda/images/{year}/{view_type}/{jpg_file.stem}"
            })
    
    return {"year": year, "view_type": view_type, "quality_level": quality_level, "total_images": len(images), "images": images}

@router.get("/images/{year}/{view_type}/{image_index}")
async def get_single_image(year: str, view_type: str, image_index: str):
    """Servir una imagen individual por índice"""
    try:
        base_path = Path(f"downloads/honda_city_{year}/ViewType.{view_type.upper()}")
        images_path = base_path / "images"
        
        if not images_path.exists():
            raise HTTPException(status_code=404, detail="Images folder not found")
        
        # Buscar imagen por índice
        image_file = images_path / f"tile_{image_index}.jpg"
        if not image_file.exists():
            # Buscar con otros patrones
            for pattern in [f"tile_{image_index}_*.jpg", f"*_{image_index}.jpg", f"tile_*_{image_index}.jpg"]:
                matches = list(images_path.glob(pattern))
                if matches:
                    image_file = matches[0]
                    break
            else:
                raise HTTPException(status_code=404, detail=f"Image {image_index} not found")
        
        return FileResponse(path=image_file, media_type="image/jpeg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/honda_city_{year}/ViewType/{view_type}/viewer_local.html")
async def serve_local_viewer_html(year: str, view_type: str):
    """Servir el viewer_local.html generado automáticamente desde Honda original"""
    try:
        base_path = Path(f"downloads/honda_city_{year}")
        viewer_file = base_path / f"ViewType.{view_type.upper()}" / "viewer_local.html"
        
        if viewer_file.exists():
            return FileResponse(
                path=viewer_file,
                media_type="text/html",
                filename="viewer_local.html"
            )
        else:
            raise HTTPException(status_code=404, detail="Viewer local no encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/honda_city_{year}/ViewType/{view_type}/assets/{asset_name}")
async def serve_honda_assets(year: str, view_type: str, asset_name: str):
    """Servir assets originales de Honda (JS, CSS) desde honda_original"""
    try:
        base_path = Path(f"downloads/honda_city_{year}")
        asset_file = base_path / "honda_original" / f"ViewType.{view_type.upper()}" / asset_name
        
        if asset_file.exists():
            # Determinar media type
            media_types = {
                '.js': 'application/javascript',
                '.css': 'text/css',
                '.html': 'text/html'
            }
            
            file_ext = asset_file.suffix.lower()
            media_type = media_types.get(file_ext, 'application/octet-stream')
            
            return FileResponse(
                path=asset_file,
                media_type=media_type,
                filename=asset_name
            )
        else:
            raise HTTPException(status_code=404, detail=f"Asset {asset_name} no encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/honda_city_2026/ViewType/{view_type}/viewer.html")
async def serve_viewer_html(view_type: str):
    if view_type.lower() == "interior":
        # VISUALIZADOR PANO2VR PARA INTERIOR (Cubo 360°)
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Honda City 2026 Interior 360°</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #000;
            font-family: Arial, sans-serif;
        }}
        #viewer-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
        }}
        #pano-viewer {{
            width: 100%;
            height: 100%;
            cursor: grab;
        }}
        #pano-viewer:active {{
            cursor: grabbing;
        }}
        .controls {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 100;
            background: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 10px;
            color: white;
        }}
        .quality-selector {{
            margin: 0 10px;
        }}
        .quality-btn {{
            background: #444;
            color: white;
            border: none;
            padding: 5px 10px;
            margin: 0 2px;
            border-radius: 3px;
            cursor: pointer;
        }}
        .quality-btn.active {{
            background: #d32f2f;
        }}
    </style>
</head>
<body>
    <div id="viewer-container">
        <canvas id="pano-viewer"></canvas>
        <div class="controls">
            <span>Calidad:</span>
            <div class="quality-selector">
                <button class="quality-btn active" onclick="changeQuality(0)">Ultra HD</button>
                <button class="quality-btn" onclick="changeQuality(1)">HD</button>
                <button class="quality-btn" onclick="changeQuality(2)">Standard</button>
            </div>
            <div style="margin-top: 5px; font-size: 12px;">
                Arrastra para navegar • Rueda del ratón para zoom
            </div>
        </div>
    </div>

    <script>
        class PanoViewer {{
            constructor() {{
                this.canvas = document.getElementById('pano-viewer');
                this.ctx = this.canvas.getContext('2d');
                this.currentQuality = 0;
                this.images = [];
                this.currentFace = 0;
                this.rotation = {{ x: 0, y: 0 }};
                this.zoom = 1.0;
                this.isDragging = false;
                this.lastMouse = {{ x: 0, y: 0 }};
                
                this.initCanvas();
                this.setupEvents();
                this.loadImages();
            }}
            
            initCanvas() {{
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
            }}
            
            setupEvents() {{
                // Mouse events
                this.canvas.addEventListener('mousedown', (e) => {{
                    this.isDragging = true;
                    this.lastMouse = {{ x: e.clientX, y: e.clientY }};
                }});
                
                this.canvas.addEventListener('mousemove', (e) => {{
                    if (this.isDragging) {{
                        const deltaX = e.clientX - this.lastMouse.x;
                        const deltaY = e.clientY - this.lastMouse.y;
                        
                        this.rotation.y += deltaX * 0.01;
                        this.rotation.x += deltaY * 0.01;
                        
                        this.rotation.x = Math.max(-Math.PI/2, Math.min(Math.PI/2, this.rotation.x));
                        
                        this.lastMouse = {{ x: e.clientX, y: e.clientY }};
                        this.render();
                    }}
                }});
                
                this.canvas.addEventListener('mouseup', () => {{
                    this.isDragging = false;
                }});
                
                // Wheel zoom
                this.canvas.addEventListener('wheel', (e) => {{
                    e.preventDefault();
                    this.zoom *= e.deltaY > 0 ? 0.9 : 1.1;
                    this.zoom = Math.max(0.5, Math.min(3.0, this.zoom));
                    this.render();
                }});
                
                // Touch events
                this.canvas.addEventListener('touchstart', (e) => {{
                    e.preventDefault();
                    if (e.touches.length === 1) {{
                        this.isDragging = true;
                        this.lastMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
                    }}
                }});
                
                this.canvas.addEventListener('touchmove', (e) => {{
                    e.preventDefault();
                    if (this.isDragging && e.touches.length === 1) {{
                        const deltaX = e.touches[0].clientX - this.lastMouse.x;
                        const deltaY = e.touches[0].clientY - this.lastMouse.y;
                        
                        this.rotation.y += deltaX * 0.01;
                        this.rotation.x += deltaY * 0.01;
                        
                        this.rotation.x = Math.max(-Math.PI/2, Math.min(Math.PI/2, this.rotation.x));
                        
                        this.lastMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
                        this.render();
                    }}
                }});
                
                this.canvas.addEventListener('touchend', () => {{
                    this.isDragging = false;
                }});
                
                // Resize
                window.addEventListener('resize', () => {{
                    this.initCanvas();
                    this.render();
                }});
            }}
            
            async loadImages() {{
                try {{
                    const response = await fetch('/api/honda/images/2026/interior/0');
                    const data = await response.json();
                    
                    // Cargar imágenes del cubo (6 caras)
                    const imagePromises = data.images.slice(0, 18).map(img => {{
                        return new Promise((resolve) => {{
                            const image = new Image();
                            image.crossOrigin = 'anonymous';
                            image.onload = () => resolve(image);
                            image.onerror = () => resolve(null);
                            image.src = img.url;
                        }});
                    }});
                    
                    this.images = await Promise.all(imagePromises);
                    this.render();
                }} catch (error) {{
                    console.error('Error loading images:', error);
                }}
            }}
            
            render() {{
                if (this.images.length === 0) return;
                
                this.ctx.fillStyle = '#000';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Renderizar cara actual basada en rotación
                const faceIndex = Math.floor(((this.rotation.y % (Math.PI * 2)) + Math.PI * 2) / (Math.PI / 3)) % 6;
                const levelIndex = this.currentQuality * 6;
                const imageIndex = levelIndex + faceIndex;
                
                if (this.images[imageIndex]) {{
                    const img = this.images[imageIndex];
                    const scale = this.zoom;
                    const w = this.canvas.width * scale;
                    const h = this.canvas.height * scale;
                    const x = (this.canvas.width - w) / 2;
                    const y = (this.canvas.height - h) / 2;
                    
                    this.ctx.drawImage(img, x, y, w, h);
                }}
            }}
        }}
        
        let viewer;
        
        function changeQuality(quality) {{
            // Update UI
            document.querySelectorAll('.quality-btn').forEach((btn, idx) => {{
                btn.classList.toggle('active', idx === quality);
            }});
            
            if (viewer) {{
                viewer.currentQuality = quality;
                viewer.render();
            }}
        }}
        
        // Initialize viewer
        window.addEventListener('load', () => {{
            viewer = new PanoViewer();
        }});
    </script>
</body>
</html>'''
    else:
        # VISUALIZADOR OBJECT2VR PARA EXTERIOR (Cilíndrico 360°)
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Honda City 2026 Exterior 360°</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #000;
            font-family: Arial, sans-serif;
        }}
        #viewer-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
        }}
        #object-viewer {{
            width: 100%;
            height: 100%;
            cursor: grab;
        }}
        #object-viewer:active {{
            cursor: grabbing;
        }}
        .controls {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 100;
            background: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 10px;
            color: white;
        }}
        .quality-selector {{
            margin: 0 10px;
        }}
        .quality-btn {{
            background: #444;
            color: white;
            border: none;
            padding: 5px 10px;
            margin: 0 2px;
            border-radius: 3px;
            cursor: pointer;
        }}
        .quality-btn.active {{
            background: #d32f2f;
        }}
    </style>
</head>
<body>
    <div id="viewer-container">
        <canvas id="object-viewer"></canvas>
        <div class="controls">
            <span>Calidad:</span>
            <div class="quality-selector">
                <button class="quality-btn active" onclick="changeQuality(0)">Ultra HD</button>
                <button class="quality-btn" onclick="changeQuality(1)">HD</button>
                <button class="quality-btn" onclick="changeQuality(2)">Standard</button>
            </div>
            <div style="margin-top: 5px; font-size: 12px;">
                Arrastra horizontalmente para rotar • Rueda del ratón para zoom
            </div>
        </div>
    </div>

    <script>
        class ObjectViewer {{
            constructor() {{
                this.canvas = document.getElementById('object-viewer');
                this.ctx = this.canvas.getContext('2d');
                this.currentQuality = 0;
                this.images = [];
                this.currentColumn = 0;
                this.totalColumns = 32;
                this.rotation = 0;
                this.zoom = 1.0;
                this.isDragging = false;
                this.lastMouse = {{ x: 0, y: 0 }};
                
                this.initCanvas();
                this.setupEvents();
                this.loadImages();
            }}
            
            initCanvas() {{
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
            }}
            
            setupEvents() {{
                // Mouse events
                this.canvas.addEventListener('mousedown', (e) => {{
                    this.isDragging = true;
                    this.lastMouse = {{ x: e.clientX, y: e.clientY }};
                }});
                
                this.canvas.addEventListener('mousemove', (e) => {{
                    if (this.isDragging) {{
                        const deltaX = e.clientX - this.lastMouse.x;
                        
                        this.rotation += deltaX * 0.01;
                        this.currentColumn = Math.floor(((this.rotation % (Math.PI * 2)) + Math.PI * 2) / (Math.PI * 2) * this.totalColumns) % this.totalColumns;
                        
                        this.lastMouse = {{ x: e.clientX, y: e.clientY }};
                        this.render();
                    }}
                }});
                
                this.canvas.addEventListener('mouseup', () => {{
                    this.isDragging = false;
                }});
                
                // Wheel zoom
                this.canvas.addEventListener('wheel', (e) => {{
                    e.preventDefault();
                    this.zoom *= e.deltaY > 0 ? 0.9 : 1.1;
                    this.zoom = Math.max(0.5, Math.min(3.0, this.zoom));
                    this.render();
                }});
                
                // Touch events
                this.canvas.addEventListener('touchstart', (e) => {{
                    e.preventDefault();
                    if (e.touches.length === 1) {{
                        this.isDragging = true;
                        this.lastMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
                    }}
                }});
                
                this.canvas.addEventListener('touchmove', (e) => {{
                    e.preventDefault();
                    if (this.isDragging && e.touches.length === 1) {{
                        const deltaX = e.touches[0].clientX - this.lastMouse.x;
                        
                        this.rotation += deltaX * 0.01;
                        this.currentColumn = Math.floor(((this.rotation % (Math.PI * 2)) + Math.PI * 2) / (Math.PI * 2) * this.totalColumns) % this.totalColumns;
                        
                        this.lastMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
                        this.render();
                    }}
                }});
                
                this.canvas.addEventListener('touchend', () => {{
                    this.isDragging = false;
                }});
                
                // Resize
                window.addEventListener('resize', () => {{
                    this.initCanvas();
                    this.render();
                }});
            }}
            
            async loadImages() {{
                try {{
                    const response = await fetch('/api/honda/images/2026/exterior/0');
                    const data = await response.json();
                    
                    // Cargar imágenes del panorama (32 columnas x 3 calidades)
                    const imagePromises = data.images.map(img => {{
                        return new Promise((resolve) => {{
                            const image = new Image();
                            image.crossOrigin = 'anonymous';
                            image.onload = () => resolve(image);
                            image.onerror = () => resolve(null);
                            image.src = img.url;
                        }});
                    }});
                    
                    this.images = await Promise.all(imagePromises);
                    this.render();
                }} catch (error) {{
                    console.error('Error loading images:', error);
                }}
            }}
            
            render() {{
                if (this.images.length === 0) return;
                
                this.ctx.fillStyle = '#000';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Renderizar columna actual basada en rotación
                const levelOffset = this.currentQuality * this.totalColumns;
                const imageIndex = levelOffset + this.currentColumn;
                
                if (this.images[imageIndex]) {{
                    const img = this.images[imageIndex];
                    const scale = this.zoom;
                    const w = this.canvas.width * scale;
                    const h = this.canvas.height * scale;
                    const x = (this.canvas.width - w) / 2;
                    const y = (this.canvas.height - h) / 2;
                    
                    this.ctx.drawImage(img, x, y, w, h);
                }}
            }}
        }}
        
        let viewer;
        
        function changeQuality(quality) {{
            // Update UI
            document.querySelectorAll('.quality-btn').forEach((btn, idx) => {{
                btn.classList.toggle('active', idx === quality);
            }});
            
            if (viewer) {{
                viewer.currentQuality = quality;
                viewer.render();
            }}
        }}
        
        // Initialize viewer
        window.addEventListener('load', () => {{
            viewer = new ObjectViewer();
        }});
    </script>
</body>
</html>'''
    
    return HTMLResponse(content=html_content)

# MANTENER TUS OTROS ENDPOINTS ORIGINALES
@router.get("/viewer/{extraction_id}")
async def get_viewer(extraction_id: str):
    """Servir visualizador 360° para una extracción específica"""
    try:
        # Buscar la extracción
        extraction = None
        if extraction_id in active_extractions:
            extraction = active_extractions[extraction_id]
        
        if not extraction:
            raise HTTPException(status_code=404, detail="Extracción no encontrada")
        
        if extraction["status"] != "completed":
            raise HTTPException(status_code=400, detail="Extracción no completada")
        
        # Path del viewer
        base_path = Path(f"downloads/honda_city_{extraction['year']}")
        view_path = base_path / f"ViewType.{extraction['view_type'].upper()}" / "viewer.html"
        
        if not view_path.exists():
            raise HTTPException(status_code=404, detail="Viewer no encontrado")
        
        return FileResponse(
            path=view_path,
            media_type="text/html",
            filename="viewer.html"
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/viewer-assets/{extraction_id}/{path:path}")
async def get_viewer_assets(extraction_id: str, path: str):
    """Servir assets del visualizador (CSS, JS, imágenes)"""
    try:
        # Buscar extracción
        extraction = None
        if extraction_id in active_extractions:
            extraction = active_extractions[extraction_id]
        
        if not extraction:
            raise HTTPException(status_code=404, detail="Extracción no encontrada")
        
        # Path del asset
        base_path = Path(f"downloads/honda_city_{extraction['year']}")
        view_path = base_path / f"ViewType.{extraction['view_type'].upper()}" / path
        
        if not view_path.exists():
            raise HTTPException(status_code=404, detail="Asset no encontrado")
        
        return FileResponse(path=view_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_honda_models():
    """
    NUEVO ENDPOINT: Obtener lista de todos los modelos Honda disponibles
    Para uso del frontend en selector de modelos
    """
    try:
        # FASE 1: Usar solo modelos confirmados
        confirmed_models = get_confirmed_models()
        models_list = []
        
        for model_info in confirmed_models:
            models_list.append({
                "model": model_info["name"].lower(),
                "name": f"Honda {model_info['name']}",
                "years": model_info["years"],
                "status": "confirmed"
            })
        
        return {
            "models": models_list,
            "total_models": len(models_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract/model")
async def start_model_extraction(request: dict, background_tasks: BackgroundTasks):
    """
    NUEVO ENDPOINT: Extraer CUALQUIER modelo Honda (no solo City)
    Compatible con el endpoint /extract original
    """
    try:
        # Validar parámetros
        model = request.get("model", "city")  # Por defecto City para compatibilidad
        year = request.get("year", "2026")
        view_type = request.get("view_type", "interior")
        
        # Si es City, usar el sistema original (compatibilidad)
        if model.lower() == "city":
            return await start_extraction(request, background_tasks)
        
        # Para otros modelos, crear extracción con nuevo sistema
        extraction_id = str(uuid.uuid4())
        
        response = {
            "extraction_id": extraction_id,
            "status": "pending",
            "model": model,
            "year": year,
            "view_type": view_type,
            "total_tiles": 0,
            "downloaded_tiles": 0,
            "failed_tiles": 0,
            "progress_percentage": 0.0,
            "estimated_time_remaining": None,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "error_message": None
        }
        
        # Guardar en storage
        active_extractions[extraction_id] = response
        
        # Iniciar extracción para nuevo modelo en background
        background_tasks.add_task(
            perform_universal_extraction,  # Nueva función
            extraction_id,
            model,
            year,
            view_type,
            request.get("quality_level", 0),
            request.get("download_path")
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def perform_universal_extraction(extraction_id: str, model: str, year: str, view_type: str, quality_level: int, download_path: Optional[str]):
    """
    NUEVA FUNCIÓN: Extracción para cualquier modelo Honda (no solo City)
    Usa el nuevo honda_service.py con extract_honda_model()
    """
    try:
        print(f"[UNIVERSAL] Iniciando extracción {model} {year} {view_type}")
        active_extractions[extraction_id]["status"] = "in_progress"
        
        # Usar el servicio actualizado con método universal
        from app.services.honda_service import HondaCityExtractor
        
        async with HondaCityExtractor() as extractor:
            # Usar el nuevo método extract_honda_model que agregaste
            stats = await extractor.extract_honda_model(model, year, view_type, quality_level, download_path)
            
            # Actualizar estado final
            extraction = active_extractions[extraction_id]
            extraction["status"] = "completed"
            extraction["total_tiles"] = stats.total_tiles
            extraction["downloaded_tiles"] = stats.downloaded_tiles
            extraction["failed_tiles"] = stats.failed_tiles
            extraction["progress_percentage"] = 100.0
            extraction["completed_at"] = datetime.now().isoformat()
            
            print(f"[UNIVERSAL] Completado {model}: {stats.downloaded_tiles} tiles")
            
    except Exception as e:
        print(f"[UNIVERSAL] Error: {e}")
        extraction = active_extractions[extraction_id]
        extraction["status"] = "failed"
        extraction["error_message"] = str(e)
        extraction["completed_at"] = datetime.now().isoformat()