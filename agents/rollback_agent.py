"""
Rollback Agent - Agente de Rollback
====================================

Este agente é responsável por:
- Receber a lista de arquivos criados pelo Executor Agent
- Remover todos os arquivos e diretórios gerados
- Garantir que o diretório volte ao estado anterior
- Retornar um relatório das operações realizadas

O Rollback é acionado automaticamente quando o Validator Agent
reprova o código gerado.
"""

from datetime import datetime
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    Requirement
)
from infrastructure.file_manager import FileManager


class RollbackAgent:
    """
    Agente Rollback - Desfaz mudanças do Executor Agent.
    
    Este agente é acionado quando:
    - Validator Agent reprova o código gerado
    - Ou quando ocorre algum erro durante o processo
    
    Ação:
    - Remove todos os arquivos criados pelo Executor
    - Remove diretórios vazios
    - Retorna relatório das remoções
    """
    
    def __init__(self):
        """
        Inicializa o Rollback Agent.
        """
        self.name = "Rollback Agent"
        logger.info(f"{self.name} inicializado")
    
    async def execute(
        self, 
        requirement: Requirement, 
        execution_result: ExecutionResult
    ) -> ExecutionResult:
        """
        Executa o rollback dos arquivos gerados.
        
        Args:
            requirement: Requisito original
            execution_result: Resultado do Executor Agent (contém arquivos a remover)
            
        Returns:
            ExecutionResult com status do rollback
        """
        start_time = datetime.now()
        
        result = ExecutionResult(
            agent_type=AgentType.ROLLBACK,
            status=ExecutionStatus.IN_PROGRESS,
            started_at=start_time
        )
        
        try:
            logger.info("="*60)
            logger.info("ROLLBACK AGENT - Iniciando rollback")
            logger.info("="*60)
            
            # Obtém o diretório do projeto
            project_path = requirement.project_config.output_directory
            
            # Inicializa o gerenciador de arquivos
            file_manager = FileManager(project_path)
            
            # Lista de arquivos para remover
            files_to_remove = execution_result.files_created
            
            if not files_to_remove:
                logger.warning("Nenhum arquivo para remover")
                result.status = ExecutionStatus.SUCCESS
                result.output = "Nenhum arquivo para remover"
                result.finished_at = datetime.now()
                result.execution_time = (result.finished_at - start_time).total_seconds()
                return result
            
            logger.info(f"Arquivos a remover: {len(files_to_remove)}")
            
            # Remove os arquivos
            removal_results = file_manager.rollback_files(files_to_remove)
            
            # Conta sucesso e falhas
            successful_removals = [f for f, status in removal_results.items() if status]
            failed_removals = [f for f, status in removal_results.items() if not status]
            
            # Gera relatório
            report = self._generate_report(
                successful_removals, 
                failed_removals,
                project_path
            )
            
            result.output = report
            result.files_created = []  # Não criou nada
            result.files_modified = []  # Não modificou nada
            
            if failed_removals:
                # Rollback parcial
                result.status = ExecutionStatus.FAILED
                result.error_message = f"Falha ao remover {len(failed_removals)} arquivos"
                logger.warning(f"Rollback parcial: {len(failed_removals)} arquivos não puderam ser removidos")
            else:
                # Rollback completo
                result.status = ExecutionStatus.SUCCESS
                logger.info("Rollback concluído com sucesso")
            
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            logger.info(f"{self.name} - Concluído em {result.execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.exception(f"Erro no {self.name}: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            return result
    
    async def rollback_directory(self, directory: str) -> dict:
        """
        Remove um diretório inteiro (para rollback completo).
        
        Args:
            directory: Caminho do diretório para remover
            
        Returns:
            Dicionário com resultado da operação
        """
        logger.info(f"Removendo diretório: {directory}")
        
        try:
            file_manager = FileManager(".")
            success = file_manager.delete_directory(directory)
            
            return {
                "success": success,
                "directory": directory,
                "message": f"Diretório {'removido' if success else 'não removido'}"
            }
            
        except Exception as e:
            logger.error(f"Erro ao remover diretório: {e}")
            return {
                "success": False,
                "directory": directory,
                "error": str(e)
            }
    
    def _generate_report(
        self, 
        successful: list[str], 
        failed: list[str],
        project_path: str
    ) -> str:
        """
        Gera um relatório do rollback.
        
        Args:
            successful: Lista de arquivos removidos com sucesso
            failed: Lista de arquivos que falharam ao remover
            project_path: Caminho do projeto
            
        Returns:
            String com o relatório formatado
        """
        report_lines = [
            "=" * 60,
            "RELATÓRIO DE ROLLBACK",
            "=" * 60,
            "",
            f"Projeto: {project_path}",
            f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"✅ Removidos com sucesso: {len(successful)}",
            f"❌ Falhas na remoção: {len(failed)}",
            "",
            "-" * 60,
            "Arquivos removidos:",
            "-" * 60,
        ]
        
        if successful:
            for i, file in enumerate(successful, 1):
                report_lines.append(f"  {i}. {file}")
        else:
            report_lines.append("  (nenhum)")
        
        if failed:
            report_lines.extend([
                "",
                "-" * 60,
                "Arquivos que não puderam ser removidos:",
                "-" * 60,
            ])
            for i, file in enumerate(failed, 1):
                report_lines.append(f"  {i}. {file}")
        
        report_lines.extend([
            "",
            "=" * 60,
            "FIM DO RELATÓRIO",
            "=" * 60,
        ])
        
        return "\n".join(report_lines)


class RollbackManager:
    """
    Gerenciador de rollback - coordena operações de rollback.
    
    Pode ser usado para:
    - Rollback automático após validação falhar
    - Rollback manual via comando
    - Rollback de operações específicas
    """
    
    def __init__(self):
        self.rollback_agent = RollbackAgent()
    
    async def automatic_rollback(
        self, 
        requirement: Requirement,
        execution_result: ExecutionResult
    ) -> ExecutionResult:
        """
        Executa rollback automático após validação falhar.
        
        Args:
            requirement: Requisito original
            execution_result: Resultado do Executor
            
        Returns:
            Resultado do rollback
        """
        logger.warning("⚠️ VALIDAÇÃO FALHOU - INICIANDO ROLLBACK AUTOMÁTICO")
        
        result = await self.rollback_agent.execute(requirement, execution_result)
        
        if result.success:
            logger.info("✅ Rollback automático concluído com sucesso")
        else:
            logger.error(f"❌ Rollback automático falhou: {result.error_message}")
        
        return result
    
    async def full_cleanup(self, directory: str) -> dict:
        """
        Limpa completamente um diretório de projeto.
        
        Args:
            directory: Caminho do diretório
            
        Returns:
            Resultado da limpeza
        """
        logger.info(f"🧹 Limpando diretório: {directory}")
        
        return await self.rollback_agent.rollback_directory(directory)
