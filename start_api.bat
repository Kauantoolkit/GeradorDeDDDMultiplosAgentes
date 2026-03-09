@echo off
echo ========================================
echo   Agentes Code Generator - API
echo ========================================
echo.
echo Iniciando API com FastAPI e WebSocket...
echo.
REM --reload desabilitado para evitar watchfiles em projetos gerados
python -m uvicorn api.server:app --host 127.0.0.1 --port 8000

