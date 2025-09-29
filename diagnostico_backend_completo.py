#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNOSTICO BACKEND COMPLETO
============================
Encuentra exactamente por que fallan las extracciones
"""

import requests
import json
import time
from datetime import datetime

def probar_endpoint_directo():
    """Probar el endpoint de extracción directamente"""
    print("PASO 1: PROBANDO ENDPOINT DE EXTRACCION DIRECTO")
    print("="*60)
    
    url = "http://127.0.0.1:8000/api/honda/extract"
    data = {
        "year": "2026",
        "view_type": "interior",
        "quality_level": 0
    }
    
    try:
        print(f"Enviando POST a: {url}")
        print(f"Datos: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"\nRESPUESTA:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.text:
            try:
                response_json = response.json()
                print(f"JSON Response:")
                print(json.dumps(response_json, indent=2))
                return response_json
            except:
                print(f"Text Response: {response.text}")
                return {"error": "Invalid JSON", "text": response.text}
        else:
            print("Empty response")
            return {"error": "Empty response"}
            
    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}

def obtener_detalles_extraccion(extraction_id):
    """Obtener detalles de una extracción específica"""
    print(f"\nPASO 2: OBTENIENDO DETALLES DE EXTRACCION {extraction_id}")
    print("="*60)
    
    url = f"http://127.0.0.1:8000/api/honda/extract/{extraction_id}"
    
    try:
        response = requests.get(url, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            details = response.json()
            print("DETALLES DE LA EXTRACCION:")
            print(json.dumps(details, indent=2))
            return details
        else:
            print(f"Error obteniendo detalles: {response.text}")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def probar_urls_honda_manualmente():
    """Probar las URLs de Honda manualmente"""
    print(f"\nPASO 3: PROBANDO URLs DE HONDA MANUALMENTE")
    print("="*60)
    
    test_urls = [
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/config.xml",
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/tiles/node1/cf_0/l_0/c_0/tile_0.jpg",
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_ext_360/tiles/c0_l0_0_0.jpg"
    ]
    
    for url in test_urls:
        try:
            print(f"Probando: {url}")
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Tamaño: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print(f"  OK - Funciona")
            else:
                print(f"  ERROR - No funciona")
                
        except Exception as e:
            print(f"  EXCEPCION: {e}")
        
        print()

def verificar_dependencias():
    """Verificar que todas las dependencias están instaladas"""
    print(f"\nPASO 4: VERIFICANDO DEPENDENCIAS")
    print("="*60)
    
    dependencias_criticas = [
        "requests", "fastapi", "uvicorn", "pathlib", 
        "datetime", "uuid", "json", "asyncio"
    ]
    
    for dep in dependencias_criticas:
        try:
            __import__(dep)
            print(f"✓ {dep}: OK")
        except ImportError:
            print(f"✗ {dep}: FALTA - pip install {dep}")

def main():
    """Diagnóstico completo"""
    print("DIAGNOSTICO BACKEND COMPLETO")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print("="*80)
    
    # Paso 1: Probar endpoint
    resultado = probar_endpoint_directo()
    
    # Paso 2: Si tenemos extraction_id, obtener detalles
    if isinstance(resultado, dict) and "extraction_id" in resultado:
        extraction_id = resultado["extraction_id"]
        detalles = obtener_detalles_extraccion(extraction_id)
        
        # Esperar un poco para que se ejecute
        print("\nEsperando 3 segundos para que se ejecute...")
        time.sleep(3)
        
        # Obtener detalles actualizados
        detalles_finales = obtener_detalles_extraccion(extraction_id)
    
    # Paso 3: Probar URLs manualmente
    probar_urls_honda_manualmente()
    
    # Paso 4: Verificar dependencias
    verificar_dependencias()
    
    print("\n" + "="*80)
    print("DIAGNOSTICO COMPLETADO")
    print("="*80)
    print("Revisa los resultados arriba para identificar el problema")

if __name__ == "__main__":
    main()








