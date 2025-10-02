"""
Honda 360° Patterns - CORREGIDOS después de validación
Todos los paths están basados en la investigación del 23 septiembre 2025
"""

# URLs base para Honda City
HONDA_CITY_PATTERNS = {
    "base_url": "https://www.honda.mx",
    "exterior_path": "/autos/city/{year}/city_{year}_ext_360",
    "interior_path": "/autos/city/{year}/city_{year}_int_360",
    
    # Configuraciones XML
    "exterior_config": "/web/img/cars/models/city/{year}/city_{year}_ext_360/honda_city_{year}_ext_out.xml",
    "interior_config": "/web/img/cars/models/city/{year}/city_{year}_int_360/pano.xml",
    
    # Paths de imágenes CORREGIDOS
    "exterior_images_base": "/web/img/cars/models/city/{year}/city_{year}_ext_360/",  # SIN 'images/'
    "interior_images_base": "/web/img/cars/models/city/{year}/city_{year}_int_360/",
}

# Patterns de tiles CORREGIDOS
TILE_PATTERNS = {
    "object2vr": {
        # Para exteriores Honda (Object2VR) - PATH CORREGIDO
        "pattern": "tiles/c{column}_l{level}_{y}_{x}.jpg",  # SIN 'images/'
        "columns": 32,
        "levels": 3,
        "tile_size": 256  # Honda usa 256x256 para exterior
    },
    "pano2vr": {
        # Para interiores Honda (Pano2VR)
        "pattern": "tiles/node1/cf_{face}/l_{level}/c_{x}/tile_{y}.jpg",
        "faces": 6,
        "levels": 3,
        "tile_size": 510
    }
}

# Resoluciones confirmadas por año
RESOLUTIONS = {
    "2026": {
        "exterior": [
            {"width": 5200, "height": 1900},
            {"width": 1600, "height": 584}, 
            {"width": 640, "height": 233}
        ],
        "interior": [
            {"width": 3708, "height": 3708},
            {"width": 1854, "height": 1854},
            {"width": 927, "height": 927}
        ]
    },
    "2024": {
        "exterior": [
            {"width": 5200, "height": 1900},
            {"width": 1600, "height": 584},
            {"width": 640, "height": 233}
        ],
        "interior": [
            {"width": 4904, "height": 4904},
            {"width": 2452, "height": 2452}, 
            {"width": 1226, "height": 1226}
        ]
    }
}

# Información técnica Honda City
HONDA_CITY_SPECS = {
    "2026": {
        "engine": "1.5L DOHC i-VTEC®",
        "power": "119 hp @ 6,600 rpm",
        "torque": "107 lb/ft @ 4,300 rpm",
        "transmission": "CVT",
        "versions": ["Sport", "Touring", "Prime"],
        "features": ["Honda Sensing®", "Display Audio 8\"", "Apple CarPlay®"]
    },
    "2024": {
        "engine": "1.5L DOHC i-VTEC®", 
        "power": "119 hp @ 6,600 rpm",
        "torque": "107 lb/ft @ 4,300 rpm",
        "transmission": "CVT",
        "versions": ["Sport", "Touring", "Prime"],
        "features": ["Honda Sensing®", "Display Audio 8\"", "Apple CarPlay®"]
    }
}

def get_honda_config_url(year: str, view_type: str) -> str:
    """Generar URL de configuración Honda basada en patterns CORREGIDOS"""
    base = HONDA_CITY_PATTERNS["base_url"]
    
    if view_type == "exterior":
        config_path = HONDA_CITY_PATTERNS["exterior_config"].format(year=year)
    elif view_type == "interior": 
        config_path = HONDA_CITY_PATTERNS["interior_config"].format(year=year)
    else:
        raise ValueError(f"view_type debe ser 'exterior' o 'interior', recibido: {view_type}")
    
    return base + config_path

def get_honda_images_base_url(year: str, view_type: str) -> str:
    """Generar URL base de imágenes Honda - CORREGIDA"""
    base = HONDA_CITY_PATTERNS["base_url"]
    
    if view_type == "exterior":
        images_path = HONDA_CITY_PATTERNS["exterior_images_base"].format(year=year)
    elif view_type == "interior":
        images_path = HONDA_CITY_PATTERNS["interior_images_base"].format(year=year) 
    else:
        raise ValueError(f"view_type debe ser 'exterior' o 'interior', recibido: {view_type}")
    
    return base + images_path

def calculate_tiles_per_level(resolution: dict, tile_size: int) -> tuple:
    """Calcular número de tiles por nivel basado en resolución"""
    # Calcular tiles redondeando hacia arriba para cubrir toda la imagen
    import math
    tiles_x = math.ceil(resolution["width"] / tile_size)
    tiles_y = math.ceil(resolution["height"] / tile_size)
    return tiles_x, tiles_y

# ====================================================================================
# EXTENSIÓN MULTI-MODELO - AGREGADO AL FINAL DEL ARCHIVO
# NO TOCA FUNCIONES EXISTENTES - SOLO AGREGA NUEVAS
# ====================================================================================

# Mapeo completo de todos los modelos Honda - SOLO MODELOS REALES CONFIRMADOS
HONDA_ALL_MODELS_PATTERNS = {
    "city": {
        "name": "Honda City",
        "years": ["2024", "2026"],  # CONFIRMADO FUNCIONANDO
        "status": "confirmed",
        "exterior_config": "/web/img/cars/models/city/{year}/city_{year}_ext_360/honda_city_{year}_ext_out.xml",
        "interior_config": "/web/img/cars/models/city/{year}/city_{year}_int_360/pano.xml",
        "exterior_images_base": "/web/img/cars/models/city/{year}/city_{year}_ext_360/",
        "interior_images_base": "/web/img/cars/models/city/{year}/city_{year}_int_360/",
    },
    "cr-v": {
        "name": "Honda CR-V",
        "years": ["2024"],  # CONFIRMADO POR SELENIUM - 3/4 ASSETS
        "status": "confirmed",
        "exterior_config": "/web/img/cars/models/cr-v/{year}/cr-v_{year}_ext_360/honda_crv_{year}_ext_out.xml",
        "interior_config": "/web/img/cars/models/cr-v/{year}/cr-v_{year}_int_360/pano.xml",
        "exterior_images_base": "/web/img/cars/models/cr-v/{year}/cr-v_{year}_ext_360/",
        "interior_images_base": "/web/img/cars/models/cr-v/{year}/cr-v_{year}_int_360/",
    }
    # NOTA: Después de investigación exhaustiva del 29/sep/2025
    # Honda City (2024,2026) y Honda CR-V (2024) tienen assets 360° funcionales
    # CR-V confirmado por Selenium con 3/4 assets obtenidos
}

def get_honda_universal_config_url(model: str, year: str, view_type: str) -> str:
    """
    Generar URL de configuración Honda para CUALQUIER modelo
    Mantiene compatibilidad total con get_honda_config_url()
    """
    base = HONDA_CITY_PATTERNS["base_url"]
    
    # Si es city, usa función original para mantener compatibilidad
    if model.lower() == "city":
        return get_honda_config_url(year, view_type)
    
    # Para otros modelos, usar el nuevo mapeo
    if model.lower() not in HONDA_ALL_MODELS_PATTERNS:
        raise ValueError(f"Modelo no soportado: {model}")
    
    model_config = HONDA_ALL_MODELS_PATTERNS[model.lower()]
    
    if view_type == "exterior":
        config_path = model_config["exterior_config"].format(year=year)
    elif view_type == "interior":
        config_path = model_config["interior_config"].format(year=year) 
    else:
        raise ValueError(f"view_type debe ser 'exterior' o 'interior', recibido: {view_type}")
    
    return base + config_path

def get_honda_universal_images_base_url(model: str, year: str, view_type: str) -> str:
    """
    Generar URL base de imágenes Honda para CUALQUIER modelo
    Mantiene compatibilidad total con get_honda_images_base_url()
    """
    base = HONDA_CITY_PATTERNS["base_url"]
    
    # Si es city, usa función original para mantener compatibilidad  
    if model.lower() == "city":
        return get_honda_images_base_url(year, view_type)
    
    # Para otros modelos, usar el nuevo mapeo
    if model.lower() not in HONDA_ALL_MODELS_PATTERNS:
        raise ValueError(f"Modelo no soportado: {model}")
    
    model_config = HONDA_ALL_MODELS_PATTERNS[model.lower()]
    
    if view_type == "exterior":
        images_path = model_config["exterior_images_base"].format(year=year)
    elif view_type == "interior":
        images_path = model_config["interior_images_base"].format(year=year)
    else:
        raise ValueError(f"view_type debe ser 'exterior' o 'interior', recibido: {view_type}")
    
    return base + images_path

def get_all_honda_models() -> dict:
    """
    Devolver lista completa de modelos Honda disponibles
    """
    return HONDA_ALL_MODELS_PATTERNS

# === FASE 1: MODELOS CONFIRMADOS HONDA 360° ===
# Basado en verificación real del 29 septiembre 2025

HONDA_CONFIRMED_MODELS = {
    "City": {
        "name": "Honda City",
        "pattern": "city/{year}/city_{year}_ext_360",
        "years": ["2024", "2026"],
        "status": "confirmed"
    },
    "CR-V": {
        "name": "Honda CR-V",
        "pattern": "cr-v/CR-V_{year}_ext_360",
        "years": ["2024"],
        "status": "confirmed"
    },
}

def get_confirmed_models():
    """Obtener solo modelos 100% confirmados"""
    return [
        {
            "name": model_data["name"].replace("Honda ", ""),
            "years": model_data["years"]
        }
        for model_data in HONDA_CONFIRMED_MODELS.values()
    ]
