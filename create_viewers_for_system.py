#!/usr/bin/env python3
"""
Script para crear viewers HTML funcionales para nuestro sistema con las 3 calidades
"""

import os
from pathlib import Path
import shutil

def create_system_viewer(quality_level: int):
    """Crear viewer HTML para nuestro sistema con una calidad específica"""
    
    year = "2026"
    view_type = "interior"
    
    print(f"\n🎯 === CREANDO VIEWER PARA CALIDAD {quality_level} ===")
    
    # Directorios
    quality_dir = Path(f"backend/downloads/honda_city_2026/ViewType.{view_type.upper()}/{quality_level}")
    system_dir = Path(f"backend/downloads/honda_city_2026_system/ViewType.{view_type.upper()}/{quality_level}")
    
    print(f"📁 Calidad: {quality_dir}")
    print(f"📁 Sistema: {system_dir}")
    
    # Crear directorio del sistema
    system_dir.mkdir(parents=True, exist_ok=True)
    (system_dir / "images").mkdir(parents=True, exist_ok=True)
    
    # 1. COPIAR IMÁGENES
    print("📸 Copiando imágenes...")
    images_source = quality_dir / "images"
    images_dest = system_dir / "images"
    
    if images_source.exists():
        for img_file in images_source.glob("*.jpg"):
            shutil.copy2(img_file, images_dest)
        print(f"   ✅ {len(list(images_source.glob('*.jpg')))} imágenes copiadas")
    
    # 2. COPIAR ASSETS
    print("📦 Copiando assets...")
    assets_to_copy = ["config.xml", "skin.js", "pano2vr_player.js", "viewer.html"]
    
    for asset in assets_to_copy:
        source_file = quality_dir / asset
        if source_file.exists():
            shutil.copy2(source_file, system_dir)
            print(f"   ✅ {asset} copiado")
    
    # 3. CREAR VIEWER FUNCIONAL PARA NUESTRO SISTEMA
    print("🔧 Creando viewer funcional...")
    
    # Leer el viewer.html original de Honda
    honda_viewer = quality_dir / "viewer.html"
    if honda_viewer.exists():
        with open(honda_viewer, 'r', encoding='utf-8') as f:
            viewer_content = f.read()
        
        # Crear viewer funcional para nuestro sistema
        system_viewer_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Honda City 2026 {view_type.title()} - Calidad {quality_level}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .viewer-container {{
            padding: 30px;
            text-align: center;
        }}
        .quality-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #007bff;
        }}
        .quality-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }}
        .quality-0 {{ background: #28a745; color: white; }}
        .quality-1 {{ background: #ffc107; color: black; }}
        .quality-2 {{ background: #6c757d; color: white; }}
        .viewer-frame {{
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .controls {{
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-warning {{ background: #ffc107; color: black; }}
        .btn-secondary {{ background: #6c757d; color: white; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .stats {{
            background: #e9ecef;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }}
        .stats h3 {{
            margin-top: 0;
            color: #495057;
        }}
        .stat-item {{
            display: inline-block;
            margin: 10px 20px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏎️ Honda City 2026</h1>
            <p>Visualizador 360° - {view_type.title()} - Calidad {quality_level}</p>
        </div>
        
        <div class="viewer-container">
            <div class="quality-info">
                <h3>🎯 Calidad de Visualización</h3>
                <span class="quality-badge quality-{quality_level}">
                    {{
                        '0': '🔥 Ultra HD (Máxima Calidad)',
                        '1': '⚡ High Definition (Alta Calidad)', 
                        '2': '📱 Standard (Calidad Estándar)'
                    }}.get('{quality_level}', 'Calidad {quality_level}')
                }}</span>
                <p>Esta visualización utiliza {len(list((system_dir / "images").glob("*.jpg")))} imágenes de alta resolución para una experiencia 360° inmersiva.</p>
            </div>
            
            <iframe 
                src="viewer.html" 
                class="viewer-frame"
                title="Honda City 2026 Viewer">
            </iframe>
            
            <div class="controls">
                <a href="viewer.html" class="btn btn-primary" target="_blank">🔍 Abrir en Nueva Pestaña</a>
                <a href="../0/viewer.html" class="btn btn-success">🔥 Calidad Ultra HD</a>
                <a href="../1/viewer.html" class="btn btn-warning">⚡ Calidad HD</a>
                <a href="../2/viewer.html" class="btn btn-secondary">📱 Calidad Standard</a>
            </div>
            
            <div class="stats">
                <h3>📊 Estadísticas de la Visualización</h3>
                <div class="stat-item">
                    <div class="stat-number">{len(list((system_dir / "images").glob("*.jpg")))}</div>
                    <div class="stat-label">Imágenes</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{quality_level}</div>
                    <div class="stat-label">Nivel de Calidad</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{view_type.title()}</div>
                    <div class="stat-label">Tipo de Vista</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">2026</div>
                    <div class="stat-label">Modelo</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        console.log('🚗 Honda City 2026 Viewer - Calidad {quality_level}');
        console.log('📸 Imágenes cargadas: {len(list((system_dir / "images").glob("*.jpg")))}');
        console.log('🎯 Tipo: {view_type}');
    </script>
</body>
</html>"""
        
        # Guardar viewer del sistema
        system_viewer_file = system_dir / "index.html"
        with open(system_viewer_file, 'w', encoding='utf-8') as f:
            f.write(system_viewer_content)
        
        print(f"   ✅ Viewer del sistema creado: {system_viewer_file}")
    
    # 4. CREAR CONFIG LOCAL
    print("⚙️ Creando config local...")
    config_source = quality_dir / "config.xml"
    if config_source.exists():
        with open(config_source, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Reemplazar rutas de imágenes por rutas locales
        config_content = config_content.replace(
            'tiles/node1/cf_%c/l_%l/c_%x/tile_%y.jpg',
            f'images/tile_%04d.jpg'
        )
        
        # Guardar config local
        config_local_file = system_dir / "config_local.xml"
        with open(config_local_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"   ✅ Config local creado: {config_local_file}")
    
    print(f"✅ Calidad {quality_level} configurada para el sistema")
    
    return len(list((system_dir / "images").glob("*.jpg")))

def main():
    """Crear viewers para las 3 calidades"""
    
    print("🎯 === CREANDO VIEWERS FUNCIONALES PARA NUESTRO SISTEMA ===")
    
    total_images = 0
    
    for quality in [0, 1, 2]:
        images_count = create_system_viewer(quality)
        total_images += images_count
    
    print(f"\n🎉 === VIEWERS DEL SISTEMA CREADOS ===")
    print(f"   ✅ Total imágenes: {total_images}")
    print(f"   📁 Ubicación: backend/downloads/honda_city_2026_system/")
    print(f"\n🌐 URLs para acceder:")
    print(f"   http://127.0.0.1:8080/honda_city_2026_system/ViewType.INTERIOR/0/index.html")
    print(f"   http://127.0.0.1:8080/honda_city_2026_system/ViewType.INTERIOR/1/index.html")
    print(f"   http://127.0.0.1:8080/honda_city_2026_system/ViewType.INTERIOR/2/index.html")

if __name__ == "__main__":
    main()





