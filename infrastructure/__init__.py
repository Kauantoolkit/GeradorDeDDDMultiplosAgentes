"""
Infraestrutura do Sistema
=========================

Módulo de infraestrutura contendo:
- LLM Provider: Conexão com Ollama
- File Manager: Operações de arquivo
"""

from .llm_provider import OllamaProvider, PromptBuilder
from .file_manager import FileManager

__all__ = [
    "OllamaProvider",
    "PromptBuilder",
    "FileManager",
]
