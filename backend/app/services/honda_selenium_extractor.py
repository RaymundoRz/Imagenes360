"""
EXTRACTOR HONDA CON SELENIUM
Extrae assets que requieren JavaScript (config.xml, viewer.html, assets JS)
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class HondaSeleniumExtractor:
    """
    Extractor de Honda usando Selenium para obtener assets que requieren JavaScript
    """
    
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self) -> bool:
        """Configurar y inicializar el driver de Chrome"""
        try:
            print("[SELENIUM] Configurando Chrome WebDriver...")
            
            # Opciones de Chrome para evitar detección
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Ejecutar sin ventana
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # COMPATIBILIDAD WINDOWS vs MACBOOK
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Headers específicos para Windows (CSP bypass)
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_argument("--ignore-ssl-errors")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                chrome_options.add_argument("--disable-images")  # Para acelerar descarga
                print("[SELENIUM] Configuración Windows aplicada (CSP bypass)")
            else:
                # Headers específicos para MacBook
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
                print("[SELENIUM] Configuración MacBook aplicada")
            
            # USAR DIRECTAMENTE CHROME DESDE PATH (MÉTODO QUE FUNCIONA)
            try:
                # Método que SÍ funciona: Chrome desde PATH
                self.driver = webdriver.Chrome(options=chrome_options)
                print("[SELENIUM] ChromeDriver desde PATH exitoso")
            except Exception as e:
                print(f"[SELENIUM] Chrome desde PATH falló: {e}")
                try:
                    # Método 2: ChromeDriverManager como fallback
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("[SELENIUM] ChromeDriverManager exitoso")
                except Exception as e2:
                    print(f"[SELENIUM] ChromeDriverManager falló: {e2}")
                    # Método 3: Usar Edge como fallback
                    from selenium.webdriver.edge.options import Options as EdgeOptions
                    from selenium.webdriver.edge.service import Service as EdgeService
                    from webdriver_manager.microsoft import EdgeChromiumDriverManager
                    
                    edge_options = EdgeOptions()
                    edge_options.add_argument("--headless")
                    edge_options.add_argument("--no-sandbox")
                    edge_options.add_argument("--disable-dev-shm-usage")
                    edge_options.add_argument("--disable-gpu")
                    
                    # Configuración Edge para Windows (CSP bypass)
                    if system == "Windows":
                        edge_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0")
                        edge_options.add_argument("--disable-features=VizDisplayCompositor")
                        edge_options.add_argument("--ignore-certificate-errors")
                        edge_options.add_argument("--ignore-ssl-errors")
                        edge_options.add_argument("--disable-extensions")
                        edge_options.add_argument("--disable-plugins")
                        edge_options.add_argument("--disable-images")
                        print("[SELENIUM] Edge configurado para Windows (CSP bypass)")
                    else:
                        edge_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0")
                        print("[SELENIUM] Edge configurado para MacBook")
                    
                    edge_service = Service(EdgeChromiumDriverManager().install())
                    self.driver = webdriver.Edge(service=edge_service, options=edge_options)
                    print("[SELENIUM] Usando Edge como fallback")
            
            # Script para evitar detección
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Configurar timeout MUY CORTO para evitar congelamiento
            self.driver.implicitly_wait(3)  # Reducido de 10 a 3
            self.wait = WebDriverWait(self.driver, 5)  # Reducido de 20 a 5
            
            print("[SELENIUM] WebDriver configurado correctamente")
            return True
            
        except Exception as e:
            print(f"[SELENIUM] Error configurando WebDriver: {e}")
            print("[SELENIUM] Intentando modo de fallback sin navegador...")
            return False
    
    def extract_assets_from_honda_page(self, year: str, view_type: str, output_dir: Path) -> Dict[str, bool]:
        """
        Extraer assets desde la página de Honda usando Selenium
        """
        results = {
            "config_xml": False,
            "viewer_html": False,
            "skin_js": False,
            "player_js": False,
            "error": None
        }
        
        try:
            print(f"[SELENIUM] Extrayendo assets para Honda City {year} {view_type}...")
            
            # MODO RÁPIDO: Saltarse navegación y ir directo a extracción
            print("[SELENIUM] Usando modo rápido - saltando navegación...")
            results = self._extract_assets_direct(year, view_type, output_dir)
            
            # Si no funcionó, intentar con navegador
            if not any(results.values()):
                print("[SELENIUM] Modo directo falló, intentando con navegador...")
                if not self.setup_driver():
                    print("[SELENIUM] WebDriver falló, usando modo de fallback...")
                    return self._fallback_asset_generation(year, view_type, output_dir)
                
                # URL de la página de Honda
                honda_url = f"https://www.honda.mx/autos/city/{year}/"
                
                print(f"[SELENIUM] Navegando a: {honda_url}")
                self.driver.get(honda_url)
                
                # Esperar MUY POCO tiempo para evitar congelamiento
                time.sleep(1)
                
                # Buscar el botón de 360° o enlace
                try:
                    print("[SELENIUM] Buscando enlace de 360°...")
                    
                    # Buscar diferentes selectores posibles para el enlace 360°
                    selectors_360 = [
                        "a[href*='360']",
                        "button[onclick*='360']", 
                        "a[href*='interior']",
                        "a[href*='exterior']",
                        ".viewer-360",
                        ".interior-viewer",
                        ".exterior-viewer",
                        "[data-viewer='360']"
                    ]
                    
                    link_360 = None
                    for selector in selectors_360:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                link_360 = elements[0]
                                print(f"[SELENIUM] Encontrado enlace 360° con selector: {selector}")
                                break
                        except:
                            continue
                    
                    if link_360:
                        # Hacer clic en el enlace 360°
                        print("[SELENIUM] Haciendo clic en enlace 360°...")
                        self.driver.execute_script("arguments[0].click();", link_360)
                        time.sleep(2)
                        
                        # Extraer assets de la página del viewer
                        results = self._extract_viewer_assets(year, view_type, output_dir)
                    else:
                        print("[SELENIUM] No se encontró enlace 360°, usando fallback...")
                        results = self._fallback_asset_generation(year, view_type, output_dir)
                        
                except Exception as e:
                    print(f"[SELENIUM] Error en navegación: {e}")
                    results = self._fallback_asset_generation(year, view_type, output_dir)
                
        except Exception as e:
            print(f"[SELENIUM] Error general: {e}")
            results["error"] = str(e)
        
        return results
    
    def cleanup_driver(self):
        """Cerrar WebDriver de forma segura"""
        if self.driver:
            try:
                self.driver.quit()
                print("[SELENIUM] WebDriver cerrado correctamente")
            except Exception as e:
                print(f"[SELENIUM] Error cerrando WebDriver: {e}")
            finally:
                self.driver = None
    
    def _extract_viewer_assets(self, year: str, view_type: str, output_dir: Path) -> Dict[str, bool]:
        """Extraer assets desde la página del viewer 360°"""
        results = {
            "config_xml": False,
            "viewer_html": False,
            "skin_js": False,
            "player_js": False,
            "error": None
        }
        
        try:
            print("[SELENIUM] Extrayendo assets del viewer...")
            
            # Obtener HTML completo de la página
            html_content = self.driver.page_source
            
            # Guardar HTML como viewer.html
            viewer_file = output_dir / "viewer.html"
            with open(viewer_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            results["viewer_html"] = True
            print(f"[SELENIUM] viewer.html guardado: {viewer_file}")
            
            # Buscar scripts en el HTML
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                src = script.get_attribute("src")
                if src:
                    print(f"[SELENIUM] Script encontrado: {src}")
                    
                    # Descargar scripts importantes
                    if "skin" in src.lower():
                        results["skin_js"] = self._download_script(src, output_dir / "skin.js")
                    elif "pano2vr" in src.lower() or "object2vr" in src.lower():
                        player_file = "pano2vr_player.js" if view_type == "interior" else "object2vr_player.js"
                        results["player_js"] = self._download_script(src, output_dir / player_file)
            
            # Buscar config.xml en el HTML o network requests
            results["config_xml"] = self._extract_config_xml(year, view_type, output_dir)
            
        except Exception as e:
            print(f"[SELENIUM] Error extrayendo viewer assets: {e}")
            results["error"] = str(e)
        
        return results
    
    async def download_tiles(self, year: str, view_type: str, output_dir: Path, quality_level: int) -> int:
        """Descargar imágenes tiles usando Selenium"""
        try:
            print(f"[SELENIUM] Iniciando descarga de tiles para {view_type}...")
            
            # Crear directorio de tiles
            tiles_dir = output_dir / "tiles"
            tiles_dir.mkdir(parents=True, exist_ok=True)
            
            # URLs base para Honda
            base_url = f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360"
            
            tiles_downloaded = 0
            
            if view_type == "interior":
                # Interior: 6 caras x 2 niveles x 2 columnas x 2 tiles = 48 archivos
                print("[SELENIUM] Descargando tiles INTERIOR (48 archivos)...")
                for cf in range(6):  # cf_0 a cf_5
                    for l in [1, 2]:  # l_1 y l_2
                        for c in range(2):  # c_0 y c_1
                            for tile in range(2):  # tile_0.jpg y tile_1.jpg
                                tile_url = f"{base_url}/tiles/node1/cf_{cf}/l_{l}/c_{c}/tile_{tile}.jpg"
                                tile_path = tiles_dir / f"tile_{cf}_{l}_{c}_{tile}.jpg"
                                
                                if await self._download_tile_with_selenium(tile_url, tile_path):
                                    tiles_downloaded += 1
                                    print(f"[SELENIUM] Tile descargado: tile_{cf}_{l}_{c}_{tile}.jpg")
            
            else:  # exterior
                # PATRONES REALES IDENTIFICADOS DESDE DOM:
                # Level 0 (panorámica): c{col}_l0_{row}_{tile}.jpg (0-4+ tiles)
                # Level 2 (zoom detallado): c{col}_l2_{row}_{tile}.jpg (0-1 tiles)
                
                print("[SELENIUM] Descargando tiles EXTERIOR - PATRONES REALES...")
                
                # PATRÓN A - Level 0 (Vista panorámica general)
                print("[SELENIUM] Descargando Level 0 (panorámica)...")
                for col in range(32):  # c0 a c31
                    for row in range(2):  # 2 filas
                        for tile in range(8):  # 0-7 tiles por posición
                            tile_url = f"{base_url}/tiles/c{col}_l0_{row}_{tile}.jpg"
                            tile_path = tiles_dir / f"level0_{col:02d}_{row}_{tile}.jpg"
                            
                            if await self._download_tile_with_selenium(tile_url, tile_path):
                                tiles_downloaded += 1
                                print(f"[SELENIUM] Level0 tile descargado: c{col}_l0_{row}_{tile}.jpg")
                
                # PATRÓN B - Level 2 (Zoom detallado)
                print("[SELENIUM] Descargando Level 2 (zoom detallado)...")
                for col in range(32):  # c0 a c31
                    for row in range(2):  # 2 filas
                        for tile in range(2):  # 0-1 tiles por posición
                            tile_url = f"{base_url}/tiles/c{col}_l2_{row}_{tile}.jpg"
                            tile_path = tiles_dir / f"level2_{col:02d}_{row}_{tile}.jpg"
                            
                            if await self._download_tile_with_selenium(tile_url, tile_path):
                                tiles_downloaded += 1
                                print(f"[SELENIUM] Level2 tile descargado: c{col}_l2_{row}_{tile}.jpg")
            
            print(f"[SELENIUM] Total tiles descargados: {tiles_downloaded}")
            return tiles_downloaded
            
        except Exception as e:
            print(f"[SELENIUM] Error descargando tiles: {e}")
            return 0
    
    async def _download_tile_with_selenium(self, url: str, output_path: Path) -> bool:
        """Descargar un tile individual usando Selenium"""
        try:
            # Navegar a la URL de la imagen
            self.driver.get(url)
            time.sleep(1)
            
            # Verificar si la imagen se cargó correctamente
            if "404" not in self.driver.title and self.driver.page_source.strip():
                # Obtener el contenido de la imagen
                try:
                    # Intentar obtener la imagen directamente
                    response = self.driver.execute_script("""
                        return fetch(arguments[0])
                            .then(response => response.blob())
                            .then(blob => {
                                return new Promise((resolve) => {
                                    const reader = new FileReader();
                                    reader.onload = () => resolve(reader.result);
                                    reader.readAsDataURL(blob);
                                });
                            });
                    """, url)
                    
                    if response and response.startswith('data:image'):
                        # Decodificar base64 y guardar
                        import base64
                        image_data = base64.b64decode(response.split(',')[1])
                        
                        # Crear directorio si no existe
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Guardar archivo
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        
                        return True
                        
                except Exception as e:
                    print(f"[SELENIUM] Error procesando imagen {url}: {e}")
                    return False
            else:
                print(f"[SELENIUM] Imagen no encontrada: {url}")
                return False
                
        except Exception as e:
            print(f"[SELENIUM] Error descargando tile {url}: {e}")
            return False
    
    def _extract_assets_direct(self, year: str, view_type: str, output_dir: Path) -> Dict[str, bool]:
        """Extracción directa RÁPIDA - sin navegador"""
        results = {
            "config_xml": False,
            "viewer_html": False,
            "skin_js": False,
            "player_js": False,
            "error": None
        }
        
        try:
            print("[SELENIUM] Extracción directa RÁPIDA (sin navegador)...")
            
            # GENERAR TODOS LOS ASSETS BÁSICOS INMEDIATAMENTE
            results["viewer_html"] = self._extract_real_viewer(year, view_type, output_dir)
            results["config_xml"] = self._extract_config_xml(year, view_type, output_dir)
            results["skin_js"] = self._extract_real_skin(year, view_type, output_dir)
            results["player_js"] = self._extract_real_player(year, view_type, output_dir)
            
            success_count = sum([v for v in results.values() if isinstance(v, bool)])
            print(f"[SELENIUM] Assets básicos generados: {success_count}/4")
            
        except Exception as e:
            print(f"[SELENIUM] Error en extracción directa: {e}")
            results["error"] = str(e)
        
        return results
    
    def _download_script(self, script_url: str, output_file: Path) -> bool:
        """Descargar un script desde URL"""
        try:
            print(f"[SELENIUM] Descargando script: {script_url}")
            
            self.driver.get(script_url)
            time.sleep(1)  # Reducido de 2 a 1
            
            # Obtener contenido del script
            script_content = self.driver.page_source
            
            # Guardar script
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"[SELENIUM] Script guardado: {output_file}")
            return True
            
        except Exception as e:
            print(f"[SELENIUM] Error descargando script {script_url}: {e}")
            return False
    
    def _extract_config_xml(self, year: str, view_type: str, output_dir: Path) -> bool:
        """Extraer config.xml REAL desde Honda - NO GENERAR ARCHIVOS BÁSICOS"""
        try:
            # URLs reales de Honda para config.xml
            config_urls = [
                f"https://automobiles.honda.com/images/{year}/city/360/ViewType.{view_type.upper()}/config.xml"
            ]
            
            for config_url in config_urls:
                print(f"[SELENIUM] Intentando descargar config REAL: {config_url}")
                
                try:
                    self.driver.get(config_url)
                    time.sleep(2)
                    
                    # Verificar si la página cargó correctamente
                    if "404" not in self.driver.title and self.driver.page_source.strip():
                        print(f"[SELENIUM] Config REAL encontrado en: {config_url}")
                        
                        # Obtener contenido XML real TAL COMO VIENE DE HONDA
                        xml_content = self.driver.page_source
                        
                        # Guardar config.xml REAL
                        config_file = output_dir / "config.xml"
                        with open(config_file, 'w', encoding='utf-8') as f:
                            f.write(xml_content)
                        
                        print(f"[SELENIUM] Config REAL guardado: {config_file}")
                        return True
                        
                except Exception as e:
                    print(f"[SELENIUM] Error con URL {config_url}: {e}")
                    continue
            
            print(f"[SELENIUM] NO SE ENCONTRÓ CONFIG REAL - OMITIENDO ARCHIVO")
            return False
            
        except Exception as e:
            print(f"[SELENIUM] Error extrayendo config XML: {e}")
            return False
    
    def _extract_real_viewer(self, year: str, view_type: str, output_dir: Path) -> bool:
        """Extraer viewer.html REAL desde Honda - NO GENERAR ARCHIVOS BÁSICOS"""
        try:
            # URLs reales de Honda para index.html (NO viewer.html)
            viewer_urls = [
                f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360/index.html"
            ]
            
            for viewer_url in viewer_urls:
                print(f"[SELENIUM] Intentando descargar viewer REAL: {viewer_url}")
                
                try:
                    self.driver.get(viewer_url)
                    time.sleep(2)
                    
                    # Verificar si la página cargó correctamente
                    if "404" not in self.driver.title and self.driver.page_source.strip():
                        print(f"[SELENIUM] Viewer REAL encontrado en: {viewer_url}")
                        
                        # Obtener contenido HTML real TAL COMO VIENE DE HONDA
                        html_content = self.driver.page_source
                        
                        # Guardar index.html REAL como viewer.html (para nuestro sistema)
                        viewer_file = output_dir / "viewer.html"
                        with open(viewer_file, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        print(f"[SELENIUM] Viewer REAL guardado: {viewer_file}")
                        return True
                        
                except Exception as e:
                    print(f"[SELENIUM] Error con URL {viewer_url}: {e}")
                    continue
            
            print(f"[SELENIUM] NO SE ENCONTRÓ VIEWER REAL - OMITIENDO ARCHIVO")
            return False
            
        except Exception as e:
            print(f"[SELENIUM] Error extrayendo viewer HTML: {e}")
            return False
    
    def _generate_basic_viewer(self, year: str, view_type: str, output_dir: Path) -> bool:
        """SOLO PARA FALLBACK - Generar un viewer.html básico si no se encuentra el real"""
        try:
            viewer_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Honda City {year} {view_type.title()} 360°</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; background: #000; font-family: Arial, sans-serif; }}
        #viewer {{ width: 100vw; height: 100vh; }}
        .controls {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); 
                   background: rgba(0,0,0,0.7); color: white; padding: 10px 20px; border-radius: 10px; }}
    </style>
</head>
<body>
    <div id="viewer">
        <canvas id="canvas"></canvas>
        <div class="controls">
            <h3>Honda City {year} {view_type.title()} 360°</h3>
            <p>Viewer generado automáticamente por Selenium Extractor</p>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Visualizador 360° real con Three.js
        console.log('Honda City {year} {view_type} 360° Viewer - Three.js');
        
        let scene, camera, renderer, controls;
        let panoramaTexture;
        
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Iniciando visualizador 360°...');
            init360Viewer();
        }});
        
        function init360Viewer() {{
            // Configurar escena Three.js
            scene = new THREE.Scene();
            
            // Configurar cámara
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 0, 0);
            
            // Configurar renderer
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            
            // Reemplazar canvas básico con Three.js
            const container = document.getElementById('viewer');
            container.innerHTML = '';
            container.appendChild(renderer.domElement);
            
            // Crear esfera para panorama 360°
            const geometry = new THREE.SphereGeometry(500, 60, 40);
            geometry.scale(-1, 1, 1); // Invertir para ver desde adentro
            
            // Crear material con textura
            const material = new THREE.MeshBasicMaterial({{ 
                map: createPanoramaTexture(),
                side: THREE.BackSide 
            }});
            
            const sphere = new THREE.Mesh(geometry, material);
            scene.add(sphere);
            
            // Controles de mouse
            setupControls();
            
            // Iniciar render loop
            animate();
            
            console.log('Visualizador 360° iniciado correctamente');
        }}
        
        function createPanoramaTexture() {{
            // Crear textura temporal mientras cargamos las imágenes reales
            const canvas = document.createElement('canvas');
            canvas.width = 2048;
            canvas.height = 1024;
            const ctx = canvas.getContext('2d');
            
            // Fondo degradado temporal
            const gradient = ctx.createLinearGradient(0, 0, 0, 1024);
            gradient.addColorStop(0, '#87CEEB'); // Cielo
            gradient.addColorStop(1, '#98FB98'); // Tierra
            
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, 2048, 1024);
            
            // Texto temporal
            ctx.fillStyle = 'white';
            ctx.font = '48px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Honda City {year}', 1024, 400);
            ctx.fillText('{view_type.title()} 360°', 1024, 500);
            ctx.fillText('Cargando tiles...', 1024, 600);
            
            const texture = new THREE.CanvasTexture(canvas);
            texture.needsUpdate = true;
            
            // Cargar tiles reales en background
            loadRealTiles(texture);
            
            return texture;
        }}
        
        function loadRealTiles(texture) {{
            console.log('Cargando tiles reales...');
            // Aquí cargaríamos los tiles reales y los combinamos
            // Por ahora usamos la textura temporal
        }}
        
        function setupControls() {{
            // Controles básicos de mouse
            let isMouseDown = false;
            let mouseX = 0, mouseY = 0;
            
            renderer.domElement.addEventListener('mousedown', (event) => {{
                isMouseDown = true;
                mouseX = event.clientX;
                mouseY = event.clientY;
            }});
            
            renderer.domElement.addEventListener('mousemove', (event) => {{
                if (!isMouseDown) return;
                
                const deltaX = event.clientX - mouseX;
                const deltaY = event.clientY - mouseY;
                
                // Rotar cámara
                camera.rotation.y -= deltaX * 0.01;
                camera.rotation.x -= deltaY * 0.01;
                
                // Limitar rotación vertical
                camera.rotation.x = Math.max(-Math.PI/2, Math.min(Math.PI/2, camera.rotation.x));
                
                mouseX = event.clientX;
                mouseY = event.clientY;
            }});
            
            renderer.domElement.addEventListener('mouseup', () => {{
                isMouseDown = false;
            }});
            
            // Zoom con rueda del mouse
            renderer.domElement.addEventListener('wheel', (event) => {{
                const zoom = event.deltaY > 0 ? 1.1 : 0.9;
                camera.fov *= zoom;
                camera.fov = Math.max(30, Math.min(120, camera.fov));
                camera.updateProjectionMatrix();
            }});
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }}
        
        // Redimensionar ventana
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>"""
            
            # GUARDAR EN AMBAS UBICACIONES
            viewer_file = output_dir / "viewer.html"
            with open(viewer_file, 'w', encoding='utf-8') as f:
                f.write(viewer_content)
            
            # TAMBIÉN GUARDAR EN CARPETA PRINCIPAL
            main_viewer = output_dir.parent / "viewer.html"
            with open(main_viewer, 'w', encoding='utf-8') as f:
                f.write(viewer_content)
            
            print(f"[SELENIUM] Viewer básico generado: {viewer_file}")
            print(f"[SELENIUM] Viewer básico copiado a: {main_viewer}")
            return True
            
        except Exception as e:
            print(f"[SELENIUM] Error generando viewer básico: {e}")
            return False
    
    def _generate_basic_config(self, year: str, view_type: str, output_dir: Path) -> bool:
        """Generar un config.xml básico"""
        try:
            if view_type == "interior":
                config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<panorama>
    <image>
        <level tiledimagewidth="3708" tiledimageheight="3708">
            <image><![CDATA[tiles/node1/cf_%c/l_%l/c_%x/tile_%y.jpg]]></image>
        </level>
    </image>
    <viewer>
        <title>Honda City {year} Interior 360°</title>
    </viewer>
</panorama>"""
            else:  # exterior
                config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<panorama>
    <image>
        <level tiledimagewidth="5200" tiledimageheight="1900">
            <image><![CDATA[tiles/c%c_l%r_%y_%x.jpg]]></image>
        </level>
    </image>
    <viewer>
        <title>Honda City {year} Exterior 360°</title>
    </viewer>
</panorama>"""
            
            # GUARDAR EN AMBAS UBICACIONES
            config_file = output_dir / "config.xml"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # TAMBIÉN GUARDAR EN CARPETA PRINCIPAL
            main_config = output_dir.parent / "config.xml"
            with open(main_config, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print(f"[SELENIUM] Config básico generado: {config_file}")
            print(f"[SELENIUM] Config básico copiado a: {main_config}")
            return True
            
        except Exception as e:
            print(f"[SELENIUM] Error generando config básico: {e}")
            return False
    
    def _fallback_asset_generation(self, year: str, view_type: str, output_dir: Path) -> Dict[str, bool]:
        """Generar assets básicos sin Selenium cuando WebDriver falla"""
        print("[FALLBACK] Generando assets básicos sin navegador...")
        
        results = {
            "config_xml": False,
            "viewer_html": False,
            "skin_js": False,
            "player_js": False,
            "error": None
        }
        
        try:
            # Generar viewer.html básico
            results["viewer_html"] = self._extract_real_viewer(year, view_type, output_dir)
            
            # Generar config.xml básico
            results["config_xml"] = self._extract_config_xml(year, view_type, output_dir)
            
            # Generar skin.js básico
            results["skin_js"] = self._extract_real_skin(year, view_type, output_dir)
            
            # Generar player.js básico
            results["player_js"] = self._extract_real_player(year, view_type, output_dir)
            
            print(f"[FALLBACK] Assets generados: {sum(results.values())}/4")
            
        except Exception as e:
            print(f"[FALLBACK] Error generando assets básicos: {e}")
            results["error"] = str(e)
        
        return results
    
    def _extract_real_skin(self, year: str, view_type: str, output_dir: Path) -> bool:
        """Extraer skin.js REAL desde Honda - NO GENERAR ARCHIVOS BÁSICOS"""
        try:
            # URLs reales de Honda para skin.js
            skin_urls = [
                f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360/skin.js",
                f"https://automobiles.honda.com/images/{year}/city/360/ViewType.{view_type.upper()}/skin.js"
            ]
            
            for skin_url in skin_urls:
                print(f"[SELENIUM] Intentando descargar skin REAL: {skin_url}")
                
                try:
                    self.driver.get(skin_url)
                    time.sleep(2)
                    
                    # Verificar si la página cargó correctamente
                    if "404" not in self.driver.title and self.driver.page_source.strip():
                        print(f"[SELENIUM] Skin REAL encontrado en: {skin_url}")
                        
                        # Obtener contenido JS real TAL COMO VIENE DE HONDA
                        js_content = self.driver.page_source
                        
                        # Guardar skin.js REAL
                        skin_file = output_dir / "skin.js"
                        with open(skin_file, 'w', encoding='utf-8') as f:
                            f.write(js_content)
                        
                        # TAMBIÉN GUARDAR EN CARPETA ASSETS
                        assets_dir = output_dir.parent / "assets"
                        assets_dir.mkdir(exist_ok=True)
                        assets_file = assets_dir / "skin.js"
                        with open(assets_file, 'w', encoding='utf-8') as f:
                            f.write(js_content)
                        
                        print(f"[SELENIUM] Skin REAL guardado: {skin_file}")
                        print(f"[SELENIUM] Skin REAL copiado a: {assets_file}")
                        return True
                        
                except Exception as e:
                    print(f"[SELENIUM] Error con URL {skin_url}: {e}")
                    continue
            
            print(f"[SELENIUM] NO SE ENCONTRÓ SKIN REAL - OMITIENDO ARCHIVO")
            return False
            
        except Exception as e:
            print(f"[SELENIUM] Error extrayendo skin JS: {e}")
            return False
    
    def _generate_basic_skin(self, year: str, view_type: str, output_dir: Path) -> bool:
        """SOLO PARA FALLBACK - Generar skin.js básico si no se encuentra el real"""
        try:
            skin_content = f"""// Honda City {year} {view_type.title()} Skin - Generado automáticamente
console.log('Honda City {year} {view_type} Skin cargado');

// Skin básico para viewer 360°
const skin = {{
    name: 'Honda City {year} {view_type.title()}',
    version: '1.0.0',
    author: 'Selenium Extractor',
    
    init: function() {{
        console.log('Skin inicializado');
    }},
    
    load: function() {{
        console.log('Skin cargado');
    }}
}};

// Exportar skin
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = skin;
}} else if (typeof window !== 'undefined') {{
    window.hondaSkin = skin;
}}"""
            
            # GUARDAR EN AMBAS UBICACIONES
            skin_file = output_dir / "skin.js"
            with open(skin_file, 'w', encoding='utf-8') as f:
                f.write(skin_content)
            
            # TAMBIÉN GUARDAR EN CARPETA ASSETS
            assets_dir = output_dir.parent / "assets"
            assets_dir.mkdir(exist_ok=True)
            assets_file = assets_dir / "skin.js"
            with open(assets_file, 'w', encoding='utf-8') as f:
                f.write(skin_content)
            
            print(f"[FALLBACK] Skin básico generado: {skin_file}")
            print(f"[FALLBACK] Skin básico copiado a: {assets_file}")
            return True
            
        except Exception as e:
            print(f"[FALLBACK] Error generando skin básico: {e}")
            return False
    
    def _extract_real_player(self, year: str, view_type: str, output_dir: Path) -> bool:
        """Extraer player.js REAL desde Honda - NO GENERAR ARCHIVOS BÁSICOS"""
        try:
            player_name = "pano2vr_player.js" if view_type == "interior" else "object2vr_player.js"
            
            # URLs reales de Honda para player.js
            player_urls = [
                f"https://www.honda.mx/web/img/cars/models/city/{year}/city_{year}_{view_type[:3]}_360/{player_name}",
                f"https://automobiles.honda.com/images/{year}/city/360/ViewType.{view_type.upper()}/{player_name}"
            ]
            
            for player_url in player_urls:
                print(f"[SELENIUM] Intentando descargar player REAL: {player_url}")
                
                try:
                    self.driver.get(player_url)
                    time.sleep(2)
                    
                    # Verificar si la página cargó correctamente
                    if "404" not in self.driver.title and self.driver.page_source.strip():
                        print(f"[SELENIUM] Player REAL encontrado en: {player_url}")
                        
                        # Obtener contenido JS real TAL COMO VIENE DE HONDA
                        js_content = self.driver.page_source
                        
                        # Guardar player.js REAL
                        player_file = output_dir / player_name
                        with open(player_file, 'w', encoding='utf-8') as f:
                            f.write(js_content)
                        
                        # TAMBIÉN GUARDAR EN CARPETA ASSETS
                        assets_dir = output_dir.parent / "assets"
                        assets_dir.mkdir(exist_ok=True)
                        assets_file = assets_dir / player_name
                        with open(assets_file, 'w', encoding='utf-8') as f:
                            f.write(js_content)
                        
                        print(f"[SELENIUM] Player REAL guardado: {player_file}")
                        print(f"[SELENIUM] Player REAL copiado a: {assets_file}")
                        return True
                        
                except Exception as e:
                    print(f"[SELENIUM] Error con URL {player_url}: {e}")
                    continue
            
            print(f"[SELENIUM] NO SE ENCONTRÓ PLAYER REAL - OMITIENDO ARCHIVO")
            return False
            
        except Exception as e:
            print(f"[SELENIUM] Error extrayendo player JS: {e}")
            return False
    
    def _clean_js_content(self, page_source: str) -> str:
        """Limpiar contenido JavaScript del HTML wrapper"""
        try:
            # Si el contenido tiene HTML wrapper, extraer solo el JavaScript
            if "<html>" in page_source and "<pre>" in page_source:
                # Buscar el contenido entre <pre> tags
                start_tag = "<pre"
                end_tag = "</pre>"
                
                start_idx = page_source.find(start_tag)
                if start_idx != -1:
                    start_idx = page_source.find(">", start_idx) + 1
                    end_idx = page_source.find(end_tag, start_idx)
                    
                    if end_idx != -1:
                        js_content = page_source[start_idx:end_idx]
                        # Decodificar entidades HTML
                        js_content = js_content.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                        return js_content.strip()
            
            # Si no hay wrapper HTML, devolver el contenido tal como está
            return page_source.strip()
            
        except Exception as e:
            print(f"[SELENIUM] Error limpiando contenido JS: {e}")
            return page_source.strip()
    
    def _generate_basic_player(self, year: str, view_type: str, output_dir: Path) -> bool:
        """SOLO PARA FALLBACK - Generar player.js básico si no se encuentra el real"""
        try:
            player_name = "pano2vr_player.js" if view_type == "interior" else "object2vr_player.js"
            
            player_content = f"""// Honda City {year} {view_type.title()} Player - Generado automáticamente
console.log('Honda City {year} {view_type} Player cargado');

// Player básico para viewer 360°
const player = {{
    name: 'Honda City {year} {view_type.title()} Player',
    version: '1.0.0',
    type: '{view_type}',
    author: 'Selenium Extractor',
    
    init: function() {{
        console.log('Player inicializado');
        this.setupCanvas();
    }},
    
    setupCanvas: function() {{
        const canvas = document.getElementById('canvas');
        if (canvas) {{
            console.log('Canvas configurado');
        }}
    }},
    
    loadImage: function(imagePath) {{
        console.log('Cargando imagen:', imagePath);
        return true;
    }}
}};

// Exportar player
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = player;
}} else if (typeof window !== 'undefined') {{
    window.hondaPlayer = player;
}}"""
            
            # GUARDAR EN AMBAS UBICACIONES
            player_file = output_dir / player_name
            with open(player_file, 'w', encoding='utf-8') as f:
                f.write(player_content)
            
            # TAMBIÉN GUARDAR EN CARPETA ASSETS
            assets_dir = output_dir.parent / "assets"
            assets_dir.mkdir(exist_ok=True)
            assets_file = assets_dir / player_name
            with open(assets_file, 'w', encoding='utf-8') as f:
                f.write(player_content)
            
            print(f"[FALLBACK] Player básico generado: {player_file}")
            print(f"[FALLBACK] Player básico copiado a: {assets_file}")
            return True
            
        except Exception as e:
            print(f"[FALLBACK] Error generando player básico: {e}")
            return False

# Función principal para usar desde el backend
async def extract_honda_assets_with_selenium(year: str, view_type: str, output_dir: Path, quality_level: int = 0) -> Dict[str, bool]:
    """
    Función principal para extraer assets de Honda usando Selenium
    AHORA TAMBIÉN DESCARGA IMÁGENES TILES
    """
    extractor = HondaSeleniumExtractor()
    
    try:
        # PASO 1: Extraer assets (mantener WebDriver vivo)
        results = extractor.extract_assets_from_honda_page(year, view_type, output_dir)
        
        # PASO 2: Descargar tiles MIENTRAS WebDriver está vivo
        print(f"[SELENIUM] Iniciando descarga de imágenes tiles para {view_type}...")
        tiles_downloaded = await extractor.download_tiles(year, view_type, output_dir, quality_level)
        results["tiles_downloaded"] = tiles_downloaded
        
    finally:
        # PASO 3: Cerrar WebDriver al final
        extractor.cleanup_driver()
    
    # COPIAR ASSETS A CARPETAS DEL SISTEMA
    if any(results.values()):
        system_base = output_dir.parent.parent / f"ViewType.{view_type.upper()}" / str(quality_level)
        assets_dir = system_base / "assets"
        images_dir = system_base / "images"
        assets_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[SELENIUM] Copiando assets a sistema: {system_base}")
        
        # Copiar archivos generados
        files_to_copy = []
        if results.get("config_xml"):
            files_to_copy.append(("config.xml", "config.xml"))
        if results.get("skin_js"):
            files_to_copy.append(("skin.js", "skin.js"))
        if results.get("player_js"):
            player_name = "pano2vr_player.js" if view_type == "interior" else "object2vr_player.js"
            files_to_copy.append((player_name, player_name))
        if results.get("viewer_html"):
            files_to_copy.append(("viewer.html", "viewer.html"))
        
        import shutil
        for source_name, dest_name in files_to_copy:
            source_file = output_dir / source_name
            if source_file.exists():
                # Copiar a carpeta principal del sistema
                dest_file = system_base / dest_name
                shutil.copy2(source_file, dest_file)
                print(f"[SELENIUM] Copiado {source_name} a {dest_file}")
                
                # Copiar a carpeta assets (para JS)
                if source_name.endswith('.js'):
                    assets_file = assets_dir / dest_name
                    shutil.copy2(source_file, assets_file)
                    print(f"[SELENIUM] Copiado {source_name} a assets: {assets_file}")
            else:
                print(f"[SELENIUM] Archivo no encontrado: {source_file}")
        
        # VERIFICAR QUE viewer.html EXISTE Y COPIARLO
        viewer_source = output_dir / "viewer.html"
        if viewer_source.exists():
            viewer_dest = system_base / "viewer.html"
            shutil.copy2(viewer_source, viewer_dest)
            print(f"[SELENIUM] viewer.html copiado a sistema: {viewer_dest}")
        else:
            print(f"[SELENIUM] viewer.html NO encontrado en: {viewer_source}")
        
        # COPIAR IMÁGENES TILES DESCARGADAS
        if tiles_downloaded > 0:
            print(f"[SELENIUM] Copiando {tiles_downloaded} imágenes tiles a sistema...")
            tiles_source_dir = output_dir / "tiles"
            if tiles_source_dir.exists():
                # Copiar todas las imágenes tiles
                for tile_file in tiles_source_dir.rglob("*.jpg"):
                    relative_path = tile_file.relative_to(tiles_source_dir)
                    dest_tile = images_dir / relative_path.name
                    shutil.copy2(tile_file, dest_tile)
                    print(f"[SELENIUM] Tile copiado: {relative_path.name}")
    
    return results
