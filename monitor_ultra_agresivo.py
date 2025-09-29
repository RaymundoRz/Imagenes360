#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR ULTRA AGRESIVO - HONDA 360°
==================================
Detecta CUALQUIER cambio inmediatamente
"""

import time
import requests
import json
from pathlib import Path
import threading
import os
from datetime import datetime

def log(message):
    """Log con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Con milisegundos
    print(f"[{timestamp}] {message}")

def contar_archivos():
    """Contar archivos rápido"""
    downloads_path = Path("backend/downloads/honda_city_2026")
    if not downloads_path.exists():
        return 0
    
    archivos = list(downloads_path.rglob("*"))
    archivos_solo = [f for f in archivos if f.is_file()]
    return len(archivos_solo)

def verificar_extracciones():
    """Verificar extracciones en backend"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/honda/extractions", timeout=1)
        if response.status_code == 200:
            extractions = response.json()
            return len(extractions), extractions
    except:
        pass
    return 0, []

def main():
    log("MONITOR ULTRA AGRESIVO INICIADO")
    log("Detectando CUALQUIER cambio...")
    
    archivos_anteriores = contar_archivos()
    extracciones_anteriores = 0
    
    log(f"Estado inicial: {archivos_anteriores} archivos")
    
    while True:
        try:
            # Verificar archivos
            archivos_actuales = contar_archivos()
            if archivos_actuales != archivos_anteriores:
                log(f"!!! ARCHIVOS CAMBIARON: {archivos_anteriores} -> {archivos_actuales}")
                archivos_anteriores = archivos_actuales
            
            # Verificar extracciones
            num_extracciones, extracciones = verificar_extracciones()
            if num_extracciones != extracciones_anteriores:
                log(f"!!! EXTRACCIONES CAMBIARON: {extracciones_anteriores} -> {num_extracciones}")
                extracciones_anteriores = num_extracciones
                
                # Mostrar detalles de extracciones
                for ext in extracciones:
                    status = ext.get("status", "unknown")
                    view_type = ext.get("view_type", "unknown")
                    progress = ext.get("progress_percentage", 0)
                    downloaded = ext.get("downloaded_tiles", 0)
                    total = ext.get("total_tiles", 0)
                    
                    log(f"    EXTRACCIÓN: {view_type} - {status} - {progress:.1f}% ({downloaded}/{total})")
            
            # Si hay extracciones activas, mostrar progreso
            for ext in extracciones:
                if ext.get("status") == "in_progress":
                    view_type = ext.get("view_type", "unknown")
                    progress = ext.get("progress_percentage", 0)
                    downloaded = ext.get("downloaded_tiles", 0)
                    total = ext.get("total_tiles", 0)
                    log(f">>> PROGRESO {view_type}: {progress:.1f}% ({downloaded}/{total})")
            
            time.sleep(0.1)  # Verificar cada 100ms
            
        except KeyboardInterrupt:
            log("MONITOR DETENIDO")
            break
        except Exception as e:
            log(f"ERROR: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    main()








