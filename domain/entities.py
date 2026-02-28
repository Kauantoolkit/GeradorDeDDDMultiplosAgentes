"""
Entidades do Sistema de Agentes
===============================

Define as entidades principais usadas no sistema de automação:
- Requisito: Representa os requisitos do projeto
- ValidationResult: Resultado da validação
- ExecutionResult: Resultado da execução de um agente
- ProjectConfig: Configurações do projeto
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid


class AgentType(Enum):
    """Tipos de agentes no sistema."""
    EXECUTOR = "executor"       # Gera código
    VALIDATOR = "validator"     # Valida código
    ROLLBACK = "rollback"       # Desfaz mudanças
    ORCHESTRATOR = "orchestrator"  # Coordena fluxo
    DOCKER_TEST = "docker_test"    # Valida containers Docker
    FIX = "fix"                 # Corrige problemas


class ValidationStatus(Enum):
    """Status de validação."""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class ExecutionStatus(Enum):
    """Status de execução de um agente."""
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACKED = "rollbacked"
    IN_PROGRESS = "in_progress"


@dataclass
class ProjectConfig:
    """Configurações do projeto a ser gerado."""
    output_directory: str = "generated"
    model: str = "llama3.2"
    framework: str = "python-fastapi"
    database: str = "postgresql"
    include_tests: bool = True
    include_docker: bool = True
    
    def to_dict(self) -> dict:
        return {
            "output_directory": self.output_directory,
            "model": self.model,
            "framework": self.framework,
            "database": self.database,
            "include_tests": self.include_tests,
            "include_docker": self.include_docker,
        }


@dataclass
class MicroserviceSpec:
    """Especificação de um microserviço."""
    name: str
    domain: str
    entities: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    ports: list[str] = field(default_factory=list)  # entrypoints/APIs
    dependencies: list[str] = field(default_factory=list)


@dataclass
class Requirement:
    """
    Representa os requisitos do projeto informados pelo usuário.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    project_config: ProjectConfig = field(default_factory=ProjectConfig)
    microservices: list[MicroserviceSpec] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_prompt(self) -> str:
        """Converte o requisito em um prompt para o agente."""
        config = self.project_config
        return f"""
Requisitos do Projeto:
{self.description}

Configurações Técnicas:
- Framework: {config.framework}
- Banco de Dados: {config.database}
- Diretório de Saída: {config.output_directory}
- Incluir Tests: {config.include_tests}
- Incluir Docker: {config.include_docker}

Gere uma estrutura de microserviços usando DDD (Domain-Driven Design) com:
- Domínios (Domains)
- Aplicação (Application)
- Infraestrutura (Infrastructure)  
- API (Presentation)
- Entidades, Value Objects, Aggregates
- Repositories, Services, Use Cases
- APIs RESTful

Identifique os microserviços necessários e defina sua estrutura completa.
"""


@dataclass
class ValidationResult:
    """
    Resultado da validação realizada pelo Validator Agent.
    """
    requirement_id: str
    status: ValidationStatus = ValidationStatus.PENDING
    approved_items: list[str] = field(default_factory=list)
    rejected_items: list[str] = field(default_factory=list)
    missing_items: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    score: float = 0.0  # 0.0 a 1.0
    feedback: str = ""
    validated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_approved(self) -> bool:
        return self.status == ValidationStatus.APPROVED
    
    @property
    def needs_rollback(self) -> bool:
        return self.status == ValidationStatus.REJECTED
    
    def approve(self):
        """Aprova a validação."""
        self.status = ValidationStatus.APPROVED
        self.score = 1.0
    
    def reject(self, reason: str):
        """Rejeita a validação."""
        self.status = ValidationStatus.REJECTED
        self.issues.append(reason)
        # Note: We keep the calculated score instead of setting it to 0.0
        # The score was already calculated before calling reject()


@dataclass
class ExecutionResult:
    """
    Resultado da execução de um agente.
    """
    agent_type: AgentType
    status: ExecutionStatus
    output: str = ""
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    error_message: str = ""
    execution_time: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime = field(default_factory=datetime.now)
    validation_result: ValidationResult | None = None
    
    @property
    def success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS
    
    @property
    def needs_rollback(self) -> bool:
        return self.status == ExecutionStatus.FAILED


@dataclass
class ProjectGenerationResult:
    """
    Resultado final da geração do projeto.
    """
    success: bool = False
    project_path: str = ""
    services: list[str] = field(default_factory=list)
    files_generated: list[str] = field(default_factory=list)
    error_message: str = ""
    execution_logs: list[str] = field(default_factory=list)
    rollback_performed: bool = False
    completed_at: datetime = field(default_factory=datetime.now)
    
    def add_log(self, message: str):
        """Adiciona uma mensagem ao log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.execution_logs.append(f"[{timestamp}] {message}")
