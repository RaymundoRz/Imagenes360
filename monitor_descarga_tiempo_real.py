#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR DE DESCARGA EN TIEMPO REAL
==================================
Monitorea el progreso de las extracciones Honda en vivo
"""

import requests
import time
import os
from pathlib import Path
import json
from datetime import datetime

def verificar_backend():
    """Verificar si el backend está funcionando"""
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=3)
        if response.status_code == 200:
            print("[OK] Backend funcionando - Puerto 8000")
            return True
        else:
            print(f"[ERROR] Backend responde HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Backend no responde: {e}")
        return False

def monitorear_extracciones_activas():
    """Monitorear todas las extracciones activas"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/honda/extractions", timeout=5)
        if response.status_code == 200:
            extracciones = response.json()
            
            if not extracciones:
                print("[INFO] No hay extracciones activas")
                return False
            
            print(f"\n[MONITOR] Extracciones activas: {len(extracciones)}")
            print("=" * 80)
            
            hay_activas = False
            for extraccion in extracciones:
                status = extraccion.get('status', 'unknown')
                year = extraccion.get('year', 'N/A')
                view_type = extraccion.get('view_type', 'N/A')
                progress = extraccion.get('progress_percentage', 0)
                downloaded = extraccion.get('downloaded_tiles', 0)
                failed = extraccion.get('failed_tiles', 0)
                total = extraccion.get('total_tiles', 0)
                
                print(f"[{status.upper()}] {year} {view_type}")
                print(f"   Progreso: {progress:.1f}% ({downloaded}+{failed}/{total})")
                
                if status in ['pending', 'in_progress']:
                    hay_activas = True
                    print(f"   Estado: ACTIVA - {status}")
                else:
                    print(f"   Estado: {status}")
                
                print("-" * 40)
            
            return hay_activas
            
        else:
            print(f"[ERROR] No se pueden obtener extracciones: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error monitoreando extracciones: {e}")
        return False

def monitorear_archivos():
    """Monitorear cambios en archivos descargados"""
    downloads_path = Path("backend/downloads")
    
    if not downloads_path.exists():
        print("[INFO] Carpeta downloads no existe aún")
        return
    
    # Buscar carpetas honda_city_*
    honda_folders = list(downloads_path.glob("honda_city_*"))
    
    if not honda_folders:
        print("[INFO] No hay carpetas Honda aún")
        return
    
    print(f"\n[ARCHIVOS] Monitoreando {len(honda_folders)} carpetas Honda")
    
    for folder in honda_folders:
        if folder.is_dir():
            # Contar archivos en la carpeta
            jpg_files = list(folder.glob("**/*.jpg"))
            xml_files = list(folder.glob("**/*.xml"))
            html_files = list(folder.glob("**/*.html"))
            
            total_files = len(jpg_files) + len(xml_files) + len(html_files)
            
            if total_files > 0:
                print(f"   {folder.name}: {len(jpg_files)} JPG, {len(xml_files)} XML, {len(html_files)} HTML")
                
                # Mostrar últimos archivos modificados
                all_files = jpg_files + xml_files + html_files
                if all_files:
                    latest_file = max(all_files, key=lambda f: f.stat().st_mtime)
                    mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
                    print(f"      Último: {latest_file.name} ({mtime.strftime('%H:%M:%S')})")

def iniciar_nueva_extraccion():
    """Iniciar una nueva extracción para probar"""
    print("\n" + "=" * 80)
    print("INICIANDO NUEVA EXTRACCIÓN DE PRUEBA")
    print("=" * 80)
    
    # Datos de la extracción
    data = {
        "year": "2026",
        "view_type": "interior",
        "quality_level": 0
    }
    
    try:
        print(f"[INICIO] Enviando petición: {data}")
        response = requests.post("http://127.0.0.1:8000/api/honda/extract", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            extraction_id = result.get('extraction_id', 'unknown')
            print(f"[EXITO] Extracción iniciada - ID: {extraction_id}")
            print(f"[EXITO] Status inicial: {result.get('status', 'unknown')}")
            return extraction_id
        else:
            print(f"[ERROR] Fallo al iniciar extracción: HTTP {response.status_code}")
            print(f"[ERROR] Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error iniciando extracción: {e}")
        return None

def monitor_principal():
    """Función principal del monitor"""
    print("MONITOR DE DESCARGA HONDA EN TIEMPO REAL")
    print("=" * 80)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    # 1. Verificar backend
    if not verificar_backend():
        print("\n[CRITICO] Backend no está funcionando. Inicia el backend primero.")
        print("Comando: cd backend && python -m uvicorn app.main:app --reload")
        return
    
    # 2. Verificar extracciones existentes
    print("\n[PASO 1] Verificando extracciones existentes...")
    hay_activas = monitorear_extracciones_activas()
    
    # 3. Si no hay activas, iniciar una nueva
    if not hay_activas:
        print("\n[PASO 2] No hay extracciones activas. Iniciando nueva...")
        extraction_id = iniciar_nueva_extraccion()
        
        if not extraction_id:
            print("[CRITICO] No se pudo iniciar extracción. Revisar backend.")
            return
    
    # 4. Monitor en tiempo real
    print("\n[PASO 3] Iniciando monitoreo en tiempo real...")
    print("Presiona Ctrl+C para detener")
    print("=" * 80)
    
    try:
        contador = 0
        while True:
            contador += 1
            print(f"\n[CICLO {contador}] {datetime.now().strftime('%H:%M:%S')}")
            
            # Monitorear extracciones
            hay_activas = monitorear_extracciones_activas()
            
            # Monitorear archivos
            monitorear_archivos()
            
            # Si no hay activas y llevamos varios ciclos, salir
            if not hay_activas and contador > 5:
                print("\n[FINALIZADO] No hay extracciones activas. Monitor terminado.")
                break
            
            # Esperar antes del siguiente ciclo
            time.sleep(0.5)  # Monitoreo rápido
            
    except KeyboardInterrupt:
        print("\n\n[DETENIDO] Monitor detenido por usuario")
    except Exception as e:
        print(f"\n[ERROR] Error en monitor: {e}")

if __name__ == "__main__":
    monitor_principal()