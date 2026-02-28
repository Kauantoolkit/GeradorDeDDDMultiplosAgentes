@echo off
REM Ativa o ambiente virtual e adiciona Ollama ao PATH
cd /d "%~dp0"

REM Ativa o virtualenv
call venv\Scripts\activate.bat

REM Adiciona Ollama ao PATH para esta sessão
set PATH=%PATH%;C:\Users\kauan\AppData\Local\Programs\ollama

echo.
echo ============================================
echo  Ambiente configurado!
echo  Ollama adicionado ao PATH
echo ============================================
echo.

REM Inicia o Ollama em segundo plano (opcional)
REM start "" "C:\Users\kauan\AppData\Local\Programs\ollama\ollama.exe" serve

REM Inicia o Python
python main.py %*
