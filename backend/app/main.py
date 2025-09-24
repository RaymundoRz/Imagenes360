from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import honda

app = FastAPI(
    title="Honda 360° Extractor API",
    description="Sistema de extracción de imágenes 360° para Honda City - Paths CORREGIDOS",
    version="1.1.0"
)

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
