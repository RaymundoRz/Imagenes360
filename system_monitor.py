#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 HONDA 360° SYSTEM DIAGNOSTIC MONITOR - VERSIÓN RÁPIDA
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import platform

class Honda360Monitor:
    def __init__(self):
        self.project_root = Path.cwd()
        self.diagnostic_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "project_structure": {},
            "backend_analysis": {},
            "frontend_analysis": {},
            "network_analysis": {},
            "problems_identified": [],
            "recommended_fixes": []
        }
        
    def log(self, message):
        """Log con timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def collect_system_info(self):
        """Recopilar información básica del sistema"""
        self.log("🔍 Recopilando información del sistema...")
        
        self.diagnostic_data["system_info"] = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "current_directory": str(self.project_root)
        }
        
    def analyze_backend(self):
        """Analizar backend Python/FastAPI"""
        self.log("🐍 Analizando backend...")
        
        backend_path = self.project_root / "backend"
        backend_info = {"exists": backend_path.exists()}
        
        if not backend_path.exists():
            self.diagnostic_data["problems_identified"].append(
                "❌ Directorio backend/ no encontrado"
            )
            return
            
        # Analizar app/routers/honda.py específicamente
        honda_router_path = backend_path / "app" / "routers" / "honda.py"
        if honda_router_path.exists():
            try:
                with open(honda_router_path, 'r', encoding='utf-8') as f:
                    honda_code = f.read()
                    backend_info["honda_router"] = {
                        "exists": True,
                        "lines": len(honda_code.split('\n')),
                        "has_extract_function": "extract_images" in honda_code,
                        "has_viewer_route": "/viewer/" in honda_code,
                        "has_quality_levels": "quality_level" in honda_code
                    }
            except Exception as e:
                backend_info["honda_router"] = {"error": str(e)}
        else:
            self.diagnostic_data["problems_identified"].append(
                "❌ app/routers/honda.py no encontrado"
            )
            
        # Analizar estructura de downloads
        downloads_path = backend_path / "downloads"
        if downloads_path.exists():
            backend_info["downloads_structure"] = self.analyze_downloads_directory(downloads_path)
        else:
            self.diagnostic_data["problems_identified"].append(
                "❌ Directorio downloads/ no encontrado"
            )
            
        self.diagnostic_data["backend_analysis"] = backend_info
        
    def analyze_downloads_directory(self, downloads_path):
        """Analizar directorio de downloads rápidamente"""
        structure = {}
        
        try:
            for item in downloads_path.iterdir():
                if item.is_dir() and "honda_city" in item.name:
                    structure[item.name] = {"type": "directory", "contents": {}}
                    
                    # Solo buscar ViewType directories
                    for subitem in item.iterdir():
                        if subitem.is_dir() and "ViewType" in subitem.name:
                            # Verificar si tiene viewer.html
                            viewer_file = subitem / "viewer.html"
                            structure[item.name]["contents"][subitem.name] = {
                                "type": "viewtype_directory",
                                "has_viewer": viewer_file.exists()
                            }
        except Exception as e:
            structure["error"] = str(e)
                        
        return structure
        
    def analyze_frontend(self):
        """Analizar frontend React"""
        self.log("⚛️  Analizando frontend...")
        
        frontend_path = self.project_root / "frontend"
        frontend_info = {"exists": frontend_path.exists()}
        
        if not frontend_path.exists():
            self.diagnostic_data["problems_identified"].append(
                "❌ Directorio frontend/ no encontrado"
            )
            return
            
        # Analizar HondaExtractor.jsx
        honda_extractor_path = frontend_path / "src" / "components" / "HondaExtractor.jsx"
        if honda_extractor_path.exists():
            try:
                with open(honda_extractor_path, 'r', encoding='utf-8') as f:
                    jsx_code = f.read()
                    frontend_info["honda_extractor"] = {
                        "exists": True,
                        "lines": len(jsx_code.split('\n')),
                        "has_openviewer": "openViewer" in jsx_code,
                        "has_completed_downloads": "completedDownloads" in jsx_code,
                        "hardcoded_interior": "ViewType.INTERIOR" in jsx_code,
                        "dynamic_viewtype": "viewType.toUpperCase()" in jsx_code,
                        "current_openviewer_code": self.extract_openviewer_function(jsx_code)
                    }
            except Exception as e:
                frontend_info["honda_extractor"] = {"error": str(e)}
        else:
            self.diagnostic_data["problems_identified"].append(
                "❌ HondaExtractor.jsx no encontrado"
            )
            
        # Analizar api.js
        api_js_path = frontend_path / "src" / "services" / "api.js"
        if api_js_path.exists():
            try:
                with open(api_js_path, 'r', encoding='utf-8') as f:
                    api_code = f.read()
                    frontend_info["api_service"] = {
                        "exists": True,
                        "lines": len(api_code.split('\n')),
                        "has_generate_viewer": "generateViewer" in api_code,
                        "has_extract_images": "extractImages" in api_code,
                        "base_url": self.extract_base_url(api_code)
                    }
            except Exception as e:
                frontend_info["api_service"] = {"error": str(e)}
        else:
            self.diagnostic_data["problems_identified"].append(
                "❌ api.js no encontrado"
            )
            
        self.diagnostic_data["frontend_analysis"] = frontend_info
        
    def extract_openviewer_function(self, jsx_code):
        """Extraer función openViewer del código JSX"""
        lines = jsx_code.split('\n')
        in_function = False
        function_lines = []
        
        for line in lines:
            if 'openViewer' in line and ('const' in line or 'function' in line):
                in_function = True
                function_lines.append(line.strip())
            elif in_function:
                function_lines.append(line.strip())
                if line.strip().endswith('};') or (line.strip() == '}' and len(function_lines) > 5):
                    break
                    
        return '\n'.join(function_lines) if function_lines else "Not found"
        
    def extract_base_url(self, api_code):
        """Extraer URL base de api.js"""
        lines = api_code.split('\n')
        for line in lines:
            if "API_BASE" in line and "http" in line:
                return line.strip()
        return "Not found"
        
    def analyze_network(self):
        """Verificar puertos importantes rápidamente"""
        self.log("🌐 Analizando red...")
        
        network_info = {}
        ports_to_check = [5173, 8000, 8080]
        
        for port in ports_to_check:
            network_info[f"port_{port}"] = self.check_port_simple(port)
            
        self.diagnostic_data["network_analysis"] = network_info
        
    def check_port_simple(self, port):
        """Verificar puerto simple"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
            
    def identify_problems(self):
        """Identificar problemas basado en el análisis"""
        self.log("🔍 Identificando problemas...")
        
        problems = []
        fixes = []
        
        # Analizar frontend
        frontend_analysis = self.diagnostic_data.get("frontend_analysis", {})
        honda_extractor = frontend_analysis.get("honda_extractor", {})
        
        if honda_extractor.get("hardcoded_interior") and not honda_extractor.get("dynamic_viewtype"):
            problems.append("❌ PROBLEMA: openViewer() hardcoded a INTERIOR")
            fixes.append("✅ FIX: Usar view_type dinámicamente en openViewer()")
            
        # Analizar red
        network_analysis = self.diagnostic_data.get("network_analysis", {})
        if not network_analysis.get("port_8080"):
            problems.append("❌ PROBLEMA: Puerto 8080 no activo (servidor de archivos)")
            fixes.append("✅ FIX: Iniciar python -m http.server 8080 en downloads/")
            
        if not network_analysis.get("port_8000"):
            problems.append("❌ PROBLEMA: Puerto 8000 no activo (backend FastAPI)")
            fixes.append("✅ FIX: Iniciar backend con uvicorn")
            
        if not network_analysis.get("port_5173"):
            problems.append("❌ PROBLEMA: Puerto 5173 no activo (frontend React)")
            fixes.append("✅ FIX: Iniciar frontend con npm run dev")
            
        self.diagnostic_data["problems_identified"].extend(problems)
        self.diagnostic_data["recommended_fixes"].extend(fixes)
        
    def generate_report(self):
        """Generar reporte JSON completo"""
        self.log("📄 Generando reporte...")
        
        self.diagnostic_data["summary"] = {
            "total_problems": len(self.diagnostic_data["problems_identified"]),
            "total_fixes": len(self.diagnostic_data["recommended_fixes"]),
            "system_health": "CRITICAL" if len(self.diagnostic_data["problems_identified"]) > 5 else "WARNING" if len(self.diagnostic_data["problems_identified"]) > 0 else "HEALTHY"
        }
        
        report_path = self.project_root / "honda_system_diagnostic.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.diagnostic_data, f, indent=2, ensure_ascii=False)
            
        return report_path
        
    def run_full_diagnostic(self):
        """Ejecutar diagnóstico completo rápido"""
        print("🔍 HONDA 360° SYSTEM DIAGNOSTIC MONITOR - VERSIÓN RÁPIDA")
        print("=" * 60)
        
        try:
            self.collect_system_info()
            self.analyze_backend()
            self.analyze_frontend()  
            self.analyze_network()
            self.identify_problems()
            
            report_path = self.generate_report()
            
            print("\n" + "=" * 60)
            print("📊 RESUMEN DEL DIAGNÓSTICO:")
            print("-" * 30)
            print(f"Problemas encontrados: {len(self.diagnostic_data['problems_identified'])}")
            print(f"Estado del sistema: {self.diagnostic_data['summary']['system_health']}")
            print(f"Reporte completo: {report_path}")
            
            if self.diagnostic_data["problems_identified"]:
                print("\n🚨 PROBLEMAS IDENTIFICADOS:")
                for problem in self.diagnostic_data["problems_identified"][:5]:
                    print(f"  {problem}")
                    
            print("\n✅ Diagnóstico rápido completado!")
            
        except Exception as e:
            print(f"❌ Error durante diagnóstico: {e}")

if __name__ == "__main__":
    monitor = Honda360Monitor()
    monitor.run_full_diagnostic()
