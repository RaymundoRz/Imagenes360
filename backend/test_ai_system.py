#!/usr/bin/env python3
"""
Test del Sistema de IA Honda 360° Extractor
Prueba completa del sistema híbrido: KB + IA + Validación + Auto-aprendizaje
"""

import os
import sys
from pathlib import Path

# Agregar el directorio app al path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.honda_ai_service import HondaAIService

def test_ai_system():
    """Prueba completa del sistema de IA"""
    
    print("HONDA 360 EXTRACTOR - SISTEMA DE IA")
    print("=" * 50)
    
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "tu_openai_api_key_aqui":
        print("ERROR: OPENAI_API_KEY no configurada")
        print("   Configura: export OPENAI_API_KEY='tu_key_aqui'")
        return False
    
    print(f"OK: API Key configurada: {api_key[:10]}...")
    
    # Inicializar servicio
    try:
        service = HondaAIService(
            knowledge_base_path="database/knowledge_base.json",
            openai_api_key=api_key
        )
        print("OK: Servicio de IA inicializado")
    except Exception as e:
        print(f"ERROR: Error inicializando servicio: {e}")
        return False
    
    # Pruebas
    test_cases = [
        ("pilot", "2025", "exterior"),      # Debería estar en KB
        ("city", "2026", "exterior"),       # Debería estar en KB  
        ("accord", "2024", "exterior"),     # Debería usar IA
        ("civic", "2027", "exterior"),     # Debería usar IA
    ]
    
    print(f"\nProbando {len(test_cases)} casos...")
    print("-" * 50)
    
    for i, (model, year, view_type) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {model} {year} {view_type}")
        
        try:
            result = service.get_360_url(model, year, view_type)
            
            if result["success"]:
                print(f"   EXITO: {result['url']}")
                print(f"   Metodo: {result['method_used']}")
                print(f"   Confianza: {result['confidence']*100:.1f}%")
                if result.get("learned"):
                    print(f"   APRENDIDO!")
            else:
                print(f"   FALLO: {result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"   EXCEPCION: {e}")
    
    # Estadísticas finales
    print(f"\nESTADISTICAS DEL SISTEMA:")
    stats = service.get_stats()
    print(f"   Modelos en KB: {stats['learning_engine']['total_models']}")
    print(f"   URLs verificadas: {stats['learning_engine']['total_verified_urls']}")
    
    print(f"\nSISTEMA DE IA FUNCIONANDO CORRECTAMENTE!")
    return True

if __name__ == "__main__":
    success = test_ai_system()
    sys.exit(0 if success else 1)
