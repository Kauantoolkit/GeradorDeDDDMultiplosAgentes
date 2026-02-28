"""
Domain Entities
===============

Entidades do domínio do sistema de agentes.
"""

from .entities import (
    AgentType,
    ExecutionStatus,
    ExecutionResult,
    ValidationStatus,
    ValidationResult,
    ProjectConfig,
    ProjectGenerationResult,
    Requirement,
    MicroserviceSpec,
)

__all__ = [
    "AgentType",
    "ExecutionStatus",
    "ExecutionResult",
    "ValidationStatus",
    "ValidationResult",
    "ProjectConfig",
    "ProjectGenerationResult",
    "Requirement",
    "MicroserviceSpec",
]
