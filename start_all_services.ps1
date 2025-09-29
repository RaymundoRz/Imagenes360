# HONDA 360° EXTRACTOR - SCRIPT DE INICIO COMPLETO
Write-Host "========================================" -ForegroundColor Green
Write-Host "   HONDA 360° EXTRACTOR - INICIANDO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "[1/4] Iniciando Backend (Puerto 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --reload --port 8000"
Start-Sleep -Seconds 3

Write-Host "[2/4] Iniciando Frontend (Puerto 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Start-Sleep -Seconds 3

Write-Host "[3/4] Iniciando Servidor de Imágenes (Puerto 8080)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend/downloads; python -m http.server 8080"
Start-Sleep -Seconds 3

Write-Host "[4/4] Verificando servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   SERVICIOS INICIADOS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backend:    http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Frontend:   http://localhost:5173" -ForegroundColor Cyan
Write-Host "File Server: http://127.0.0.1:8080" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Yellow
Read-Host



