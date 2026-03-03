@echo off
echo ========================================
echo   Agentes Code Generator - API
echo ========================================
echo.
echo Iniciando API com FastAPI e WebSocket...
echo.
python -m uvicorn api.server:app --host 127.0.0.1 --port 8000
