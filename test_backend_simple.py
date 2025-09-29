#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST BACKEND SIMPLE - Verificar si el backend responde
"""

import requests
import time

def test_backend():
    print("🧪 PROBANDO BACKEND SIMPLE")
    print("=" * 40)
    
    try:
        print("⏳ Enviando request a backend...")
        start_time = time.time()
        
        response = requests.get('http://127.0.0.1:8000/health', timeout=30)
        
        duration = time.time() - start_time
        
        print(f"✅ ÉXITO!")
        print(f"   Status: {response.status_code}")
        print(f"   Tiempo: {duration:.2f}s")
        print(f"   Respuesta: {response.text}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Backend no responde en 30s")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Backend no acepta conexiones")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_backend()
    print("\n" + "=" * 40)
    if success:
        print("🎉 Backend funciona correctamente")
    else:
        print("💥 Backend tiene problemas")
    print("=" * 40)



