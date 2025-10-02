"""
Validador de URLs
Verifica automáticamente si las URLs predichas funcionan
"""

import requests
from typing import List, Dict

class URLValidator:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def validate_url(self, url: str) -> Dict:
        """Valida una URL con HEAD request"""
        result = {
            "url": url,
            "valid": False,
            "status_code": None,
            "exists": False
        }
        
        try:
            response = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["valid"] = True
                result["exists"] = True
            elif response.status_code in [301, 302]:
                result["exists"] = True
        
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def validate_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Valida lista de predicciones y retorna solo las válidas"""
        print(f"Validando {len(predictions)} predicciones...")
        
        validated = []
        
        for i, pred in enumerate(predictions, 1):
            viewer_url = pred.get("viewer_url")
            tiles_base = pred.get("tiles_base")
            
            print(f"   [{i}/{len(predictions)}] {viewer_url}")
            
            # Validar viewer URL
            viewer_result = self.validate_url(viewer_url)
            pred["viewer_validation"] = viewer_result
            
            if viewer_result["valid"]:
                print(f"      OK Viewer")
                
                # Validar tiles (opcional, verifica primer tile)
                if tiles_base:
                    first_tile = tiles_base + "c0_l0_0_0.jpg"
                    tiles_result = self.validate_url(first_tile)
                    pred["tiles_validation"] = tiles_result
                    
                    if tiles_result["valid"]:
                        print(f"      OK Tiles")
                        pred["fully_validated"] = True
                    else:
                        print(f"      WARNING: Tiles inaccesibles")
                        pred["fully_validated"] = False
                else:
                    pred["fully_validated"] = False
                
                validated.append(pred)
            else:
                print(f"      ERROR: No valido ({viewer_result.get('status_code', 'Error')})")
        
        # Ordenar por confianza
        validated.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        print(f"\nOK {len(validated)}/{len(predictions)} URLs validas")
        
        return validated
    
    def quick_check(self, url: str) -> bool:
        """Verificación rápida (True/False)"""
        try:
            response = requests.head(url, headers=self.headers, timeout=5)
            return response.status_code == 200
        except:
            return False
