@echo off
REM ============================================
REM Script de Validacao de Containers Docker
REM ============================================
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================
echo  VALIDACAO DE DOCKERS - MICROSSERVIÇOS
echo ============================================
echo.

REM Verifica se Docker esta instalado
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERRO: Docker nao encontrado. Instale o Docker primeiro.
    exit /b 1
)

REM Verifica se docker-compose esta instalado
where docker-compose >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERRO: docker-compose nao encontrado.
    exit /b 1
)

echo [OK] Docker encontrado
echo [OK] docker-compose encontrado
echo.

REM Parar containers existentes
echo Parando containers existentes...
docker-compose down --remove-orphans 2>nul
echo.

REM Build das imagens
echo ============================================
echo  BUILD DAS IMAGENS
echo ============================================
docker-compose build
if %ERRORLEVEL% neq 0 (
    echo ERRO: Falha no build das imagens
    exit /b 1
)
echo [OK] Build concluido
echo.

REM Iniciar containers
echo ============================================
echo  INICIANDO CONTAINERS
echo ============================================
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo ERRO: Falha ao iniciar containers
    exit /b 1
)
echo [OK] Containers iniciados
echo.

REM Aguardarcontainers ficarem prontos
echo Aguardando containers ficarem prontos...
timeout /t 15 /nobreak >nul

echo.
echo ============================================
echo  STATUS DOS CONTAINERS
echo ============================================
docker-compose ps
echo.


echo.
echo ============================================
echo  Verificando orders
echo ============================================
for /f "tokens=*" %%p in ('docker-compose port orders 8000 2^>nul') do set SERVICE_PORT=%%p
if not defined SERVICE_PORT (
    echo WARNING: nao foi possivel resolver porta do servico orders
) else (
    curl -s http://!SERVICE_PORT!/health || echo "WARNING: orders nao responde em http://!SERVICE_PORT!/health"
)
set SERVICE_PORT=

echo.
echo ============================================
echo  Verificando users
echo ============================================
for /f "tokens=*" %%p in ('docker-compose port users 8000 2^>nul') do set SERVICE_PORT=%%p
if not defined SERVICE_PORT (
    echo WARNING: nao foi possivel resolver porta do servico users
) else (
    curl -s http://!SERVICE_PORT!/health || echo "WARNING: users nao responde em http://!SERVICE_PORT!/health"
)
set SERVICE_PORT=

echo.
echo ============================================
echo  Verificando products
echo ============================================
for /f "tokens=*" %%p in ('docker-compose port products 8000 2^>nul') do set SERVICE_PORT=%%p
if not defined SERVICE_PORT (
    echo WARNING: nao foi possivel resolver porta do servico products
) else (
    curl -s http://!SERVICE_PORT!/health || echo "WARNING: products nao responde em http://!SERVICE_PORT!/health"
)
set SERVICE_PORT=

echo.
echo ============================================
echo  Verificando payment
echo ============================================
for /f "tokens=*" %%p in ('docker-compose port payment 8000 2^>nul') do set SERVICE_PORT=%%p
if not defined SERVICE_PORT (
    echo WARNING: nao foi possivel resolver porta do servico payment
) else (
    curl -s http://!SERVICE_PORT!/health || echo "WARNING: payment nao responde em http://!SERVICE_PORT!/health"
)
set SERVICE_PORT=


echo.
echo ============================================
echo  VALIDACAO CONCLUIDA
echo ============================================
echo.
echo Para ver os logs: docker-compose logs -f
echo Para parar: docker-compose down
echo.
