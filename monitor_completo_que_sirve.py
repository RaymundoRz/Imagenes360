#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR COMPLETO QUE SIRVE - HONDA 360°
======================================
Detecta TODOS los procesos y cambios en tiempo real
"""

import time
import requests
import json
from pathlib import Path
import threading
import os
from datetime import datetime
import subprocess
import sys

class MonitorCompleto:
    def __init__(self):
        self.frontend_url = "http://localhost:5174"
        self.backend_url = "http://127.0.0.1:8000"
        self.file_server_url = "http://127.0.0.1:8080"
        self.downloads_path = Path("backend/downloads/honda_city_2026")
        self.monitoring = True
        
        # Estados para detectar cambios
        self.archivos_count = 0
        self.extracciones_activas = {}
        self.ultima_actividad = time.time()
        
    def log(self, message, tipo="INFO"):
        """Log con timestamp y tipo"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        if tipo == "CAMBIO":
            print(f"[{timestamp}] 🔄 {message}")
        elif tipo == "ERROR":
            print(f"[{timestamp}] ❌ {message}")
        elif tipo == "SUCCESS":
            print(f"[{timestamp}] ✅ {message}")
        elif tipo == "PROCESO":
            print(f"[{timestamp}] 🚀 {message}")
        else:
            print(f"[{timestamp}] ℹ️  {message}")
    
    def verificar_servicios(self):
        """Verificar todos los servicios"""
        self.log("=== VERIFICANDO SERVICIOS ===")
        servicios_ok = 0
        
        # Frontend
        try:
            response = requests.get(self.frontend_url, timeout=2)
            self.log(f"Frontend (5174): OK - HTTP {response.status_code}", "SUCCESS")
            servicios_ok += 1
        except:
            self.log("Frontend (5174): NO DISPONIBLE", "ERROR")
        
        # Backend
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            self.log(f"Backend (8000): OK - HTTP {response.status_code}", "SUCCESS")
            servicios_ok += 1
        except:
            self.log("Backend (8000): NO DISPONIBLE", "ERROR")
        
        # File Server
        try:
            response = requests.get(self.file_server_url, timeout=2)
            self.log(f"File Server (8080): OK - HTTP {response.status_code}", "SUCCESS")
            servicios_ok += 1
        except:
            self.log("File Server (8080): NO DISPONIBLE", "ERROR")
        
        self.log(f"Servicios funcionando: {servicios_ok}/3")
        return servicios_ok == 3
    
    def contar_archivos_detallado(self):
        """Contar archivos con detalles"""
        if not self.downloads_path.exists():
            return {"total": 0, "jpg": 0, "xml": 0, "html": 0, "js": 0, "json": 0, "por_carpeta": {}}
        
        archivos = list(self.downloads_path.rglob("*"))
        archivos_solo = [f for f in archivos if f.is_file()]
        
        conteo = {
            "total": len(archivos_solo),
            "jpg": len([f for f in archivos_solo if f.suffix.lower() == ".jpg"]),
            "xml": len([f for f in archivos_solo if f.suffix.lower() == ".xml"]),
            "html": len([f for f in archivos_solo if f.suffix.lower() == ".html"]),
            "js": len([f for f in archivos_solo if f.suffix.lower() == ".js"]),
            "json": len([f for f in archivos_solo if f.suffix.lower() == ".json"]),
            "por_carpeta": {}
        }
        
        # Contar por carpeta
        for carpeta in ["ViewType.INTERIOR", "ViewType.EXTERIOR", "honda_original"]:
            carpeta_path = self.downloads_path / carpeta
            if carpeta_path.exists():
                archivos_carpeta = list(carpeta_path.rglob("*"))
                archivos_carpeta_solo = [f for f in archivos_carpeta if f.is_file()]
                conteo["por_carpeta"][carpeta] = len(archivos_carpeta_solo)
            else:
                conteo["por_carpeta"][carpeta] = 0
        
        return conteo
    
    def monitorear_extracciones(self):
        """Monitorear extracciones del backend"""
        try:
            response = requests.get(f"{self.backend_url}/api/honda/extractions", timeout=1)
            if response.status_code == 200:
                extractions = response.json()
                
                for extraction in extractions:
                    ext_id = extraction.get("extraction_id", "unknown")[:8]
                    status = extraction.get("status", "unknown")
                    view_type = extraction.get("view_type", "unknown")
                    progress = extraction.get("progress_percentage", 0)
                    downloaded = extraction.get("downloaded_tiles", 0)
                    total = extraction.get("total_tiles", 0)
                    
                    # Detectar cambios de estado
                    if ext_id not in self.extracciones_activas:
                        self.log(f"NUEVA EXTRACCIÓN DETECTADA: {ext_id} - {view_type}", "PROCESO")
                        self.extracciones_activas[ext_id] = {"status": status, "progress": progress}
                        self.ultima_actividad = time.time()
                    elif self.extracciones_activas[ext_id]["status"] != status:
                        self.log(f"CAMBIO DE ESTADO: {ext_id} - {view_type}: {self.extracciones_activas[ext_id]['status']} → {status}", "CAMBIO")
                        self.extracciones_activas[ext_id]["status"] = status
                        self.ultima_actividad = time.time()
                    elif status == "in_progress" and abs(self.extracciones_activas[ext_id]["progress"] - progress) > 5:
                        self.log(f"PROGRESO: {ext_id} - {view_type}: {progress:.1f}% ({downloaded}/{total})", "PROCESO")
                        self.extracciones_activas[ext_id]["progress"] = progress
                        self.ultima_actividad = time.time()
                
                return len([e for e in extractions if e.get("status") == "in_progress"]) > 0
        except:
            pass
        return False
    
    def monitorear_archivos(self):
        """Monitorear cambios en archivos"""
        conteo_actual = self.contar_archivos_detallado()
        
        if conteo_actual["total"] != self.archivos_count:
            diferencia = conteo_actual["total"] - self.archivos_count
            self.log(f"ARCHIVOS CAMBIARON: +{diferencia} archivos (total: {conteo_actual['total']})", "CAMBIO")
            self.log(f"    JPG: {conteo_actual['jpg']}, XML: {conteo_actual['xml']}, HTML: {conteo_actual['html']}, JS: {conteo_actual['js']}, JSON: {conteo_actual['json']}")
            
            # Mostrar por carpeta
            for carpeta, count in conteo_actual["por_carpeta"].items():
                self.log(f"    {carpeta}: {count} archivos")
            
            self.archivos_count = conteo_actual["total"]
            self.ultima_actividad = time.time()
            return True
        return False
    
    def verificar_endpoints_backend(self):
        """Verificar que todos los endpoints estén funcionando"""
        endpoints = [
            ("/api/honda/extractions", "GET"),
            ("/health", "GET"),
            ("/", "GET")
        ]
        
        for endpoint, method in endpoints:
            try:
                url = f"{self.backend_url}{endpoint}"
                response = requests.get(url, timeout=1)
                # Solo log si hay error
                if response.status_code != 200:
                    self.log(f"Endpoint {endpoint}: HTTP {response.status_code}", "ERROR")
            except:
                self.log(f"Endpoint {endpoint}: NO DISPONIBLE", "ERROR")
    
    def mostrar_resumen_final(self):
        """Mostrar resumen completo final"""
        self.log("=== RESUMEN FINAL COMPLETO ===")
        
        conteo = self.contar_archivos_detallado()
        self.log(f"ARCHIVOS TOTALES: {conteo['total']}")
        self.log(f"  JPG: {conteo['jpg']}")
        self.log(f"  XML: {conteo['xml']}")
        self.log(f"  HTML: {conteo['html']}")
        self.log(f"  JS: {conteo['js']}")
        self.log(f"  JSON: {conteo['json']}")
        
        self.log("POR CARPETA:")
        for carpeta, count in conteo["por_carpeta"].items():
            self.log(f"  {carpeta}: {count} archivos")
        
        # Mostrar extracciones procesadas
        self.log(f"EXTRACCIONES PROCESADAS: {len(self.extracciones_activas)}")
        for ext_id, info in self.extracciones_activas.items():
            self.log(f"  {ext_id}: {info['status']}")
        
        # Verificar estructura esperada
        self.log("VERIFICACIÓN ESTRUCTURA:")
        
        # ViewType.INTERIOR
        interior_path = self.downloads_path / "ViewType.INTERIOR"
        if interior_path.exists():
            images_path = interior_path / "images"
            config_path = interior_path / "config_local.json"
            self.log(f"  ViewType.INTERIOR: ✅")
            self.log(f"    images/: {'✅' if images_path.exists() else '❌'}")
            self.log(f"    config_local.json: {'✅' if config_path.exists() else '❌'}")
        else:
            self.log(f"  ViewType.INTERIOR: ❌")
        
        # ViewType.EXTERIOR
        exterior_path = self.downloads_path / "ViewType.EXTERIOR"
        if exterior_path.exists():
            images_path = exterior_path / "images"
            config_path = exterior_path / "config_local.json"
            self.log(f"  ViewType.EXTERIOR: ✅")
            self.log(f"    images/: {'✅' if images_path.exists() else '❌'}")
            self.log(f"    config_local.json: {'✅' if config_path.exists() else '❌'}")
        else:
            self.log(f"  ViewType.EXTERIOR: ❌")
        
        # honda_original
        honda_orig_path = self.downloads_path / "honda_original"
        if honda_orig_path.exists():
            self.log(f"  honda_original/: ✅")
        else:
            self.log(f"  honda_original/: ❌")
    
    def ejecutar_monitoreo(self):
        """Ejecutar el monitoreo completo"""
        self.log("🚀 MONITOR COMPLETO INICIADO 🚀")
        self.log("=" * 60)
        
        if not self.verificar_servicios():
            self.log("ALGUNOS SERVICIOS NO ESTÁN DISPONIBLES - CONTINUANDO MONITOREO", "ERROR")
        
        # Estado inicial
        self.archivos_count = self.contar_archivos_detallado()["total"]
        self.log(f"ESTADO INICIAL: {self.archivos_count} archivos")
        self.log("👀 MONITOREANDO TODO EN TIEMPO REAL...")
        self.log(f"🌐 Frontend: {self.frontend_url}")
        self.log("⏰ Presiona Ctrl+C para detener")
        self.log("")
        
        contador_ciclos = 0
        try:
            while self.monitoring:
                contador_ciclos += 1
                
                # Monitorear extracciones (prioritario)
                hay_extracciones_activas = self.monitorear_extracciones()
                
                # Monitorear archivos
                hubo_cambio_archivos = self.monitorear_archivos()
                
                # Cada 10 ciclos, verificar endpoints
                if contador_ciclos % 20 == 0:
                    self.verificar_endpoints_backend()
                
                # Si no hay actividad en 10 segundos y hay archivos, mostrar resumen
                tiempo_sin_actividad = time.time() - self.ultima_actividad
                if (not hay_extracciones_activas and 
                    tiempo_sin_actividad > 10 and 
                    self.archivos_count > 0 and 
                    len(self.extracciones_activas) > 0):
                    
                    self.log("🏁 SIN ACTIVIDAD POR 10s - MOSTRANDO RESUMEN FINAL")
                    self.mostrar_resumen_final()
                    break
                
                time.sleep(0.2)  # Monitorear cada 200ms
                
        except KeyboardInterrupt:
            self.log("🛑 MONITOR DETENIDO POR USUARIO")
            self.mostrar_resumen_final()

def main():
    monitor = MonitorCompleto()
    monitor.ejecutar_monitoreo()

if __name__ == "__main__":
    main()








