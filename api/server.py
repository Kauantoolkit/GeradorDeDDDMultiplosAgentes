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
from agents.orchestrator import OrchestratorAgent


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
        orchestrator = OrchestratorAgent(llm_provider=llm_provider)

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
