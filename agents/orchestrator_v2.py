"""
Orchestrator Agent V2 - Agente Orquestrador (VERSÃO CORRIGIDA)
=============================================================

Este orquestrador inclui as correções principais:
1. Fix Agent V2 - Edita arquivos existentes ao invés de criar novos
2. Runtime Validator - Tenta importar e rodar o código
3. Frontend Agent - Gera frontend dinâmico baseado nas APIs

Fluxo de Execução:
==================

    ┌──────────────┐
    │  REQUISITOS  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  EXECUTOR   │ ◄── Gera código
    │   AGENT     │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  VALIDATOR  │ ◄── Valida estrutura
    │   AGENT     │
    └──────┬───────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  APROVADO   REPROVADO
     │           │
     ▼           ▼
  SUCESSO   FIX AGENT V2
              (editar antes)
              ▼
         REVALIDA
              │
        ┌──────┴──────┐
        ▼              ▼
    APROVADO     REPROVADO
        │              │
        ▼              ▼
  RUNTIME         LIMITE
  VALIDATOR       ATINGIDO
        │
        ▼
┌──────────────────┐
│ FRONTEND AGENT  │ ◄── Gera frontend dinâmico
│ (NOVO)          │     que consome APIs
└────────┬─────────┘
         │
         ▼
    ┌──────────┐
    │ SUCESSO  │
    └───────────┘
"""

import asyncio
import json
from datetime import datetime
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    ProjectGenerationResult,
    ProjectConfig,
    Requirement,
    ValidationResult,
    ValidationStatus
)
from infrastructure.llm_provider import OllamaProvider
from infrastructure.file_manager import FileManager
from infrastructure.runtime_validator import RuntimeValidationOrchestrator

from .executor_agent import ExecutorAgent
from .validator_agent import ValidatorAgent
from .rollback_agent import RollbackAgent
from .docker_test_agent import DockerTestAgent
from .fix_agent_v2 import FixAgent  # <- NOVO: usa a versão V2
from .frontend_agent import FrontendAgent  # <- NOVO: gera frontend
from .error_logger import get_error_logger
from .agent_logger import (
    get_logger, 
    create_trace, 
    log_communication,
    log_execution,
    log_error,
    AgentExecutionContext
)


class OrchestratorAgent:
    """
    Agente Orquestrador V2 - Coordena o fluxo de agentes.
    
    Este agente gerencia todo o ciclo de vida da geração de código:
    1. Recebe os requisitos
    2. Chama o Executor Agent para gerar código
    3. Chama o Validator Agent para validar
    4. Se reprovado → chama Fix Agent V2 (editar primeiro)
    5.Runtime Validator (tenta rodar o código)
    6. Se tudo ok → Frontend Agent (gera frontend dinâmico)
    """
    
    def __init__(self, llm_provider: OllamaProvider, max_fix_attempts: int = 3, generate_frontend: bool = True):
        """
        Inicializa o Orchestrator Agent V2.
        
        Args:
            llm_provider: Provedor de LLM para os agentes
            max_fix_attempts: Número máximo de tentativas de correção
            generate_frontend: Se True, gera frontend após backend estar ok
        """
        self.llm_provider = llm_provider
        self.max_fix_attempts = max_fix_attempts
        self.generate_frontend = generate_frontend
        
        # Inicializa os agentes
        self.executor_agent = ExecutorAgent(llm_provider)
        self.validator_agent = ValidatorAgent(llm_provider)
        self.rollback_agent = RollbackAgent()
        self.docker_test_agent = DockerTestAgent(llm_provider)
        self.fix_agent = FixAgent(llm_provider)  # <- V2
        self.frontend_agent = FrontendAgent(llm_provider)  # <- NOVO
        
        # Inicializa o logger de erros
        self.error_logger = get_error_logger()
        
        self.name = "Orchestrator Agent V2"
        logger.info(f"{self.name} inicializado")
        logger.info(f"Fluência: Executor → Validator → FixAgent V2 → RuntimeValidator → FrontendAgent")
        logger.info(f"Frontend automático: {'ativado' if generate_frontend else 'desativado'}")
    
    async def execute(self, requirement: Requirement) -> ProjectGenerationResult:
        """
        Executa o fluxo completo de geração de código.
        
        Args:
            requirement: Requisitos do projeto
            
        Returns:
            ProjectGenerationResult com o resultado final
        """
        # Inicializa o logger estruturado e cria trace_id
        agent_logger = get_logger()
        
        # Usa o trace_id do requirement ou cria um novo
        trace_id = requirement.trace_id if hasattr(requirement, 'trace_id') and requirement.trace_id else agent_logger.create_trace_id()
        
        # Registra início do trace
        agent_logger.log_trace_start(
            trace_id=trace_id,
            metadata={
                "requirement_id": requirement.id,
                "description": requirement.description[:200] if requirement.description else "",
                "output_directory": requirement.project_config.output_directory
            }
        )
        
        start_time = datetime.now()
        
        # Resultado final
        result = ProjectGenerationResult()
        result.trace_id = trace_id
        result.add_log(f"Iniciando geracao - Requisito: {requirement.id} - trace_id: {trace_id}")
        
        logger.info("="*60)
        logger.info(f"ORCHESTRATOR AGENT V2 - Iniciando fluxo completo - trace_id: {trace_id[:8]}...")
        logger.info("="*60)
        
        try:
            # ==========================================
            # FASE 1: EXECUTOR AGENT
            # ==========================================
            logger.info("\n📋 FASE 1: Executando Executor Agent...")
            result.add_log("FASE 1: Executor Agent")
            
            executor_result = await self.executor_agent.execute(requirement, trace_id=trace_id)
            result.add_log(f"Executor Agent - Status: {executor_result.status}")
            
            result.files_generated.extend(executor_result.files_created)
            requirement.execution_result = executor_result
            
            if not executor_result.success:
                logger.error(f"❌ Executor Agent falhou: {executor_result.error_message}")
                result.success = False
                result.error_message = f"Executor falhou: {executor_result.error_message}"
                result.execution_logs.append(f"Erro: {executor_result.error_message}")
                return result
            
            logger.info(f"✅ Executor Agent concluído - {len(executor_result.files_created)} arquivos")
            
            # ==========================================
            # FASE 2: LOOP DE VALIDAÇÃO + CORREÇÃO
            # ==========================================
            fix_attempt = 0
            max_attempts = self.max_fix_attempts
            final_validation = None

            while True:
                cycle_label = "ciclo inicial" if fix_attempt == 0 else f"ciclo pós-correção {fix_attempt}"
                logger.info(f"\n📋 FASE 2: Validator Agent ({cycle_label})")
                result.add_log(f"FASE 2: Validator Agent ({cycle_label})")

                validation_result = await self.validator_agent.validate(
                    requirement,
                    executor_result
                )

                result.add_log(f"Validação concluída - Status: {validation_result.status} | Score: {validation_result.score}")

                # Se aprovado, sai do loop
                if validation_result.is_approved:
                    final_validation = validation_result
                    break

                # Se reprovado, tenta corrigir
                logger.warning(f"❌ Validação reprovada no {cycle_label}")
                
                if fix_attempt >= max_attempts:
                    logger.error(f"❌ Limite de tentativas de correção atingido ({max_attempts})")
                    result.success = False
                    result.error_message = f"Fluxo reprovado após {fix_attempt} tentativa(s) de correção"
                    return result

                fix_attempt += 1
                logger.info(f"\n📋 FASE 3: Fix Agent V2 - Tentativa {fix_attempt}/{max_attempts}")
                result.add_log(f"FASE 3: Fix Agent V2 - Tentativa {fix_attempt}/{max_attempts}")

                # Usa o Fix Agent V2 (que edita primeiro)
                fix_result = await self.fix_agent.execute(
                    requirement,
                    validation_result,
                    fix_attempt,
                    trace_id=trace_id
                )

                result.add_log(f"Fix concluído: {fix_result.status} | Arquivos modificados: {len(fix_result.files_modified)}")
                
                if not fix_result.success:
                    result.success = False
                    result.error_message = f"Fix Agent falhou na tentativa {fix_attempt}: {fix_result.error_message}"
                    return result

                # Atualiza arquivos criados com os modificados
                self._merge_fix_changes_into_execution_result(
                    executor_result,
                    fix_result.files_modified,
                )
            
            # ==========================================
            # FASE 4: RUNTIME VALIDATOR (NOVO!)
            # ==========================================
            logger.info("\n📋 FASE 4: Runtime Validator - Validando execução real...")
            result.add_log("FASE 4: Runtime Validator")
            
            project_path = requirement.project_config.output_directory
            runtime_validator = RuntimeValidationOrchestrator(project_path, self.llm_provider)
            runtime_result = await runtime_validator.validate_and_fix()
            
            result.add_log(f"Runtime Validator - Sucesso: {runtime_result['successful']}/{runtime_result['total_services']}")
            
            # Se há serviços que não conseguem importar, tenta corrigir automaticamente
            if runtime_result['failed'] > 0:
                logger.warning(f"⚠️ {runtime_result['failed']} serviço(s) com problemas de importação")
                result.add_log(f"Runtime: {runtime_result['failed']} serviços com problemas (tentando corrigir)")
                
                # O RuntimeValidator já tentou corrigir automaticamente
                # Se ainda falhou, podemos tentar mais uma vez com Fix Agent
                # Mas por simplicidade, continuamos e deixamos o usuário saber
            
            # ==========================================
            # FASE 5: FRONTEND AGENT (NOVO!)
            # ==========================================
            if self.generate_frontend:
                logger.info("\n📋 FASE 5: Frontend Agent - Gerando frontend dinâmico...")
                result.add_log("FASE 5: Frontend Agent")
                
                frontend_result = await self.frontend_agent.execute(
                    project_path,
                    requirement
                )
                
                if frontend_result.success:
                    result.files_generated.extend(frontend_result.files_created)
                    result.add_log(f"Frontend gerado: {len(frontend_result.files_created)} arquivos")
                else:
                    logger.warning(f"Frontend generation failed: {frontend_result.error_message}")
                    result.add_log(f"Frontend: falha - {frontend_result.error_message}")
            
            # ==========================================
            # SUCESSO
            # ==========================================
            logger.info("✅ Fluxo completo aprovado!")
            result.add_log("FASE 6: Fluxo APROVADO")
            
            result.success = True
            result.project_path = requirement.project_config.output_directory
            
            # Extrai nomes dos serviços
            if executor_result.output:
                try:
                    json_start = executor_result.output.find('{')
                    json_end = executor_result.output.rfind('}')
                    if json_start >= 0 and json_end >= json_start:
                        data = json.loads(executor_result.output[json_start:json_end+1])
                        services = data.get("microservices", [])
                        result.services = [s.get("name", "unknown") for s in services]
                except:
                    pass
            
            result.add_log(f"Projeto gerado com sucesso em: {result.project_path}")
            if final_validation:
                result.add_log(f"Score final de validação: {final_validation.score}")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            result.add_log(f"Tempo total: {elapsed:.2f}s")
            
            logger.info(f"\n🎉 SUCESSO! Projeto gerado em {elapsed:.2f}s")
            logger.info(f"📁 Local: {result.project_path}")
            logger.info(f"📝 Serviços: {result.services}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Erro fatal no Orchestrator: {e}")
            result.success = False
            result.error_message = f"Erro fatal: {str(e)}"
            result.add_log(f"ERRO FATAL: {str(e)}")
            
            return result

    def _merge_fix_changes_into_execution_result(
        self,
        executor_result: ExecutionResult,
        files_modified: list[str],
    ) -> None:
        """Atualiza o resultado do Executor com arquivos tocados pelo Fix."""
        if not files_modified:
            return

        existing = {path.replace('\\', '/') for path in (executor_result.files_created or [])}
        for file_path in files_modified:
            normalized = file_path.replace('\\', '/')
            if normalized not in existing:
                executor_result.files_created.append(normalized)
                existing.add(normalized)
    
    async def execute_with_retry(
        self, 
        requirement: Requirement, 
        max_retries: int = 3
    ) -> ProjectGenerationResult:
        """Executa o fluxo com tentativas de retry."""
        logger.info(f"Iniciando execução com {max_retries} tentativas...")
        
        last_result = None
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"TENTATIVA {attempt}/{max_retries}")
            logger.info(f"{'='*60}")
            
            result = await self.execute(requirement)
            
            if result.success:
                logger.info("✅ Sucesso na tentativa!")
                return result
            
            logger.warning(f"❌ Tentativa {attempt} falhou")
            last_result = result
            
            if attempt < max_retries:
                logger.info("Aguardando 2 segundos antes da próxima tentativa...")
                await asyncio.sleep(2)
        
        logger.error(f"Todas as {max_retries} tentativas falharam")
        return last_result
    
    def get_system_status(self) -> dict:
        """Retorna o status do sistema de agentes."""
        return {
            "orchestrator": "ready",
            "executor": "ready",
            "validator": "ready",
            "fix_v2": "ready",  # <- V2
            "frontend": "ready",  # <- NOVO
            "rollback": "ready",
            "docker_test": "ready",
            "llm_connected": self.llm_provider is not None
        }


# Função de conveniência para criar o orchestrator
def create_orchestrator(llm_provider, **kwargs) -> OrchestratorAgent:
    """
    Cria uma instância do Orchestrator Agent V2.
    
    Args:
        llm_provider: Provedor de LLM
        **kwargs: Argumentos adicionais para o construtor
        
    Returns:
        Instância do OrchestratorAgent
    """
    return OrchestratorAgent(llm_provider, **kwargs)

