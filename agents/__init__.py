"""
Agentes do Sistema de Automação
===============================

Módulo contendo os agentes do sistema (V3):

- OrchestratorV3: Orquestrador principal com loop de auto-reparo
- CodeAgent: Agente unificado para geração e correção de código
- RuntimeRunner: Validação objetiva de runtime
- FrontendAgent: Geração de frontend
- RollbackAgent: Rollback em caso de erros
"""

# V3 agents (recommended)
from .orchestrator_v3 import OrchestratorV3, create_orchestrator_v3
from .code_agent import CodeAgent
from .runtime_runner import RuntimeRunner, RuntimeRunnerOrchestrator
from .frontend_agent import FrontendAgent
from .rollback_agent import RollbackAgent, RollbackManager

__all__ = [
    # V3 agents
    "OrchestratorV3",
    "create_orchestrator_v3",
    "CodeAgent",
    "RuntimeRunner",
    "RuntimeRunnerOrchestrator",
    "FrontendAgent",
    "RollbackAgent",
    "RollbackManager",
]
