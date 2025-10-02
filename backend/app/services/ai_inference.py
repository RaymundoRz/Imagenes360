"""
Motor de Inferencia con IA usando GEMINI (GRATIS)
Predice URLs usando Gemini cuando no existen en knowledge base
"""

import json
import os
from typing import List, Dict
import google.generativeai as genai

class AIInferenceEngine:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_kb()
        
        # Configurar Gemini (versión simplificada)
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Error configurando Gemini: {e}")
                self.model = None
        else:
            self.model = None
    
    def _load_kb(self) -> dict:
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def predict_url(self, model_slug: str, year: str, view_type: str = "exterior") -> List[Dict]:
        # PASO 1: Buscar en knowledge base
        if model_slug in self.knowledge_base.get("models", {}):
            model_data = self.knowledge_base["models"][model_slug]
            if year in model_data.get("verified_years", {}):
                verified = model_data["verified_years"][year].get(view_type)
                if verified:
                    return [{
                        "url": verified["viewer_url"],
                        "tiles_base": verified["tiles_base"],
                        "folder_name": verified["folder_name"],
                        "confidence": 1.0,
                        "source": "knowledge_base",
                        "verified": True
                    }]
        
        # PASO 2: Usar IA para predecir
        context = self._prepare_context(model_slug, year)
        predictions = self._ask_gemini(model_slug, year, view_type, context)
        return predictions
    
    def _prepare_context(self, model_slug: str, year: str) -> dict:
        context = {
            "target_model": model_slug,
            "target_year": year,
            "same_model_other_years": [],
            "similar_models": []
        }
        
        # Datos del mismo modelo en otros años
        if model_slug in self.knowledge_base.get("models", {}):
            model_data = self.knowledge_base["models"][model_slug]
            for yr, data in model_data.get("verified_years", {}).items():
                if "exterior" in data:
                    context["same_model_other_years"].append({
                        "year": yr,
                        "folder_name": data["exterior"]["folder_name"],
                        "viewer_url": data["exterior"]["viewer_url"],
                        "tiles_base": data["exterior"]["tiles_base"]
                    })
        
        # Otros modelos similares
        for slug, data in self.knowledge_base.get("models", {}).items():
            if slug != model_slug:
                for yr, yr_data in data.get("verified_years", {}).items():
                    if "exterior" in yr_data:
                        context["similar_models"].append({
                            "model": slug,
                            "year": yr,
                            "folder_name": yr_data["exterior"]["folder_name"]
                        })
                        if len(context["similar_models"]) >= 5:
                            break
        
        return context
    
    def _ask_gemini(self, model_slug: str, year: str, view_type: str, context: dict) -> List[Dict]:
        if not self.model:
            print("ERROR: Gemini no configurado (falta GEMINI_API_KEY)")
            return []
        
        prompt = f"""Eres experto en URLs de Honda México. Predice URLs 360° para:
- Modelo: {model_slug}
- Año: {year}
- Tipo: {view_type}

EJEMPLOS DEL MISMO MODELO:
{json.dumps(context["same_model_other_years"], indent=2)}

EJEMPLOS DE OTROS MODELOS:
{json.dumps(context["similar_models"], indent=2)}

REGLAS:
1. folder_name varía: PascalCase, lowercase, UPPERCASE
2. Algunos tienen /360/ en el path
3. pilot usa "honda_pilot_black" en URL pero "PILOT_BLACK" en folder

GENERA 3 URLS candidatas. RESPONDE SOLO JSON VÁLIDO (sin markdown, sin explicaciones):
[
  {{
    "folder_name": "CR-V_2025_ext_360",
    "viewer_url": "https://www.honda.mx/autos/cr-v/CR-V_2025_ext_360",
    "tiles_base": "https://www.honda.mx/web/img/cars/models/crv/2025/CR-V_2025_ext_360/tiles/",
    "confidence": 0.9,
    "reasoning": "Sigue pattern de 2023"
  }}
]"""

        try:
            response = self.model.generate_content(prompt)
            ai_response = response.text.strip()
            
            # Limpiar markdown si existe
            if "```" in ai_response:
                ai_response = ai_response.split("```")[1]
                if ai_response.startswith("json"):
                    ai_response = ai_response[4:]
            
            predictions = json.loads(ai_response)
            
            for pred in predictions:
                pred["source"] = "ai_inference"
                pred["verified"] = False
            
            return predictions
            
        except Exception as e:
            print(f"ERROR: Error en Gemini: {e}")
            return []
