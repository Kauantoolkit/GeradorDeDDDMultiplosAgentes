"""
Entidades do Sistema de Agentes
===============================

Define as entidades principais usadas no sistema de automação:
- Requisito: Representa os requisitos do projeto
- ValidationResult: Resultado da validação
- ExecutionResult: Resultado da execução de um agente
- ProjectConfig: Configurações do projeto
- BoundedContextSpec: Especificação de Contexto Delimitado DDD
- AggregateSpec: Especificação de Agregado DDD
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
import uuid


class AgentType(Enum):
    """Tipos de agentes no sistema (V3)."""
    CODE = "code"              # Unificado: geração + correção
    RUNTIME_RUNNER = "runtime_runner"  # Validação objetiva de runtime
    ROLLBACK = "rollback"       # Desfaz mudanças
    ORCHESTRATOR = "orchestrator"  # Coordena fluxo
    FRONTEND = "frontend"       # Gera frontend


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


# ============================================================
# DDD SPECIFICATIONS - Domain-Driven Design Structures
# ============================================================

@dataclass
class ValueObjectSpec:
    """
    Especificação de Value Object para DDD.
    Value Objects são imutáveis e comparados por valor.
    """
    name: str
    attributes: dict = field(default_factory=dict)
    validations: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)  # Comportamentos


@dataclass
class DomainEventSpec:
    """
    Especificação de Domain Event para DDD.
    Eventos de domínio representam ocorrências significativas.
    """
    name: str
    attributes: dict = field(default_factory=dict)
    related_aggregate: str = ""


@dataclass
class DomainServiceSpec:
    """
    Especificação de Domain Service para DDD.
    Services de domínio encapsulam operações que não pertencem a entidades.
    """
    name: str
    methods: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class EntitySpec:
    """
    Especificação de Entidade para DDD.
    Entidades têm identidade e ciclo de vida.
    """
    name: str
    attributes: dict = field(default_factory=dict)
    behaviors: list[str] = field(default_factory=list)  # Métodos com regras
    relationships: list[str] = field(default_factory=list)


@dataclass
class AggregateSpec:
    """
    Especificação de Aggregate Root para DDD.
    Agregado é um cluster de entidades e value objects com raiz.
    """
    name: str
    root_entity: str  # Nome da entidade raiz
    entities: list[str] = field(default_factory=list)  # Entidades internas
    value_objects: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)  # Regras de invariância
    behaviors: list[str] = field(default_factory=list)  # Comportamentos do agregado


@dataclass
class UseCaseSpec:
    """
    Especificação de Use Case para DDD.
    Use Cases orquestram agregados e serviços.
    """
    name: str
    input_dto: str = ""
    output_dto: str = ""
    aggregate: str = ""
    steps: list[str] = field(default_factory=list)
    validates_business_rules: bool = True


@dataclass
class BoundedContextSpec:
    """
    Especificação de Bounded Context para DDD.
    Representa um limite explícito onde um modelo de domínio é válido.
    """
    name: str  # Nome do contexto (ex: "Billing", "Academia", "Shipping")
    aggregate_root: str  # Nome do agregado raiz
    entities: list[EntitySpec] = field(default_factory=list)
    value_objects: list[ValueObjectSpec] = field(default_factory=list)
    domain_services: list[DomainServiceSpec] = field(default_factory=list)
    domain_events: list[DomainEventSpec] = field(default_factory=list)
    use_cases: list[UseCaseSpec] = field(default_factory=list)
    ports: list[str] = field(default_factory=list)  # APIs/endpoints
    dependencies: list[str] = field(default_factory=list)  # Outros contextos
    
    def to_dict(self) -> dict:
        """Converte para dicionário para uso em prompts."""
        return {
            "bounded_context": self.name,
            "aggregate_root": self.aggregate_root,
            "entities": [e.name for e in self.entities],
            "value_objects": [vo.name for vo in self.value_objects],
            "domain_services": [ds.name for ds in self.domain_services],
            "domain_events": [de.name for de in self.domain_events],
            "use_cases": [uc.name for uc in self.use_cases],
            "ports": self.ports,
            "dependencies": self.dependencies,
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
    Suporta tanto entrada textual quanto estruturada DDD.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # ID único da execução
    description: str = ""
    project_config: ProjectConfig = field(default_factory=ProjectConfig)
    microservices: list[MicroserviceSpec] = field(default_factory=list)
    
    # Novos campos para DDD estruturado
    bounded_contexts: list[BoundedContextSpec] = field(default_factory=list)
    use_ddd_mode: bool = False  # Se True, usa modo DDD completo
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_prompt(self) -> str:
        """Converte o requisito em um prompt para o agente."""
        config = self.project_config
        
        # Se tem contextos delimitados, usa modo DDD estruturado
        if self.use_ddd_mode and self.bounded_contexts:
            return self._to_ddd_prompt()
        
        # Modo tradicional (legado)
        return self._to_legacy_prompt()
    
    def _to_ddd_prompt(self) -> str:
        """Gera prompt no modo DDD estruturado."""
        contexts_info = []
        for ctx in self.bounded_contexts:
            ctx_info = f"""
=== Bounded Context: {ctx.name} ===
Aggregate Root: {ctx.aggregate_root}
Entities: {', '.join([e.name for e in ctx.entities])}
Value Objects: {', '.join([vo.name for vo in ctx.value_objects])}
Domain Services: {', '.join([ds.name for ds in ctx.domain_services])}
Use Cases: {', '.join([uc.name for uc in ctx.use_cases])}
"""
            contexts_info.append(ctx_info)
        
        return f"""
GERAÇÃO DE PROJETO COM DOMAIN-DRIVEN DESIGN (DDD)

Requisitos: {self.description}

Configurações Técnicas:
- Framework: {config.framework}
- Banco de Dados: {config.database}
- Diretório de Saída: {config.output_directory}
- Incluir Tests: {config.include_tests}
- Incluir Docker: {config.include_docker}

{' '.join(contexts_info)}

INSTRUÇÕES DDD OBRIGATÓRIAS:

1. ESTRUTURA DE CAMADAS (Clean Architecture):
   /domain          - Entidades, Value Objects, Aggregates, Events, Services
   /application    - Use Cases, DTOs, Mappers, Ports (interfaces)
   /infrastructure - Repositories (implementação), Database, Mappers
   /api            - Controllers, Routes, Schemas

2. REGRAS DDD:
   - DOMÍNIO NÃO PODE IMPORTAR NADA DE FRAMEWORK
   - Repositórios são INTERFACES no domínio, IMPLEMENTAÇÕES na infraestrutura
   - Entities têm comportamento (não são apenas dados)
   - Value Objects são imutáveis com validação
   - Aggregate Roots controlam invariantes
   - Domain Events representam ocorrências significativas

3. CADA ARQUIVO DEVE TER:
   - Código REAL e FUNCIONAL
   - Regras de negócio encapsuladas
   - Sem dependência de ORM no domínio

Gere a estrutura completa DDD com todos os arquivos necessários.
"""
    
    def _to_legacy_prompt(self) -> str:
        """Gera prompt no modo tradicional (legado)."""
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
    trace_id: str = ""  # ID único da execução para correlação de logs
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
    def approved(self) -> bool:
        """Compatibilidade retroativa para chamadores legados."""
        return self.is_approved
    
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
    database_urls: dict = field(default_factory=dict)  # URLs de banco para o usuário criar
    waiting_for_databases: bool = False  # Flag para indicar que está esperando criação de bancos
    
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
    trace_id: str = ""  # ID único da execução para correlação de logs
    project_path: str = ""
    services: list[str] = field(default_factory=list)
    files_generated: list[str] = field(default_factory=list)
    database_urls: dict = field(default_factory=dict)  # URLs de banco para o usuário criar
    error_message: str = ""
    execution_logs: list[str] = field(default_factory=list)
    rollback_performed: bool = False
    completed_at: datetime = field(default_factory=datetime.now)
    
    def add_log(self, message: str):
        """Adiciona uma mensagem ao log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.execution_logs.append(f"[{timestamp}] {message}")
