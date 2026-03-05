"""
Docker Test Agent - Agente de Teste de Docker
==============================================

Este agente é responsável por:
- Gerar um docker-compose.yml unificado com todos os serviços
- Criar scripts de validação (validate_dockers.bat)
- Validar se os containers estão rodando corretamente
- Executar testes de saúde (health checks) nos serviços
"""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    ValidationResult,
    ValidationStatus,
    Requirement
)
from infrastructure.llm_provider import OllamaProvider, PromptBuilder
from infrastructure.file_manager import FileManager


class DockerTestAgent:
    """
    Agente de Teste de Docker - Valida containers localmente.
    
    Este agente:
    1. Gera docker-compose.yml unificado
    2. Cria scripts de validação
    3. Executa testes de Docker
    """
    
    def __init__(self, llm_provider: OllamaProvider = None):
        """
        Inicializa o Docker Test Agent.
        
        Args:
            llm_provider: Provedor de LLM (opcional, para geração avançada)
        """
        self.llm_provider = llm_provider
        self.name = "Docker Test Agent"
        logger.info(f"{self.name} inicializado")
    
    async def execute(self, requirement: Requirement, execution_result: ExecutionResult) -> ExecutionResult:
        """
        Executa a validação de Docker.
        
        Args:
            requirement: Requisitos do projeto
            execution_result: Resultado da execução do Executor
            
        Returns:
            ExecutionResult com status da validação Docker
        """
        start_time = datetime.now()
        
        logger.info("="*60)
        logger.info("DOCKER TEST AGENT - Iniciando validação")
        logger.info("="*60)
        
        result = ExecutionResult(
            agent_type=AgentType.DOCKER_TEST,
            status=ExecutionStatus.SUCCESS
        )
        
        try:
            # Identifica os serviços gerados
            services = self._extract_services(execution_result)
            
            if not services:
                logger.warning("Nenhum serviço identificado para validação Docker")
                result.status = ExecutionStatus.FAILED
                result.error_message = "Nenhum serviço identificado"
                return result
            
            logger.info(f"Serviços identificados: {services}")
            
            # Gera docker-compose.yml unificado
            docker_compose_path = await self._generate_unified_docker_compose(
                requirement, 
                services
            )
            
            # Gera script de validação
            validate_script_path = await self._generate_validation_script(
                services,
                requirement.project_config.output_directory
            )
            
            # Tenta executar a validação Docker
            docker_result = await self._run_docker_validation(
                services,
                requirement.project_config.output_directory
            )
            
            result.status = ExecutionStatus.SUCCESS if docker_result.get("success") else ExecutionStatus.FAILED
            if not docker_result.get("success"):
                result.error_message = (
                    docker_result.get("error")
                    or docker_result.get("build_error")
                    or docker_result.get("up_error")
                    or "Validação Docker falhou"
                )
            result.output = json.dumps({
                "docker_compose_path": docker_compose_path,
                "validate_script_path": validate_script_path,
                "docker_validation": docker_result,
                "services": services
            }, indent=2)
            
            logger.info(f"✅ Docker Test Agent concluído em {(datetime.now() - start_time).total_seconds():.2f}s")
            
        except Exception as e:
            logger.exception(f"Erro no {self.name}: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
        
        return result
    
    def _extract_services(self, execution_result: ExecutionResult) -> list[str]:
        """
        Extrai os nomes dos serviços do resultado da execução.
        
        Args:
            execution_result: Resultado do Executor
            
        Returns:
            Lista de nomes de serviços
        """
        services = []
        
        # Tenta extrair do output JSON
        try:
            if execution_result.output:
                json_start = execution_result.output.find('{')
                json_end = execution_result.output.rfind('}')
                if json_start >= 0 and json_end >= json_start:
                    data = json.loads(execution_result.output[json_start:json_end+1])
                    if "microservices" in data:
                        services = [s.get("name", "") for s in data["microservices"]]
        except Exception as e:
            logger.warning(f"Erro ao extrair serviços do output: {e}")
        
        # Se não conseguiu extrair, verifica os arquivos gerados
        if not services and execution_result.files_created:
            for file_path in execution_result.files_created:
                if "docker-compose.yml" in file_path:
                    # Extrai nome do serviço do caminho
                    parts = file_path.split(os.sep)
                    if "services" in parts:
                        idx = parts.index("services")
                        if idx + 1 < len(parts):
                            service_name = parts[idx + 1]
                            if service_name not in services:
                                services.append(service_name)
        
        return services
    
    async def _generate_unified_docker_compose(
        self, 
        requirement: Requirement, 
        services: list[str]
    ) -> str:
        """
        Gera um docker-compose.yml unificado para todos os serviços.
        
        Usa estrutura dict Python e yaml.safe_dump() para geração robusta
        e livre de erros estruturais.
        
        Args:
            requirement: Requisitos do projeto
            services: Lista de nomes dos serviços
            
        Returns:
            Caminho do arquivo gerado
        """
        logger.info("Gerando docker-compose.yml unificado...")
        
        # Porta inicial para serviços
        base_service_port = 8001
        base_db_port = 5432
        
        # Define se cada serviço precisa de banco (extensível)
        # Por padrão, todos os serviços têm banco PostgreSQL
        services_needing_db = set(services)
        
        # GENERIC: Nome da rede deve ser dinâmico, baseado no projeto
        # Não deve haver referências a domínios específicos
        project_network_name = "project-network"
        
        # Início da construção da estrutura Docker Compose como dict
        # NOTA: Não usamos mais 'version' pois está obsoleto nas versões recentes do Docker Compose
        compose = {
            "services": {},
            "networks": {project_network_name: {"driver": "bridge"}},
            "volumes": {}
        }
        
        logger.info(f"Construindo estrutura Docker Compose para {len(services)} serviços...")
        
        # Processa cada serviço
        for idx, service_name in enumerate(services):
            # CORREÇÃO CRÍTICA: Normalizar nome do serviço (hífen -> sublinhado)
            # Os diretórios são criados com sublinhado (order_service), não hífen (order-service)
            normalized_service_name = service_name.replace('-', '_')
            
            # Porta dinâmica baseada no índice (evita conflitos)
            service_port = base_service_port + idx
            db_port = base_db_port + idx + 1  # Offset para evitar conflito com porta padrão
            
            logger.info(f"  - {normalized_service_name}: porta={service_port}, db_port={db_port}")
            
            # Define container do serviço principal usando nome normalizado
            service_container_name = normalized_service_name
            db_container_name = f"db-{normalized_service_name}"
            
            # Configuração do serviço - CORRIGIDO: usa nome normalizado para o context
            compose["services"][service_container_name] = {
                "build": {
                    "context": f"./services/{normalized_service_name}",
                    "dockerfile": "Dockerfile"
                },
                "ports": [f"{service_port}:8000"],
                "environment": [
                    f"DATABASE_URL=postgresql://postgres:postgres@{db_container_name}:5432/{normalized_service_name}",
                    f"SERVICE_NAME={normalized_service_name}"
                ],
                "depends_on": [db_container_name],
                "networks": [project_network_name]
            }
            
            # Adiciona banco de dados apenas se o serviço precisa
            if service_name in services_needing_db:
                # Configuração do banco de dados
                compose["services"][db_container_name] = {
                    "image": "postgres",
                    "environment": [
                        "POSTGRES_PASSWORD=postgres",
                        f"POSTGRES_DB={normalized_service_name}"
                    ],
                    "ports": [f"{db_port}:5432"],
                    "volumes": [f"pgdata-{normalized_service_name}:/var/lib/postgresql/data"],
                    "networks": [project_network_name]
                }
                
                # Define volume para persistência do banco
                compose["volumes"][f"pgdata-{normalized_service_name}"] = None
        
        logger.info(f"Estrutura Docker Compose pronta: {len(compose['services'])} serviços/contêineres")
        
        # Gera YAML a partir da estrutura dict
        docker_compose_content = self._to_compose_yaml(compose)
        
        # Escreve o arquivo
        output_dir = requirement.project_config.output_directory
        docker_compose_path = os.path.join(output_dir, "docker-compose.yml")
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(docker_compose_path, 'w', encoding='utf-8') as f:
            f.write(docker_compose_content)
        
        logger.info(f"docker-compose.yml gerado em: {docker_compose_path}")
        return docker_compose_path
    

    def _to_compose_yaml(self, compose: dict) -> str:
        """Serializa a estrutura do docker compose para YAML sem dependências externas."""

        def _scalar(value):
            if value is None:
                return ""
            text = str(value)
            if text == "" or any(ch in text for ch in [":", "#", "{", "}", "[", "]"]):
                return f'"{text}"'
            return text

        def _dump(obj, indent=0):
            sp = "  " * indent
            lines = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        lines.append(f"{sp}{k}:")
                        lines.extend(_dump(v, indent + 1))
                    elif v is None:
                        lines.append(f"{sp}{k}:")
                    else:
                        lines.append(f"{sp}{k}: {_scalar(v)}")
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        lines.append(f"{sp}-")
                        lines.extend(_dump(item, indent + 1))
                    else:
                        lines.append(f"{sp}- {_scalar(item)}")
            else:
                lines.append(f"{sp}{_scalar(obj)}")
            return lines

        return "\n".join(_dump(compose)) + "\n"

    async def _generate_validation_script(self, services: list[str], output_dir: str) -> str:
        """
        Gera o script de validação validate_dockers.bat.
        
        Args:
            services: Lista de nomes dos serviços
            
        Returns:
            Caminho do script gerado
        """
        logger.info("Gerando script de validação...")
        
        # GENERIC: Portas devem ser dinâmicas baseadas no índice do serviço
        base_port = 8001
        
        # Gera verificações de saúde para cada serviço com portas dinâmicas
        health_checks = []
        for idx, service in enumerate(services):
            port = base_port + idx
            health_checks.append(f"""
echo.
echo ============================================
echo  Verificando {service} (porta {port})
echo ============================================
curl -s http://localhost:{port}/health || echo "WARNING: {service} nao responde em http://localhost:{port}/health"
""")
        
        health_check_section = "".join(health_checks)
        
        script_content = f"""@echo off
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

{health_check_section}

echo.
echo ============================================
echo  VALIDACAO CONCLUIDA
echo ============================================
echo.
echo Para ver os logs: docker-compose logs -f
echo Para parar: docker-compose down
echo.
"""
        
        # Salva o script
        script_path = os.path.join(output_dir, "validate_dockers.bat")
        
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"Script de validacao gerado em: {script_path}")
        return script_path
    
    async def _run_docker_validation(self, services: list[str], output_dir: str) -> dict:
        """
        Executa a validação real dos containers Docker.
        
        Args:
            services: Lista de serviços
            
        Returns:
            Dicionário com resultado da validação
        """
        logger.info("Executando validacao Docker real...")
        
        result = {
            "docker_available": False,
            "containers_running": [],
            "containers_failed": [],
            "health_checks": {},
            "success": False
        }
        
        # Verifica se Docker está disponível
        try:
            check_docker = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            result["docker_available"] = check_docker.returncode == 0
        except Exception as e:
            logger.warning(f"Docker nao disponivel: {e}")
            return result
        
        if not result["docker_available"]:
            logger.warning("Docker nao esta instalado ou nao esta rodando")
            return result
        
        # Tenta fazer build e start
        try:
            # Build
            logger.info("Executando docker-compose build...")
            build_result = subprocess.run(
                ["docker-compose", "build"],
                capture_output=True,
                text=True,
                cwd=output_dir,
                timeout=300
            )
            
            if build_result.returncode != 0:
                result["build_error"] = build_result.stderr
                logger.warning(f"Build falhou: {build_result.stderr}")
                return result
            
            # Up
            logger.info("Executando docker-compose up -d...")
            up_result = subprocess.run(
                ["docker-compose", "up", "-d"],
                capture_output=True,
                text=True,
                cwd=output_dir,
                timeout=120
            )
            
            if up_result.returncode != 0:
                result["up_error"] = up_result.stderr
                logger.warning(f"Up falhou: {up_result.stderr}")
                return result
            
            # Espera um pouco
            await asyncio.sleep(10)
            
            # Verifica containers
            ps_result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                cwd=output_dir,
                timeout=30
            )
            result["containers_status"] = ps_result.stdout
            
            # GENERIC: Portas dinâmicas baseadas no índice do serviço
            base_port = 8001
            
            for idx, service in enumerate(services):
                port = base_port + idx
                try:
                    check = subprocess.run(
                        ["curl", "-s", f"http://localhost:{port}/health"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    result["health_checks"][service] = {
                        "port": port,
                        "status": "up" if check.returncode == 0 else "down",
                        "response": check.stdout[:200] if check.stdout else ""
                    }
                except Exception as e:
                    result["health_checks"][service] = {
                        "port": port,
                        "status": "error",
                        "error": str(e)
                    }
            
            result["success"] = True
            logger.info("Validacao Docker concluida com sucesso")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Timeout durante validacao Docker"
            logger.warning("Timeout durante validacao Docker")
        except Exception as e:
            result["error"] = str(e)
            logger.warning(f"Erro durante validacao Docker: {e}")
        
        return result


class DockerValidationRules:
    """Regras de validacao para Docker."""
    
    @staticmethod
    def check_docker_installed() -> bool:
        """Verifica se Docker esta instalado."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def check_docker_running() -> bool:
        """Verifica se Docker esta rodando."""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def check_docker_compose_installed() -> bool:
        """Verifica se docker-compose esta instalado."""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
