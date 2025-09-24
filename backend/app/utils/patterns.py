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
