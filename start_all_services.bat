@echo off
echo ========================================
echo    HONDA 360° EXTRACTOR - INICIANDO
echo ========================================
echo.

echo [1/4] Iniciando Backend (Puerto 8000)...
start "Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul

echo [2/4] Iniciando Frontend (Puerto 5173)...
start "Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo [3/4] Iniciando Servidor de Imágenes (Puerto 8080)...
start "File Server" cmd /k "cd backend/downloads && python -m http.server 8080"
timeout /t 3 /nobreak >nul

echo [4/4] Verificando servicios...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo    SERVICIOS INICIADOS
echo ========================================
echo Backend:    http://127.0.0.1:8000
echo Frontend:   http://localhost:5173
echo File Server: http://127.0.0.1:8080
echo ========================================
echo.
echo Presiona cualquier tecla para continuar...
pause >nul



