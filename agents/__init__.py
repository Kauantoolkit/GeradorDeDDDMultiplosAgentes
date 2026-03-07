"""
Agentes do Sistema de Automação
===============================

Módulo contendo os agentes do sistema:

NOVO (V3 - Refactored):
- OrchestratorV3: Simplified orchestrator with self-repair loop
- CodeAgent: Unified agent for code generation and fixing
- RuntimeRunner: Objective runtime validation

LEGACY (V2 - Deprecated):
- OrchestratorAgent: Original orchestrator
- ExecutorAgent: Code generation (merged into CodeAgent)
- ValidatorAgent: Validation (replaced by RuntimeRunner)
"""

# New V3 agents (recommended)
from .orchestrator_v3 import OrchestratorV3, create_orchestrator_v3
from .code_agent import CodeAgent
from .runtime_runner import RuntimeRunner, RuntimeRunnerOrchestrator

# Legacy V2 agents (deprecated but still available)
from .orchestrator import OrchestratorAgent, AgentWorkflow
from .orchestrator_v2 import OrchestratorAgent as OrchestratorAgentV2
from .executor_agent import ExecutorAgent
from .validator_agent import ValidatorAgent, ValidationRules
from .rollback_agent import RollbackAgent, RollbackManager
from .frontend_agent import FrontendAgent

__all__ = [
    # New V3 agents (recommended)
    "OrchestratorV3",
    "create_orchestrator_v3",
    "CodeAgent",
    "RuntimeRunner",
    "RuntimeRunnerOrchestrator",
    
    # Legacy V2 agents (deprecated)
    "OrchestratorAgent",
    "OrchestratorAgentV2",
    "ExecutorAgent",
    "ValidatorAgent",
    "ValidationRules",
    "RollbackAgent",
    "RollbackManager",
    "FrontendAgent",
    "AgentWorkflow",
]
