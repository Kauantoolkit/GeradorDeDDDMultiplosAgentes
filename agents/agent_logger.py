"""
Agente Logger - Sistema de Logging Estruturado
==============================================

Este módulo fornece logging estruturado para o sistema de agentes,
com as seguintes funcionalidades:

- Geração de trace_id único por execução
- Geração de message_id único por mensagem
- Logging em formato JSON
- Persistência em arquivo dedicado
- Stack traces completos para erros
- Correlação de logs via trace_id

Uso:
    from agents.agent_logger import get_logger, create_trace
    
    # Criar contexto de execução
    logger = get_logger()
    trace_id = create_trace()
    
    # Log de execução de agente
    logger.log_agent_execution(
        agent_name="ExecutorAgent",
        trace_id=trace_id,
        input_data={"requirement": "..."},
        output_data={"files_created": ["..."]},
        execution_time_ms=15000
    )
"""

import json
import os
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from loguru import logger


class LogType(Enum):
    """Tipos de log suportados."""
    AGENT_EXECUTION = "AGENT_EXECUTION"
    AGENT_ERROR = "AGENT_ERROR"
    AGENT_COMMUNICATION = "AGENT_COMMUNICATION"
    TRACE_START = "TRACE_START"
    TRACE_END = "TRACE_END"
    SYSTEM_EVENT = "SYSTEM_EVENT"


class AgentLogger:
    """
    Logger Estruturado para Agentes.
    
    Fornece métodos para logging estruturado com:
    - trace_id para correlação deexecuções
    - message_id para cada comunicação
    - Logging em JSON para fácil parsing
    - Persistência em arquivo dedicado
    """
    
    def __init__(self, log_dir: str = "logs", log_file: str = "agent_execution.log"):
        """
        Inicializa o AgentLogger.
        
        Args:
            log_dir: Diretório para salvar os logs
            log_file: Nome do arquivo de log
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / log_file
        
        # Garante que o diretório existe
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configura o logger
        self._setup_logger()
        
        # Armazena traces ativos
        self._active_traces: dict[str, datetime] = {}
        
        print(f"[AgentLogger] Inicializado - Arquivo: {self.log_file}")
    
    def _setup_logger(self):
        """Configura o logger para persistência em arquivo."""
        # Remove handlers existentes do loguru
        logger.remove()
        
        # Adiciona handler para arquivo JSON
        logger.add(
            str(self.log_file),
            rotation="10 MB",
            retention="30 days",
            level="DEBUG",
            format="{message}",
            serialize=False  # We'll serialize manually
        )
        
        # Adiciona handler para console (opcional, em desenvolvimento)
        logger.add(
            lambda msg: print(f"[AGENT] {msg}"),
            level="INFO",
            format="{time:HH:mm:ss} | {level} | {message}"
        )
    
    def _serialize_log(self, log_entry: dict) -> str:
        """
        Serializa entrada de log para JSON.
        
        Args:
            log_entry: Dicionário com dados do log
            
        Returns:
            String JSON formatada
        """
        return json.dumps(log_entry, ensure_ascii=False, indent=None)
    
    def _write_log(self, log_entry: dict):
        """
        Escreve log no arquivo.
        
        Args:
            log_entry: Dicionário com dados do log
        """
        try:
            log_line = self._serialize_log(log_entry)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except Exception as e:
            print(f"[AgentLogger] Erro ao escrever log: {e}")
    
    def create_trace_id(self) -> str:
        """
        Cria um novo trace_id único.
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    def create_message_id(self) -> str:
        """
        Cria um novo message_id único.
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    def log_agent_execution(
        self,
        agent_name: str,
        trace_id: str,
        input_data: Optional[dict] = None,
        output_data: Optional[dict] = None,
        execution_time_ms: float = 0.0,
        status: str = "success",
        error: Optional[dict] = None
    ) -> str:
        """
        Registra execução de um agente.
        
        Args:
            agent_name: Nome do agente
            trace_id: ID da execução
            input_data: Dados de entrada
            output_data: Dados de saída
            execution_time_ms: Tempo de execução em milissegundos
            status: Status da execução (success/failure)
            error: Dados do erro (se houver)
            
        Returns:
            message_id gerado
        """
        message_id = self.create_message_id()
        
        # Limita tamanho dos dados para evitar logs excessivamente grandes
        input_serializable = self._make_serializable(input_data) if input_data else None
        output_serializable = self._make_serializable(output_data) if output_data else None
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "message_id": message_id,
            "type": LogType.AGENT_ERROR.value if error else LogType.AGENT_EXECUTION.value,
            "agent_name": agent_name,
            "input": input_serializable,
            "output": output_serializable,
            "execution_time_ms": round(execution_time_ms, 2),
            "status": status,
        }
        
        if error:
            log_entry["error"] = error
        
        # Escreve no arquivo
        self._write_log(log_entry)
        
        # Também log no loguru para debug
        logger.info(
            f"AGENT_EXECUTION | {agent_name} | trace_id={trace_id[:8]}... | "
            f"time={execution_time_ms:.0f}ms | status={status}"
        )
        
        return message_id
    
    def log_agent_error(
        self,
        agent_name: str,
        trace_id: str,
        error: Exception,
        input_data: Optional[dict] = None,
        context: Optional[dict] = None
    ) -> str:
        """
        Registra erro de um agente com stack trace completo.
        
        Args:
            agent_name: Nome do agente
            trace_id: ID da execução
            error: Exception ocorrida
            input_data: Dados de entrada (opcional)
            context: Contexto adicional (opcional)
            
        Returns:
            message_id gerado
        """
        message_id = self.create_message_id()
        
        # Captura stack trace
        stack_trace = traceback.format_exc()
        
        # Limita tamanho dos dados
        input_serializable = self._make_serializable(input_data) if input_data else None
        context_serializable = self._make_serializable(context) if context else None
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "message_id": message_id,
            "type": LogType.AGENT_ERROR.value,
            "agent_name": agent_name,
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "stack_trace": stack_trace
            },
            "input": input_serializable,
            "context": context_serializable,
            "status": "failure"
        }
        
        # Escreve no arquivo
        self._write_log(log_entry)
        
        # Também log no loguru
        logger.error(
            f"AGENT_ERROR | {agent_name} | trace_id={trace_id[:8]}... | "
            f"error={type(error).__name__}: {str(error)}"
        )
        
        return message_id
    
    def log_agent_communication(
        self,
        from_agent: str,
        to_agent: str,
        trace_id: str,
        payload: Optional[dict] = None,
        status: str = "success",
        execution_time_ms: float = 0.0
    ) -> str:
        """
        Registra comunicação entre agentes.
        
        Args:
            from_agent: Agente remetente
            to_agent: Agente destinatário
            trace_id: ID da execução
            payload: Dados enviados
            status: Status da comunicação
            execution_time_ms: Tempo de execução
            
        Returns:
            message_id gerado
        """
        message_id = self.create_message_id()
        
        payload_serializable = self._make_serializable(payload) if payload else None
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "message_id": message_id,
            "type": LogType.AGENT_COMMUNICATION.value,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "payload": payload_serializable,
            "status": status,
            "execution_time_ms": round(execution_time_ms, 2)
        }
        
        # Escreve no arquivo
        self._write_log(log_entry)
        
        # Log no loguru
        direction = f"{from_agent} → {to_agent}"
        logger.info(
            f"AGENT_COMMUNICATION | {direction} | trace_id={trace_id[:8]}... | "
            f"time={execution_time_ms:.0f}ms | status={status}"
        )
        
        return message_id
    
    def log_trace_start(self, trace_id: str, metadata: Optional[dict] = None) -> None:
        """
        Registra início de uma execução (trace).
        
        Args:
            trace_id: ID da execução
            metadata: Metadados adicionais
        """
        metadata_serializable = self._make_serializable(metadata) if metadata else None
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "message_id": self.create_message_id(),
            "type": LogType.TRACE_START.value,
            "metadata": metadata_serializable
        }
        
        self._write_log(log_entry)
        self._active_traces[trace_id] = datetime.now(timezone.utc)
        
        logger.info(f"TRACE_START | trace_id={trace_id[:8]}...")
    
    def log_trace_end(
        self,
        trace_id: str,
        status: str = "success",
        summary: Optional[dict] = None
    ) -> None:
        """
        Registra fim de uma execução (trace).
        
        Args:
            trace_id: ID da execução
            status: Status final (success/failure)
            summary: Resumo da execução
        """
        # Calcula duração total
        start_time = self._active_traces.get(trace_id)
        duration_ms = 0.0
        if start_time:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        summary_serializable = self._make_serializable(summary) if summary else None
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "message_id": self.create_message_id(),
            "type": LogType.TRACE_END.value,
            "status": status,
            "total_duration_ms": round(duration_ms, 2),
            "summary": summary_serializable
        }
        
        self._write_log(log_entry)
        
        if trace_id in self._active_traces:
            del self._active_traces[trace_id]
        
        logger.info(f"TRACE_END | trace_id={trace_id[:8]}... | status={status} | duration={duration_ms:.0f}ms")
    
    def _make_serializable(self, obj: Any, max_depth: int = 5, current_depth: int = 0) -> Any:
        """
        Converte objetos para formato serializável JSON.
        
        Args:
            obj: Objeto a serializar
            max_depth: Profundidade máxima de recursão
            current_depth: Profundidade atual
            
        Returns:
            Dicionário serializável
        """
        if current_depth >= max_depth:
            return f"<max_depth_reached: {type(obj).__name__}>"
        
        if obj is None:
            return None
        
        if isinstance(obj, (str, int, float, bool)):
            # Limita strings muito longas
            if isinstance(obj, str) and len(obj) > 10000:
                return obj[:10000] + "... [truncated]"
            return obj
        
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        if isinstance(obj, Enum):
            return obj.value
        
        if isinstance(obj, (list, tuple)):
            return [
                self._make_serializable(item, max_depth, current_depth + 1)
                for item in obj[:100]  # Limita a 100 itens
            ]
        
        if hasattr(obj, '__dict__'):
            # Converte dataclass ou objeto
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    result[key] = self._make_serializable(value, max_depth, current_depth + 1)
            return result
        
        if hasattr(obj, 'to_dict') and callable(obj.to_dict):
            return self._make_serializable(obj.to_dict(), max_depth, current_depth + 1)
        
        # Fallback para string
        try:
            return str(obj)
        except:
            return f"<unserializable: {type(obj).__name__}>"
    
    def get_trace_summary(self, trace_id: str) -> list[dict]:
        """
        Retorna todos os logs de uma execução específica.
        
        Args:
            trace_id: ID da execução
            
        Returns:
            Lista de entradas de log
        """
        if not self.log_file.exists():
            return []
        
        logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("trace_id") == trace_id:
                            logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Erro ao ler logs: {e}")
        
        return logs


# Instância global do logger
_agent_logger_instance: Optional[AgentLogger] = None


def get_logger() -> AgentLogger:
    """
    Retorna a instância global do AgentLogger.
    
    Returns:
        Instância do AgentLogger
    """
    global _agent_logger_instance
    
    if _agent_logger_instance is None:
        _agent_logger_instance = AgentLogger()
    
    return _agent_logger_instance


def create_trace(metadata: Optional[dict] = None) -> str:
    """
    Cria um novo trace_id e registra início.
    
    Args:
        metadata: Metadados adicionais
        
    Returns:
        trace_id criado
    """
    agent_logger = get_logger()
    trace_id = agent_logger.create_trace_id()
    agent_logger.log_trace_start(trace_id, metadata)
    return trace_id


def get_trace_id() -> Optional[str]:
    """
    Retorna um novo trace_id (para uso interno).
    
    Returns:
        trace_id único
    """
    agent_logger = get_logger()
    return agent_logger.create_trace_id()


class AgentExecutionContext:
    """
    Contexto de execução de um agente.
    
    Mantém o estado da execução atual e fornece
    métodos convenientes para logging.
    """
    
    def __init__(
        self,
        agent_name: str,
        trace_id: str,
        input_data: Optional[dict] = None
    ):
        """
        Inicializa o contexto de execução.
        
        Args:
            agent_name: Nome do agente
            trace_id: ID da execução
            input_data: Dados de entrada
        """
        self.agent_name = agent_name
        self.trace_id = trace_id
        self.input_data = input_data
        self.start_time = datetime.now()
        self.message_id: Optional[str] = None
        self.output_data: Optional[dict] = None
        self.error: Optional[Exception] = None
        self._logger = get_logger()
    
    def start(self) -> str:
        """
        Inicia o contexto e retorna message_id.
        
        Returns:
            message_id gerado
        """
        self.message_id = self._logger.create_message_id()
        return self.message_id
    
    def end(
        self,
        output_data: Optional[dict] = None,
        status: str = "success",
        error: Optional[Exception] = None
    ) -> float:
        """
        Finaliza o contexto e registra o log.
        
        Args:
            output_data: Dados de saída
            status: Status da execução
            error: Erro (se houver)
            
        Returns:
            Tempo de execução em milissegundos
        """
        # Calcula tempo de execução
        execution_time_ms = (datetime.now() - self.start_time).total_seconds() * 1000
        
        self.output_data = output_data
        self.error = error
        
        # Converte erro para dict se necessário
        error_dict = None
        if error:
            error_dict = {
                "type": type(error).__name__,
                "message": str(error)
            }
        
        # Log da execução
        self._logger.log_agent_execution(
            agent_name=self.agent_name,
            trace_id=self.trace_id,
            input_data=self._logger._make_serializable(self.input_data),
            output_data=self._logger._make_serializable(output_data),
            execution_time_ms=execution_time_ms,
            status=status,
            error=error_dict
        )
        
        return execution_time_ms
    
    def end_with_error(self, error: Exception, context: Optional[dict] = None) -> float:
        """
        Finaliza o contexto com erro.
        
        Args:
            error: Exception ocorrida
            context: Contexto adicional
            
        Returns:
            Tempo de execução em milissegundos
        """
        execution_time_ms = (datetime.now() - self.start_time).total_seconds() * 1000
        
        # Log do erro
        self._logger.log_agent_error(
            agent_name=self.agent_name,
            trace_id=self.trace_id,
            error=error,
            input_data=self._logger._make_serializable(self.input_data),
            context=context
        )
        
        return execution_time_ms
    
    def log_communication(
        self,
        to_agent: str,
        payload: Optional[dict] = None,
        status: str = "success"
    ) -> str:
        """
        Registra comunicação para outro agente.
        
        Args:
            to_agent: Agente destinatário
            payload: Dados enviados
            status: Status
            
        Returns:
            message_id gerado
        """
        return self._logger.log_agent_communication(
            from_agent=self.agent_name,
            to_agent=to_agent,
            trace_id=self.trace_id,
            payload=payload,
            status=status
        )


# Funções de conveniência para uso rápido
def log_execution(
    agent_name: str,
    trace_id: str,
    input_data: Optional[dict] = None,
    output_data: Optional[dict] = None,
    execution_time_ms: float = 0.0,
    status: str = "success",
    error: Optional[dict] = None
) -> str:
    """
    Função de conveniência para logging de execução.
    
    Args:
        agent_name: Nome do agente
        trace_id: ID da execução
        input_data: Dados de entrada
        output_data: Dados de saída
        execution_time_ms: Tempo de execução
        status: Status
        error: Erro
        
    Returns:
        message_id
    """
    return get_logger().log_agent_execution(
        agent_name=agent_name,
        trace_id=trace_id,
        input_data=input_data,
        output_data=output_data,
        execution_time_ms=execution_time_ms,
        status=status,
        error=error
    )


def log_error(
    agent_name: str,
    trace_id: str,
    error: Exception,
    input_data: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    """
    Função de conveniência para logging de erro.
    
    Args:
        agent_name: Nome do agente
        trace_id: ID da execução
        error: Exception
        input_data: Dados de entrada
        context: Contexto adicional
        
    Returns:
        message_id
    """
    return get_logger().log_agent_error(
        agent_name=agent_name,
        trace_id=trace_id,
        error=error,
        input_data=input_data,
        context=context
    )


def log_communication(
    from_agent: str,
    to_agent: str,
    trace_id: str,
    payload: Optional[dict] = None,
    status: str = "success",
    execution_time_ms: float = 0.0
) -> str:
    """
    Função de conveniência para logging de comunicação.
    
    Args:
        from_agent: Agente remetente
        to_agent: Agente destinatário
        trace_id: ID da execução
        payload: Dados enviados
        status: Status
        execution_time_ms: Tempo de execução
        
    Returns:
        message_id
    """
    return get_logger().log_agent_communication(
        from_agent=from_agent,
        to_agent=to_agent,
        trace_id=trace_id,
        payload=payload,
        status=status,
        execution_time_ms=execution_time_ms
    )

