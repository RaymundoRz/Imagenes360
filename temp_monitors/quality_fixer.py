#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 HONDA 360° QUALITY FIXER
===========================
Script automático que detecta y arregla problemas de calidad 
en los visualizadores Pano2VR.

Detecta:
- ✅ Config.xml apuntando a carpetas incorrectas
- ✅ Archivos de imágenes de baja vs alta calidad  
- ✅ Mapeo incorrecto de quality_level
- ✅ Genera reporte detallado de calidades
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
import json
from datetime import datetime
import re

class Honda360QualityFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.downloads_path = self.project_root / "backend" / "downloads"
        self.analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "quality_analysis": {},
            "config_problems": [],
            "image_analysis": {},
            "recommendations": [],
            "auto_fixes_applied": []
        }
        
    def log(self, message):
        """Log con timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def analyze_honda_downloads(self):
        """Analizar todos los directorios Honda"""
        self.log("🔍 Analizando calidades Honda 360°...")
        
        if not self.downloads_path.exists():
            self.log("❌ Directorio downloads no encontrado")
            return
            
        for honda_dir in self.downloads_path.iterdir():
            if honda_dir.is_dir() and "honda_city" in honda_dir.name:
                self.log(f"📁 Analizando {honda_dir.name}...")
                self.analyze_honda_directory(honda_dir)
                
    def analyze_honda_directory(self, honda_dir):
        """Analizar un directorio específico de Honda"""
        honda_name = honda_dir.name
        self.analysis_data["quality_analysis"][honda_name] = {}
        
        # Buscar ViewType directories
        for viewtype_dir in honda_dir.iterdir():
            if viewtype_dir.is_dir() and "ViewType." in viewtype_dir.name:
                viewtype_name = viewtype_dir.name
                self.log(f"  📂 Analizando {viewtype_name}...")
                
                analysis = self.analyze_viewtype_directory(viewtype_dir)
                self.analysis_data["quality_analysis"][honda_name][viewtype_name] = analysis
                
    def analyze_viewtype_directory(self, viewtype_dir):
        """Analizar directorio ViewType específico"""
        analysis = {
            "config_xml_analysis": {},
            "image_directories": {},
            "quality_problems": [],
            "recommendations": []
        }
        
        # Analizar config.xml
        config_xml_path = viewtype_dir / "config.xml"
        if config_xml_path.exists():
            analysis["config_xml_analysis"] = self.analyze_config_xml(config_xml_path)
        else:
            analysis["quality_problems"].append("❌ config.xml no encontrado")
            
        # Analizar directorios de imágenes
        image_dirs = self.find_image_directories(viewtype_dir)
        analysis["image_directories"] = image_dirs
        
        # Detectar problemas de calidad
        problems = self.detect_quality_problems(analysis, viewtype_dir.name)
        analysis["quality_problems"].extend(problems)
        
        return analysis
        
    def analyze_config_xml(self, config_xml_path):
        """Analizar archivo config.xml"""
        analysis = {
            "exists": True,
            "cube_urls": [],
            "quality_levels": [],
            "problems": []
        }
        
        try:
            tree = ET.parse(config_xml_path)
            root = tree.getroot()
            
            # Buscar elementos cube
            for cube in root.iter('cube'):
                url = cube.get('url', '')
                if url:
                    analysis["cube_urls"].append(url)
                    
            # Buscar elementos level
            for level in root.iter('level'):
                width = level.get('tiledimagewidth', '')
                height = level.get('tiledimageheight', '')
                if width and height:
                    analysis["quality_levels"].append({
                        "width": width,
                        "height": height
                    })
                    
            self.log(f"    📄 Config.xml analizado: {len(analysis['cube_urls'])} URLs encontradas")
            
        except Exception as e:
            analysis["problems"].append(f"❌ Error leyendo XML: {e}")
            
        return analysis
        
    def find_image_directories(self, viewtype_dir):
        """Encontrar directorios con imágenes"""
        image_dirs = {}
        
        for item in viewtype_dir.iterdir():
            if item.is_dir():
                # Contar imágenes y analizar tamaños
                image_files = list(item.glob("**/*.jpg")) + list(item.glob("**/*.jpeg"))
                
                if image_files:
                    sizes = [f.stat().st_size for f in image_files[:5]]  # Sample de 5 archivos
                    avg_size = sum(sizes) / len(sizes) if sizes else 0
                    
                    image_dirs[item.name] = {
                        "image_count": len(image_files),
                        "avg_file_size": int(avg_size),
                        "size_category": self.categorize_image_quality(avg_size),
                        "sample_sizes": sizes
                    }
                    
                    self.log(f"    📸 {item.name}: {len(image_files)} imágenes, ~{int(avg_size/1024)}KB promedio")
                    
        return image_dirs
        
    def categorize_image_quality(self, avg_size):
        """Categorizar calidad basada en tamaño promedio"""
        if avg_size > 20000:  # > 20KB
            return "ULTRA_HD"
        elif avg_size > 10000:  # > 10KB
            return "HIGH_DEFINITION"
        elif avg_size > 5000:   # > 5KB
            return "STANDARD"
        else:
            return "LOW_QUALITY"
            
    def detect_quality_problems(self, analysis, viewtype_name):
        """Detectar problemas específicos de calidad"""
        problems = []
        
        config_analysis = analysis.get("config_xml_analysis", {})
        image_dirs = analysis.get("image_directories", {})
        cube_urls = config_analysis.get("cube_urls", [])
        
        # Problema 1: Config.xml apunta a carpeta de baja calidad
        if cube_urls:
            for url in cube_urls:
                if "tiles/" in url:
                    # Verificar si hay carpetas de mejor calidad disponibles
                    high_quality_dirs = [
                        name for name, info in image_dirs.items() 
                        if info["size_category"] in ["ULTRA_HD", "HIGH_DEFINITION"]
                    ]
                    
                    if high_quality_dirs:
                        problems.append(
                            f"❌ Config.xml usa 'tiles/' (baja calidad) pero hay {high_quality_dirs} disponibles"
                        )
                        
        # Problema 2: Múltiples calidades pero usando la peor
        if len(image_dirs) > 1:
            quality_levels = [(name, info["size_category"]) for name, info in image_dirs.items()]
            has_ultra_hd = any(cat == "ULTRA_HD" for _, cat in quality_levels)
            config_uses_low = any("tiles" in url for url in cube_urls)
            
            if has_ultra_hd and config_uses_low:
                problems.append(
                    f"❌ Tiene ULTRA_HD disponible pero config.xml usa calidad baja"
                )
                
        return problems
        
    def generate_recommendations(self):
        """Generar recomendaciones automáticas"""
        self.log("💡 Generando recomendaciones...")
        
        recommendations = []
        
        for honda_name, honda_data in self.analysis_data["quality_analysis"].items():
            for viewtype_name, viewtype_data in honda_data.items():
                problems = viewtype_data.get("quality_problems", [])
                image_dirs = viewtype_data.get("image_directories", {})
                
                if problems:
                    # Encontrar la mejor calidad disponible
                    best_dir = None
                    best_quality = "LOW_QUALITY"
                    
                    for dir_name, dir_info in image_dirs.items():
                        if dir_info["size_category"] == "ULTRA_HD":
                            best_dir = dir_name
                            best_quality = "ULTRA_HD"
                            break
                        elif dir_info["size_category"] == "HIGH_DEFINITION" and best_quality != "ULTRA_HD":
                            best_dir = dir_name
                            best_quality = "HIGH_DEFINITION"
                            
                    if best_dir:
                        recommendations.append({
                            "honda": honda_name,
                            "viewtype": viewtype_name,
                            "action": "UPDATE_CONFIG_XML",
                            "current_quality": "LOW (tiles/)",
                            "recommended_dir": best_dir,
                            "recommended_quality": best_quality,
                            "fix_command": f"Cambiar config.xml para usar '{best_dir}/' en lugar de 'tiles/'"
                        })
                        
        self.analysis_data["recommendations"] = recommendations
        
    def auto_fix_config_xml(self, apply_fixes=False):
        """Arreglar automáticamente archivos config.xml"""
        if not apply_fixes:
            self.log("🔧 Modo DIAGNÓSTICO - no se aplicarán cambios")
            return
            
        self.log("🔧 Aplicando arreglos automáticos...")
        
        for rec in self.analysis_data["recommendations"]:
            if rec["action"] == "UPDATE_CONFIG_XML":
                honda_name = rec["honda"]
                viewtype_name = rec["viewtype"]
                new_dir = rec["recommended_dir"]
                
                config_path = self.downloads_path / honda_name / viewtype_name / "config.xml"
                
                if config_path.exists():
                    success = self.update_config_xml(config_path, new_dir)
                    if success:
                        self.analysis_data["auto_fixes_applied"].append({
                            "file": str(config_path),
                            "change": f"tiles/ → {new_dir}/",
                            "status": "SUCCESS"
                        })
                        self.log(f"    ✅ Actualizado {viewtype_name} para usar {new_dir}")
                    else:
                        self.log(f"    ❌ Error actualizando {viewtype_name}")
                        
    def update_config_xml(self, config_path, new_dir):
        """Actualizar archivo config.xml específico"""
        try:
            # Leer archivo como texto (más seguro que XML parsing)
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Reemplazar tiles/ con nuevo directorio
            original_content = content
            content = content.replace('tiles/', f'{new_dir}/')
            
            # Verificar que se hizo algún cambio
            if content != original_content:
                # Hacer backup
                backup_path = config_path.with_suffix('.xml.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                    
                # Escribir nuevo contenido
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                return True
            else:
                return False
                
        except Exception as e:
            self.log(f"❌ Error actualizando {config_path}: {e}")
            return False
            
    def generate_report(self):
        """Generar reporte detallado"""
        self.log("📄 Generando reporte...")
        
        # Agregar estadísticas generales
        total_problems = sum(
            len(vt.get("quality_problems", [])) 
            for hd in self.analysis_data["quality_analysis"].values()
            for vt in hd.values()
        )
        
        self.analysis_data["summary"] = {
            "total_honda_models": len(self.analysis_data["quality_analysis"]),
            "total_problems": total_problems,
            "total_recommendations": len(self.analysis_data["recommendations"]),
            "total_fixes_applied": len(self.analysis_data["auto_fixes_applied"]),
            "scan_complete": True
        }
        
        # Guardar reporte
        report_path = self.project_root / "honda_quality_analysis.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_data, f, indent=2, ensure_ascii=False)
            
        return report_path
        
    def run_quality_analysis(self, apply_fixes=False):
        """Ejecutar análisis completo de calidad"""
        print("🔧 HONDA 360° QUALITY FIXER")
        print("=" * 50)
        
        try:
            self.analyze_honda_downloads()
            self.generate_recommendations()
            self.auto_fix_config_xml(apply_fixes)
            
            report_path = self.generate_report()
            
            print("\n" + "=" * 50)
            print("📊 RESUMEN DE ANÁLISIS DE CALIDAD:")
            print("-" * 30)
            print(f"Modelos Honda analizados: {self.analysis_data['summary']['total_honda_models']}")
            print(f"Problemas detectados: {self.analysis_data['summary']['total_problems']}")
            print(f"Recomendaciones generadas: {self.analysis_data['summary']['total_recommendations']}")
            print(f"Arreglos aplicados: {self.analysis_data['summary']['total_fixes_applied']}")
            print(f"Reporte guardado en: {report_path}")
            
            if self.analysis_data["recommendations"]:
                print("\n🎯 RECOMENDACIONES PRINCIPALES:")
                for i, rec in enumerate(self.analysis_data["recommendations"][:3], 1):
                    print(f"  {i}. {rec['viewtype']}: {rec['fix_command']}")
                    
            if apply_fixes:
                print("\n✅ ARREGLOS APLICADOS AUTOMÁTICAMENTE")
            else:
                print("\n💡 Para aplicar arreglos automáticamente, ejecuta:")
                print("    python quality_fixer.py --fix")
                
        except Exception as e:
            print(f"❌ Error durante análisis: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    apply_fixes = "--fix" in sys.argv
    
    fixer = Honda360QualityFixer()
    fixer.run_quality_analysis(apply_fixes)
