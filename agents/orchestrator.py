"""
Orchestrator Agent - Agente Orquestrador
=========================================

Este agente é responsável por:
- Coordenar o fluxo completo entre os agentes
- Gerenciar o estado da execução
- Decidir quando acionar cada agente
- Controlar o ciclo de execução, validação e correção
- Retornar o resultado final da geração

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
    │  VALIDATOR  │ ◄── Valida código
    │   AGENT     │
    └──────┬───────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  APROVADO   REPROVADO
     │           │
     ▼           ▼
  SUCESSO   FIX AGENT
              (loop)
              ▼
         REVALIDA
              │
        ┌──────┴──────┐
        ▼              ▼
    APROVADO     REPROVADO
        │              │
        ▼              ▼
   SUCESSO      FALHA
           (arquivos mantidos para debug)
"""

import asyncio
from datetime import datetime
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    ProjectGenerationResult,
    ProjectConfig,
    Requirement,
    ValidationStatus
)
from infrastructure.llm_provider import OllamaProvider
from infrastructure.file_manager import FileManager

from .executor_agent import ExecutorAgent
from .validator_agent import ValidatorAgent
from .rollback_agent import RollbackAgent
from .docker_test_agent import DockerTestAgent
from .fix_agent import FixAgent
from .error_logger import get_error_logger
from .agent_logger import get_logger, create_trace, log_communication


class OrchestratorAgent:
    """
    Agente Orquestrador - Coordena o fluxo de agentes.
    
    Este agente gerencia todo o ciclo de vida da geração de código:
    1. Recebe os requisitos
    2. Chama o Executor Agent para gerar código
    3. Chama o Validator Agent para validar
    4. Se aprovado → retorna sucesso
    5. Se reprovado → chama Fix Agent para correção → revalida
    6. Se ainda reprovado após limite → Mantém arquivos para debug
    """
    
    def __init__(self, llm_provider: OllamaProvider, max_fix_attempts: int = 3):
        """
        Inicializa o Orchestrator Agent.
        
        Args:
            llm_provider: Provedor de LLM para os agentes
            max_fix_attempts: Número máximo de tentativas de correção
        """
        self.llm_provider = llm_provider
        self.max_fix_attempts = max_fix_attempts
        
        # Inicializa os agentes
        self.executor_agent = ExecutorAgent(llm_provider)
        self.validator_agent = ValidatorAgent(llm_provider)
        self.rollback_agent = RollbackAgent()
        self.docker_test_agent = DockerTestAgent(llm_provider)
        self.fix_agent = FixAgent(llm_provider)
        
        # Inicializa o logger de erros
        self.error_logger = get_error_logger()
        
        self.name = "Orchestrator Agent"
        logger.info(f"{self.name} inicializado")
        logger.info(f"Fluência: Executor → Validator → Fix Agent (max {max_fix_attempts}x) → Docker Test")
    
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
        result.trace_id = trace_id  # Armazena trace_id no resultado
        result.add_log(f"Iniciando geracao - Requisito: {requirement.id} - trace_id: {trace_id}")
        
        logger.info("="*60)
        logger.info(f"ORCHESTRATOR AGENT - Iniciando fluxo completo - trace_id: {trace_id[:8]}...")
        logger.info("="*60)
        
        try:
            # ==========================================
            # FASE 1: EXECUTOR AGENT
            # ==========================================
            logger.info("\n📋 FASE 1: Executando Executor Agent...")
            result.add_log("FASE 1: Executor Agent")
            
            executor_result = await self.executor_agent.execute(requirement)
            result.add_log(f"Executor Agent - Status: {executor_result.status}")
            
            # Log de comunicacao entre agentes
            log_communication(
                from_agent="OrchestratorAgent",
                to_agent="ExecutorAgent",
                trace_id=trace_id,
                payload={"requirement_id": requirement.id},
                status="success" if executor_result.success else "failure",
                execution_time_ms=0
            )
            
            result.files_generated.extend(executor_result.files_created)
            
            if not executor_result.success:
                # Executor falhou, já sabemos o resultado
                logger.error(f"❌ Executor Agent falhou: {executor_result.error_message}")
                result.success = False
                result.error_message = f"Executor falhou: {executor_result.error_message}"
                result.execution_logs.append(f"Erro: {executor_result.error_message}")
                
                return result
            
            logger.info(f"✅ Executor Agent concluído - {len(executor_result.files_created)} arquivos")
            
            # ==========================================
            # FASE 2: VALIDATOR AGENT
            # ==========================================
            logger.info("\n📋 FASE 2: Executando Validator Agent...")
            result.add_log("FASE 2: Validator Agent")
            
            validation_result = await self.validator_agent.validate(
                requirement, 
                executor_result
            )
            
            # Log de comunicacao Executor -> Validator
            log_communication(
                from_agent="ExecutorAgent",
                to_agent="ValidatorAgent",
                trace_id=trace_id,
                payload={"requirement_id": requirement.id},
                status="success",
                execution_time_ms=0
            )
            
            result.add_log(f"Validacao concluida - Status: {validation_result.status}")
            result.add_log(f"Score: {validation_result.score}")
            
            if validation_result.needs_rollback:
                # ==========================================
                # FASE 3: FIX AGENT (loop de correção)
                # ==========================================
                logger.warning(f"❌ Validação reprovada: {validation_result.feedback}")
                result.add_log(f"VALIDAÇÃO REPROVADA: {validation_result.feedback}")
                
                # Loop de correção com Fix Agent
                fix_attempt = 0
                max_attempts = self.max_fix_attempts
                validation_approved = False
                
                while fix_attempt < max_attempts:
                    fix_attempt += 1
                    
                    logger.info(f"\n📋 FASE 3: Fix Agent - Tentativa {fix_attempt}/{max_attempts}")
                    result.add_log(f"FASE 3: Fix Agent - Tentativa {fix_attempt}/{max_attempts}")
                    
                    # Executa correção
                    fix_result = await self.fix_agent.execute(
                        requirement,
                        validation_result,
                        fix_attempt
                    )
                    
                    result.add_log(f"Fix concluído: {fix_result.status}")
                    
                    # Revalida após correção
                    logger.info("Revalidando após correção...")
                    validation_result = await self.validator_agent.validate(
                        requirement,
                        executor_result
                    )
                    
                    result.add_log(f"Re-validação - Status: {validation_result.status}, Score: {validation_result.score}")
                    
                    if not validation_result.needs_rollback:
                        validation_approved = True
                        logger.info(f"✅ Validação APROVADA após {fix_attempt} tentativa(s) de correção!")
                        result.add_log(f"Validação aprovada após {fix_attempt} correção(ões)")
                        break
                    
                    logger.warning(f"❌ Ainda precisa de correção - Tentativa {fix_attempt}/{max_attempts}")
                    
                    if fix_attempt >= max_attempts:
                        logger.error(f"❌ Limite de tentativas de correção atingido ({max_attempts})")
                        result.add_log(f"Limite de correções atingido ({max_attempts})")
                
                # Se não conseguiu aprovar após correções, mantém os arquivos para debug
                if not validation_approved:
                    logger.warning("Fix Agent não conseguiu corrigir. Arquivos mantidos para debug.")
                    result.add_log("FASE 3b: Validação falhou - Arquivos mantidos para debug")
                    
                    result.success = False
                    result.error_message = (
                        f"Validação reprovada (score final: {validation_result.score}). "
                        f"Foram realizadas {fix_attempt} tentativa(s) de correção. "
                        "Os arquivos gerados foram mantidos para debug."
                    )
                    return result
            
            # ==========================================
            # FASE 4: DOCKER TEST AGENT (opcional)
            # ==========================================
            logger.info("\n📋 FASE 4: Executando Docker Test Agent...")
            result.add_log("FASE 4: Docker Test Agent")
            
            docker_test_result = await self.docker_test_agent.execute(
                requirement, 
                executor_result
            )
            
            # Log de comunicacao Validator -> DockerTestAgent
            log_communication(
                from_agent="ValidatorAgent",
                to_agent="DockerTestAgent",
                trace_id=trace_id,
                payload={"requirement_id": requirement.id},
                status="success" if docker_test_result.success else "failure",
                execution_time_ms=0
            )
            
            result.add_log(f"Docker Test concluido - Status: {docker_test_result.status}")
            
            if docker_test_result.success:
                result.add_log("Docker validation: SUCCESS")
                logger.info("✅ Docker Test Agent concluído com sucesso")
            else:
                result.add_log(f"Docker Test warning: {docker_test_result.error_message}")
                logger.warning(f"⚠️ Docker Test Agent: {docker_test_result.error_message}")
            
            # ==========================================
            # SUCESSO
            # ==========================================
            logger.info("✅ Validação APROVADA!")
            result.add_log("FASE 5: Validação APROVADA")
            
            result.success = True
            result.project_path = requirement.project_config.output_directory
            
            # Extrai nomes dos serviços
            if executor_result.output:
                import json
                try:
                    # Tenta extrair serviços do output
                    json_start = executor_result.output.find('{')
                    json_end = executor_result.output.rfind('}')
                    if json_start >= 0 and json_end >= json_start:
                        data = json.loads(executor_result.output[json_start:json_end+1])
                        services = data.get("microservices", [])
                        result.services = [s.get("name", "unknown") for s in services]
                except:
                    pass
            
            result.add_log(f"Projeto gerado com sucesso em: {result.project_path}")
            
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
    
    async def execute_with_retry(
        self, 
        requirement: Requirement, 
        max_retries: int = 3
    ) -> ProjectGenerationResult:
        """
        Executa o fluxo com tentativas de retry.
        
        Args:
            requirement: Requisitos do projeto
            max_retries: Número máximo de tentativas
            
        Returns:
            ProjectGenerationResult com o resultado final
        """
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
        """
        Retorna o status do sistema de agentes.
        
        Returns:
            Dicionário com status dos agentes
        """
        return {
            "orchestrator": "ready",
            "executor": "ready",
            "validator": "ready",
            "fix": "ready",
            "rollback": "ready",
            "docker_test": "ready",
            "llm_connected": self.llm_provider is not None
        }
    
    async def validate_project_structure(
        self, 
        project_path: str, 
        expected_services: list[str]
    ) -> dict:
        """
        Valida a estrutura do projeto gerado.
        
        Args:
            project_path: Caminho do projeto
            expected_services: Serviços esperados
            
        Returns:
            Dicionário com resultado da validação
        """
        logger.info("Validando estrutura do projeto...")
        
        file_manager = FileManager(project_path)
        
        results = {
            "project_exists": False,
            "services_found": [],
            "services_missing": [],
            "structure_valid": False
        }
        
        # Verifica se o diretório existe
        import os
        if os.path.exists(project_path):
            results["project_exists"] = True
            
            # Lista serviços
            services_path = os.path.join(project_path, "services")
            if os.path.exists(services_path):
                found_services = [
                    d for d in os.listdir(services_path) 
                    if os.path.isdir(os.path.join(services_path, d))
                ]
                results["services_found"] = found_services
                results["services_missing"] = [
                    s for s in expected_services if s not in found_services
                ]
                
                results["structure_valid"] = len(found_services) > 0
        
        return results


class AgentWorkflow:
    """
    Workflow de execução dos agentes.
    
    Define o fluxo de trabalho e permite customização.
    """
    
    def __init__(self, llm_provider: OllamaProvider):
        self.orchestrator = OrchestratorAgent(llm_provider)
    
    async def run(self, requirements_text: str, config: ProjectConfig) -> ProjectGenerationResult:
        """
        Executa o workflow completo.
        
        Args:
            requirements_text: Descrição dos requisitos
            config: Configurações do projeto
            
        Returns:
            Resultado da geração
        """
        # Cria o requisito
        requirement = Requirement(
            description=requirements_text,
            project_config=config
        )
        
        # Executa via orchestrator
        return await self.orchestrator.execute(requirement)
    
    async def run_with_feedback(
        self, 
        requirements_text: str, 
        config: ProjectConfig,
        feedback_callback=None
    ) -> ProjectGenerationResult:
        """
        Executa o workflow com callback de feedback.
        
        Args:
            requirements_text: Descrição dos requisitos
            config: Configurações do projeto
            feedback_callback: Função callback para feedback
            
        Returns:
            Resultado da geração
        """
        requirement = Requirement(
            description=requirements_text,
            project_config=config
        )
        
        # Executa e reporta progresso
        result = await self.orchestrator.execute(requirement)
        
        if feedback_callback:
            feedback_callback(result)
        
        return result
