"""
Constantes de Mensagens e Níveis de Log
=======================================

Este arquivo define constantes para padronização de mensagens
e níveis de logging em todo o sistema de agentes.

Padrões de Logging:
- ERROR: Falhas que impedem continuação (exceções não tratadas, arquivos críticos não encontrados)
- WARNING: Problemas recuperáveis (fallback usado, valor padrão aplicado, arquivos opcionais não encontrados)
- INFO: Progresso normal (início/fim de operações bem-sucedidas)

Idioma:
- Mensagens de interface: Português
- Logs técnicos: Inglês (para debugging)

Uso:
    from agents.constants import AgentMessages, FileMessages, ValidationMessages, TechnicalMessages
    
    logger.info(AgentMessages.EXECUTOR_START)
    logger.info(FileMessages.FILE_CREATED.format(path="/path/to/file"))
"""

from enum import Enum


class LogLevel(Enum):
    """Níveis de log padronizados."""
    ERROR = "error"      # Falhas que impedem continuação
    WARNING = "warning"  # Problemas recuperáveis
    INFO = "info"        # Progresso normal


# ============================================================
# MENSAGENS DE AGENTES - PORTUGUÊS
# ============================================================

class AgentMessages:
    """Mensagens dos agentes em português."""
    
    # Executor Agent
    EXECUTOR_START = "EXECUTOR AGENT - Iniciando geração de código"
    EXECUTOR_COMPLETE = "Executor Agent concluído em {time}s"
    EXECUTOR_FAILED = "Executor Agent falhou: {error}"
    EXECUTOR_FILES_CREATED = "Arquivos criados: {count}"
    
    # Validator Agent
    VALIDATOR_START = "VALIDATOR AGENT - Iniciando validação"
    VALIDATOR_COMPLETE = "Validação concluída"
    VALIDATOR_APPROVED = "Validação APROVADA - Score: {score}"
    VALIDATOR_REJECTED = "Validação REPROVADA - Score: {score}"
    VALIDATOR_GUARDRAILS = "Guardrails de qualidade detectaram inconsistências: {issues}"
    VALIDATOR_MANUAL = "Realizando validação manual..."
    VALIDATOR_AUTO_REJECTED = "Executor Agent falhou - validação automática reprovada"
    
    # Fix Agent
    FIX_START = "FIX AGENT - Tentativa {attempt}"
    FIX_COMPLETE = "Correções aplicadas: {count} arquivos modificados"
    FIX_NO_ISSUES = "Nenhum problema identificado para corrigir"
    FIX_FILE_MODIFIED = "Modificado: {path}"
    FIX_FILE_CREATED = "Criado: {path}"
    FIX_FILE_IGNORED = "Ignorado (placeholder): {path}"
    FIX_FILE_NOT_FOUND = "Arquivo não encontrado: {path}"
    FIX_LLM_PARSE_ERROR = "Não foi possível parsear resposta do LLM para correção"
    
    # Rollback Agent
    ROLLBACK_START = "ROLLBACK AGENT - Iniciando rollback"
    ROLLBACK_COMPLETE = "Rollback concluído com sucesso"
    ROLLBACK_PARTIAL = "Rollback parcial: {count} arquivos não puderam ser removidos"
    ROLLBACK_NO_FILES = "Nenhum arquivo para remover"
    
    # Orchestrator
    ORCHESTRATOR_START = "ORCHESTRATOR AGENT - Iniciando fluxo completo"
    ORCHESTRATOR_PHASE_1 = "FASE 1: Executor Agent"
    ORCHESTRATOR_PHASE_2 = "FASE 2: Validator Agent"
    ORCHESTRATOR_PHASE_3 = "FASE 3: Docker Test Agent"
    ORCHESTRATOR_PHASE_4 = "FASE 4: Fix Agent"
    ORCHESTRATOR_SUCCESS = "Fluxo gerar->validar->testar aprovado!"
    ORCHESTRATOR_FAILED = "Fluxo falhou: {reason}"
    ORCHESTRATOR_MAX_ATTEMPTS = "Limite de tentativas de correção atingido"
    ORCHESTRATOR_RETRY = "Tentativa {attempt}/{max} falhou"


# ============================================================
# MENSAGENS DE ARQUIVOS - PORTUGUÊS
# ============================================================

class FileMessages:
    """Mensagens de operações de arquivo."""
    
    FILE_CREATED = "Arquivo criado: {path}"
    FILE_MODIFIED = "Arquivo modificado: {path}"
    FILE_DELETED = "Arquivo removido: {path}"
    FILE_NOT_FOUND = "Arquivo não encontrado: {path}"
    FILE_READ_ERROR = "Erro ao ler arquivo: {path}"
    FILE_WRITE_ERROR = "Erro ao criar arquivo: {path}"
    FILE_EMPTY = "Arquivo vazio: {path}"
    FILE_SYNTAX_ERROR = "Erro de sintaxe em {path}: {error}"
    
    DIR_CREATED = "Diretório criado: {path}"
    DIR_DELETED = "Diretório removido: {path}"
    DIR_NOT_FOUND = "Diretório não encontrado: {path}"


# ============================================================
# MENSAGENS DE VALIDAÇÃO - PORTUGUÊS
# ============================================================

class ValidationMessages:
    """Mensagens de validação."""
    
    PLACEHOLDER_FOUND = "Placeholder não substituído em {path}"
    DUPLICATE_ROUTE = "Rota duplicada detectada: {route}"
    MISSING_DEPENDENCY = "Dependência obrigatória ausente: {dep}"
    ENTITY_MISSING = "Entidade não encontrada: {entity}"
    INVALID_IMPORT = "Import inválido em {path}: {import_symbol}"
    DOMAIN_LAYER_VIOLATION = "Domínio importa de camada externa: {path}"
    ANEMIC_ENTITY = "Entidade anêmica detectada: {entity}"


# ============================================================
# MENSAGENS DE LOG TÉCNICO - INGLÊS
# ============================================================

class TechnicalMessages:
    """Mensagens técnicas em inglês para logs."""
    
    # Initialization
    AGENT_INITIALIZED = "{agent} initialized"
    PROVIDER_INITIALIZED = "{provider} initialized with model: {model}"
    FILE_MANAGER_INITIALIZED = "FileManager initialized at: {path}"
    
    # Execution
    STARTING_EXECUTION = "Starting execution..."
    EXECUTION_COMPLETE = "Execution complete in {time}s"
    EXECUTION_FAILED = "Execution failed: {error}"
    CALLING_LLM = "Calling LLM for {task}..."
    LLM_RESPONSE_RECEIVED = "LLM response received ({length} chars)"
    
    # Parsing
    JSON_PARSE_ERROR = "Failed to parse JSON: {error}"
    CONTENT_TRUNCATED = "Content truncated for debugging"
    JSON_EXTRACTED = "JSON extracted successfully"
    
    # Validation
    GUARDRAILS_TRIGGERED = "Guardrails triggered: {issues}"
    VALIDATION_FAILED = "Validation failed: {reason}"
    VALIDATION_SUCCESS = "Validation passed - Score: {score}"
    
    # Files
    FILE_SKIPPED = "File skipped: {reason}"
    CONTENT_INVALID = "Invalid content for {path}"
    PLACEHOLDER_DETECTED = "Unresolved placeholder detected: {placeholder}"
    FALLBACK_USED = "Using fallback for: {item}"
    ALTERNATIVE_PATH = "Found file at alternative path: {path}"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_message(template: str, **kwargs) -> str:
    """
    Formata uma mensagem com parâmetros.
    
    Args:
        template: Template da mensagem
        **kwargs: Parâmetros para substituição
        
    Returns:
        Mensagem formatada
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"{template} [ERROR: missing parameter: {e}]"


def get_log_level_for_error(error_type: str) -> LogLevel:
    """
    Determina o nível de log apropriado para um tipo de erro.
    
    Args:
        error_type: Tipo de erro ou descrição
        
    Returns:
        Nível de log apropriado
    """
    error_lower = error_type.lower()
    
    # Errors que impedem continuação -> ERROR
    critical_errors = [
        "syntax error",
        "import error", 
        "critical",
        "failed to start",
        "cannot proceed",
        "fatal",
        "unable to continue",
    ]
    
    # Problemas recuperáveis -> WARNING
    recoverable_errors = [
        "not found",
        "fallback",
        "optional",
        "skipped",
        "timeout",
        "retry",
        "alternative",
    ]
    
    if any(critical in error_lower for critical in critical_errors):
        return LogLevel.ERROR
    
    if any(recoverable in error_lower for recoverable in recoverable_errors):
        return LogLevel.WARNING
    
    return LogLevel.INFO


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    'LogLevel',
    'AgentMessages',
    'FileMessages', 
    'ValidationMessages',
    'TechnicalMessages',
    'format_message',
    'get_log_level_for_error',
]

