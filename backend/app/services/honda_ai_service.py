"""
Honda AI Service - Servicio Principal Integrado
Sistema híbrido: Knowledge Base + IA + Validación + Auto-aprendizaje
"""

import os
from typing import Dict
from datetime import datetime
from .ai_inference import AIInferenceEngine
from .url_validator import URLValidator
from .learning_engine import LearningEngine

class HondaAIService:
    """
    Servicio principal que integra todo el sistema inteligente
    """
    
    def __init__(self, knowledge_base_path: str, gemini_api_key: str = None):
        """
        Inicializa el servicio completo
        
        Args:
            knowledge_base_path: Ruta a knowledge_base.json
            gemini_api_key: API key de Gemini (opcional, usa env var si no se proporciona)
        """
        if gemini_api_key:
            os.environ['GEMINI_API_KEY'] = gemini_api_key
        
        self.ai_engine = AIInferenceEngine(knowledge_base_path)
        self.validator = URLValidator()
        self.learning_engine = LearningEngine(knowledge_base_path)
    
    def get_360_url(self, model_slug: str, year: str, view_type: str = "exterior") -> Dict:
        """
        Obtiene URL 360° de forma inteligente con auto-aprendizaje
        
        FLUJO:
        1. Busca en knowledge base (instantáneo)
        2. Si no existe, usa IA para predecir
        3. Valida predicciones automáticamente
        4. Aprende de URLs válidas
        
        Args:
            model_slug: Slug del modelo (ej: "cr-v-hibrido")
            year: Año del modelo (ej: "2025")
            view_type: "exterior" o "interior"
        
        Returns:
            Dict con resultado completo
        """
        
        result = {
            "model": model_slug,
            "year": year,
            "view_type": view_type,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "method_used": None,
            "url": None,
            "confidence": 0.0
        }
        
        print(f"\nBuscando URL para: {model_slug} {year} {view_type}")
        
        # CAPA 1: Knowledge Base (0ms)
        print("   [CAPA 1] Knowledge base...")
        predictions = self.ai_engine.predict_url(model_slug, year, view_type)
        
        if predictions and predictions[0].get("source") == "knowledge_base":
            print("   Encontrado en KB (instantaneo)")
            result["success"] = True
            result["method_used"] = "knowledge_base"
            result["url"] = predictions[0]["url"]
            result["tiles_base"] = predictions[0].get("tiles_base")
            result["confidence"] = 1.0
            result["verified"] = True
            return result
        
        # CAPA 2: IA Inference (1-2 seg)
        print("   [CAPA 2] No encontrado. Consultando IA...")
        
        if not predictions:
            result["error"] = "IA no pudo generar predicciones"
            return result
        
        print(f"   IA genero {len(predictions)} predicciones")
        
        # CAPA 3: Validación Automática (0.5 seg por URL)
        print("   [CAPA 3] Validando predicciones...")
        validated = self.validator.validate_predictions(predictions)
        
        if not validated:
            print("   Ninguna URL valida encontrada")
            result["error"] = "No se encontraron URLs válidas"
            result["tried_urls"] = [p["viewer_url"] for p in predictions]
            return result
        
        # Tomar la mejor
        best = validated[0]
        
        print(f"   URL valida encontrada!")
        print(f"   {best['viewer_url']}")
        
        # CAPA 4: Auto-Aprendizaje
        print("   [CAPA 4] Aprendiendo...")
        learned = self.learning_engine.learn_from_validated_url(
            model_slug, year, view_type, best
        )
        
        if learned:
            print("   Aprendido! Proxima vez sera instantaneo")
        
        result["success"] = True
        result["method_used"] = "ai_validation"
        result["url"] = best["viewer_url"]
        result["tiles_base"] = best.get("tiles_base")
        result["folder_name"] = best.get("folder_name")
        result["confidence"] = best.get("confidence", 0.0)
        result["verified"] = True
        result["learned"] = learned
        
        return result
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del sistema completo"""
        return {
            "learning_engine": self.learning_engine.get_stats(),
            "timestamp": datetime.now().isoformat()
        }


# EJEMPLO DE USO:
if __name__ == "__main__":
    import os
    
    # Inicializar
    service = HondaAIService(
        knowledge_base_path="backend/database/knowledge_base.json",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Buscar URL
    result = service.get_360_url("pilot", "2025", "exterior")
    
    if result["success"]:
        print(f"\n✅ URL: {result['url']}")
        print(f"   Método: {result['method_used']}")
        print(f"   Confianza: {result['confidence']*100}%")
    else:
        print(f"\n❌ No encontrada: {result.get('error')}")
