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
            requirement.execution_result = executor_result
            
            if not executor_result.success:
                # Executor falhou, já sabemos o resultado
                logger.error(f"❌ Executor Agent falhou: {executor_result.error_message}")
                result.success = False
                result.error_message = f"Executor falhou: {executor_result.error_message}"
                result.execution_logs.append(f"Erro: {executor_result.error_message}")
                
                return result
            
            logger.info(f"✅ Executor Agent concluído - {len(executor_result.files_created)} arquivos")
            
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

                log_communication(
                    from_agent="ExecutorAgent",
                    to_agent="ValidatorAgent",
                    trace_id=trace_id,
                    payload={"requirement_id": requirement.id, "cycle": cycle_label},
                    status="success",
                    execution_time_ms=0
                )

                result.add_log(f"Validação concluída - Status: {validation_result.status} | Score: {validation_result.score}")

                docker_issues: list[str] = []
                if validation_result.is_approved:
                    logger.info(f"\n📋 FASE 3: Docker Test Agent ({cycle_label})")
                    result.add_log(f"FASE 3: Docker Test Agent ({cycle_label})")

                    docker_test_result = await self.docker_test_agent.execute(
                        requirement,
                        executor_result
                    )

                    log_communication(
                        from_agent="ValidatorAgent",
                        to_agent="DockerTestAgent",
                        trace_id=trace_id,
                        payload={"requirement_id": requirement.id, "cycle": cycle_label},
                        status="success" if docker_test_result.success else "failure",
                        execution_time_ms=0
                    )

                    docker_ok, docker_issues, docker_requires_user_action = self._analyze_docker_result(docker_test_result)
                    if docker_ok:
                        result.add_log("Docker test: APROVADO")
                    else:
                        result.add_log(f"Docker test: REPROVADO - {', '.join(docker_issues)}")

                    if docker_requires_user_action:
                        logger.warning("⚠️ Docker Test requer ação do usuário antes de continuar")
                        result.add_log("Docker test bloqueado aguardando ação do usuário")
                        result.success = False
                        result.error_message = (
                            "Validação bloqueada: é necessária ação manual para executar os testes Docker. "
                            f"Detalhes: {'; '.join(docker_issues)}"
                        )
                        return result
                else:
                    result.add_log("FASE 3: Docker Test Agent pulado (validação semântica reprovada)")

                combined_issues = self._collect_flow_issues(validation_result, docker_issues)
                if not combined_issues:
                    final_validation = validation_result
                    break

                logger.warning(f"❌ Fluxo reprovado no {cycle_label}. Problemas: {combined_issues}")
                result.add_log(f"Fluxo reprovado ({cycle_label}) - problemas: {' | '.join(combined_issues)}")

                if fix_attempt >= max_attempts:
                    logger.error(f"❌ Limite de tentativas de correção atingido ({max_attempts})")
                    result.add_log(f"Limite de correções atingido ({max_attempts})")
                    result.success = False
                    result.error_message = (
                        f"Fluxo reprovado após {fix_attempt} tentativa(s) de correção. "
                        f"Últimos problemas: {'; '.join(combined_issues)}. "
                        "Arquivos mantidos para debug."
                    )
                    return result

                fix_attempt += 1
                logger.info(f"\n📋 FASE 4: Fix Agent - Tentativa {fix_attempt}/{max_attempts}")
                result.add_log(f"FASE 4: Fix Agent - Tentativa {fix_attempt}/{max_attempts}")

                fix_input = self._build_fix_validation_payload(validation_result, docker_issues)
                fix_result = await self.fix_agent.execute(
                    requirement,
                    fix_input,
                    fix_attempt
                )

                result.add_log(f"Fix concluído: {fix_result.status} | Arquivos modificados: {len(fix_result.files_modified)}")
                if not fix_result.success:
                    result.success = False
                    result.error_message = f"Fix Agent falhou na tentativa {fix_attempt}: {fix_result.error_message}"
                    return result
            
            # ==========================================
            # SUCESSO
            # ==========================================
            logger.info("✅ Fluxo gerar→validar→testar aprovado!")
            result.add_log("FASE 5: Fluxo APROVADO")
            
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

    def _analyze_docker_result(self, docker_test_result: ExecutionResult) -> tuple[bool, list[str], bool]:
        """Extrai status real do teste Docker e retorna problemas e flag de ação manual."""
        issues = []
        requires_user_action = False

        if not docker_test_result.success and not docker_test_result.output:
            return False, [docker_test_result.error_message or "Docker Test Agent falhou"], False

        try:
            payload = json.loads(docker_test_result.output) if docker_test_result.output else {}
            docker_validation = payload.get("docker_validation", {})

            if not docker_validation.get("success", False):
                if docker_validation.get("requires_user_action", False):
                    requires_user_action = True
                    user_message = docker_validation.get("user_action_message")
                    user_items = docker_validation.get("user_action_items", [])
                    if user_message:
                        issues.append(f"Ação manual necessária: {user_message}")
                    for item in user_items:
                        issues.append(f"Ação do usuário: {item}")

                if not docker_validation.get("docker_available", True):
                    issues.append("Docker indisponível no ambiente")

                for error_key in ["build_error", "up_error", "error"]:
                    if docker_validation.get(error_key):
                        issues.append(f"Docker {error_key}: {docker_validation[error_key]}")

                health_checks = docker_validation.get("health_checks", {})
                for service, status_data in health_checks.items():
                    if status_data.get("status") != "up":
                        issues.append(f"Health check falhou para {service} (status={status_data.get('status')})")

                if not issues:
                    issues.append("Validação Docker retornou falha sem detalhes")

        except Exception as exc:
            issues.append(f"Falha ao interpretar resultado do Docker Test Agent: {exc}")

        return len(issues) == 0, issues, requires_user_action

    def _collect_flow_issues(self, validation_result: ValidationResult, docker_issues: list[str]) -> list[str]:
        """Consolida problemas de validação e teste em uma única lista."""
        issues = []

        if validation_result.needs_rollback:
            if validation_result.feedback:
                issues.append(f"Validação: {validation_result.feedback}")
            issues.extend([f"Validação issue: {issue}" for issue in validation_result.issues])
            issues.extend([f"Validação rejeitado: {item}" for item in validation_result.rejected_items])
            issues.extend([f"Validação faltando: {item}" for item in validation_result.missing_items])

        issues.extend([f"Teste: {issue}" for issue in docker_issues])

        # Remove duplicatas mantendo ordem
        unique_issues = []
        for issue in issues:
            if issue and issue not in unique_issues:
                unique_issues.append(issue)

        return unique_issues

    def _build_fix_validation_payload(
        self,
        validation_result: ValidationResult,
        docker_issues: list[str]
    ) -> ValidationResult:
        """Monta payload de validação para o FixAgent incluindo falhas de teste."""
        merged = ValidationResult(
            requirement_id=validation_result.requirement_id,
            trace_id=validation_result.trace_id,
            status=validation_result.status,
            approved_items=list(validation_result.approved_items),
            rejected_items=list(validation_result.rejected_items),
            missing_items=list(validation_result.missing_items),
            issues=list(validation_result.issues),
            score=validation_result.score,
            feedback=validation_result.feedback,
            validated_at=validation_result.validated_at,
        )

        for issue in docker_issues:
            merged.issues.append(f"Docker/Teste: {issue}")
            merged.rejected_items.append(f"Teste Docker: {issue}")

        if docker_issues and merged.status != ValidationStatus.REJECTED:
            merged.status = ValidationStatus.REJECTED
            if merged.feedback:
                merged.feedback = f"{merged.feedback} | Falhas de teste: {'; '.join(docker_issues)}"
            else:
                merged.feedback = f"Falhas de teste: {'; '.join(docker_issues)}"

        return merged
    
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
