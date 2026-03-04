"""
Infraestrutura do Sistema
=========================

Módulo de infraestrutura contendo:
- LLM Provider: Conexão com Ollama
- File Manager: Operações de arquivo
- Integrity Validator: Validação de código gerado
- Normalizer: Normalização de nomes de serviços
"""

from .llm_provider import OllamaProvider, PromptBuilder
from .file_manager import FileManager
from .integrity_validator import IntegrityValidator, validate_project
from .normalizer import (
    ServiceNameNormalizer,
    DomainNameNormalizer,
    EntityNameNormalizer,
    NameValidator,
    normalize_service_name,
    validate_and_normalize_service_name,
    validate_service_structure,
)

__all__ = [
    # LLM Provider
    "OllamaProvider",
    "PromptBuilder",
    # File Manager
    "FileManager",
    # Integrity Validator
    "IntegrityValidator",
    "validate_project",
    # Normalizer
    "ServiceNameNormalizer",
    "DomainNameNormalizer",
    "EntityNameNormalizer",
    "NameValidator",
    "normalize_service_name",
    "validate_and_normalize_service_name",
    "validate_service_structure",
]
