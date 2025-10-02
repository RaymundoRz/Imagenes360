"""
Motor de Auto-Aprendizaje
Aprende de URLs validadas y actualiza automáticamente el knowledge base
"""

import json
import os
from typing import Dict
from datetime import datetime
from pathlib import Path

class LearningEngine:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_kb()
    
    def _load_kb(self) -> dict:
        if not os.path.exists(self.knowledge_base_path):
            return self._create_initial_kb()
        
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_initial_kb(self) -> dict:
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0",
                "total_models": 0
            },
            "models": {},
            "global_patterns": {"naming_conventions": {}},
            "learning_stats": {"total_verified_urls": 0, "success_rate": 0.0}
        }
    
    def _save_kb(self):
        """Guarda knowledge base actualizado"""
        Path(self.knowledge_base_path).parent.mkdir(parents=True, exist_ok=True)
        self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
        
        print(f"Knowledge base actualizado")
    
    def learn_from_validated_url(self, model_slug: str, year: str, view_type: str, validated_data: Dict) -> bool:
        """Aprende de una URL validada y actualiza el knowledge base"""
        
        # Verificar si ya existe
        if model_slug in self.knowledge_base.get("models", {}):
            model_data = self.knowledge_base["models"][model_slug]
            if year in model_data.get("verified_years", {}):
                if view_type in model_data["verified_years"][year]:
                    print(f"ℹ️  {model_slug} {year} {view_type} ya existe")
                    return False
        
        # Crear estructura del modelo si no existe
        if model_slug not in self.knowledge_base["models"]:
            self.knowledge_base["models"][model_slug] = {
                "display_name": model_slug.replace('-', ' ').title(),
                "slug": model_slug,
                "folder_slug": self._infer_folder_slug(validated_data.get("folder_name", "")),
                "verified_years": {},
                "pattern_rules": {}
            }
        
        model_data = self.knowledge_base["models"][model_slug]
        
        # Crear año si no existe
        if year not in model_data["verified_years"]:
            model_data["verified_years"][year] = {}
        
        # Agregar datos validados
        model_data["verified_years"][year][view_type] = {
            "viewer_url": validated_data.get("viewer_url"),
            "tiles_base": validated_data.get("tiles_base"),
            "folder_name": validated_data.get("folder_name"),
            "naming_pattern": self._detect_naming_pattern(validated_data.get("folder_name", "")),
            "has_360_subfolder": "/360/" in validated_data.get("tiles_base", ""),
            "verified_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "verified",
            "learned_from_ai": validated_data.get("source") == "ai_inference",
            "confidence": validated_data.get("confidence", 1.0)
        }
        
        # Actualizar pattern rules
        if not model_data.get("pattern_rules"):
            model_data["pattern_rules"] = self._infer_pattern_rules(
                model_slug,
                validated_data.get("folder_name", ""),
                validated_data.get("tiles_base", "")
            )
        
        # Actualizar estadísticas
        self.knowledge_base["learning_stats"]["total_verified_urls"] += 1
        self.knowledge_base["metadata"]["total_models"] = len(self.knowledge_base["models"])
        
        # Guardar
        self._save_kb()
        
        print(f"APRENDIDO: {model_slug} {year} {view_type}")
        print(f"   URL: {validated_data.get('viewer_url')}")
        print(f"   Confianza: {validated_data.get('confidence', 1.0)*100}%")
        
        return True
    
    def _infer_folder_slug(self, folder_name: str) -> str:
        """Infiere folder slug desde folder name"""
        parts = folder_name.lower().replace('_', '-').split('-')
        cleaned = [p for p in parts if not p.isdigit() and p not in ['ext', 'int', '360', 'exterior', 'interior']]
        return '-'.join(cleaned)
    
    def _detect_naming_pattern(self, folder_name: str) -> str:
        """Detecta patrón de nomenclatura"""
        if not folder_name:
            return "unknown"
        
        if folder_name[0].isupper() and '_' in folder_name and '-' in folder_name:
            return "UPPERCASE_with_hyphens"
        elif folder_name[0].isupper() and '_' in folder_name:
            return "PascalCase_with_underscores" if any(c.islower() for c in folder_name) else "UPPERCASE_with_underscores"
        elif folder_name[0].islower() and '_' in folder_name:
            return "lowercase_with_underscores"
        elif folder_name in ["exterior_360", "interior_360"]:
            return "generic_folder"
        else:
            return "custom"
    
    def _infer_pattern_rules(self, model_slug: str, folder_name: str, tiles_base: str) -> dict:
        """Infiere reglas de patrón"""
        return {
            "naming": folder_name.replace(folder_name.split('_')[-3], "{year}") if folder_name else "unknown",
            "path_structure": tiles_base.replace(folder_name, "{folder_name}") if tiles_base else "unknown",
            "confidence": "medium",
            "learned_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas de aprendizaje"""
        stats = self.knowledge_base.get("learning_stats", {})
        stats["total_models"] = len(self.knowledge_base.get("models", {}))
        return stats
