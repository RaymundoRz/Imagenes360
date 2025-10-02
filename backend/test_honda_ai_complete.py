"""
Test Completo del Sistema Honda AI
Prueba todo el flujo: KB -> IA -> Validación -> Aprendizaje
"""

import os
import sys
from datetime import datetime

# Ajustar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.honda_ai_service import HondaAIService

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def test_knowledge_base_lookup():
    """TEST 1: Búsqueda en Knowledge Base (instantánea)"""
    print_separator("TEST 1: Knowledge Base Lookup")
    
    service = HondaAIService(
        knowledge_base_path="database/knowledge_base.json"
    )
    
    # Modelo que SÍ existe en KB
    result = service.get_360_url("pilot", "2025", "exterior")
    
    print(f"\nRESULTADO:")
    print(f"   Exito: {result['success']}")
    print(f"   Metodo: {result['method_used']}")
    print(f"   URL: {result['url']}")
    print(f"   Confianza: {result['confidence']*100}%")
    print(f"   Timestamp: {result['timestamp']}")
    
    assert result['success'] == True
    assert result['method_used'] == 'knowledge_base'
    assert result['confidence'] == 1.0
    
    print("\nTEST 1 PASADO: KB lookup funciona correctamente")

def test_ai_inference_and_learning():
    """TEST 2: IA + Validación + Aprendizaje"""
    print_separator("TEST 2: IA Inference + Validation + Learning")
    
    # Verificar API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\nADVERTENCIA: GEMINI_API_KEY no configurada")
        print("   Ejecuta: export GEMINI_API_KEY='tu-api-key'")
        print("   Saltando este test...")
        return
    
    service = HondaAIService(
        knowledge_base_path="database/knowledge_base.json",
        gemini_api_key=api_key
    )
    
    # Modelo que NO existe en KB (probará IA)
    # Usamos CR-V 2025 (tenemos 2023 en KB, IA deberá predecir 2025)
    result = service.get_360_url("cr-v", "2025", "exterior")
    
    print(f"\nRESULTADO:")
    print(f"   Exito: {result['success']}")
    print(f"   Metodo: {result['method_used']}")
    
    if result['success']:
        print(f"   URL: {result['url']}")
        print(f"   Confianza: {result['confidence']*100}%")
        print(f"   Aprendido: {result.get('learned', False)}")
        
        if result.get('learned'):
            print("\n   Sistema aprendio! Proxima consulta sera instantanea")
    else:
        print(f"   Error: {result.get('error')}")
        if 'tried_urls' in result:
            print(f"   URLs intentadas:")
            for url in result['tried_urls']:
                print(f"      - {url}")
    
    print("\nTEST 2 COMPLETADO")

def test_multiple_models():
    """TEST 3: Múltiples modelos"""
    print_separator("TEST 3: Múltiples Modelos")
    
    service = HondaAIService(
        knowledge_base_path="database/knowledge_base.json"
    )
    
    test_cases = [
        ("city", "2026", "exterior"),
        ("cr-v-hibrido", "2026", "exterior"),
        ("accord-hibrido", "2024", "exterior"),
    ]
    
    results = []
    
    for model, year, view in test_cases:
        print(f"\nProbando: {model} {year} {view}")
        result = service.get_360_url(model, year, view)
        
        results.append({
            "model": model,
            "year": year,
            "success": result['success'],
            "method": result['method_used'],
            "url": result.get('url', 'N/A')
        })
        
        if result['success']:
            print(f"   OK {result['method_used']}: {result['url'][:50]}...")
        else:
            print(f"   Error: {result.get('error')}")
    
    # Resumen
    print("\nRESUMEN:")
    print(f"   Total: {len(results)}")
    print(f"   Exitosos: {sum(1 for r in results if r['success'])}")
    print(f"   Fallidos: {sum(1 for r in results if not r['success'])}")
    
    print("\nTEST 3 COMPLETADO")

def test_learning_stats():
    """TEST 4: Estadísticas de aprendizaje"""
    print_separator("TEST 4: Learning Stats")
    
    service = HondaAIService(
        knowledge_base_path="database/knowledge_base.json"
    )
    
    stats = service.get_stats()
    
    print("\nESTADISTICAS DEL SISTEMA:")
    print(f"   Total de modelos: {stats['learning_engine']['total_models']}")
    print(f"   URLs verificadas: {stats['learning_engine']['total_verified_urls']}")
    print(f"   Tasa de exito: {stats['learning_engine']['success_rate']}%")
    print(f"   Timestamp: {stats['timestamp']}")
    
    print("\nTEST 4 COMPLETADO")

def run_all_tests():
    """Ejecuta todos los tests"""
    print_separator("INICIANDO TESTS DEL SISTEMA HONDA AI")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Knowledge Base (siempre funciona)
        test_knowledge_base_lookup()
        
        # Test 2: IA (requiere API key)
        test_ai_inference_and_learning()
        
        # Test 3: Múltiples modelos
        test_multiple_models()
        
        # Test 4: Estadísticas
        test_learning_stats()
        
        print_separator("TODOS LOS TESTS COMPLETADOS")
        
    except Exception as e:
        print(f"\nERROR EN TESTS: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
