@echo off
REM Adiciona o Ollama ao PATH temporariamente e executa o Python
set PATH=%PATH%;C:\Users\kauan\AppData\Local\Programs\ollama
python %*
