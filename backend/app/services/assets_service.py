import aiohttp
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class HondaAssetsDownloader:
    """
    Descargador de assets JS/CSS de Honda para reconstrucción offline
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_assets_urls(self, year: str, view_type: str) -> List[str]:
        """Obtener URLs de assets según año y tipo de vista"""
        base_url = f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360/"
        
        if view_type == "exterior":
            return [
                f"{base_url}object2vr_player.js",
                f"{base_url}skin.js"
            ]
        elif view_type == "interior":
            return [
                f"{base_url}pano2vr_player.js", 
                f"{base_url}skin.js"
            ]
        else:
            raise ValueError(f"view_type debe ser 'exterior' o 'interior'")
    
    async def download_asset(self, url: str, download_dir: Path) -> bool:
        """Descargar un asset individual"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Extraer nombre del archivo de la URL
                    filename = url.split('/')[-1]
                    file_path = download_dir / filename
                    
                    # Crear directorio si no existe
                    download_dir.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    print(f"✅ Asset descargado: {filename} ({len(content)} bytes)")
                    return True
                    
                else:
                    print(f"❌ Error descargando {url}: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Exception descargando {url}: {e}")
            return False
    
    async def download_all_assets(self, year: str, view_type: str, 
                                download_path: Optional[str] = None) -> Dict:
        """Descargar todos los assets para un modelo específico"""
        
        # Crear directorio de assets
        if download_path:
            assets_dir = Path(download_path) / "assets"
        else:
            assets_dir = Path("downloads") / f"honda_city_{year}" / view_type / "assets"
        
        assets_urls = self.get_assets_urls(year, view_type)
        
        print(f"📦 Descargando {len(assets_urls)} assets para {year} {view_type}...")
        
        results = {
            "total_assets": len(assets_urls),
            "successful_downloads": 0,
            "failed_downloads": 0,
            "download_path": str(assets_dir),
            "assets": []
        }
        
        for asset_url in assets_urls:
            success = await self.download_asset(asset_url, assets_dir)
            
            asset_info = {
                "url": asset_url,
                "filename": asset_url.split('/')[-1],
                "downloaded": success
            }
            
            results["assets"].append(asset_info)
            
            if success:
                results["successful_downloads"] += 1
            else:
                results["failed_downloads"] += 1
        
        print(f"📊 Assets descargados: {results['successful_downloads']}/{results['total_assets']}")
        
        return results
