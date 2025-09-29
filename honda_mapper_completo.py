#!/usr/bin/env python3
"""
🎯 HONDA MAPPER COMPLETO - INGENIERÍA REVERSA
Recrear el proceso original de descubrimiento automático
"""

import requests
import threading
import time
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class HondaDiscovery:
    def __init__(self):
        self.session = requests.Session()
        # HEADERS PARA EVADIR BLOQUEOS
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.honda.mx/'
        })
        
        self.found_files = []
        self.working_base_urls = []
        
    def test_url(self, url, delay=0.1):
        """Probar una URL específica con evasión de bloqueos"""
        try:
            time.sleep(delay)  # Anti-rate limiting
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200 and len(response.content) > 0:
                print(f"✅ ENCONTRADO: {url} ({len(response.content)} bytes)")
                self.found_files.append({
                    "url": url,
                    "size": len(response.content),
                    "status": response.status_code
                })
                return True
            elif response.status_code == 403:
                print(f"🚫 BLOQUEADO (403): {url}")
                return False
            else:
                print(f"❌ HTTP {response.status_code}: {url}")
                return False
                
        except Exception as e:
            print(f"💥 ERROR: {url} - {str(e)}")
            return False
    
    def discover_base_urls(self):
        """PASO 1: Descubrir URLs base que funcionan"""
        print("🔍 PASO 1: DESCUBRIENDO URLs BASE...")
        
        # TODAS LAS POSIBLES URLs BASE
        possible_bases = [
            # Honda México (las que encontramos)
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360",
            "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_ext_360",
            "https://www.honda.mx/autos/city/2026/city_2026_int_360", 
            "https://www.honda.mx/autos/city/2026/city_2026_ext_360",
            
            # Honda USA (original que funcionaba)
            "https://automobiles.honda.com/images/2026/city/360/ViewType.INTERIOR",
            "https://automobiles.honda.com/images/2026/city/360/ViewType.EXTERIOR",
            
            # Variaciones adicionales
            "https://www.honda.com/content/dam/honda/2026/city/360/interior",
            "https://www.honda.com/content/dam/honda/2026/city/360/exterior",
            
            # CDN alternativo
            "https://cdn.honda.com/2026/city/360/interior",
            "https://cdn.honda.com/2026/city/360/exterior",
            
            # Honda global
            "https://global.honda.com/content/city/2026/360/interior",
            "https://global.honda.com/content/city/2026/360/exterior"
        ]
        
        # Test simple files para verificar base URLs
        test_files = [
            "tiles/node1/cf_0/l_2/c_0/tile_0.jpg",  # Interior
            "tiles/c0_l2_0_0.jpg",                  # Exterior
            "config.xml",
            "viewer.html"
        ]
        
        for base_url in possible_bases:
            print(f"\n📍 PROBANDO BASE: {base_url}")
            success_count = 0
            
            for test_file in test_files:
                if self.test_url(f"{base_url}/{test_file}", 0.2):
                    success_count += 1
            
            if success_count > 0:
                success_rate = success_count / len(test_files)
                self.working_base_urls.append({
                    "url": base_url,
                    "success_rate": success_rate
                })
                print(f"🎯 BASE PARCIALMENTE FUNCIONAL: {success_rate:.1%}")
        
        return len(self.working_base_urls) > 0
    
    def map_tile_structure(self, base_url, view_type):
        """PASO 2: Mapear estructura completa de tiles"""
        print(f"\n🗺️ PASO 2: MAPEANDO TILES - {view_type}")
        
        found_tiles = []
        
        if "interior" in view_type.lower():
            # PATRÓN INTERIOR: tiles/node1/cf_X/l_Y/c_Z/tile_W.jpg
            print("🏠 Mapeando tiles INTERIOR (Cubo 6 caras)...")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                for cf in range(6):      # 6 caras del cubo
                    for l in range(4):   # 4 niveles de calidad
                        for c in range(3):   # Hasta 3 columnas por cara
                            for tile in range(3):  # Hasta 3 tiles por columna
                                tile_url = f"{base_url}/tiles/node1/cf_{cf}/l_{l}/c_{c}/tile_{tile}.jpg"
                                future = executor.submit(self.test_url, tile_url, 0.1)
                                futures.append((future, tile_url))
                
                for future, url in futures:
                    if future.result():
                        found_tiles.append(url)
        
        else:
            # PATRÓN EXTERIOR: tiles/cX_lY_Z_W.jpg  
            print("🚗 Mapeando tiles EXTERIOR (Panorama cilíndrico)...")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                for c in range(32):      # 32 columnas del panorama
                    for l in range(3):   # 3 niveles de calidad
                        for y in range(2):   # Hasta 2 filas
                            for x in range(2):   # Hasta 2 tiles por celda
                                tile_url = f"{base_url}/tiles/c{c}_l{l}_{y}_{x}.jpg"
                                future = executor.submit(self.test_url, tile_url, 0.1)
                                futures.append((future, tile_url))
                
                for future, url in futures:
                    if future.result():
                        found_tiles.append(url)
        
        print(f"📊 Total tiles encontrados: {len(found_tiles)}")
        return found_tiles
    
    def discover_assets(self, base_url):
        """PASO 3: Descubrir assets (JS, CSS, Config)"""
        print(f"\n⚙️ PASO 3: DESCUBRIENDO ASSETS...")
        
        asset_files = [
            "config.xml",
            "viewer.html",
            "index.html",
            "assets/pano2vr_player.js",
            "assets/object2vr_player.js", 
            "assets/skin.js",
            "assets/style.css",
            "pano.xml",
            "honda_city_2026_ext_out.xml"
        ]
        
        found_assets = []
        
        for asset in asset_files:
            asset_url = f"{base_url}/{asset}"
            if self.test_url(asset_url, 0.2):
                found_assets.append(asset_url)
        
        print(f"📊 Total assets encontrados: {len(found_assets)}")
        return found_assets
    
    def full_discovery(self):
        """PROCESO COMPLETO DE DESCUBRIMIENTO"""
        print("🚀 INICIANDO DESCUBRIMIENTO COMPLETO DE HONDA")
        print("=" * 60)
        
        # PASO 1: Encontrar URLs base
        if not self.discover_base_urls():
            print("❌ No se encontraron URLs base funcionales")
            return False
        
        print(f"\n✅ ENCONTRADAS {len(self.working_base_urls)} URLs base funcionales")
        
        # PASO 2 y 3: Para cada URL base funcional
        all_results = {}
        
        for base_info in self.working_base_urls:
            base_url = base_info["url"]
            print(f"\n🎯 PROCESANDO: {base_url}")
            
            # Determinar tipo de vista
            if "int" in base_url or "interior" in base_url.lower():
                view_type = "interior"
            else:
                view_type = "exterior"
            
            # Mapear tiles
            tiles = self.map_tile_structure(base_url, view_type)
            
            # Descubrir assets
            assets = self.discover_assets(base_url)
            
            all_results[base_url] = {
                "view_type": view_type,
                "tiles": tiles,
                "assets": assets,
                "total_files": len(tiles) + len(assets)
            }
        
        # GUARDAR RESULTADOS
        results_file = "honda_discovery_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "discovery_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_found_files": len(self.found_files),
                "working_base_urls": len(self.working_base_urls),
                "results": all_results,
                "all_files": self.found_files
            }, f, indent=2)
        
        print(f"\n📁 Resultados guardados en: {results_file}")
        
        # MOSTRAR RESUMEN
        print("\n🏆 RESUMEN FINAL:")
        for base_url, data in all_results.items():
            print(f"✅ {base_url}")
            print(f"   📊 {data['view_type'].upper()}: {len(data['tiles'])} tiles + {len(data['assets'])} assets")
        
        return len(all_results) > 0

def main():
    discovery = HondaDiscovery()
    success = discovery.full_discovery()
    
    if success:
        print("\n🎉 ¡DESCUBRIMIENTO EXITOSO!")
        print("📋 Revisar honda_discovery_results.json para detalles completos")
    else:
        print("\n💥 DESCUBRIMIENTO FALLIDO")
        print("🔧 Revisar bloqueos de IP o cambios en Honda")

if __name__ == "__main__":
    main()
