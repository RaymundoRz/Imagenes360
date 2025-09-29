#!/usr/bin/env python3
"""
🕵️ DETECTIVE HONDA - DESCUBRIR POR QUÉ NOS BLOQUEAN
Analizar qué está pasando con el acceso a Honda
"""

import requests
import time
import json
from urllib.parse import urlparse
import socket

def test_basic_connectivity():
    """Probar conectividad básica"""
    print("🌐 PROBANDO CONECTIVIDAD BÁSICA...")
    
    test_sites = [
        "https://www.google.com",
        "https://www.honda.mx",
        "https://www.honda.com", 
        "https://automobiles.honda.com"
    ]
    
    for site in test_sites:
        try:
            response = requests.get(site, timeout=5)
            print(f"✅ {site}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {site}: {str(e)}")

def test_honda_main_pages():
    """Probar páginas principales de Honda"""
    print("\n🏠 PROBANDO PÁGINAS PRINCIPALES HONDA...")
    
    honda_pages = [
        "https://www.honda.mx",
        "https://www.honda.mx/autos",
        "https://www.honda.mx/autos/city",
        "https://www.honda.mx/autos/city/2024",
        "https://www.honda.mx/autos/city/2026"
    ]
    
    for page in honda_pages:
        try:
            response = requests.get(page, timeout=10)
            print(f"✅ {page}: HTTP {response.status_code}")
            
            # Buscar referencias a 360 en el HTML
            if "360" in response.text:
                print(f"   🎯 CONTIENE '360' en el HTML")
                
        except Exception as e:
            print(f"❌ {page}: {str(e)}")

def test_different_headers():
    """Probar diferentes User-Agents y headers"""
    print("\n🕴️ PROBANDO DIFERENTES USER-AGENTS...")
    
    test_url = "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/tiles/node1/cf_0/l_2/c_0/tile_0.jpg"
    
    user_agents = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # Firefox Windows  
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        
        # Safari Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        
        # Mobile Chrome
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        
        # Sin User-Agent
        ""
    ]
    
    for i, ua in enumerate(user_agents):
        try:
            headers = {
                'User-Agent': ua,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.honda.mx/autos/city/2026',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
            if ua == "":
                headers = {}  # Sin headers
                
            response = requests.get(test_url, headers=headers, timeout=10)
            ua_name = f"User-Agent {i+1}" if ua else "Sin User-Agent"
            
            if response.status_code == 200:
                print(f"✅ {ua_name}: HTTP {response.status_code} ({len(response.content)} bytes)")
                return True  # FOUND WORKING HEADER
            else:
                print(f"❌ {ua_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"💥 {ua_name}: {str(e)}")
        
        time.sleep(1)  # Pausa entre requests
    
    return False

def test_with_session():
    """Probar con sesión persistente simulando navegador real"""
    print("\n🍪 PROBANDO CON SESIÓN COMPLETA (COOKIES, etc)...")
    
    session = requests.Session()
    
    # PASO 1: Visitar página principal para obtener cookies
    try:
        print("1️⃣ Visitando página principal Honda...")
        main_response = session.get("https://www.honda.mx/autos/city/2026", timeout=10)
        print(f"   📊 HTTP {main_response.status_code}")
        print(f"   🍪 Cookies recibidas: {len(session.cookies)}")
        
        # PASO 2: Intentar acceder a imagen con cookies
        print("2️⃣ Intentando acceso a imagen con cookies...")
        test_url = "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/tiles/node1/cf_0/l_2/c_0/tile_0.jpg"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.honda.mx/autos/city/2026',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        
        img_response = session.get(test_url, headers=headers, timeout=10)
        
        if img_response.status_code == 200:
            print(f"✅ CON SESIÓN: HTTP {img_response.status_code} ({len(img_response.content)} bytes)")
            return True
        else:
            print(f"❌ CON SESIÓN: HTTP {img_response.status_code}")
            
    except Exception as e:
        print(f"💥 ERROR EN SESIÓN: {str(e)}")
    
    return False

def check_ip_status():
    """Verificar si nuestra IP está bloqueada"""
    print("\n🌍 VERIFICANDO STATUS DE IP...")
    
    try:
        # Obtener IP pública
        ip_response = requests.get("https://httpbin.org/ip", timeout=5)
        public_ip = ip_response.json()["origin"]
        print(f"📍 IP Pública: {public_ip}")
        
        # Probar desde diferentes servicios
        test_services = [
            "https://httpbin.org/get",
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://api.github.com"
        ]
        
        print("🔬 Probando otros servicios...")
        for service in test_services:
            try:
                response = requests.get(service, timeout=5)
                print(f"✅ {service}: HTTP {response.status_code}")
            except:
                print(f"❌ {service}: Error")
                
    except Exception as e:
        print(f"💥 Error verificando IP: {str(e)}")

def analyze_response_headers():
    """Analizar headers de respuesta de Honda"""
    print("\n📋 ANALIZANDO HEADERS DE RESPUESTA...")
    
    test_urls = [
        "https://www.honda.mx",
        "https://www.honda.mx/autos/city/2026",
        "https://www.honda.mx/web/img/cars/models/city/2026/city_2026_int_360/tiles/node1/cf_0/l_2/c_0/tile_0.jpg"
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔍 Analizando: {url}")
            response = requests.get(url, timeout=10)
            
            print(f"   📊 Status: {response.status_code}")
            
            # Headers importantes
            important_headers = [
                'Server', 'X-Rate-Limit', 'X-Blocked', 'CF-Ray', 
                'X-Forwarded-For', 'Set-Cookie', 'WWW-Authenticate',
                'X-Frame-Options', 'X-Content-Type-Options'
            ]
            
            for header in important_headers:
                if header in response.headers:
                    print(f"   🏷️ {header}: {response.headers[header]}")
                    
        except Exception as e:
            print(f"💥 Error analizando {url}: {str(e)}")

def main():
    print("🕵️ DETECTIVE HONDA - ANÁLISIS DE BLOQUEO")
    print("=" * 60)
    
    # BATERÍA DE PRUEBAS
    test_basic_connectivity()
    test_honda_main_pages()
    check_ip_status()
    analyze_response_headers()
    
    print("\n" + "="*60)
    print("🧪 PROBANDO EVASIÓN DE BLOQUEOS...")
    
    # Probar diferentes estrategias
    strategies = [
        ("User-Agents", test_different_headers),
        ("Sesión completa", test_with_session)
    ]
    
    working_strategy = None
    
    for strategy_name, strategy_func in strategies:
        print(f"\n🎯 ESTRATEGIA: {strategy_name}")
        if strategy_func():
            working_strategy = strategy_name
            break
        print(f"❌ {strategy_name} FALLÓ")
    
    print("\n" + "="*60)
    print("🏆 DIAGNÓSTICO FINAL:")
    
    if working_strategy:
        print(f"✅ ESTRATEGIA EXITOSA: {working_strategy}")
        print("🔧 RECOMENDACIÓN: Implementar esta estrategia en el extractor")
    else:
        print("❌ TODAS LAS ESTRATEGIAS FALLARON")
        print("🚨 POSIBLES CAUSAS:")
        print("   • IP bloqueada por requests masivos")
        print("   • Geoblocking (país/región)")
        print("   • Rate limiting agresivo")
        print("   • Detección de bots")
        print("   • Cambio en la estructura de Honda")

if __name__ == "__main__":
    main()








