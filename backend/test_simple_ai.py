"""
Test Simple - Sistema Honda AI (Solo Knowledge Base)
"""

import os
import sys

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.honda_ai_service import HondaAIService

def test_simple():
    """Test simple del sistema (solo Knowledge Base)"""
    
    print("="*70)
    print("  TEST SIMPLE - HONDA AI (SOLO KNOWLEDGE BASE)")
    print("="*70)
    
    # Inicializar servicio (sin IA por ahora)
    service = HondaAIService(
        knowledge_base_path="database/knowledge_base.json"
    )
    
    # TEST 1: Modelos en Knowledge Base
    print("\nTEST 1: Modelos en Knowledge Base")
    print("-" * 70)
    
    test_cases = [
        ("pilot", "2025", "exterior"),
        ("city", "2026", "exterior"),
        ("cr-v-hibrido", "2026", "exterior"),
        ("accord-hibrido", "2024", "exterior"),
    ]
    
    success_count = 0
    
    for model, year, view in test_cases:
        print(f"\nProbando: {model} {year} {view}")
        result = service.get_360_url(model, year, view)
        
        if result['success']:
            print(f"   EXITO: {result['method_used']}")
            print(f"   URL: {result['url'][:60]}...")
            print(f"   Confianza: {result['confidence']*100}%")
            success_count += 1
        else:
            print(f"   FALLO: {result.get('error')}")
    
    # TEST 2: Estadísticas
    print("\nTEST 2: Estadísticas del Sistema")
    print("-" * 70)
    stats = service.get_stats()
    print(f"   Modelos en KB: {stats['learning_engine']['total_models']}")
    print(f"   URLs verificadas: {stats['learning_engine']['total_verified_urls']}")
    print(f"   Tasa de exito: {stats['learning_engine']['success_rate']}%")
    
    # Resumen
    print("\n" + "="*70)
    print(f"  RESUMEN: {success_count}/{len(test_cases)} tests exitosos")
    print("="*70)
    
    if success_count == len(test_cases):
        print("  SISTEMA FUNCIONANDO PERFECTAMENTE")
    else:
        print("  ALGUNOS TESTS FALLARON")

if __name__ == "__main__":
    try:
        test_simple()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
