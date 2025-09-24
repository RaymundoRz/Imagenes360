from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from typing import List, Dict, Optional
import uuid
from datetime import datetime
from pathlib import Path
import logging
import os

from app.models.honda import (
    ExtractionRequest, 
    ExtractionResponse, 
    HondaCityModel, 
    HondaListResponse,
    ExtractionStatus,
    TileExtractionStats
)
from app.services.honda_service import HondaCityExtractor
from app.services.assets_service import HondaAssetsDownloader
from app.utils.patterns import HONDA_CITY_SPECS, RESOLUTIONS

router = APIRouter()

# Storage en memoria para extracciones activas (en producción usar Redis/DB)
active_extractions: Dict[str, ExtractionResponse] = {}

@router.get("/models", response_model=HondaListResponse)
async def list_honda_models():
    """Listar todos los modelos Honda City disponibles"""
    
    models = []
    available_years = ["2024", "2026"]
    
    for year in available_years:
        specs = HONDA_CITY_SPECS[year]
        resolutions = RESOLUTIONS[year]
        
        # Calcular número aproximado de tiles
        # Exterior: 32 columns × ~44 tiles promedio por column  
        total_exterior = 32 * 44
        
        # Interior: 6 faces × tiles variables por face
        interior_res = resolutions["interior"][0]
        approx_tiles_per_face = (interior_res["width"] // 510) * (interior_res["height"] // 510)
        total_interior = 6 * approx_tiles_per_face
        
        model = HondaCityModel(
            year=year,
            engine=specs["engine"],
            power=specs["power"], 
            torque=specs["torque"],
            transmission=specs["transmission"],
            versions=specs["versions"],
            features=specs["features"],
            total_exterior_tiles=total_exterior,
            total_interior_tiles=total_interior,
            exterior_config_url=f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_ext_360/honda_city_{year}_ext_out.xml",
            interior_config_url=f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_int_360/pano.xml"
        )
        
        models.append(model)
    
    return HondaListResponse(
        available_years=available_years,
        models=models,
        total_models=len(models)
    )

@router.post("/extract", response_model=ExtractionResponse)
async def start_extraction(request: ExtractionRequest, background_tasks: BackgroundTasks):
    """Iniciar extracción de imágenes Honda City"""
    
    # Generar ID único para la extracción
    extraction_id = str(uuid.uuid4())
    
    # Crear response inicial
    response = ExtractionResponse(
        extraction_id=extraction_id,
        status=ExtractionStatus.PENDING,
        year=request.year,
        view_type=request.view_type,
        total_tiles=0,  # Se calculará en background
        created_at=datetime.now().isoformat()
    )
    
    # Guardar en storage
    active_extractions[extraction_id] = response
    
    # Iniciar extracción en background
    background_tasks.add_task(
        perform_extraction, 
        extraction_id, 
        request.year, 
        request.view_type,
        request.quality_level,
        request.download_path
    )
    
    return response

async def perform_extraction(extraction_id: str, year: str, view_type: str, 
                           quality_level: int, download_path: Optional[str]):
    """Función background para realizar la extracción"""
    
    try:
        # Actualizar estado
        active_extractions[extraction_id].status = ExtractionStatus.IN_PROGRESS
        
        # Realizar extracción
        async with HondaCityExtractor() as extractor:
            stats = await extractor.extract_honda_city(
                year=year,
                view_type=view_type, 
                quality_level=quality_level,
                download_path=download_path
            )
        
        # Actualizar con resultados
        extraction = active_extractions[extraction_id]
        extraction.status = ExtractionStatus.COMPLETED
        extraction.total_tiles = stats.total_tiles
        extraction.downloaded_tiles = stats.successful_downloads
        extraction.failed_tiles = stats.failed_downloads
        extraction.progress_percentage = 100.0
        extraction.completed_at = datetime.now().isoformat()
        
    except Exception as e:
        # Manejar errores
        extraction = active_extractions[extraction_id]
        extraction.status = ExtractionStatus.FAILED
        extraction.error_message = str(e)
        extraction.completed_at = datetime.now().isoformat()

@router.get("/extract/{extraction_id}", response_model=ExtractionResponse)
async def get_extraction_status(extraction_id: str):
    """Obtener estado de una extracción específica"""
    
    if extraction_id not in active_extractions:
        raise HTTPException(status_code=404, detail="Extracción no encontrada")
    
    return active_extractions[extraction_id]

@router.get("/extractions", response_model=List[ExtractionResponse])
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

@router.get("/config/{year}/{view_type}")
async def get_config_info(year: str, view_type: str):
    """Obtener información de configuración sin extraer"""
    
    if year not in ["2024", "2026"]:
        raise HTTPException(status_code=400, detail="Año debe ser 2024 o 2026")
    
    if view_type not in ["exterior", "interior"]:
        raise HTTPException(status_code=400, detail="view_type debe ser 'exterior' o 'interior'")
    
    try:
        async with HondaCityExtractor() as extractor:
            config = await extractor.get_config(year, view_type)
            return {
                "config_url": config.url,
                "technology": config.technology,
                "levels": config.levels,
                "max_resolution": config.max_resolution,
                "columns": config.columns,
                "faces": config.faces,
                "tile_pattern": config.tile_pattern
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")

# =====================================================
# NUEVOS ENDPOINTS - ASSETS Y VIEWER GENERATION
# =====================================================

@router.post("/download-assets")
async def download_honda_assets(request: ExtractionRequest, background_tasks: BackgroundTasks):
    """Descargar assets JS/CSS de Honda para reconstrucción offline"""
    
    # Generar ID único para la descarga de assets
    assets_id = str(uuid.uuid4())
    
    # Crear response inicial
    response = {
        "assets_id": assets_id,
        "status": "pending",
        "year": request.year,
        "view_type": request.view_type,
        "message": "Descarga de assets iniciada",
        "created_at": datetime.now().isoformat()
    }
    
    # Iniciar descarga de assets en background
    background_tasks.add_task(
        download_assets_background,
        assets_id,
        request.year,
        request.view_type, 
        request.download_path
    )
    
    return response

async def download_assets_background(assets_id: str, year: str, view_type: str, download_path: Optional[str]):
    """Función background para descargar assets"""
    try:
        async with HondaAssetsDownloader() as downloader:
            results = await downloader.download_all_assets(
                year=year,
                view_type=view_type,
                download_path=download_path
            )
            
            print(f"✅ Assets descargados para {assets_id}")
            print(f"   Exitosos: {results['successful_downloads']}")
            print(f"   Fallidos: {results['failed_downloads']}")
            print(f"   Ubicación: {results['download_path']}")
            
    except Exception as e:
        print(f"❌ Error descargando assets {assets_id}: {e}")

@router.post("/generate-viewer/{extraction_id}")
async def generate_offline_viewer(extraction_id: str):
    """Generar visualizador 360° offline usando imágenes y assets descargados"""
    
    if extraction_id not in active_extractions:
        raise HTTPException(status_code=404, detail="Extracción no encontrada")
    
    extraction = active_extractions[extraction_id]
    
    if extraction.status != ExtractionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Extracción no completada")
    
    try:
        # Generar HTML del visualizador offline
        viewer_html = generate_viewer_html(
            extraction.year,
            extraction.view_type,
            extraction.extraction_id
        )
        
        # Guardar HTML en el directorio de descarga
        view_type_folder = f"ViewType.{extraction.view_type.upper()}"
        download_dir = Path("downloads") / f"honda_city_{extraction.year}" / view_type_folder
        html_file = download_dir / "viewer.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(viewer_html)
        
        return {
            "status": "success",
            "message": "Visualizador offline generado",
            "viewer_path": str(html_file),
            "extraction_id": extraction_id,
            "instructions": "Abre viewer.html en tu navegador para ver el 360° offline"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando visualizador: {str(e)}")

def generate_viewer_html(year: str, view_type: str, extraction_id: str) -> str:
    """Generar HTML del visualizador 360° offline"""
    
    if view_type == "exterior":
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Honda City {year} - Exterior 360°</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #container {{ width: 100%; height: 100vh; background: #000; }}
        #info {{ position: absolute; top: 10px; left: 10px; color: white; z-index: 1000; }}
        #debug {{ position: absolute; top: 100px; left: 10px; color: red; z-index: 1000; font-size: 12px; }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Honda City {year} - Exterior 360°</h3>
        <p>Usa el mouse para rotar. Rueda para zoom.</p>
    </div>
    <div id="debug"></div>
    <div id="container"></div>
    
    <script>
        console.log("Loading exterior scripts...");
        document.getElementById('debug').innerHTML = 
            'Loading: ./assets/object2vr_player.js<br>' +
            'Config: ./config.xml<br>' +
            'Location: ' + window.location.href;
    </script>
    
    <script src="./assets/object2vr_player.js" onerror="console.error('Failed to load object2vr_player.js')"></script>
    <script src="./assets/skin.js" onerror="console.error('Failed to load skin.js')"></script>
    
    <script>
        window.addEventListener('load', function() {{
            console.log("Scripts loaded, initializing Object2VR player...");
            try {{
                if (typeof object2vrPlayer === 'undefined') {{
                    throw new Error('object2vrPlayer not found');
                }}
                
                var player = new object2vrPlayer("container");
                player.readConfigUrl("./config.xml");
                
                console.log("Honda City {year} Exterior 360° - Visualizador cargado");
            }} catch(e) {{
                console.error("Error cargando visualizador:", e);
                document.getElementById('container').innerHTML = 
                    '<div style="color:white;padding:20px;"><h2>Error de depuración:</h2><pre>' + e.toString() + '</pre></div>';
            }}
        }});
    </script>
</body>
</html>'''
    
    else:  # interior
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Honda City {year} - Interior 360°</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #container {{ width: 100%; height: 100vh; background: #000; }}
        #info {{ position: absolute; top: 10px; left: 10px; color: white; z-index: 1000; }}
        #debug {{ position: absolute; top: 100px; left: 10px; color: red; z-index: 1000; font-size: 12px; }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Honda City {year} - Interior 360°</h3>
        <p>Usa el mouse para mirar alrededor. Rueda para zoom.</p>
    </div>
    <div id="debug"></div>
    <div id="container"></div>
    
    <script>
        console.log("Loading interior scripts...");
        document.getElementById('debug').innerHTML = 
            'Loading: ./assets/pano2vr_player.js<br>' +
            'Config: ./config.xml<br>' +
            'Location: ' + window.location.href;
    </script>
    
    <script src="./assets/pano2vr_player.js" onerror="console.error('Failed to load pano2vr_player.js')"></script>
    <script src="./assets/skin.js" onerror="console.error('Failed to load skin.js')"></script>
    
    <script>
        window.addEventListener('load', function() {{
            console.log("Scripts loaded, initializing Pano2VR player...");
            try {{
                if (typeof pano2vrPlayer === 'undefined') {{
                    throw new Error('pano2vrPlayer not found');
                }}
                
                var player = new pano2vrPlayer("container");
                player.readConfigUrl("./config.xml");
                
                console.log("Honda City {year} Interior 360° - Visualizador cargado");
            }} catch(e) {{
                console.error("Error cargando visualizador:", e);
                document.getElementById('container').innerHTML = 
                    '<div style="color:white;padding:20px;"><h2>Error de depuración:</h2><pre>' + e.toString() + '</pre></div>';
            }}
        }});
    </script>
</body>
</html>'''

# Endpoint de prueba rápida
@router.post("/test-extraction")
async def test_extraction():
    """Endpoint de prueba para validar que todo funciona"""
    
    try:
        async with HondaCityExtractor() as extractor:
            # Probar obtener configuración
            config = await extractor.get_config("2026", "exterior")
            
            # Generar algunas URLs de prueba (solo las primeras 5)
            tiles = extractor.generate_tile_urls("2026", "exterior", config, 0)
            
            return {
                "status": "success",
                "message": "Sistema funcionando correctamente",
                "config_technology": config.technology,
                "total_tiles_available": len(tiles),
                "sample_tile_urls": [tile.url for tile in tiles[:5]]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en test: {str(e)}")

@router.get("/viewer/{extraction_id}")
async def get_viewer(extraction_id: str):
    """Servir visualizador 360° para una extracción específica"""
    try:
        # Buscar la extracción en la base de datos
        extraction = None
        for ext in extraction_storage.values():
            if ext.extraction_id == extraction_id:
                extraction = ext
                break
        
        if not extraction:
            raise HTTPException(status_code=404, detail="Extracción no encontrada")
        
        if extraction.status != "completed":
            raise HTTPException(status_code=400, detail="Extracción no completada")
        
        # Path del viewer
        base_path = Path(f"downloads/honda_city_{extraction.year}")
        view_path = base_path / f"ViewType.{extraction.view_type.upper()}" / "viewer.html"
        
        if not view_path.exists():
            raise HTTPException(status_code=404, detail="Viewer no encontrado")
        
        return FileResponse(
            path=view_path,
            media_type="text/html",
            filename="viewer.html"
        )
        
    except Exception as e:
        logger.error(f"Error sirviendo viewer {extraction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/viewer-assets/{extraction_id}/{path:path}")
async def get_viewer_assets(extraction_id: str, path: str):
    """Servir assets del visualizador (CSS, JS, imágenes)"""
    try:
        # Buscar extracción
        extraction = None
        for ext in extraction_storage.values():
            if ext.extraction_id == extraction_id:
                extraction = ext
                break
        
        if not extraction:
            raise HTTPException(status_code=404, detail="Extracción no encontrada")
        
        # Path del asset
        base_path = Path(f"downloads/honda_city_{extraction.year}")
        view_path = base_path / f"ViewType.{extraction.view_type.upper()}" / path
        
        if not view_path.exists():
            raise HTTPException(status_code=404, detail="Asset no encontrado")
        
        return FileResponse(path=view_path)
        
    except Exception as e:
        logger.error(f"Error sirviendo asset {path} para {extraction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
