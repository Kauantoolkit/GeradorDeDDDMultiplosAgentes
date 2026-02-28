"""
Error Logger - Registro de Erros dos Agentes
============================================

Este módulo é responsável por:
- Registrar erros e problemas encontrados durante a validação
- Criar logs estruturados para análise posterior
- Manter histórico de correções aplicadas
- Permitir aprimoramento contínuo dos agentes

Os logs são salvos em: logs/agent_errors.log
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from loguru import logger


class ErrorLogger:
    """
    Logger de Erros - Registra e analisa erros dos agentes.
    
    Mantém um histórico estruturado de:
    - Problemas identificados pelo Validator
    - Correções aplicadas pelo Fix Agent
    - Resultados das tentativas de correção
    
    Formato do log:
    {
        "timestamp": "2024-01-01 12:00:00",
        "requirement_id": "...",
        "attempt": 1,
        "validator_issues": [...],
        "fix_applied": [...],
        "result": "success" | "failed",
        "score_after_fix": 0.8
    }
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Inicializa o Error Logger.
        
        Args:
            log_dir: Diretório para salvar os logs
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / "agent_errors.log"
        
        # Garante que o diretório existe
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configura o logger
        self._setup_logger()
        
        self.name = "Error Logger"
        logger.info(f"{self.name} inicializado - Arquivo: {self.log_file}")
    
    def _setup_logger(self):
        """Configura o logger para arquivo."""
        # Remove handlers existentes
        logger.remove()
        
        # Adiciona handler para arquivo
        logger.add(
            self.log_file,
            rotation="10 MB",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        
        # Adiciona handler para console (opcional)
        logger.add(
            lambda msg: print(msg),
            level="INFO",
            format="{time:HH:mm:ss} | {level} | {message}"
        )
    
    def log_validation_failure(
        self,
        requirement_id: str,
        validation_result: Any,
        attempt: int = 1
    ):
        """
        Registra uma falha de validação.
        
        Args:
            requirement_id: ID do requisito
            validation_result: Resultado da validação
            attempt: Número da tentativa
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "VALIDATION_FAILURE",
            "requirement_id": requirement_id,
            "attempt": attempt,
            "score": validation_result.score,
            "issues": validation_result.issues,
            "rejected_items": validation_result.rejected_items,
            "missing_items": validation_result.missing_items,
            "feedback": validation_result.feedback
        }
        
        # Log estruturado
        logger.info(f"VALIDATION_FAILURE | Attempt {attempt} | Score: {validation_result.score}")
        logger.info(f"  Issues: {validation_result.issues}")
        logger.info(f"  Rejected: {validation_result.rejected_items}")
        logger.info(f"  Missing: {validation_result.missing_items}")
        
        # Salva em arquivo JSON
        self._append_json_log(log_entry)
        
        return log_entry
    
    def log_fix_attempt(
        self,
        requirement_id: str,
        issues_to_fix: list[str],
        actions_taken: list[str],
        files_modified: list[str],
        attempt: int,
        success: bool
    ):
        """
        Registra uma tentativa de correção do Fix Agent.
        
        Args:
            requirement_id: ID do requisito
            issues_to_fix: Lista de problemas a corrigir
            actions_taken: Ações realizadas pelo Fix Agent
            files_modified: Arquivos modificados
            attempt: Número da tentativa
            success: Se a correção foi bem-sucedida
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "FIX_ATTEMPT",
            "requirement_id": requirement_id,
            "attempt": attempt,
            "issues_to_fix": issues_to_fix,
            "actions_taken": actions_taken,
            "files_modified": files_modified,
            "success": success
        }
        
        # Log estruturado
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"FIX_ATTEMPT | Attempt {attempt} | {status}")
        logger.info(f"  Issues to fix: {issues_to_fix}")
        logger.info(f"  Actions taken: {actions_taken}")
        logger.info(f"  Files modified: {files_modified}")
        
        # Salva em arquivo JSON
        self._append_json_log(log_entry)
        
        return log_entry
    
    def log_final_result(
        self,
        requirement_id: str,
        total_attempts: int,
        success: bool,
        final_score: float = 0.0,
        error_message: str = ""
    ):
        """
        Registra o resultado final após todas as tentativas.
        
        Args:
            requirement_id: ID do requisito
            total_attempts: Total de tentativas realizadas
            success: Se o processo foi bem-sucedido
            final_score: Score final após correções
            error_message: Mensagem de erro (se houver)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "FINAL_RESULT",
            "requirement_id": requirement_id,
            "total_attempts": total_attempts,
            "success": success,
            "final_score": final_score,
            "error_message": error_message
        }
        
        # Log estruturado
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"FINAL_RESULT | {status} | Attempts: {total_attempts} | Final Score: {final_score}")
        
        if error_message:
            logger.info(f"  Error: {error_message}")
        
        # Salva em arquivo JSON
        self._append_json_log(log_entry)
        
        return log_entry
    
    def _append_json_log(self, log_entry: dict):
        """
        Adiciona entrada ao arquivo de log JSON.
        
        Args:
            log_entry: Dicionário com os dados do log
        """
        try:
            # Lê logs existentes
            existing_logs = []
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                existing_logs.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
            
            # Adiciona novo log
            existing_logs.append(log_entry)
            
            # Limita a 1000 entradas mais recentes
            if len(existing_logs) > 1000:
                existing_logs = existing_logs[-1000:]
            
            # Reescreve o arquivo
            with open(self.log_file, 'w', encoding='utf-8') as f:
                for entry in existing_logs:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    
        except Exception as e:
            logger.error(f"Erro ao salvar log JSON: {e}")
    
    def get_error_summary(self, requirement_id: str = None) -> dict:
        """
        Retorna um resumo dos erros registrados.
        
        Args:
            requirement_id: Filtrar por requisito específico (opcional)
            
        Returns:
            Dicionário com resumo dos erros
        """
        if not self.log_file.exists():
            return {"total_entries": 0, "errors": []}
        
        errors = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        
                        # Filtra por requirement_id se especificado
                        if requirement_id:
                            if entry.get("requirement_id") != requirement_id:
                                continue
                        
                        if entry.get("type") in ["VALIDATION_FAILURE", "FIX_ATTEMPT"]:
                            errors.append(entry)
                            
                    except json.JSONDecodeError:
                        continue
            
            # Agrupa erros por tipo
            summary = {
                "total_entries": len(errors),
                "validation_failures": len([e for e in errors if e.get("type") == "VALIDATION_FAILURE"]),
                "fix_attempts": len([e for e in errors if e.get("type") == "FIX_ATTEMPT"]),
                "errors": errors[-50:]  # Últimos 50 erros
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao ler resumo de erros: {e}")
            return {"total_entries": 0, "errors": [], "error": str(e)}
    
    def get_common_issues(self, limit: int = 10) -> list[dict]:
        """
        Retorna os problemas mais comuns encontrados.
        
        Args:
            limit: Número de problemas a retornar
            
        Returns:
            Lista de problemas mais comuns com contagem
        """
        if not self.log_file.exists():
            return []
        
        issue_counts = {}
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        
                        if entry.get("type") == "VALIDATION_FAILURE":
                            issues = entry.get("issues", [])
                            for issue in issues:
                                issue_counts[issue] = issue_counts.get(issue, 0) + 1
                                
                    except json.JSONDecodeError:
                        continue
            
            # Ordena por contagem e retorna os mais comuns
            sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"issue": issue, "count": count} for issue, count in sorted_issues[:limit]]
            
        except Exception as e:
            logger.error(f"Erro ao analisar problemas comuns: {e}")
            return []


# Instância global do ErrorLogger
_error_logger_instance = None


def get_error_logger() -> ErrorLogger:
    """
    Retorna a instância global do ErrorLogger.
    
    Returns:
        Instância do ErrorLogger
    """
    global _error_logger_instance
    
    if _error_logger_instance is None:
        _error_logger_instance = ErrorLogger()
    
    return _error_logger_instance
