"""
Servidor API com FastAPI e WebSocket
=====================================

Servidor que fornece:
- API REST para iniciar geração de projetos
- WebSocket para comunicação em tempo real com o frontend

Uso:
    uvicorn api.server:app --reload --port 8000
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uuid

# Adiciona o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.entities import Requirement, ProjectConfig
from infrastructure.llm_provider import OllamaProvider, ensure_ollama_running, check_ollama_installation
from agents.orchestrator_v3 import OrchestratorV3


# ==================== CONFIGURAÇÃO ====================

# Configuração de logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)
logger.add("logs/api_server.log", rotation="10 MB", retention="7 days", level="DEBUG")


# ==================== WEBSOCKET MANAGER ====================

class ConnectionManager:
    """
    Gerenciador de conexões WebSocket.
    
    Mantém registro de todas as conexões ativas e permite
    broadcast de mensagens para todos os clientes conectados.
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_info: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Aceita e registra uma nova conexão."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.client_info[client_id] = {
            "connected_at": datetime.now(),
            "websocket": websocket
        }
        logger.info(f"Cliente {client_id} conectado. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """Remove uma conexão."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if client_id in self.client_info:
            del self.client_info[client_id]
        logger.info(f"Cliente {client_id} desconectado. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envia mensagem para um cliente específico."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os clientes conectados."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Erro ao broadcast: {e}")
                disconnected.append(connection)
        
        # Remove conexões desconectadas
        for conn in disconnected:
            self.active_connections.remove(conn)


# Instância global do gerenciador
manager = ConnectionManager()

# Tasks pendentes (aguardando criação de bancos)
pending_tasks: Dict[str, dict] = {}


def build_error_payload(
    *,
    code: str,
    message: str,
    task_id: str | None = None,
    exception: Exception | None = None,
    hints: list[str] | None = None,
    context: dict | None = None,
) -> dict:
    """Cria payload padronizado para erros enviados ao frontend e logs."""
    error_id = str(uuid.uuid4())[:8]

    payload = {
        "error_id": error_id,
        "error_code": code,
        "message": message,
        "hints": hints or [],
        "context": context or {}
    }

    if task_id:
        payload["task_id"] = task_id

    if exception:
        payload["error"] = str(exception)
        payload["exception_type"] = type(exception).__name__
        payload["stack_trace"] = traceback.format_exc(limit=8)

    return payload


# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Agentes Code Generator API",
    description="API para geração de microserviços com agentes AI",
    version="1.0.0"
)

# CORS - Permite todas as origens (para desenvolvimento)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== WEBSOCKET ENDPOINT ====================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Endpoint WebSocket para comunicação em tempo real.
    
    O cliente deve se conectar com um client_id único para
    receber atualizações sobre a execução dos agentes.
    """
    await manager.connect(websocket, client_id)
    
    try:
        # Envia mensagem de boas-vindas
        await manager.send_personal_message({
            "type": "connected",
            "client_id": client_id,
            "message": "Conectado ao servidor de agentes",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Mantém a conexão aberta
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Processa mensagens recebidas do cliente
                await handle_client_message(message, websocket, client_id)
            except json.JSONDecodeError:
                logger.warning(f"Mensagem inválida recebida: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.exception(f"Erro no WebSocket: {e}")
        manager.disconnect(websocket, client_id)


async def handle_client_message(message: dict, websocket: WebSocket, client_id: str):
    """Processa mensagens recebidas do cliente."""
    msg_type = message.get("type")
    
    if msg_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }, websocket)
    
    elif msg_type == "status":
        # Retorna status dos agentes
        await manager.send_personal_message({
            "type": "status",
            "agents": {
                "orchestrator": "ready",
                "executor": "ready",
                "validator": "ready",
                "fix": "ready",
                "rollback": "ready",
                "docker_test": "ready"
            },
            "timestamp": datetime.now().isoformat()
        }, websocket)


# ==================== REST ENDPOINTS ====================

@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "name": "Agentes Code Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/{client_id}"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/generate")
async def generate_project(request: dict):
    """
    Inicia a geração de um novo projeto.
    
    Args:
        request: Dicionário com:
            - requirements: str - Descrição dos requisitos
            - model: str (opcional) - Modelo Ollama
            - output: str (opcional) - Diretório de saída
    
    Returns:
        JSON com ID da task e status inicial
    """
    try:
        # Extrai dados da requisição
        requirements_text = request.get("requirements", "")
        model = request.get("model", "llama3.2")
        output_dir = request.get("output", "generated")
        framework = request.get("framework", "python-fastapi")
        database = request.get("database", "postgresql")
        
        if not requirements_text:
            raise HTTPException(status_code=400, detail="Requirements não pode estar vazio")
        
        # Gera ID único para a task
        task_id = str(uuid.uuid4())
        
        # Inicia execução em background
        asyncio.create_task(
            execute_generation(
                task_id=task_id,
                requirements=requirements_text,
                model=model,
                output_dir=output_dir,
                framework=framework,
                database=database
            )
        )
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Geração iniciada",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_payload = build_error_payload(
            code="GENERATION_START_FAILED",
            message="Falha ao iniciar geração.",
            exception=e,
            hints=[
                "Verifique se a API backend está saudável em /health.",
                "Confira se o JSON enviado possui os campos esperados.",
                "Revise o log logs/api_server.log para stack trace completo."
            ],
            context={
                "request_keys": sorted(list(request.keys())) if isinstance(request, dict) else [],
            }
        )
        logger.exception(
            f"[error_id={error_payload['error_id']}] Erro ao iniciar geração | payload={error_payload}"
        )
        raise HTTPException(status_code=500, detail=error_payload)


@app.get("/api/tasks")
async def list_tasks():
    """Lista todas as tasks ativas."""
    return {
        "tasks": [],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Retorna o status de uma task específica."""
    return {
        "task_id": task_id,
        "status": "unknown",
        "message": "Task não encontrada"
    }


@app.post("/api/continue/{task_id}")
async def continue_after_database_creation(task_id: str):
    """
    Continua a execução após o usuário criar os bancos de dados.
    
    O frontend chama este endpoint quando o usuário confirma
    que criou os bancos no pgAdmin.
    """
    global pending_tasks
    
    if task_id not in pending_tasks:
        raise HTTPException(
            status_code=404, 
            detail=f"Task {task_id} não encontrada ou já finalizada"
        )
    
    task_data = pending_tasks[task_id]
    requirement = task_data["requirement"]
    result = task_data["result"]
    
    # Inicia continuação em background
    asyncio.create_task(
        continue_generation(
            task_id=task_id,
            requirement=requirement,
            result=result
        )
    )
    
    return {
        "task_id": task_id,
        "status": "continuing",
        "message": "Continuando validação após criação dos bancos",
        "timestamp": datetime.now().isoformat()
    }


async def continue_generation(task_id: str, requirement, result):
    """Continua a execução após criação de bancos COM AUTO-CRIAÇÃO DE BANCOS."""
    
    async def send_update(event_type: str, data: dict):
        """Envia atualização para o cliente."""
        message = {
            "type": event_type,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            **data
        }
        await manager.broadcast(message)
    
    logger.info(f"[task_id={task_id}] Continuing after database creation WITH AUTO-DATABASE CREATION")
    
    try:
        # ============================================================
        # PASSO 1: Criar os bancos de dados automaticamente
        # ============================================================
        await send_update("agent_status", {
            "agent": "system",
            "status": "running",
            "message": "Criando bancos de dados automaticamente...",
            "diagnostics": {
                "task_id": task_id,
                "phase": "creating_databases"
            }
        })
        
        # Importar o criador de bancos
        from infrastructure.database_creator import create_databases, check_psql_available
        
        database_urls = result.database_urls if hasattr(result, 'database_urls') else {}
        
        if not database_urls:
            logger.warning(f"[task_id={task_id}] No database URLs found to create")
            await send_update("agent_status", {
                "agent": "system",
                "status": "running",
                "message": "Nenhuma URL de banco encontrada, pulando criação...",
                "diagnostics": {
                    "task_id": task_id,
                    "phase": "no_databases"
                }
            })
        else:
            # Verificar se psql está disponível
            if not check_psql_available():
                logger.warning(f"[task_id={task_id}] psql not found, requesting manual creation")
                await send_update("agent_status", {
                    "agent": "system",
                    "status": "running",
                    "message": "psql não encontrado. Por favor, crie os bancos manualmente no pgAdmin.",
                    "diagnostics": {
                        "task_id": task_id,
                        "phase": "psql_not_found"
                    }
                })
            else:
                # Criar os bancos automaticamente
                logger.info(f"[task_id={task_id}] Creating databases: {database_urls}")
                db_result = create_databases(database_urls)
                
                # Enviar resultado para o frontend
                if db_result["success"]:
                    created_count = len(db_result["created"])
                    await send_update("agent_status", {
                        "agent": "system",
                        "status": "running",
                        "message": f"Bancos de dados criados automaticamente: {', '.join(db_result['created'])}",
                        "diagnostics": {
                            "task_id": task_id,
                            "phase": "databases_created",
                            "created_databases": db_result["created"],
                            "messages": db_result["messages"]
                        }
                    })
                else:
                    # Alguns bancos falharam
                    await send_update("agent_status", {
                        "agent": "system",
                        "status": "running",
                        "message": f"Alguns bancos não puderam ser criados: {', '.join(db_result['failed'])}. Por favor, crie manualmente.",
                        "diagnostics": {
                            "task_id": task_id,
                            "phase": "databases_partial",
                            "created": db_result["created"],
                            "failed": db_result["failed"],
                            "messages": db_result["messages"]
                        }
                    })
        
        # ============================================================
        # PASSO 2: Iniciar validação dos serviços
        # ============================================================
        await send_update("agent_status", {
            "agent": "system",
            "status": "running",
            "message": "Iniciando validação dos serviços...",
            "diagnostics": {
                "task_id": task_id,
                "phase": "continuation_validation"
            }
        })
        
        # Importar RuntimeRunner para validar
        from agents.runtime_runner import RuntimeRunnerOrchestrator
        from agents.code_agent import CodeAgent
        
        project_path = result.project_path
        runtime_runner = RuntimeRunnerOrchestrator(project_path)
        
        # Get the LLM provider from pending_tasks (stored during initial generation)
        task_data = pending_tasks.get(task_id, {})
        llm_provider = task_data.get("llm_provider")
        
        if not llm_provider:
            logger.warning(f"[task_id={task_id}] No LLM provider found, creating new one")
            llm_provider = OllamaProvider(model="llama3.2")
        
        code_agent = CodeAgent(llm_provider)
        
        max_repair_attempts = 5
        repair_attempt = 0
        
        logger.info(f"[task_id={task_id}] Starting self-repair loop (max {max_repair_attempts} attempts)")
        
        while repair_attempt < max_repair_attempts:
            repair_attempt += 1
            
            logger.info(f"[task_id={task_id}] Self-Repair: Attempt {repair_attempt}/{max_repair_attempts}")
            await send_update("agent_status", {
                "agent": "system",
                "status": "running",
                "message": f"Validando serviços (tentativa {repair_attempt}/{max_repair_attempts})...",
                "diagnostics": {
                    "task_id": task_id,
                    "phase": f"self_repair_attempt_{repair_attempt}"
                }
            })
            
            # Execute validation
            logger.info(f"[task_id={task_id}] Running runtime validation...")
            validation_result = await runtime_runner.validate_and_fix()
            
            errors = validation_result.get("errors", [])
            failed_services = validation_result.get("failed", 0)
            
            # Extract detailed error info for frontend
            detailed_errors = []
            for err in errors:
                detailed_errors.append({
                    "type": err.get("type", "unknown"),
                    "service": err.get("service", "unknown"),
                    "message": err.get("message", ""),
                    "missing_dependency": err.get("missing_dependency")
                })
            
            logger.info(f"[task_id={task_id}] Validation: {failed_services} failed, {len(errors)} errors")
            
            # Check if validation passed
            if not errors and failed_services == 0:
                logger.info(f"[task_id={task_id}] Validation PASSED!")
                await send_update("agent_status", {
                    "agent": "system",
                    "status": "running",
                    "message": "Todos os serviços validados com sucesso!",
                    "diagnostics": {
                        "task_id": task_id,
                        "phase": "validation_passed"
                    }
                })
                break
            
            # Validation failed - show detailed errors to user
            logger.warning(f"[task_id={task_id}] Validation found issues: {failed_services} failed, {len(errors)} errors")
            
            # Create detailed error summary for frontend
            error_summary = f"{len(errors)} erros encontrados"
            if failed_services > 0:
                service_names = list(set([e.get("service", "?") for e in errors]))
                error_summary += f" em {len(service_names)} serviço(s): {', '.join(service_names[:3])}"
                if len(service_names) > 3:
                    error_summary += f" (+{len(service_names)-3} mais)"
            
            # Show first error as example
            if errors:
                first_error = errors[0]
                error_summary += f". Primeiro erro: {first_error.get('message', '')[:80]}"
            
            await send_update("agent_status", {
                "agent": "code_agent",
                "status": "running",
                "message": error_summary,
                "diagnostics": {
                    "task_id": task_id,
                    "phase": f"fixing_attempt_{repair_attempt}",
                    "errors_count": len(errors),
                    "failed_services": failed_services,
                    "detailed_errors": detailed_errors[:5]  # Send first 5 errors
                }
            })
            
            # Call CodeAgent to fix the errors
            fix_result = await code_agent.fix(
                requirement=requirement,
                runtime_errors=errors,
                attempt=repair_attempt,
                trace_id=task_id
            )
            
            if fix_result.success and fix_result.files_modified:
                logger.info(f"[task_id={task_id}] Fix applied: {len(fix_result.files_modified)} files modified")
                await send_update("agent_status", {
                    "agent": "code_agent",
                    "status": "running",
                    "message": f"Correção aplicada em {len(fix_result.files_modified)} arquivos",
                    "diagnostics": {
                        "task_id": task_id,
                        "files_modified": fix_result.files_modified
                    }
                })
            else:
                logger.warning(f"[task_id={task_id}] Fix attempt {repair_attempt} did not modify any files")
            
            # If this is the last attempt, we'll report the remaining errors
            if repair_attempt == max_repair_attempts:
                logger.warning(f"[task_id={task_id}] Max repair attempts reached")
        
        # Final validation check
        logger.info(f"[task_id={task_id}] Running final validation...")
        final_validation = await runtime_runner.validate_and_fix()
        
        final_errors = final_validation.get("errors", [])
        final_failed = final_validation.get("failed", 0)
        
        # ============================================================
        # PASSO 3: GERAR FRONTEND
        # ============================================================
        await send_update("agent_status", {
            "agent": "system",
            "status": "running",
            "message": "Gerando frontend...",
            "diagnostics": {
                "task_id": task_id,
                "phase": "generating_frontend"
            }
        })
        
        # Importar FrontendAgent
        from agents.frontend_agent import FrontendAgent
        
        # Criar instância do FrontendAgent
        frontend_agent = FrontendAgent(llm_provider)
        
        # Inicializar resultado do frontend (para caso de erro)
        frontend_result = None
        
        # Executar geração do frontend
        try:
            frontend_result = await frontend_agent.execute(project_path, requirement)
            
            if frontend_result.success:
                frontend_files_count = len(frontend_result.files_created)
                await send_update("agent_status", {
                    "agent": "system",
                    "status": "running",
                    "message": f"Frontend gerado: {frontend_files_count} arquivos",
                    "diagnostics": {
                        "task_id": task_id,
                        "phase": "frontend_generated",
                        "frontend_files": frontend_result.files_created
                    }
                })
            else:
                logger.warning(f"Frontend generation failed: {frontend_result.error_message}")
                await send_update("agent_status", {
                    "agent": "system",
                    "status": "running",
                    "message": f"Frontend generation failed: {frontend_result.error_message}",
                    "diagnostics": {
                        "task_id": task_id,
                        "phase": "frontend_failed"
                    }
                })
        except Exception as e:
            logger.error(f"Error generating frontend: {e}")
            await send_update("agent_status", {
                "agent": "system",
                "status": "running",
                "message": f"Erro ao gerar frontend: {str(e)}",
                "diagnostics": {
                    "task_id": task_id,
                    "phase": "frontend_error"
                }
            })
        
        # Limpa a task pendente
        if task_id in pending_tasks:
            del pending_tasks[task_id]
        
        # Verificar se o frontend foi gerado com sucesso
        frontend_generated = frontend_result is not None and frontend_result.success
        frontend_files = frontend_result.files_created if frontend_result and frontend_result.success else []
        
        if not final_errors and final_failed == 0:
            logger.info(f"[task_id={task_id}] SUCCESS! All services validated after {repair_attempt} attempts")
            await send_update("generation_success", {
                "message": f"Projeto gerado e corrigido! ({repair_attempt} tentativas de correção)",
                "project_path": result.project_path,
                "files_count": len(result.files_generated),
                "services": result.services,
                "frontend_files": frontend_files,
                "frontend_generated": frontend_generated,
                "trace_id": result.trace_id,
                "logs": result.execution_logs[-20:] + [f"✓ Self-repair: {repair_attempt} attempts, all services OK"],
                "diagnostics": {
                    "task_id": task_id,
                    "phase": "complete",
                    "repair_attempts": repair_attempt
                }
            })
        else:
            logger.warning(f"[task_id={task_id}] Some issues remain: {final_failed} failed, {len(final_errors)} errors")
            await send_update("generation_success", {
                "message": f"Bancos criados. {final_failed} serviços ainda têm problemas após {repair_attempt} tentativas",
                "project_path": result.project_path,
                "files_count": len(result.files_generated),
                "services": result.services,
                "frontend_files": frontend_files,
                "frontend_generated": frontend_generated,
                "trace_id": result.trace_id,
                "logs": result.execution_logs[-20:] + [f"⚠ Self-repair: {repair_attempt} attempts, {final_failed} services failed"],
                "diagnostics": {
                    "task_id": task_id,
                    "phase": "complete_with_warnings",
                    "remaining_errors": len(final_errors),
                    "failed_services": final_failed
                }
            })
        
    except Exception as e:
        logger.exception(f"[task_id={task_id}] Erro na continuação: {e}")
        
        # Limpa a task pendente mesmo com erro
        if task_id in pending_tasks:
            del pending_tasks[task_id]
        
        await send_update("generation_error", {
            "error": "continuation_failed",
            "message": f"Erro ao continuar: {str(e)}",
            "task_id": task_id
        })


# ==================== EXECUÇÃO DOS AGENTES ====================

async def execute_generation(
    task_id: str,
    requirements: str,
    model: str,
    output_dir: str,
    framework: str,
    database: str
):
    """
    Executa o fluxo de agentes e envia atualizações via WebSocket.
    """

    async def send_update(event_type: str, data: dict):
        """Envia atualização para o cliente."""
        message = {
            "type": event_type,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            **data
        }
        await manager.broadcast(message)
    
    # Usa o trace_id do task_id para o logger
    from agents.agent_logger import get_or_create_logger, reset_logger
    
    # Reseta logger anterior e cria novo com trace_id específico
    reset_logger()
    agent_logger = get_or_create_logger(
        trace_id=task_id,
        metadata={
            "requirements": requirements[:500],  # Limita tamanho
            "model": model,
            "framework": framework,
            "database": database,
            "output_dir": output_dir
        }
    )
    
    logger.info(f"[task_id={task_id}] Logger de execução inicializado: {agent_logger.execution_log_file}")

    try:
        logger.info(
            f"[task_id={task_id}] Iniciando execução | model={model} framework={framework} database={database} output={output_dir}"
        )

        await send_update("agent_status", {
            "agent": "system",
            "status": "starting",
            "message": "Inicializando sistema de agentes...",
            "diagnostics": {
                "task_id": task_id,
                "phase": "bootstrap"
            }
        })

        config = ProjectConfig(
            output_directory=output_dir,
            model=model,
            framework=framework,
            database=database
        )
        requirement = Requirement(description=requirements, project_config=config)

        await send_update("agent_status", {
            "agent": "system",
            "status": "running",
            "message": "Verificando Ollama...",
            "diagnostics": {
                "task_id": task_id,
                "phase": "ollama_preflight"
            }
        })

        if not check_ollama_installation():
            error_payload = build_error_payload(
                code="OLLAMA_NOT_INSTALLED",
                message="Ollama não está instalado no sistema.",
                task_id=task_id,
                hints=[
                    "Instale o Ollama em https://ollama.com.",
                    "Após instalar, execute `ollama list` no terminal para confirmar.",
                    "Reinicie a API após a instalação."
                ],
                context={"model": model}
            )
            logger.error(f"[task_id={task_id}] [error_id={error_payload['error_id']}] {error_payload['message']}")
            await send_update("generation_error", {
                **error_payload,
                "error": "ollama_not_installed"
            })
            return

        if not ensure_ollama_running():
            error_payload = build_error_payload(
                code="OLLAMA_START_FAILED",
                message="Não foi possível iniciar o Ollama.",
                task_id=task_id,
                hints=[
                    "Confirme se o serviço Ollama está em execução.",
                    "Teste manualmente com `ollama list` no terminal.",
                    "Verifique bloqueios de firewall/antivírus no host."
                ],
                context={"model": model}
            )
            logger.error(f"[task_id={task_id}] [error_id={error_payload['error_id']}] {error_payload['message']}")
            await send_update("generation_error", {
                **error_payload,
                "error": "ollama_not_running"
            })
            return

        await send_update("agent_status", {
            "agent": "system",
            "status": "running",
            "message": f"Inicializando modelo: {model}"
        })
        llm_provider = OllamaProvider(model=model)
        orchestrator = OrchestratorV3(llm_provider=llm_provider)

        await send_update("agent_status", {
            "agent": "orchestrator",
            "status": "running",
            "message": "Executando fluxo unificado: gerar → validar → testar → corrigir",
            "diagnostics": {
                "task_id": task_id,
                "phase": "orchestrator_execution"
            }
        })

        result = await orchestrator.execute(requirement)

        # Check if waiting for database creation
        if hasattr(result, 'waiting_for_databases') and result.waiting_for_databases:
            logger.info(f"[task_id={task_id}] Waiting for database creation")
            
            # Send message to frontend asking user to create databases
            await send_update("database_creation_required", {
                "message": "Por favor, crie os bancos de dados no pgAdmin antes de continuar",
                "database_urls": result.database_urls,
                "project_path": result.project_path,
                "files_count": len(result.files_generated),
                "services": result.services,
                "trace_id": result.trace_id,
                "logs": result.execution_logs[-20:],
                "task_id": task_id
            })
            
            # Store the result for continuation later
            # The frontend will call /api/continue/{task_id} when user confirms
            pending_tasks[task_id] = {
                "requirement": requirement,
                "result": result,
                "llm_provider": llm_provider,
                "orchestrator": orchestrator
            }
            
            return

        for log_line in result.execution_logs[-50:]:
            await send_update("agent_log", {
                "agent": "orchestrator",
                "status": "running",
                "message": log_line
            })

        if result.success:
            await send_update("generation_success", {
                "message": "Projeto gerado com sucesso!",
                "project_path": result.project_path,
                "files_count": len(result.files_generated),
                "services": result.services,
                "trace_id": result.trace_id,
                "logs": result.execution_logs[-20:],
                "diagnostics": {
                    "task_id": task_id,
                    "model": model,
                    "framework": framework,
                    "database": database
                }
            })
        else:
            error_payload = build_error_payload(
                code="ORCHESTRATOR_REJECTED_FLOW",
                message=result.error_message or "Fluxo de geração reprovado",
                task_id=task_id,
                hints=[
                    "Confira os últimos logs da timeline para identificar em qual agente falhou.",
                    "Use trace_id para correlacionar logs estruturados de agentes.",
                    "Revise os arquivos gerados para entender o motivo da reprovação."
                ],
                context={
                    "trace_id": result.trace_id,
                    "project_path": result.project_path,
                    "services": result.services
                }
            )
            await send_update("generation_error", {
                **error_payload,
                "trace_id": result.trace_id,
                "logs": result.execution_logs[-30:]
            })

    except Exception as e:
        error_payload = build_error_payload(
            code="UNHANDLED_EXECUTION_EXCEPTION",
            message="Erro fatal na execução da geração.",
            task_id=task_id,
            exception=e,
            hints=[
                "Verifique o stack trace retornado no frontend.",
                "Abra logs/api_server.log para mais contexto.",
                "Reexecute com requisitos mínimos para isolar o problema."
            ],
            context={
                "model": model,
                "framework": framework,
                "database": database,
                "output_dir": output_dir
            }
        )
        logger.exception(
            f"[task_id={task_id}] [error_id={error_payload['error_id']}] Erro na execução | payload={error_payload}"
        )
        await send_update("generation_error", {
            **error_payload
        })


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
