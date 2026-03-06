"""
Fix Agent - Agente de Correção
==============================

Este agente é responsável por:
- Receber feedback do Validator Agent sobre problemas encontrados
- Analisar os problemas e criar plano de correção
- Aplicar correções nos arquivos gerados
- Registrar as ações realizadas para logs
- Retornar relatório das correções aplicadas

O Fix Agent é acionado automaticamente quando o Validator Agent
reprova o código gerado, tentando corrigir os problemas antes
de uma nova validação.

MUDANÇAS IMPLEMENTADAS:
- Logging estruturado com trace_id
- Busca flexível de arquivos para resolver inconsistências de caminhos entre agentes
"""

import json
import re
import ast
from datetime import datetime
from typing import Any
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    Requirement,
    ValidationResult
)
from infrastructure.llm_provider import OllamaProvider, PromptBuilder
from infrastructure.file_manager import FileManager

from .error_logger import get_error_logger

# Import agent logger for structured logging
from agents.agent_logger import (
    get_logger,
    log_execution,
    log_error,
    log_communication,
    AgentExecutionContext
)


class FixAgent:
    """
    Agente Fix - Corrige problemas identificados pelo Validator.
    
    Este agente recebe:
    - Requirement: Requisitos originais
    - ValidationResult: Resultado da validação com problemas
    
    E retorna:
    - ExecutionResult: Resultado das correções aplicadas
    
    Fluxo:
    1. Analisa os problemas identificados
    2. Cria plano de correção
    3. Aplica correções nos arquivos
    4. Registra ações no log
    5. Retorna resultado
    """
    
    def __init__(self, llm_provider: OllamaProvider = None):
        """
        Inicializa o Fix Agent.
        
        Args:
            llm_provider: Provedor de LLM para correção (opcional)
        """
        self.llm_provider = llm_provider
        self.name = "Fix Agent"
        self.error_logger = get_error_logger()
        logger.info(f"{self.name} inicializado")
    
    async def execute(
        self,
        requirement: Requirement,
        validation_result: ValidationResult,
        attempt: int = 1,
        trace_id: str = None
    ) -> ExecutionResult:
        """
        Executa a correção dos problemas identificados.
        
        Args:
            requirement: Requisito original
            validation_result: Resultado da validação com problemas
            attempt: Número da tentativa de correção
            trace_id: ID único da execução (opcional)
            
        Returns:
            ExecutionResult com status das correções
        """
        start_time = datetime.now()
        
        # Get or create logger with trace_id
        agent_logger = get_logger()
        if trace_id is None:
            trace_id = agent_logger.create_trace_id()
        
        # Create execution context for structured logging
        context = AgentExecutionContext(
            agent_name=self.name,
            trace_id=trace_id,
            input_data={
                "requirement_id": requirement.id,
                "attempt": attempt,
                "issues_count": len(validation_result.issues) if validation_result else 0,
                "rejected_items": validation_result.rejected_items if validation_result else [],
                "missing_items": validation_result.missing_items if validation_result else []
            }
        )
        context.start()
        
        result = ExecutionResult(
            agent_type=AgentType.FIX,
            status=ExecutionStatus.IN_PROGRESS,
            started_at=start_time
        )
        
        try:
            logger.info("="*60)
            logger.info(f"FIX AGENT - Tentativa {attempt}")
            logger.info("="*60)
            
            # Registra a tentativa de correção
            self.error_logger.log_validation_failure(
                requirement.id,
                validation_result,
                attempt
            )
            
            # Coleta problemas a corrigir
            issues_to_fix = self._collect_issues(validation_result)
            
            if not issues_to_fix:
                logger.warning("Nenhum problema identificado para corrigir")
                result.status = ExecutionStatus.SUCCESS
                result.output = "Nenhum problema para corrigir"
                return result
            
            logger.info(f"Problemas identificados: {len(issues_to_fix)}")
            for issue in issues_to_fix:
                logger.info(f"  - {issue}")
            
            # Cria plano de correção
            fix_plan = self._create_fix_plan(issues_to_fix)
            
            # Obtém o execution_result do requisito
            execution_result = requirement.execution_result if hasattr(requirement, 'execution_result') else None
            
            # Aplica correções
            files_modified = await self._apply_fixes(
                requirement,
                validation_result,
                execution_result,
                fix_plan,
                issues_to_fix
            )

            if not files_modified:
                result.status = ExecutionStatus.FAILED
                result.error_message = (
                    "FixAgent não aplicou alterações; "
                    "encerrando tentativa sem progresso"
                )
                logger.error(result.error_message)
                return result
            
            # Registra as correções aplicadas
            self.error_logger.log_fix_attempt(
                requirement_id=requirement.id,
                issues_to_fix=issues_to_fix,
                actions_taken=fix_plan.get("actions", []),
                files_modified=files_modified,
                attempt=attempt,
                success=len(files_modified) > 0
            )
            
            result.files_modified = files_modified
            result.status = ExecutionStatus.SUCCESS
            result.output = self._generate_fix_report(issues_to_fix, fix_plan, files_modified)
            
            logger.info(f"Correções aplicadas: {len(files_modified)} arquivos modificados")
            
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            # End execution context with success
            context.end(
                output_data={
                    "files_modified": files_modified,
                    "status": result.status.value,
                    "execution_time": result.execution_time
                },
                status="success"
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Erro no {self.name}: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            # End execution context with error
            context.end_with_error(e, context={"error": str(e)})
            
            # Registra o erro
            self.error_logger.log_fix_attempt(
                requirement_id=requirement.id,
                issues_to_fix=[],
                actions_taken=[],
                files_modified=[],
                attempt=attempt,
                success=False
            )
            
            return result
    
    def _collect_issues(self, validation_result: ValidationResult) -> list[str]:
        """
        Coleta todos os problemas identificados na validação.
        
        Args:
            validation_result: Resultado da validação
            
        Returns:
            Lista de problemas identificados
        """
        issues = []
        
        # Adiciona issues principais
        issues.extend(validation_result.issues)
        
        # Adiciona itens rejeitados
        for item in validation_result.rejected_items:
            issues.append(f"Rejeitado: {item}")
        
        # Adiciona itens faltantes
        for item in validation_result.missing_items:
            issues.append(f"Faltando: {item}")
        
        # Remove duplicatas
        unique_issues = list(set(issues))
        
        return unique_issues
    
    def _create_fix_plan(self, issues: list[str]) -> dict:
        """
        Cria um plano de correção baseado nos problemas identificados.
        
        Args:
            issues: Lista de problemas
            
        Returns:
            Dicionário com plano de correção
        """
        plan = {
            "actions": [],
            "files_to_check": [],
            "patterns_to_fix": []
        }
        
        for issue in issues:
            issue_lower = issue.lower()
            
            # Problemas comuns e suas correções
            if "domain" in issue_lower and "faltando" in issue_lower:
                plan["actions"].append("Criar estrutura de domínio DDD")
                plan["files_to_check"].append("domain/")
            
            if "entity" in issue_lower and "faltando" in issue_lower:
                plan["actions"].append("Definir entidades do domínio")
                plan["patterns_to_fix"].append("entities")
            
            if "repository" in issue_lower and "faltando" in issue_lower:
                plan["actions"].append("Implementar padrão Repository")
                plan["patterns_to_fix"].append("repositories")
            
            if "use case" in issue_lower or "usecase" in issue_lower:
                plan["actions"].append("Criar casos de uso")
                plan["patterns_to_fix"].append("use_cases")
            
            if "api" in issue_lower or "route" in issue_lower:
                plan["actions"].append("Definir rotas de API")
                plan["patterns_to_fix"].append("routes")
            
            if "docker" in issue_lower:
                plan["actions"].append("Adicionar configuração Docker")
                plan["patterns_to_fix"].append("docker")
            
            if "test" in issue_lower and "faltando" in issue_lower:
                plan["actions"].append("Criar testes unitários")
                plan["patterns_to_fix"].append("tests")
            
            if "schema" in issue_lower or "dto" in issue_lower:
                plan["actions"].append("Definir schemas e DTOs")
                plan["patterns_to_fix"].append("schemas")
            
            if "import" in issue_lower or "erro" in issue_lower and "sintaxe" in issue_lower:
                plan["actions"].append("Corrigir imports e sintaxe")
                plan["patterns_to_fix"].append("imports")
        
        # Remove ações duplicadas
        plan["actions"] = list(set(plan["actions"]))
        plan["files_to_check"] = list(set(plan["files_to_check"]))
        plan["patterns_to_fix"] = list(set(plan["patterns_to_fix"]))
        
        return plan
    
    async def _apply_fixes(
        self,
        requirement: Requirement,
        validation_result: ValidationResult,
        execution_result: Any,
        fix_plan: dict,
        issues: list[str]
    ) -> list[str]:
        """
        Aplica as correções nos arquivos.
        
        Args:
            requirement: Requisito original
            validation_result: Resultado da validação
            execution_result: Resultado da execução do Executor
            fix_plan: Plano de correção
            issues: Lista de problemas
            
        Returns:
            Lista de arquivos modificados
        """
        files_modified = []
        project_path = requirement.project_config.output_directory
        file_manager = FileManager(project_path)

        # Correções determinísticas para problemas recorrentes de dependência
        files_modified.extend(
            self._fix_emailstr_dependencies(
                file_manager=file_manager,
                execution_result=execution_result,
            )
        )
        
        # Se tem LLM, usa para sugerir correções
        if self.llm_provider:
            files_modified.extend(
                await self._fix_with_llm(
                    file_manager,
                    requirement,
                    validation_result,
                    execution_result,
                    project_path
                )
            )
        else:
            # Fallback: tenta correções básicas
            files_modified.extend(
                self._fix_basic(
                    file_manager,
                    fix_plan,
                    project_path
                )
            )
        
        return files_modified

    def _fix_emailstr_dependencies(
        self,
        file_manager: FileManager,
        execution_result: Any,
    ) -> list[str]:
        """Garante dependência de email quando EmailStr é utilizado nos schemas."""
        modified: list[str] = []

        service_names: set[str] = set()
        files_created = getattr(execution_result, "files_created", []) or []
        for file_path in files_created:
            normalized = file_path.replace("\\", "/")
            parts = normalized.split("/")
            if "services" in parts:
                idx = parts.index("services") + 1
                if idx < len(parts) and parts[idx]:
                    service_names.add(parts[idx])

        services_root = file_manager.base_path / "services"
        if services_root.exists():
            for service_dir in services_root.iterdir():
                if service_dir.is_dir():
                    service_names.add(service_dir.name)

        for service_name in sorted(service_names):
            # Usa busca flexível para encontrar schemas
            schema_content = file_manager.read_file_flexible(f"services/{service_name}/api/schemas.py")
            if not schema_content or "EmailStr" not in schema_content:
                continue

            requirements_path = f"services/{service_name}/requirements.txt"
            requirements_content = file_manager.read_file(requirements_path)
            if requirements_content is None:
                continue

            normalized_requirements = requirements_content.lower()
            has_email_dep = (
                "email-validator" in normalized_requirements
                or "pydantic[email]" in normalized_requirements
            )
            if has_email_dep:
                continue

            new_content = requirements_content.rstrip() + "\nemail-validator>=2.0.0\n"
            if file_manager.create_file(requirements_path, new_content):
                modified.append(requirements_path)
                logger.info(
                    f"  Modificado: {requirements_path} (adicionada dependência email-validator)"
                )

        return modified
    
    async def _fix_with_llm(
        self,
        file_manager: FileManager,
        requirement: Requirement,
        validation_result: ValidationResult,
        execution_result: Any,
        project_path: str
    ) -> list[str]:
        """
        Usa LLM para sugerir e aplicar correções.
        
        Args:
            file_manager: Gerenciador de arquivos
            requirement: Requisito original
            validation_result: Resultado da validação
            execution_result: Resultado da execução do Executor
            project_path: Caminho do projeto
            
        Returns:
            Lista de arquivos modificados
        """
        files_modified = []
        
        try:
            relevant_files = self._select_relevant_files(validation_result, execution_result)
            context_snippets = self._build_file_context_snippets(file_manager, relevant_files)

            # Constrói prompt para correção usando o novo PromptBuilder
            prompt = PromptBuilder.build_fix_prompt(
                requirement,
                validation_result,
                execution_result,
                file_context=context_snippets,
            )
            
            # Chama LLM
            logger.info("Chamando LLM para gerar correções...")
            llm_output = await self.llm_provider.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=4000
            )
            
            fix_data = self._parse_fix_json(llm_output)
            if not fix_data:
                logger.warning("Não foi possível parsear resposta do LLM para correção")
                return files_modified

            fixes = fix_data.get("fixes", [])
            for fix in fixes:
                # CORREÇÃO: Normalizar caminhos recebidos do LLM (hífen → underscore)
                file_path = fix.get("file_path")
                if file_path:
                    file_path = file_path.replace('-', '_')
                
                content = fix.get("content")
                action = fix.get("action", "modify")

                if file_path and action in {"modify", "create"} and self._looks_like_placeholder(content or ""):
                    logger.warning(f"  Ignorado (placeholder): {file_path}")
                    continue

                if file_path and action == "create":
                    if not self._is_content_valid_for_file(file_path, content or ""):
                        logger.warning(f"  Ignorado (conteúdo inválido): {file_path}")
                        continue

                    if file_manager.create_file(file_path, content or ""):
                        files_modified.append(file_path)
                        logger.info(f"  Criado: {file_path}")

                elif file_path and action == "modify":
                    # CORREÇÃO: Usar read_file_flexible para encontrar o arquivo em múltiplos locais
                    # Isso resolve problemas de caminhos inconsistentes entre Executor e FixAgent
                    existing_content = file_manager.read_file_flexible(file_path)
                    if existing_content is None:
                        logger.warning(f"  Arquivo para modificação não encontrado: {file_path} (tentando busca flexível)")
                        # Tenta encontrar em todos os serviços como último recurso
                        found_path = file_manager.find_file_with_flexible_search(file_path)
                        if found_path:
                            logger.info(f"  Encontrado arquivo em caminho alternativo: {found_path}")
                            existing_content = file_manager.read_file(found_path)
                            file_path = found_path  # Usa o caminho encontrado
                        else:
                            continue

                    if fix.get("append"):
                        new_content = existing_content + "\n" + (content or "")
                    else:
                        new_content = content or existing_content

                    if new_content == existing_content:
                        logger.info(f"  Sem alterações reais: {file_path}")
                        continue

                    if not self._is_content_valid_for_file(file_path, new_content):
                        logger.warning(f"  Ignorado (conteúdo inválido): {file_path}")
                        continue

                    if file_manager.create_file(file_path, new_content):
                        files_modified.append(file_path)
                        logger.info(f"  Modificado: {file_path}")

                elif file_path and action == "patch":
                    # CORREÇÃO: Usar read_file_flexible para encontrar o arquivo
                    existing_content = file_manager.read_file_flexible(file_path)
                    if existing_content is None:
                        logger.warning(f"  Arquivo para patch não encontrado: {file_path}")
                        # Tenta encontrar em todos os serviços
                        found_path = file_manager.find_file_with_flexible_search(file_path)
                        if found_path:
                            logger.info(f"  Encontrado arquivo em caminho alternativo: {found_path}")
                            existing_content = file_manager.read_file(found_path)
                            file_path = found_path
                        else:
                            continue

                    patched_content = self._apply_search_replace_patch(existing_content, fix)
                    if patched_content is None or patched_content == existing_content:
                        logger.warning(f"  Patch ignorado (sem alteração aplicável): {file_path}")
                        continue

                    if not self._is_content_valid_for_file(file_path, patched_content):
                        logger.warning(f"  Ignorado (patch inválido): {file_path}")
                        continue

                    if file_manager.create_file(file_path, patched_content):
                        files_modified.append(file_path)
                        logger.info(f"  Patch aplicado: {file_path}")
        
        except Exception as e:
            logger.error(f"Erro ao usar LLM para correção: {e}")
        
        return files_modified

    def _select_relevant_files(self, validation_result: ValidationResult, execution_result: Any) -> list[str]:
        """Seleciona arquivos potencialmente relevantes com base nas issues de validação."""
        files = getattr(execution_result, "files_created", []) or []
        if not files:
            return []

        # CORREÇÃO: Normalizar nomes de arquivos (hífen → underscore)
        # O LLM pode retornar "order-service" mas o projeto usa "order_service"
        normalized_files = []
        for f in files:
            normalized = f.replace('-', '_')
            normalized_files.append(normalized)
        
        # Usar arquivo original se existir, caso contrário usar normalizado
        final_files = []
        for orig, norm in zip(files, normalized_files):
            if orig in files:
                final_files.append(orig)
            elif norm in files:
                final_files.append(norm)
            else:
                final_files.append(orig)  # keep original as fallback

        terms: set[str] = set()
        for issue in validation_result.issues + validation_result.rejected_items + validation_result.missing_items:
            for token in re.findall(r"[a-zA-Z_][a-zA-Z0-9_./-]*", issue.lower()):
                if len(token) >= 4:
                    terms.add(token)
                    # Also add normalized version (hyphen to underscore)
                    terms.add(token.replace('-', '_'))

        ranked: list[tuple[int, str]] = []
        for file_path in final_files:
            normalized = file_path.lower().replace("\\", "/")
            score = sum(1 for term in terms if term in normalized)
            ranked.append((score, file_path))

        ranked.sort(key=lambda item: item[0], reverse=True)
        top_matches = [path for score, path in ranked if score > 0][:10]
        if top_matches:
            return top_matches

        return final_files[:8]

    def _build_file_context_snippets(self, file_manager: FileManager, files: list[str]) -> str:
        """Monta snippets curtos de arquivos para orientar o LLM sem estourar contexto."""
        snippets: list[str] = []
        for file_path in files[:10]:
            # Usa busca flexível para encontrar arquivos
            content = file_manager.read_file_flexible(file_path)
            if content is None:
                continue

            truncated = content[:1200]
            snippets.append(f"### {file_path}\n```\n{truncated}\n```")

        return "\n\n".join(snippets)

    def _looks_like_placeholder(self, content: str) -> bool:
        """Heurística simples para evitar gravar placeholders vazios."""
        lowered = content.lower()
        markers = [
            "todo", "placeholder", "add your code", "implemente aqui",
            "adicionar aqui", "to be implemented", "pass  #",
        ]
        return any(marker in lowered for marker in markers)

    def _apply_search_replace_patch(self, existing_content: str, fix: dict) -> str | None:
        """Aplica patch simples baseado em search/replace retornado pelo LLM."""
        search = fix.get("search")
        replace = fix.get("replace", "")
        if not isinstance(search, str):
            return None

        if search not in existing_content:
            return None

        return existing_content.replace(search, replace)

    def _is_content_valid_for_file(self, file_path: str, content: str) -> bool:
        """Valida conteúdo básico para evitar que o Fix Agent quebre arquivos existentes."""
        if not file_path.endswith(".py"):
            return True

        try:
            ast.parse(content)
            return True
        except SyntaxError as exc:
            logger.warning(f"Conteúdo Python inválido para {file_path}: {exc}")
            return False

    def _parse_fix_json(self, llm_output: str) -> dict | None:
        """
        Extrai JSON de correções do LLM com múltiplas estratégias de parsing.
        
        Improved to handle various LLM output formats and parsing failures.
        """
        candidates: list[str] = []

        # Strategy 1: Try markdown json block
        markdown_match = re.search(r"```json\s*(\{.*?\})\s*```", llm_output, re.DOTALL)
        if markdown_match:
            candidates.append(markdown_match.group(1))

        # Strategy 2: Try to find JSON between braces
        start = llm_output.find('{')
        end = llm_output.rfind('}')
        if start >= 0 and end > start:
            candidates.append(llm_output[start:end + 1])

        # Strategy 3: Try to find JSON array
        array_start = llm_output.find('[')
        array_end = llm_output.rfind(']')
        if array_start >= 0 and array_end > array_start:
            candidates.append(llm_output[array_start:array_end + 1])

        # Clean up candidates - remove trailing commas and fix common issues
        for candidate in list(candidates):
            # Fix trailing commas
            cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
            # Remove single-line comments
            cleaned = re.sub(r"//.*?(\n|$)", "\n", cleaned)
            # Remove multi-line comments
            cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
            candidates.append(cleaned)

        # Try to parse each candidate
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                # Verify it's a valid fix structure
                if isinstance(parsed, dict):
                    if "fixes" in parsed and isinstance(parsed.get("fixes"), list):
                        return parsed
                    # If it's a dict but not with "fixes", wrap it
                    return {"fixes": [parsed]}
                elif isinstance(parsed, list):
                    # If it's a list, wrap it
                    return {"fixes": parsed}
            except json.JSONDecodeError:
                continue

        # Last resort: try to extract any JSON-like structure
        logger.warning("Não foi possível parsear resposta do LLM para correção")
        logger.debug(f"Output recebido: {llm_output[:500]}...")
        
        return None
    
    def _fix_basic(
        self,
        file_manager: FileManager,
        fix_plan: dict,
        project_path: str
    ) -> list[str]:
        """
        Aplica correções básicas sem LLM.
        
        Args:
            file_manager: Gerenciador de arquivos
            fix_plan: Plano de correção
            project_path: Caminho do projeto
            
        Returns:
            Lista de arquivos modificados
        """
        files_modified = []
        
        # Lista arquivos existentes
        all_files = file_manager.list_files(".")
        
        # Para cada padrão a corrigir
        for pattern in fix_plan.get("patterns_to_fix", []):
            logger.info(f"  Verificando padrão: {pattern}")
            
            if pattern == "docker":
                # Gera docker-compose se não existir
                docker_compose_path = "docker-compose.yml"
                if docker_compose_path not in all_files:
                    content = self._generate_docker_compose()
                    if file_manager.create_file(docker_compose_path, content):
                        files_modified.append(docker_compose_path)
                        logger.info(f"  Criado: {docker_compose_path}")
        
        return files_modified
    
    def _build_fix_prompt(self, requirement: Requirement, issues: list[str]) -> str:
        """
        Constrói prompt para LLM sugerir correções.
        
        Args:
            requirement: Requisito original
            issues: Lista de problemas
            
        Returns:
            Prompt formatado
        """
        issues_text = "\n".join([f"- {issue}" for issue in issues])
        
        return f"""
Você é um agente de correção de código. Analise os problemas identificados
e sugira correções específicas.

## Requisitos Originais
{requirement.description}

## Problemas Identificados
{issues_text}

## Sua Tarefa
Analise cada problema e gere um plano de correção em JSON com o seguinte formato:

{{
    "fixes": [
        {{
            "file_path": "caminho/arquivo.py",
            "action": "create" | "modify",
            "content": "conteúdo completo do arquivo ou parte a adicionar",
            "reason": "por que esta correção é necessária"
        }}
    ]
}}

Apenas retorne o JSON, sem outros textos.
"""
    
    def _generate_docker_compose(self) -> str:
        """
        Gera um docker-compose.yml básico.
        
        Returns:
            Conteúdo do docker-compose.yml
        """
        return '''version: '3.8'

services:
  # Adicione seus serviços aqui
  # Exemplo:
  # app:
  #   build: .
  #   ports:
  #     - "8000:8000"
  #   environment:
  #     - DATABASE_URL=postgresql://postgres:postgres@db:5432/mydb
  #   depends_on:
  #     - db
  #
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_PASSWORD: postgres
  #     POSTGRES_DB: mydb
  #   volumes:
  #     - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
'''
    
    def _generate_fix_report(
        self,
        issues: list[str],
        fix_plan: dict,
        files_modified: list[str]
    ) -> str:
        """
        Gera relatório das correções aplicadas.
        
        Args:
            issues: Problemas identificados
            fix_plan: Plano de correção
            files_modified: Arquivos modificados
            
        Returns:
            Relatório formatado
        """
        report_lines = [
            "=" * 60,
            "RELATÓRIO DE CORREÇÕES",
            "=" * 60,
            "",
            f"Problemas identificados: {len(issues)}",
            "",
            "-" * 60,
            "Problemas:",
            "-" * 60,
        ]
        
        for issue in issues:
            report_lines.append(f"  - {issue}")
        
        report_lines.extend([
            "",
            "-" * 60,
            "Ações realizadas:",
            "-" * 60,
        ])
        
        for action in fix_plan.get("actions", []):
            report_lines.append(f"  ✓ {action}")
        
        if not fix_plan.get("actions"):
            report_lines.append("  (nenhuma ação específica)")
        
        report_lines.extend([
            "",
            "-" * 60,
            "Arquivos modificados:",
            "-" * 60,
        ])
        
        if files_modified:
            for file in files_modified:
                report_lines.append(f"  - {file}")
        else:
            report_lines.append("  (nenhum arquivo modificado)")
        
        report_lines.extend([
            "",
            "=" * 60,
            "FIM DO RELATÓRIO",
            "=" * 60,
        ])
        
        return "\n".join(report_lines)


class FixManager:
    """
    Gerenciador de correções - coordena múltiplas tentativas.
    
    Controla o loop de:
    1. Validação → Falha
    2. Fix Agent → Correção
    3. Validação → Sucesso ou nova falha
    4. Repetir até limite ou sucesso
    """
    
    def __init__(self, llm_provider: OllamaProvider = None):
        self.fix_agent = FixAgent(llm_provider)
        self.error_logger = get_error_logger()
    
    async def execute_with_fix_loop(
        self,
        requirement: Requirement,
        validation_result: ValidationResult,
        validator_agent: Any,
        executor_result: Any,
        max_attempts: int = 3
    ) -> dict:
        """
        Executa o loop de correção até sucesso ou limite.
        
        Args:
            requirement: Requisito original
            validation_result: Resultado da validação
            validator_agent: Agente validador para revalidação
            executor_result: Resultado do executor
            max_attempts: Máximo de tentativas de correção
            
        Returns:
            Dicionário com resultado final
        """
        logger.info(f"Iniciando loop de correção (max: {max_attempts} tentativas)")
        
        current_validation = validation_result
        attempt = 1
        
        while attempt <= max_attempts:
            logger.info(f"\n{'='*60}")
            logger.info(f"CICLO DE CORREÇÃO {attempt}/{max_attempts}")
            logger.info(f"{'='*60}")
            
            # Se já está aprovado, sai do loop
            if current_validation.status.value == "approved":
                logger.info("✅ Validação aprovada!")
                break
            
            # Executa correção
            fix_result = await self.fix_agent.execute(
                requirement,
                current_validation,
                attempt
            )
            
            # Revalida
            logger.info("Revalidando após correção...")
            current_validation = await validator_agent.validate(
                requirement,
                executor_result
            )
            
            if current_validation.status.value == "approved":
                logger.info("✅ Validação aprovada após correção!")
                break
            
            attempt += 1
        
        # Registra resultado final
        self.error_logger.log_final_result(
            requirement_id=requirement.id,
            total_attempts=attempt,
            success=current_validation.status.value == "approved",
            final_score=current_validation.score,
            error_message="" if current_validation.status.value == "approved" else "Limite de tentativas atingido"
        )
        
        return {
            "validation_result": current_validation,
            "total_attempts": attempt,
            "success": current_validation.status.value == "approved"
        }

