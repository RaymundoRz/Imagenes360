#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 HONDA 360° ADVANCED QUALITY FIXER
====================================
Script mejorado que detecta y arregla problemas de calidad 
en visualizadores Pano2VR con patrones complejos.

Detecta patrones como:
- ✅ tiles/node1/cf_%c/l_%l/c_%x/tile_%y.jpg
- ✅ tiles/c%c_l%r_%y_%x.jpg
- ✅ tiles/c15_l1_0_0.jpg
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
import json
from datetime import datetime
import re

class AdvancedHonda360QualityFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.downloads_path = self.project_root / "backend" / "downloads"
        self.analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "quality_analysis": {},
            "complex_patterns_found": [],
            "recommendations": [],
            "auto_fixes_applied": []
        }
        
    def log(self, message):
        """Log con timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def analyze_complex_patterns(self):
        """Analizar patrones complejos en config.xml"""
        self.log("🔍 Analizando patrones complejos...")
        
        if not self.downloads_path.exists():
            self.log("❌ Directorio downloads no encontrado")
            return
            
        for honda_dir in self.downloads_path.iterdir():
            if honda_dir.is_dir() and "honda_city" in honda_dir.name:
                self.log(f"📁 Analizando {honda_dir.name}...")
                self.analyze_honda_complex_patterns(honda_dir)
                
    def analyze_honda_complex_patterns(self, honda_dir):
        """Analizar patrones complejos en un directorio Honda"""
        honda_name = honda_dir.name
        self.analysis_data["quality_analysis"][honda_name] = {}
        
        for viewtype_dir in honda_dir.iterdir():
            if viewtype_dir.is_dir() and "ViewType." in viewtype_dir.name:
                viewtype_name = viewtype_dir.name
                self.log(f"  📂 Analizando {viewtype_name}...")
                
                analysis = self.analyze_viewtype_complex_patterns(viewtype_dir)
                self.analysis_data["quality_analysis"][honda_name][viewtype_name] = analysis
                
    def analyze_viewtype_complex_patterns(self, viewtype_dir):
        """Analizar patrones complejos en directorio ViewType"""
        analysis = {
            "config_xml_patterns": {},
            "available_directories": {},
            "pattern_problems": [],
            "recommendations": []
        }
        
        # Analizar config.xml
        config_xml_path = viewtype_dir / "config.xml"
        if config_xml_path.exists():
            analysis["config_xml_patterns"] = self.analyze_config_complex_patterns(config_xml_path)
        else:
            analysis["pattern_problems"].append("❌ config.xml no encontrado")
            
        # Analizar directorios disponibles
        analysis["available_directories"] = self.find_available_directories(viewtype_dir)
        
        # Detectar problemas de patrones complejos
        problems = self.detect_complex_pattern_problems(analysis, viewtype_dir.name)
        analysis["pattern_problems"].extend(problems)
        
        return analysis
        
    def analyze_config_complex_patterns(self, config_xml_path):
        """Analizar patrones complejos en config.xml"""
        analysis = {
            "exists": True,
            "complex_patterns": [],
            "simple_patterns": [],
            "recommended_changes": []
        }
        
        try:
            with open(config_xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Buscar patrones complejos
            complex_patterns = [
                r'leveltileurl="([^"]*)"',
                r'imagepath="([^"]*)"',
                r'url="([^"]*)"'
            ]
            
            for pattern in complex_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match and ('%' in match or 'tiles' in match):
                        analysis["complex_patterns"].append({
                            "pattern": match,
                            "type": "COMPLEX_URL",
                            "needs_analysis": True
                        })
                        
                        # Detectar si usa tiles/ (potencial problema)
                        if 'tiles/' in match:
                            analysis["recommended_changes"].append({
                                "current": match,
                                "issue": "Uses tiles/ directory",
                                "needs_replacement": True
                            })
                            
            self.log(f"    📄 Patrones complejos encontrados: {len(analysis['complex_patterns'])}")
            
        except Exception as e:
            analysis["problems"] = [f"❌ Error leyendo archivo: {e}"]
            
        return analysis
        
    def find_available_directories(self, viewtype_dir):
        """Encontrar directorios disponibles para reemplazo"""
        directories = {}
        
        for item in viewtype_dir.iterdir():
            if item.is_dir() and item.name not in ['assets']:
                # Analizar contenido del directorio
                image_files = list(item.glob("**/*.jpg")) + list(item.glob("**/*.jpeg"))
                
                if image_files:
                    sizes = [f.stat().st_size for f in image_files[:10]]
                    avg_size = sum(sizes) / len(sizes) if sizes else 0
                    
                    directories[item.name] = {
                        "image_count": len(image_files),
                        "avg_file_size": int(avg_size),
                        "quality_category": self.categorize_quality(avg_size),
                        "recommended_for_replacement": avg_size > 10000  # > 10KB
                    }
                    
                    self.log(f"    📁 {item.name}: {len(image_files)} imágenes, ~{int(avg_size/1024)}KB")
                    
        return directories
        
    def categorize_quality(self, avg_size):
        """Categorizar calidad basada en tamaño"""
        if avg_size > 50000:
            return "ULTRA_HD"
        elif avg_size > 20000:
            return "HIGH_DEFINITION"
        elif avg_size > 10000:
            return "STANDARD"
        else:
            return "LOW_QUALITY"
            
    def detect_complex_pattern_problems(self, analysis, viewtype_name):
        """Detectar problemas específicos con patrones complejos"""
        problems = []
        
        config_analysis = analysis.get("config_xml_patterns", {})
        available_dirs = analysis.get("available_directories", {})
        complex_patterns = config_analysis.get("complex_patterns", [])
        
        # Problema 1: Patrón usa tiles/ pero hay mejor calidad disponible
        for pattern_info in complex_patterns:
            pattern = pattern_info["pattern"]
            
            if "tiles/" in pattern:
                # Buscar directorios de mejor calidad
                high_quality_dirs = [
                    name for name, info in available_dirs.items()
                    if info["quality_category"] in ["ULTRA_HD", "HIGH_DEFINITION"]
                ]
                
                if high_quality_dirs:
                    problems.append({
                        "type": "COMPLEX_PATTERN_ISSUE",
                        "pattern": pattern,
                        "issue": f"Usa 'tiles/' pero hay mejor calidad: {high_quality_dirs}",
                        "recommended_fix": self.generate_pattern_replacement(pattern, high_quality_dirs[0])
                    })
                    
        return problems
        
    def generate_pattern_replacement(self, original_pattern, new_directory):
        """Generar reemplazo de patrón complejo"""
        # Reemplazar tiles/ con nuevo directorio
        new_pattern = original_pattern.replace("tiles/", f"{new_directory}/")
        
        return {
            "original": original_pattern,
            "replacement": new_pattern,
            "directory": new_directory
        }
        
    def auto_fix_complex_patterns(self, apply_fixes=False):
        """Arreglar automáticamente patrones complejos"""
        if not apply_fixes:
            self.log("🔧 Modo DIAGNÓSTICO - no se aplicarán cambios")
            return
            
        self.log("🔧 Aplicando arreglos de patrones complejos...")
        
        for honda_name, honda_data in self.analysis_data["quality_analysis"].items():
            for viewtype_name, viewtype_data in honda_data.items():
                problems = viewtype_data.get("pattern_problems", [])
                
                for problem in problems:
                    if problem["type"] == "COMPLEX_PATTERN_ISSUE":
                        success = self.apply_pattern_fix(honda_name, viewtype_name, problem)
                        if success:
                            self.analysis_data["auto_fixes_applied"].append({
                                "honda": honda_name,
                                "viewtype": viewtype_name,
                                "fix": problem["recommended_fix"],
                                "status": "SUCCESS"
                            })
                            self.log(f"    ✅ Arreglado {viewtype_name}: {problem['recommended_fix']['original']} → {problem['recommended_fix']['replacement']}")
                            
    def apply_pattern_fix(self, honda_name, viewtype_name, problem):
        """Aplicar arreglo específico de patrón"""
        try:
            config_path = self.downloads_path / honda_name / viewtype_name / "config.xml"
            
            if not config_path.exists():
                return False
                
            # Leer archivo
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Aplicar reemplazo
            original = problem["recommended_fix"]["original"]
            replacement = problem["recommended_fix"]["replacement"]
            
            if original in content:
                # Hacer backup
                backup_path = config_path.with_suffix('.xml.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                # Aplicar cambio
                new_content = content.replace(original, replacement)
                
                # Escribir archivo actualizado
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                return True
            else:
                return False
                
        except Exception as e:
            self.log(f"❌ Error aplicando arreglo: {e}")
            return False
            
    def generate_advanced_report(self):
        """Generar reporte avanzado"""
        self.log("📄 Generando reporte avanzado...")
        
        total_problems = sum(
            len(vt.get("pattern_problems", []))
            for hd in self.analysis_data["quality_analysis"].values()
            for vt in hd.values()
        )
        
        self.analysis_data["summary"] = {
            "total_honda_models": len(self.analysis_data["quality_analysis"]),
            "total_complex_patterns": sum(
                len(vt.get("config_xml_patterns", {}).get("complex_patterns", []))
                for hd in self.analysis_data["quality_analysis"].values()
                for vt in hd.values()
            ),
            "total_pattern_problems": total_problems,
            "total_fixes_applied": len(self.analysis_data["auto_fixes_applied"]),
            "scan_complete": True
        }
        
        report_path = self.project_root / "honda_advanced_quality_analysis.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_data, f, indent=2, ensure_ascii=False)
            
        return report_path
        
    def run_advanced_analysis(self, apply_fixes=False):
        """Ejecutar análisis avanzado completo"""
        print("🔧 HONDA 360° ADVANCED QUALITY FIXER")
        print("=" * 50)
        
        try:
            self.analyze_complex_patterns()
            self.auto_fix_complex_patterns(apply_fixes)
            
            report_path = self.generate_advanced_report()
            
            print("\n" + "=" * 50)
            print("📊 RESUMEN DE ANÁLISIS AVANZADO:")
            print("-" * 30)
            print(f"Modelos Honda analizados: {self.analysis_data['summary']['total_honda_models']}")
            print(f"Patrones complejos encontrados: {self.analysis_data['summary']['total_complex_patterns']}")
            print(f"Problemas de patrones: {self.analysis_data['summary']['total_pattern_problems']}")
            print(f"Arreglos aplicados: {self.analysis_data['summary']['total_fixes_applied']}")
            print(f"Reporte guardado en: {report_path}")
            
            if apply_fixes:
                print("\n✅ ARREGLOS DE PATRONES COMPLEJOS APLICADOS")
            else:
                print("\n💡 Para aplicar arreglos automáticamente, ejecuta:")
                print("    python advanced_quality_fixer.py --fix")
                
        except Exception as e:
            print(f"❌ Error durante análisis avanzado: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    apply_fixes = "--fix" in sys.argv
    
    fixer = AdvancedHonda360QualityFixer()
    fixer.run_advanced_analysis(apply_fixes)
