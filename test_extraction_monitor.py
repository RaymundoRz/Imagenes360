#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST EXTRACTION MONITOR - HONDA 360° EXTRACTOR
==============================================
Simula extracción de usuario desde frontend y monitorea todo el proceso
"""

import time
import requests
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import sys
import os

class ExtractionMonitor:
    def __init__(self):
        self.log_file = "test_extraction_log.txt"
        self.start_time = datetime.now()
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://127.0.0.1:5174"
        self.file_server_url = "http://127.0.0.1:8080"
        self.extraction_results = {}
        self.errors = []
        self.warnings = []
        
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def check_services(self):
        """Verificar que todos los servicios estén corriendo"""
        self.log("=== VERIFICANDO SERVICIOS ===")
        
        services = {
            "Backend (8000)": self.backend_url,
            "Frontend (5174)": self.frontend_url,
            "File Server (8080)": self.file_server_url
        }
        
        all_running = True
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    self.log(f"✅ {service_name}: OK")
                else:
                    self.log(f"⚠️ {service_name}: Status {response.status_code}", "WARNING")
                    all_running = False
            except Exception as e:
                self.log(f"❌ {service_name}: ERROR - {str(e)}", "ERROR")
                all_running = False
                self.errors.append(f"{service_name} no disponible: {str(e)}")
        
        return all_running
    
    def test_backend_health(self):
        """Probar health check del backend"""
        self.log("=== PROBANDO HEALTH CHECK BACKEND ===")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Health Check: {data}")
                return True
            else:
                self.log(f"❌ Health Check falló: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Health Check error: {str(e)}", "ERROR")
            self.errors.append(f"Health check falló: {str(e)}")
            return False
    
    def simulate_user_extraction(self, year="2026", view_type="interior", quality_level=0):
        """Simular extracción como usuario desde frontend"""
        self.log(f"=== SIMULANDO EXTRACCIÓN USUARIO ===")
        self.log(f"Parámetros: Año={year}, Vista={view_type}, Calidad={quality_level}")
        
        try:
            # 1. Llamar endpoint de extracción
            extraction_url = f"{self.backend_url}/api/honda/extract"
            payload = {
                "year": year,
                "view_type": view_type,
                "quality_level": quality_level
            }
            
            self.log(f"Enviando request a: {extraction_url}")
            self.log(f"Payload: {payload}")
            
            response = requests.post(extraction_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Extracción iniciada: {data}")
                self.extraction_results[f"{view_type}_{quality_level}"] = data
                return data
            else:
                self.log(f"❌ Extracción falló: {response.status_code} - {response.text}", "ERROR")
                self.errors.append(f"Extracción falló: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"❌ Error en extracción: {str(e)}", "ERROR")
            self.errors.append(f"Error extracción: {str(e)}")
            return None
    
    def monitor_extraction_progress(self, extraction_id, timeout=120):
        """Monitorear progreso de extracción"""
        self.log(f"=== MONITOREANDO EXTRACCIÓN {extraction_id} ===")
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            try:
                # Verificar status de extracción
                status_url = f"{self.backend_url}/api/honda/status/{extraction_id}"
                response = requests.get(status_url, timeout=10)
                
                if response.status_code == 200:
                    status_data = response.json()
                    current_status = status_data.get("status", "unknown")
                    
                    if current_status != last_status:
                        self.log(f"📊 Status cambio: {last_status} → {current_status}")
                        last_status = current_status
                    
                    if current_status == "completed":
                        self.log(f"✅ Extracción completada: {status_data}")
                        return True
                    elif current_status == "error":
                        self.log(f"❌ Extracción falló: {status_data}", "ERROR")
                        self.errors.append(f"Extracción {extraction_id} falló")
                        return False
                    
                else:
                    self.log(f"⚠️ Status check falló: {response.status_code}", "WARNING")
                
            except Exception as e:
                self.log(f"⚠️ Error monitoreando: {str(e)}", "WARNING")
            
            time.sleep(2)
        
        self.log(f"⏰ Timeout alcanzado para extracción {extraction_id}", "WARNING")
        self.warnings.append(f"Timeout en extracción {extraction_id}")
        return False
    
    def test_viewer_functionality(self, year="2026", view_type="interior", quality_level=0):
        """Probar funcionalidad del visualizador 360°"""
        self.log(f"=== PROBANDO VISUALIZADOR 360° ===")
        self.log(f"Parámetros: {year}/{view_type}/{quality_level}")
        
        # URLs a probar
        viewer_urls = [
            f"{self.file_server_url}/honda_city_{year}/ViewType.{view_type.upper()}/{quality_level}/index.html",
            f"{self.file_server_url}/honda_city_{year}/ViewType.{view_type.upper()}/{quality_level}/viewer.html",
            f"{self.backend_url}/api/honda/honda_city_{year}/ViewType.{view_type.upper()}/{quality_level}/viewer.html"
        ]
        
        working_urls = []
        
        for url in viewer_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ Viewer OK: {url}")
                    working_urls.append(url)
                else:
                    self.log(f"⚠️ Viewer Status {response.status_code}: {url}", "WARNING")
            except Exception as e:
                self.log(f"❌ Viewer Error: {url} - {str(e)}", "ERROR")
        
        if working_urls:
            self.log(f"✅ {len(working_urls)} viewers funcionando")
            return working_urls
        else:
            self.log(f"❌ Ningún viewer funciona", "ERROR")
            self.errors.append("Ningún visualizador 360° funciona")
            return []
    
    def check_file_structure(self, year="2026"):
        """Verificar estructura de archivos generada"""
        self.log(f"=== VERIFICANDO ESTRUCTURA DE ARCHIVOS ===")
        
        base_path = Path(f"backend/downloads/honda_city_{year}")
        
        if not base_path.exists():
            self.log(f"❌ Directorio base no existe: {base_path}", "ERROR")
            self.errors.append(f"Directorio {base_path} no existe")
            return False
        
        # Verificar estructura esperada
        expected_structure = [
            "ViewType.INTERIOR/0/",
            "ViewType.INTERIOR/1/", 
            "ViewType.INTERIOR/2/",
            "ViewType.EXTERIOR/0/",
            "ViewType.EXTERIOR/1/",
            "ViewType.EXTERIOR/2/"
        ]
        
        missing_dirs = []
        for dir_path in expected_structure:
            full_path = base_path / dir_path
            if full_path.exists():
                # Contar archivos
                files = list(full_path.glob("*"))
                images = list(full_path.glob("images/*.jpg"))
                self.log(f"✅ {dir_path}: {len(files)} archivos, {len(images)} imágenes")
            else:
                self.log(f"❌ Faltante: {dir_path}", "ERROR")
                missing_dirs.append(dir_path)
                self.errors.append(f"Directorio faltante: {dir_path}")
        
        return len(missing_dirs) == 0
    
    def generate_final_report(self):
        """Generar reporte final"""
        self.log("=== GENERANDO REPORTE FINAL ===")
        
        duration = datetime.now() - self.start_time
        
        report = {
            "test_duration": str(duration),
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "extraction_results": self.extraction_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings)
        }
        
        # Guardar reporte JSON
        with open("test_extraction_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"📊 REPORTE FINAL:")
        self.log(f"   Duración: {duration}")
        self.log(f"   Errores: {len(self.errors)}")
        self.log(f"   Advertencias: {len(self.warnings)}")
        self.log(f"   Extracciones: {len(self.extraction_results)}")
        
        if self.errors:
            self.log("❌ ERRORES ENCONTRADOS:")
            for error in self.errors:
                self.log(f"   - {error}")
        
        if self.warnings:
            self.log("⚠️ ADVERTENCIAS:")
            for warning in self.warnings:
                self.log(f"   - {warning}")
        
        return report
    
    def run_full_test(self):
        """Ejecutar test completo"""
        self.log("🚀 INICIANDO TEST COMPLETO HONDA 360° EXTRACTOR")
        self.log("=" * 60)
        
        # Limpiar log anterior
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        
        try:
            # 1. Verificar servicios
            if not self.check_services():
                self.log("❌ Servicios no disponibles. Abortando test.", "ERROR")
                return False
            
            # 2. Health check backend
            if not self.test_backend_health():
                self.log("❌ Backend no saludable. Abortando test.", "ERROR")
                return False
            
            # 3. Simular extracciones
            test_cases = [
                ("2026", "interior", 0),
                ("2026", "interior", 1), 
                ("2026", "interior", 2),
                ("2026", "exterior", 0),
                ("2026", "exterior", 1),
                ("2026", "exterior", 2)
            ]
            
            successful_extractions = 0
            
            for year, view_type, quality in test_cases:
                self.log(f"\n--- EXTRACCIÓN: {year}/{view_type}/{quality} ---")
                
                # Simular extracción
                extraction_result = self.simulate_user_extraction(year, view_type, quality)
                
                if extraction_result:
                    extraction_id = extraction_result.get("extraction_id")
                    if extraction_id:
                        # Monitorear progreso
                        if self.monitor_extraction_progress(extraction_id):
                            successful_extractions += 1
                            
                            # Probar viewer
                            viewers = self.test_viewer_functionality(year, view_type, quality)
                            if viewers:
                                self.log(f"✅ Viewer funcional para {view_type} calidad {quality}")
                            else:
                                self.log(f"❌ Viewer no funcional para {view_type} calidad {quality}", "ERROR")
                        else:
                            self.log(f"❌ Extracción {extraction_id} no completada", "ERROR")
                    else:
                        self.log(f"❌ No se obtuvo extraction_id", "ERROR")
                else:
                    self.log(f"❌ Extracción falló para {view_type} calidad {quality}", "ERROR")
            
            # 4. Verificar estructura de archivos
            self.check_file_structure("2026")
            
            # 5. Generar reporte final
            report = self.generate_final_report()
            
            self.log("\n" + "=" * 60)
            self.log(f"🎉 TEST COMPLETADO")
            self.log(f"   Extracciones exitosas: {successful_extractions}/{len(test_cases)}")
            self.log(f"   Errores: {len(self.errors)}")
            self.log(f"   Advertencias: {len(self.warnings)}")
            self.log("=" * 60)
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.log(f"💥 Error crítico en test: {str(e)}", "ERROR")
            self.errors.append(f"Error crítico: {str(e)}")
            return False

def main():
    """Función principal"""
    print("🧪 HONDA 360° EXTRACTOR - TEST COMPLETO")
    print("=" * 50)
    print("Simulando extracción de usuario desde frontend")
    print("Monitoreando todos los procesos internos")
    print("=" * 50)
    
    monitor = ExtractionMonitor()
    success = monitor.run_full_test()
    
    if success:
        print("\n✅ TEST COMPLETADO EXITOSAMENTE")
        print("📄 Revisa test_extraction_log.txt para detalles")
        print("📊 Revisa test_extraction_report.json para reporte")
    else:
        print("\n❌ TEST COMPLETADO CON ERRORES")
        print("📄 Revisa test_extraction_log.txt para errores")
        print("📊 Revisa test_extraction_report.json para reporte")
    
    return success

if __name__ == "__main__":
    main()
