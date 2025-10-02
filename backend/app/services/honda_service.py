import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import re
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from app.utils.patterns import (
    get_honda_config_url,  # Mantener para compatibilidad
    get_honda_images_base_url,  # Mantener para compatibilidad
    get_honda_universal_config_url,  # AGREGAR
    get_honda_universal_images_base_url,  # AGREGAR
    TILE_PATTERNS,
    RESOLUTIONS, 
    calculate_tiles_per_level
)
from app.models.honda import TileInfo, ConfigInfo, TileExtractionStats

class HondaCityExtractor:
    """
    Extractor específico para Honda City - 100% lógica tradicional
    Basado en el reconnaissance completo y paths CORREGIDOS
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_config(self, year: str, view_type: str) -> ConfigInfo:
        """
        Descargar y parsear configuración XML Honda
        Usa los patterns CORREGIDOS del reconnaissance
        """
        config_url = get_honda_config_url(year, view_type)
        
        async with self.session.get(config_url) as response:
            if response.status != 200:
                raise Exception(f"Error descargando config {config_url}: {response.status}")
            
            content = await response.text()
            
        # Determinar tecnología basada en el XML
        if '<vrobject' in content:
            technology = "object2vr"
        elif '<panorama' in content:
            technology = "pano2vr"
        else:
            raise Exception(f"Tecnología XML desconocida en {config_url}")
        
        # Parsear XML para extraer información
        root = ET.fromstring(content)
        
        if technology == "object2vr":
            # Para exterior (Object2VR)
            input_elem = root.find('input')
            columns = int(input_elem.get('columns', 32))
            rows = int(input_elem.get('rows', 1))
            levels = len(root.findall('.//level'))
            
            # Obtener resolución máxima
            first_level = root.find('.//level')
            max_resolution = {
                "width": int(first_level.get('width')),
                "height": int(first_level.get('height'))
            }
            
            tile_pattern = input_elem.get('leveltileurl')
            
            return ConfigInfo(
                url=config_url,
                content=content,
                technology=technology,
                columns=columns,
                rows=rows,
                levels=levels,
                max_resolution=max_resolution,
                tile_pattern=tile_pattern
            )
        
        elif technology == "pano2vr":
            # Para interior (Pano2VR)
            input_elem = root.find('input')
            levels = len(root.findall('.//level'))
            
            # Pano2VR siempre tiene 6 caras (cubo)
            faces = 6
            
            # Resolución máxima
            max_resolution = {
                "width": int(input_elem.get('width')),
                "height": int(input_elem.get('height'))
            }
            
            tile_pattern = input_elem.get('leveltileurl')
            
            return ConfigInfo(
                url=config_url,
                content=content,
                technology=technology,
                faces=faces,
                levels=levels,
                max_resolution=max_resolution,
                tile_pattern=tile_pattern
            )
    
    def generate_tile_urls(self, year: str, view_type: str, config: ConfigInfo, quality_level: int = 0) -> List[TileInfo]:
        """
        Generar todas las URLs de tiles basado en configuración
        USAR PATHS CORREGIDOS
        """
        base_url = get_honda_images_base_url(year, view_type)
        tiles = []
        
        if config.technology == "object2vr":
            # Exterior - Object2VR con PATHS CORREGIDOS
            pattern = TILE_PATTERNS["object2vr"]
            resolutions = RESOLUTIONS[year]["exterior"]
            resolution = resolutions[quality_level]
            
            tiles_x, tiles_y = calculate_tiles_per_level(resolution, pattern["tile_size"])
            
            for column in range(config.columns):
                for y in range(tiles_y):
                    for x in range(tiles_x):
                        # USAR PATTERN CORREGIDO: sin 'images/'
                        tile_path = pattern["pattern"].format(
                            column=column, 
                            level=quality_level, 
                            y=y, 
                            x=x
                        )
                        
                        tile_url = base_url + tile_path
                        
                        tiles.append(TileInfo(
                            url=tile_url,
                            level=quality_level,
                            column=column,
                            x=x,
                            y=y
                        ))
        
        elif config.technology == "pano2vr":
            # Interior - Pano2VR
            pattern = TILE_PATTERNS["pano2vr"] 
            resolutions = RESOLUTIONS[year]["interior"]
            resolution = resolutions[quality_level]
            
            tiles_x, tiles_y = calculate_tiles_per_level(resolution, pattern["tile_size"])
            
            for face in range(6):  # 6 caras del cubo
                for y in range(tiles_y):
                    for x in range(tiles_x):
                        tile_path = pattern["pattern"].format(
                            face=face,
                            level=quality_level,
                            x=x,
                            y=y
                        )
                        
                        tile_url = base_url + tile_path
                        
                        tiles.append(TileInfo(
                            url=tile_url,
                            level=quality_level,
                            face=face,
                            x=x,
                            y=y
                        ))
        
        return tiles
    
    async def download_tile(self, tile: TileInfo, download_dir: Path) -> bool:
        """Descargar un tile individual"""
        try:
            async with self.session.get(tile.url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Crear subdirectorios según estructura Honda config
                    if tile.column is not None:  # Object2VR - patrón Honda exacto
                        file_path = download_dir / "tiles" / f"c{tile.column}_l{tile.level}_{tile.y}_{tile.x}.jpg"
                    else:  # Pano2VR - mantener estructura actual
                        file_path = download_dir / "tiles" / "node1" / f"cf_{tile.face}" / f"l_{tile.level}" / f"c_{tile.x}" / f"tile_{tile.y}.jpg"
                    
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    tile.downloaded = True
                    tile.file_size = len(content)
                    return True
                    
                else:
                    print(f"Error descargando {tile.url}: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"Exception descargando {tile.url}: {e}")
            return False
    
    async def download_tiles_parallel(self, tiles: List[TileInfo], download_dir: Path, 
                                    max_concurrent: int = 10) -> TileExtractionStats:
        """
        Descargar tiles en paralelo con control de concurrencia
        """
        start_time = datetime.now()
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(tile: TileInfo):
            async with semaphore:
                return await self.download_tile(tile, download_dir)
        
        # Ejecutar descargas en paralelo
        results = await asyncio.gather(
            *[download_with_semaphore(tile) for tile in tiles],
            return_exceptions=True
        )
        
        # Calcular estadísticas
        successful = sum(1 for result in results if result is True)
        failed = len(results) - successful
        
        total_size_bytes = sum(tile.file_size or 0 for tile in tiles if tile.downloaded)
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        end_time = datetime.now()
        download_time = (end_time - start_time).total_seconds()
        
        speed_mbps = (total_size_mb / download_time) if download_time > 0 else 0
        
        return TileExtractionStats(
            total_tiles=len(tiles),
            successful_downloads=successful,
            failed_downloads=failed,
            total_size_mb=round(total_size_mb, 2),
            download_time_seconds=round(download_time, 2),
            average_speed_mbps=round(speed_mbps, 2)
        )
    
    async def extract_honda_city(self, year: str, view_type: str, quality_level: int = 0, 
                               download_path: Optional[str] = None) -> TileExtractionStats:
        """
        Método principal de extracción Honda City
        TODO EL PROCESO COMPLETO con PATHS CORREGIDOS
        """
        # 1. Crear directorio de descarga
        if download_path:
            download_dir = Path(download_path)
        else:
            download_dir = Path("downloads") / f"honda_city_{year}" / f"ViewType.{view_type.upper()}"
        
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Obtener configuración
        print(f"🔧 Obteniendo configuración Honda City {year} {view_type}...")
        config = await self.get_config(year, view_type)
        
        # 3. Generar URLs de tiles
        print(f"🎯 Generando URLs de tiles (nivel {quality_level})...")
        tiles = self.generate_tile_urls(year, view_type, config, quality_level)
        
        print(f"📊 Total de tiles a descargar: {len(tiles)}")
        
        # 4. Descargar tiles en paralelo
        print(f"⬇️ Iniciando descarga paralela...")
        stats = await self.download_tiles_parallel(tiles, download_dir)
        
        # 5. Guardar configuración XML
        config_file = download_dir / "config.xml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config.content)
        
        print(f"✅ Extracción completada!")
        print(f"   📊 Exitosas: {stats.successful_downloads}/{stats.total_tiles}")
        print(f"   💾 Tamaño total: {stats.total_size_mb} MB")
        print(f"   ⏱️ Tiempo: {stats.download_time_seconds}s")
        print(f"   🚀 Velocidad: {stats.average_speed_mbps} MB/s")
        
        return stats
    
    async def extract_honda_model(self, model: str, year: str, view_type: str, 
                              quality_level: int = 0, download_path: Optional[str] = None) -> TileExtractionStats:
        """
        Método universal para extraer CUALQUIER modelo Honda
        Usa las nuevas funciones universales de patterns.py
        """
        # Si es City, usar el método específico existente para mantener compatibilidad
        if model.lower() == "city":
            return await self.extract_honda_city(year, view_type, quality_level, download_path)
        
        # Para otros modelos, usar lógica universal
        # 1. Crear directorio de descarga
        if download_path:
            download_dir = Path(download_path)
        else:
            download_dir = Path("downloads") / f"honda_{model}_{year}" / f"ViewType.{view_type.upper()}"
        
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Obtener configuración usando función universal
        print(f"Obteniendo configuración Honda {model} {year} {view_type}...")
        config_url = get_honda_universal_config_url(model, year, view_type)
        
        async with self.session.get(config_url) as response:
            if response.status != 200:
                raise Exception(f"Error descargando config {config_url}: {response.status}")
            content = await response.text()
        
        # Crear ConfigInfo básico
        if 'object2vr' in content.lower():
            config = ConfigInfo(content=content, technology="object2vr", columns=32)
        else:
            config = ConfigInfo(content=content, technology="pano2vr", columns=6)
        
        # 3. Generar URLs usando función universal
        base_url = get_honda_universal_images_base_url(model, year, view_type)
        tiles = []
        
        # Usar misma lógica de generación que extract_honda_city
        if config.technology == "object2vr":
            pattern = TILE_PATTERNS["object2vr"]
            resolutions = RESOLUTIONS.get(year, RESOLUTIONS["2024"])["exterior"]
            resolution = resolutions[quality_level]
            tiles_x, tiles_y = calculate_tiles_per_level(resolution, pattern["tile_size"])
            
            for column in range(config.columns):
                for y in range(tiles_y):
                    for x in range(tiles_x):
                        tile_path = pattern["pattern"].format(column=column, level=quality_level, y=y, x=x)
                        tile_url = base_url + tile_path
                        tiles.append(TileInfo(url=tile_url, level=quality_level, column=column, x=x, y=y))
        
        # 4. Descargar tiles
        print(f"Iniciando descarga paralela de {len(tiles)} tiles...")
        stats = await self.download_tiles_parallel(tiles, download_dir)
        
        # 5. Guardar configuración
        config_file = download_dir / "config.xml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Extracción {model} {year} completada!")
        return stats
