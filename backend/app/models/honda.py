from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ViewType(str, Enum):
    EXTERIOR = "exterior"
    INTERIOR = "interior"

class HondaYear(str, Enum):
    YEAR_2024 = "2024"
    YEAR_2026 = "2026"

class ExtractionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"  
    COMPLETED = "completed"
    FAILED = "failed"

class TileInfo(BaseModel):
    """Información de un tile individual"""
    url: str
    level: int
    column: Optional[int] = None  # Para Object2VR (exterior)
    face: Optional[int] = None    # Para Pano2VR (interior)
    x: int
    y: int
    downloaded: bool = False
    file_size: Optional[int] = None

class ExtractionRequest(BaseModel):
    """Request para iniciar extracción"""
    year: HondaYear = Field(..., description="Año del Honda City")
    view_type: ViewType = Field(..., description="Tipo de vista a extraer") 
    quality_level: int = Field(0, description="Nivel de calidad (0=máxima, 2=mínima)")
    download_path: Optional[str] = Field(None, description="Path personalizado de descarga")

class ExtractionResponse(BaseModel):
    """Response de estado de extracción"""
    extraction_id: str
    status: ExtractionStatus
    year: str
    view_type: str
    total_tiles: int
    downloaded_tiles: int = 0
    failed_tiles: int = 0
    progress_percentage: float = 0.0
    estimated_time_remaining: Optional[int] = None  # segundos
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

class TileExtractionStats(BaseModel):
    """Estadísticas de extracción de tiles"""
    total_tiles: int
    successful_downloads: int  
    failed_downloads: int
    total_size_mb: float
    download_time_seconds: float
    average_speed_mbps: float

class HondaCityModel(BaseModel):
    """Modelo completo Honda City con toda la información"""
    year: str
    model: str = "Honda City"
    
    # Especificaciones técnicas
    engine: str
    power: str
    torque: str
    transmission: str
    versions: List[str]
    features: List[str]
    
    # Información de imágenes 360°
    exterior_available: bool = True
    interior_available: bool = True
    total_exterior_tiles: int
    total_interior_tiles: int
    
    # URLs de configuración
    exterior_config_url: str
    interior_config_url: str
    
    # Metadata de extracción
    extracted_at: Optional[str] = None
    extraction_stats: Optional[Dict[str, TileExtractionStats]] = None

class HondaListResponse(BaseModel):
    """Response para listar modelos Honda disponibles"""
    available_years: List[str]
    models: List[HondaCityModel]
    total_models: int

class ConfigInfo(BaseModel):
    """Información de configuración XML"""
    url: str
    content: str
    technology: str  # "object2vr" o "pano2vr"
    columns: Optional[int] = None
    rows: Optional[int] = None  
    faces: Optional[int] = None
    levels: int
    max_resolution: Dict[str, int]
    tile_pattern: str
