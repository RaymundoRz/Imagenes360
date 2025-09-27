from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import honda

app = FastAPI(
    title="Honda 360° Extractor API",
    description="Sistema de extracción de imágenes 360° para Honda City - Paths CORREGIDOS",
    version="1.1.0"
)

# ✅ ARREGLAR CORS - SOPORTE COMPLETO
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(honda.router, prefix="/api/honda", tags=["honda"])

@app.get("/")
async def root():
    return {
        "message": "Honda 360° Extractor API - CORREGIDO",
        "status": "active",
        "version": "1.1.0",
        "fixes": ["exterior_tiles_paths_corrected"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "honda-extractor", "validation": "passed"}

@app.get("/api/honda/status/{extraction_id}")
async def get_extraction_status(extraction_id: str):
    """
    Endpoint para verificar estado de extracción
    """
    from pathlib import Path
    
    try:
        # Verificar si existe extracción
        base_path = Path("downloads") / "honda_city_2026" 
        
        if base_path.exists():
            # Contar archivos extraídos
            interior_path = base_path / "ViewType.INTERIOR" / "0"
            
            file_count = 0
            if interior_path.exists():
                file_count = len(list(interior_path.glob("*.jpg")))
            
            return {
                "status": "completed",
                "extraction_id": extraction_id,
                "files_extracted": file_count,
                "total_expected": 48,  # Interior tiles esperados
                "progress": min(100, (file_count / 48) * 100),
                "message": f"Extracción completada: {file_count}/48 archivos"
            }
        else:
            return {
                "status": "not_found", 
                "extraction_id": extraction_id,
                "files_extracted": 0,
                "progress": 0,
                "message": "Extracción no encontrada"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "extraction_id": extraction_id, 
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
