#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR OBSERVADOR INTELIGENTE
==============================
Solo observa - NO inicia nada automáticamente
"""

import requests
import time
from pathlib import Path
from datetime import datetime

def verificar_servicios():
    """Verificar servicios básicos"""
    servicios = {}
    
    # Backend
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        servicios["Backend"] = "OK" if response.status_code == 200 else f"HTTP {response.status_code}"
    except:
        servicios["Backend"] = "ERROR"
    
    # Frontend  
    try:
        response = requests.get("http://127.0.0.1:5174", timeout=2)
        servicios["Frontend"] = "OK" if response.status_code in [200, 404] else f"HTTP {response.status_code}"
    except:
        servicios["Frontend"] = "ERROR"
    
    return servicios

def obtener_extracciones():
    """Obtener extracciones sin errores"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/honda/extractions", timeout=3)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def contar_archivos():
    """Contar archivos descargados"""
    downloads_path = Path("backend/downloads")
    if not downloads_path.exists():
        return 0, None
    
    honda_folders = list(downloads_path.glob("honda_city_*"))
    total_archivos = 0
    ultima_modificacion = None
    
    for folder in honda_folders:
        if folder.is_dir():
            archivos = list(folder.glob("**/*.*"))
            total_archivos += len(archivos)
            
            for archivo in archivos:
                if archivo.is_file():
                    mtime = datetime.fromtimestamp(archivo.stat().st_mtime)
                    if ultima_modificacion is None or mtime > ultima_modificacion:
                        ultima_modificacion = mtime
    
    return total_archivos, ultima_modificacion

def main():
    """Monitor principal"""
    print("MONITOR OBSERVADOR HONDA")
    print("="*60)
    print("Solo observa - NO inicia extracciones automáticamente")
    print("Inicia tu descarga desde el frontend")
    print("="*60)
    print("Presiona Ctrl+C para detener\n")
    
    extracciones_anteriores = []
    ciclo = 0
    
    try:
        while True:
            ciclo += 1
            
            servicios = verificar_servicios()
            extracciones = obtener_extracciones()
            total_archivos, ultima_mod = contar_archivos()
            
            # Detectar nuevas extracciones
            if len(extracciones) > len(extracciones_anteriores):
                print(f"🚨 NUEVA EXTRACCIÓN DETECTADA!")
            
            print(f"\n[CICLO {ciclo}] {datetime.now().strftime('%H:%M:%S')}")
            print(f"Servicios: Backend={servicios['Backend']}, Frontend={servicios['Frontend']}")
            print(f"Extracciones: {len(extracciones)}")
            
            if extracciones:
                for ext in extracciones:
                    status = ext.get('status', 'unknown')
                    progress = ext.get('progress_percentage', 0)
                    downloaded = ext.get('downloaded_tiles', 0)
                    total = ext.get('total_tiles', 0)
                    view_type = ext.get('view_type', 'N/A')
                    
                    print(f"  └─ {view_type} {status} - {progress:.1f}% ({downloaded}/{total})")
            
            print(f"Archivos: {total_archivos}")
            if ultima_mod:
                print(f"Última modificación: {ultima_mod.strftime('%H:%M:%S')}")
            
            extracciones_anteriores = extracciones.copy()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\n✋ Monitor detenido correctamente")

if __name__ == "__main__":
    main()








