"""
Test Rápido con Gemini - Sistema Honda AI
"""

import os
import sys

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configurar API key DIRECTAMENTE (para test rápido)
os.environ['GEMINI_API_KEY'] = "AIzaSyAsGo_IOaSZhUb35wpdKQZCIwyFewqR-aE"

from services.honda_ai_service import HondaAIService

def test_quick():
    """Test rápido del sistema completo"""
    
    print("="*70)
    print("  TEST RAPIDO - HONDA AI CON GEMINI")
    print("="*70)
    
    # Inicializar servicio
    service = HondaAIService(
        knowledge_base_path="database/knowledge_base.json",
        gemini_api_key="AIzaSyAsGo_IOaSZhUb35wpdKQZCIwyFewqR-aE"
    )
    
    # TEST 1: Knowledge Base (instantáneo)
    print("\nTEST 1: Modelo en Knowledge Base")
    print("-" * 70)
    result1 = service.get_360_url("pilot", "2025", "exterior")
    
    if result1['success']:
        print(f"EXITO")
        print(f"   Metodo: {result1['method_used']}")
        print(f"   URL: {result1['url']}")
        print(f"   Confianza: {result1['confidence']*100}%")
    else:
        print(f"FALLO: {result1.get('error')}")
    
    # TEST 2: IA Gemini (predecir + validar)
    print("\nTEST 2: Modelo NO en KB (usara Gemini)")
    print("-" * 70)
    print("   Probando: CR-V 2025 (tenemos 2023 en KB)")
    result2 = service.get_360_url("cr-v", "2025", "exterior")
    
    if result2['success']:
        print(f"EXITO")
        print(f"   Metodo: {result2['method_used']}")
        print(f"   URL: {result2['url']}")
        print(f"   Confianza: {result2['confidence']*100}%")
        if result2.get('learned'):
            print(f"   Sistema aprendio! Ahora esta en KB")
    else:
        print(f"FALLO: {result2.get('error')}")
    
    # TEST 3: Verificar aprendizaje
    print("\nTEST 3: Verificar Auto-Aprendizaje")
    print("-" * 70)
    stats = service.get_stats()
    print(f"   Modelos en KB: {stats['learning_engine']['total_models']}")
    print(f"   URLs verificadas: {stats['learning_engine']['total_verified_urls']}")
    
    print("\n" + "="*70)
    print("  TESTS COMPLETADOS")
    print("="*70)

if __name__ == "__main__":
    try:
        test_quick()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

