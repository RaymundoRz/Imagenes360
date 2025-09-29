#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DE EXTRACCION FINAL CORREGIDA
==================================
Prueba que la extracción funcione correctamente después de las correcciones
"""

import requests
import json
import time

def test_extraccion():
    print("PROBANDO EXTRACCION FINAL CORREGIDA")
    print("="*50)
    
    # Datos para la extracción
    data = {
        "year": "2026",
        "view_type": "interior", 
        "quality_level": 0
    }
    
    # Paso 1: Iniciar extracción
    print("Paso 1: Iniciando extracción...")
    response = requests.post("http://127.0.0.1:8000/api/honda/extract", json=data)
    
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    extraction_id = result["extraction_id"]
    print(f"Extracción iniciada: {extraction_id}")
    
    # Paso 2: Monitorear progreso
    print("\nPaso 2: Monitoreando progreso...")
    
    for i in range(15):  # Máximo 15 segundos
        time.sleep(1)
        
        # Obtener estado
        status_response = requests.get(f"http://127.0.0.1:8000/api/honda/extract/{extraction_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            
            estado = status["status"]
            progreso = status["progress_percentage"]
            descargados = status["downloaded_tiles"]
            total = status["total_tiles"]
            fallidos = status["failed_tiles"]
            
            print(f"[{i+1:2d}s] {estado} - {progreso:.1f}% ({descargados}+{fallidos}/{total})")
            
            # Si terminó
            if estado in ["completed", "failed"]:
                print(f"\nFINALIZADO: {estado}")
                
                if "error_message" in status and status["error_message"]:
                    print(f"Error: {status['error_message']}")
                
                if estado == "completed":
                    print("[EXITO] Extracción completada correctamente!")
                    return True
                else:
                    print("[FALLO] Extracción falló")
                    return False
        else:
            print(f"[ERROR] No se pudo obtener estado: {status_response.status_code}")
    
    print("\n[TIMEOUT] Extracción tomó demasiado tiempo")
    return False

if __name__ == "__main__":
    success = test_extraccion()
    print(f"\nResultado final: {'EXITO' if success else 'FALLO'}")








