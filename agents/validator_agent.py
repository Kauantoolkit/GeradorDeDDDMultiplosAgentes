"""
Validator Agent - Agente Validador
==================================

Este agente é responsável por:
- Receber o código gerado pelo Executor Agent
- Comparar com os requisitos originais
- Validar se a estrutura DDD está correta
- Verificar se todos os componentes estão presentes
- Decidir se aprova ou reprova o código gerado
- Se reprovar, acionar o Rollback Agent
"""

import json
from datetime import datetime
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    ValidationResult,
    ValidationStatus,
    Requirement
)
from infrastructure.llm_provider import OllamaProvider, PromptBuilder
from infrastructure.file_manager import FileManager


class ValidatorAgent:
    """
    Agente Validator - Valida código gerado vs requisitos.
    
    Este agente recebe:
    - Requirement: Requisitos originais
    - ExecutionResult: Resultado do Executor Agent
    
    E retorna:
    - ValidationResult: Resultado da validação (approved/rejected)
    """
    
    def __init__(self, llm_provider: OllamaProvider):
        """
        Inicializa o Validator Agent.
        
        Args:
            llm_provider: Provedor de LLM para validação
        """
        self.llm_provider = llm_provider
        self.name = "Validator Agent"
        logger.info(f"{self.name} inicializado")
    
    async def validate(
        self, 
        requirement: Requirement, 
        execution_result: ExecutionResult
    ) -> ValidationResult:
        """
        Valida o código gerado contra os requisitos.
        
        Args:
            requirement: Requisitos originais
            execution_result: Resultado da execução do Executor
            
        Returns:
            ValidationResult com status de aprovação
        """
        start_time = datetime.now()
        
        logger.info("="*60)
        logger.info("VALIDATOR AGENT - Iniciando validação")
        logger.info("="*60)
        
        # Se o Executor falhou, já sabemos que precisa de rollback
        if execution_result.status == ExecutionStatus.FAILED:
            logger.warning("Executor Agent falhou - validação automática reprovada")
            result = ValidationResult(
                requirement_id=requirement.id,
                status=ValidationStatus.REJECTED,
                score=0.0,
                feedback="Executor Agent falhou durante a geração de código"
            )
            result.reject("Executor Agent falhou")
            return result
        
        try:
            # Constrói o prompt de validação
            prompt = PromptBuilder.build_validator_prompt(
                requirement, 
                execution_result
            )
            
            # Chama o LLM para validar
            logger.info("Chamando LLM para validação...")
            llm_output = await self.llm_provider.generate(
                prompt=prompt,
                temperature=0.2,  # Baixa temperatura para ser mais crítico
                max_tokens=2000
            )
            
            # Parseia o resultado
            validation_data = self._parse_validation_output(llm_output)
            
            # Cria o resultado da validação
            result = ValidationResult(
                requirement_id=requirement.id,
                validated_at=datetime.now()
            )
            
            if validation_data:
                status = validation_data.get("status", "rejected")
                result.score = validation_data.get("score", 0.0)
                result.approved_items = validation_data.get("approved_items", [])
                result.rejected_items = validation_data.get("rejected_items", [])
                result.missing_items = validation_data.get("missing_items", [])
                result.issues = validation_data.get("issues", [])
                result.feedback = validation_data.get("feedback", "")
                
                # Determina status
                if status == "approved" and result.score >= 0.7:
                    result.approve()
                    logger.info(f"✅ Validação APROVADA - Score: {result.score}")
                else:
                    result.reject(result.feedback or "Não atingiu score mínimo (0.7)")
                    logger.warning(f"❌ Validação REPROVADA - Score: {result.score}")
            else:
                # Se não conseguiu parsear, faz validação manual
                result = self._manual_validation(requirement, execution_result)
            
            return result
            
        except Exception as e:
            logger.exception(f"Erro no {self.name}: {e}")
            result = ValidationResult(
                requirement_id=requirement.id,
                status=ValidationStatus.REJECTED,
                score=0.0
            )
            result.reject(f"Erro na validação: {str(e)}")
            return result
    
    def _parse_validation_output(self, llm_output: str) -> dict | None:
        """
        Parseia a saída do LLM em JSON de validação.
        
        Args:
            llm_output: Texto retornado pelo LLM
            
        Returns:
            Dicionário com os dados de validação ou None
        """
        try:
            # Tenta encontrar JSON no texto
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}')
            
            if json_start >= 0 and json_end >= json_start:
                json_str = llm_output[json_start:json_end+1]
                return json.loads(json_str)
            
            return json.loads(llm_output)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON de validação: {e}")
            return None
    
    def _manual_validation(
        self, 
        requirement: Requirement, 
        execution_result: ExecutionResult
    ) -> ValidationResult:
        """
        Realiza validação manual quando o LLM falha.
        
        Args:
            requirement: Requisitos originais
            execution_result: Resultado do Executor
            
        Returns:
            ValidationResult com validação manual
        """
        result = ValidationResult(
            requirement_id=requirement.id,
            validated_at=datetime.now()
        )
        
        logger.info("Realizando validação manual...")
        
        # Verificações básicas
        checks = []
        
        # 1. Verifica se há arquivos criados
        if execution_result.files_created:
            checks.append("Arquivos criados: OK")
            result.approved_items.append("Estrutura de arquivos")
        else:
            checks.append("Arquivos criados: FALHA")
            result.rejected_items.append("Estrutura de arquivos")
            result.missing_items.append("Nenhum arquivo criado")
        
        # 2. Verifica se há output do LLM
        if execution_result.output:
            checks.append("Código gerado: OK")
            result.approved_items.append("Código gerado")
        else:
            checks.append("Código gerado: FALHA")
            result.rejected_items.append("Código gerado")
        
        # 3. Verifica tamanho do output
        if len(execution_result.output) > 500:
            checks.append("Tamanho do código: OK")
            result.approved_items.append("Código com tamanho adequado")
        else:
            checks.append("Tamanho do código: INSUFICIENTE")
            result.rejected_items.append("Código muito curto")
        
        # Calcula score baseado nas verificações
        approved_count = len(result.approved_items)
        total_checks = approved_count + len(result.rejected_items)
        
        if total_checks > 0:
            result.score = approved_count / total_checks
        else:
            result.score = 0.0
        
        # Determina aprovação
        if result.score >= 0.5:
            result.approve()
            logger.info(f"✅ Validação manual APROVADA - Score: {result.score}")
        else:
            result.reject("Não passou na validação manual")
            logger.warning(f"❌ Validação manual REPROVADA - Score: {result.score}")
        
        result.feedback = "\n".join(checks)
        
        return result
    
    async def validate_structure(
        self, 
        project_path: str, 
        expected_services: list[str]
    ) -> dict[str, bool]:
        """
        Valida a estrutura física dos arquivos gerados.
        
        Args:
            project_path: Caminho do projeto
            expected_services: Lista de serviços esperados
            
        Returns:
            Dicionário com resultados da validação estrutural
        """
        logger.info("Validando estrutura de arquivos...")
        
        file_manager = FileManager(project_path)
        structure_checks = {}
        
        for service in expected_services:
            service_path = f"services/{service}"
            
            # Verifica se diretório existe
            files = file_manager.list_files(service_path)
            structure_checks[service] = len(files) > 0
            
            # Verifica estrutura DDD
            ddd_paths = [
                f"{service_path}/domain",
                f"{service_path}/application",
                f"{service_path}/infrastructure",
                f"{service_path}/api"
            ]
            
            for ddd_path in ddd_paths:
                ddd_files = file_manager.list_files(ddd_path)
                if not ddd_files:
                    logger.warning(f"Camada DDD não encontrada: {ddd_path}")
        
        return structure_checks


class ValidationRules:
    """
    Regras de validação predefined para verificar qualidade do código.
    """
    
    @staticmethod
    def check_ddd_structure(files: list[str]) -> dict[str, bool]:
        """
        Verifica se a estrutura DDD está completa.
        
        Args:
            files: Lista de arquivos gerados
            
        Returns:
            Dicionário com resultados das verificações
        """
        required_layers = ["domain", "application", "infrastructure", "api"]
        results = {}
        
        for layer in required_layers:
            layer_files = [f for f in files if f"/{layer}/" in f]
            results[layer] = len(layer_files) > 0
        
        return results
    
    @staticmethod
    def check_entities(files: list[str]) -> bool:
        """Verifica se há entidades definidas."""
        entity_files = [f for f in files if "entities.py" in f]
        return len(entity_files) > 0
    
    @staticmethod
    def check_use_cases(files: list[str]) -> bool:
        """Verifica se há use cases definidos."""
        usecase_files = [f for f in files if "use_cases" in f]
        return len(usecase_files) > 0
    
    @staticmethod
    def check_repositories(files: list[str]) -> bool:
        """Verifica se há repositórios definidos."""
        repo_files = [f for f in files if "repositories" in f]
        return len(repo_files) > 0
    
    @staticmethod
    def check_api_routes(files: list[str]) -> bool:
        """Verifica se há rotas de API definidas."""
        route_files = [f for f in files if "routes" in f]
        return len(route_files) > 0
