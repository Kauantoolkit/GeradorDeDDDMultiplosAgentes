"""
Fix Agent V2 - Agente de Correção (VERSÃO CORRIGIDA)
=====================================================

Este agente é responsável por:
- Receber feedback do Validator Agent sobre problemas encontrados
- Analisar os problemas e criar plano de correção
- Aplicar correções nos arquivos gerados
- PRIORIZAR EDITAR arquivos existentes ao invés de CRIAR novos
- Registrar as ações realizadas para logs
- Retornar relatório das correções aplicadas

MUDANÇAS DESTA VERSÃO:
- Nova lógica: ANTES de CRIAR, verificar se arquivo já existe
- Se existir (exatamente ou similar), converter action para "modify"
- Evita duplicação de arquivos (problema principal identificado)
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
    
    FLUXO:
    1. Analisa os problemas identificados
    2. Cria plano de correção
    3. Aplica correções nos arquivos (PRIORIZANDO EDITAR)
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
        self.name = "Fix Agent V2"
        self.error_logger = get_error_logger()
        logger.info(f"{self.name} inicializado - COM CORREÇÃO: Editar primeiro, criar depois")
    
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
            logger.info(f"FIX AGENT V2 - Tentativa {attempt}")
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
        """Coleta todos os problemas identificados na validação."""
        issues = []
        issues.extend(validation_result.issues)
        for item in validation_result.rejected_items:
            issues.append(f"Rejeitado: {item}")
        for item in validation_result.missing_items:
            issues.append(f"Faltando: {item}")
        unique_issues = list(set(issues))
        return unique_issues
    
    def _create_fix_plan(self, issues: list[str]) -> dict:
        """Cria um plano de correção baseado nos problemas identificados."""
        plan = {
            "actions": [],
            "files_to_check": [],
            "patterns_to_fix": []
        }
        
        for issue in issues:
            issue_lower = issue.lower()
            
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
            
            if "import" in issue_lower or ("erro" in issue_lower and "sintaxe" in issue_lower):
                plan["actions"].append("Corrigir imports e sintaxe")
                plan["patterns_to_fix"].append("imports")
        
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
        """Aplica as correções nos arquivos."""
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
                await self._fix_with_llm_v2(
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
                logger.info(f"  Modificado: {requirements_path} (adicionada dependência email-validator)")

        return modified
    
    # ========================================================================
    # NOVO MÉTODO: _fix_with_llm_v2 - COM CORREÇÃO PRINCIPAL
    # Prioriza EDITAR arquivos existentes ao invés de CRIAR novos
    # ========================================================================
    
    async def _fix_with_llm_v2(
        self,
        file_manager: FileManager,
        requirement: Requirement,
        validation_result: ValidationResult,
        execution_result: Any,
        project_path: str
    ) -> list[str]:
        """
        Usa LLM para sugerir e aplicar correções.
        
        CORREÇÃO PRINCIPAL: 
        - ANTES de CRIAR novo arquivo, verificar se já existe
        - Se existir (exatamente ou similar), converter action para "modify"
        - Isso evita duplicação de arquivos como order_service duplicated
        """
        files_modified = []
        
        try:
            relevant_files = self._select_relevant_files(validation_result, execution_result)
            context_snippets = self._build_file_context_snippets(file_manager, relevant_files)

            # Constrói prompt para correção
            prompt = PromptBuilder.build_fix_prompt(
                requirement,
                validation_result,
                execution_result,
                file_context=context_snippets,
            )
            
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
            
            # ================================================================
            # CORREÇÃO CRÍTICA: Mapear TODOS os arquivos existentes PRIMEIRO
            # ================================================================
            existing_files = self._get_all_existing_files(file_manager, project_path)
            logger.info(f"Arquivos existentes mapeados: {len(existing_files)}")
            
            for fix in fixes:
                file_path = fix.get("file_path")
                if file_path:
                    file_path = file_path.replace('-', '_')
                
                content = fix.get("content")
                action = fix.get("action", "modify")

                if file_path and action in {"modify", "create"} and self._looks_like_placeholder(content or ""):
                    logger.warning(f"  Ignorado (placeholder): {file_path}")
                    continue

                # ============================================================
                # CORREÇÃO: Antes de CRIAR, verificar se já existe
                # ============================================================
                if file_path and action == "create":
                    # Verifica se o arquivo EXATAMENTE já existe
                    exact_match = file_manager.read_file_flexible(file_path)
                    if exact_match:
                        logger.info(f"  Arquivo já existe: {file_path} → convertendo para EDITAR")
                        action = "modify"
                        content = content or exact_match
                    else:
                        # Não existe exatamente - procurar arquivo SIMILAR
                        similar_path = self._find_similar_file(file_path, existing_files)
                        if similar_path:
                            logger.info(f"  Encontrado arquivo similar: {file_path} → {similar_path}")
                            file_path = similar_path
                            action = "modify"
                            existing_content = file_manager.read_file(similar_path)
                            if existing_content and content:
                                content = content
                            elif existing_content:
                                content = existing_content

                # Processa action = "modify" ou "patch"
                if file_path and action == "modify":
                    existing_content = file_manager.read_file_flexible(file_path)
                    if existing_content is None:
                        # Não encontrou - procurar similar
                        similar_path = self._find_similar_file(file_path, existing_files)
                        if similar_path:
                            logger.info(f"  Encontrado arquivo similar para modificação: {file_path} → {similar_path}")
                            existing_content = file_manager.read_file(similar_path)
                            file_path = similar_path
                        else:
                            logger.warning(f"  Arquivo para modificação não encontrado: {file_path}")
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
                    existing_content = file_manager.read_file_flexible(file_path)
                    if existing_content is None:
                        similar_path = self._find_similar_file(file_path, existing_files)
                        if similar_path:
                            logger.info(f"  Encontrado arquivo similar para patch: {file_path} → {similar_path}")
                            existing_content = file_manager.read_file(similar_path)
                            file_path = similar_path
                        else:
                            logger.warning(f"  Arquivo para patch não encontrado: {file_path}")
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
    
    def _get_all_existing_files(self, file_manager: FileManager, project_path: str) -> list[str]:
        """Retorna lista de TODOS os arquivos existentes no projeto."""
        try:
            all_files = file_manager.list_files(".")
            return all_files
        except Exception as e:
            logger.warning(f"Erro ao listar arquivos existentes: {e}")
            return []
    
    def _find_similar_file(self, target_path: str, existing_files: list[str]) -> str | None:
        """
        Encontra arquivo similar ao caminho alvo na lista de arquivos existentes.
        
        Exemplo:
        - target: services/order_service/domain/entities.py
        - existing: services/order_service/domain/order_entities.py
        - retorna: services/order_service/domain/order_entities.py
        """
        if not existing_files:
            return None
            
        target_name = target_path.split('/')[-1] if '/' in target_path else target_path
        target_dir = '/'.join(target_path.split('/')[:-1]) if '/' in target_path else ''
        
        # Estratégia 1: Mesmo nome de arquivo em diretório similar
        for existing in existing_files:
            existing_name = existing.split('/')[-1] if '/' in existing else existing
            existing_dir = '/'.join(existing.split('/')[:-1]) if '/' in existing else ''
            
            if existing_name == target_name:
                if target_dir and existing_dir:
                    if target_dir.replace('_', '') in existing_dir.replace('_', ''):
                        return existing
                    target_service = self._extract_service_name(target_dir)
                    existing_service = self._extract_service_name(existing_dir)
                    if target_service == existing_service:
                        return existing
        
        # Estratégia 2: Mesmo padrão de nomenclatura
        for existing in existing_files:
            if '_entities.py' in existing and '_entities.py' in target_path:
                if self._same_service_dir(target_path, existing):
                    return existing
            if '_value_objects.py' in existing and '_value_objects.py' in target_path:
                if self._same_service_dir(target_path, existing):
                    return existing
            if '_aggregates.py' in existing and '_aggregates.py' in target_path:
                if self._same_service_dir(target_path, existing):
                    return existing
        
        return None
    
    def _extract_service_name(self, path: str) -> str | None:
        """Extrai nome do serviço de um caminho."""
        parts = path.replace('\\', '/').split('/')
        if 'services' in parts:
            idx = parts.index('services') + 1
            if idx < len(parts):
                return parts[idx]
        return None
    
    def _same_service_dir(self, path1: str, path2: str) -> bool:
        """Verifica se dois caminhos pertencem ao mesmo serviço."""
        service1 = self._extract_service_name(path1)
        service2 = self._extract_service_name(path2)
        return service1 is not None and service1 == service2

    # Métodos existentes (mantidos para compatibilidade)
    
    def _select_relevant_files(self, validation_result: ValidationResult, execution_result: Any) -> list[str]:
        """Seleciona arquivos potencialmente relevantes com base nas issues de validação."""
        files = getattr(execution_result, "files_created", []) or []
        if not files:
            return []

        normalized_files = []
        for f in files:
            normalized = f.replace('-', '_')
            normalized_files.append(normalized)
        
        final_files = []
        for orig, norm in zip(files, normalized_files):
            if orig in files:
                final_files.append(orig)
            elif norm in files:
                final_files.append(norm)
            else:
                final_files.append(orig)

        terms: set[str] = set()
        for issue in validation_result.issues + validation_result.rejected_items + validation_result.missing_items:
            for token in re.findall(r"[a-zA-Z_][a-zA-Z0-9_./-]*", issue.lower()):
                if len(token) >= 4:
                    terms.add(token)
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
        """Monta snippets curtos de arquivos para orientar o LLM."""
        snippets: list[str] = []
        for file_path in files[:10]:
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
        """Valida conteúdo básico para evitar que o Fix Agent quebre arquivos."""
        if not file_path.endswith(".py"):
            return True
        try:
            ast.parse(content)
            return True
        except SyntaxError as exc:
            logger.warning(f"Conteúdo Python inválido para {file_path}: {exc}")
            return False

    def _parse_fix_json(self, llm_output: str) -> dict | None:
        """Extrai JSON de correções do LLM com múltiplas estratégias de parsing."""
        candidates: list[str] = []

        markdown_match = re.search(r"```json\s*(\{.*?\})\s*```", llm_output, re.DOTALL)
        if markdown_match:
            candidates.append(markdown_match.group(1))

        start = llm_output.find('{')
        end = llm_output.rfind('}')
        if start >= 0 and end > start:
            candidates.append(llm_output[start:end + 1])

        array_start = llm_output.find('[')
        array_end = llm_output.rfind(']')
        if array_start >= 0 and array_end > array_start:
            candidates.append(llm_output[array_start:array_end + 1])

        for candidate in list(candidates):
            cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
            cleaned = re.sub(r"//.*?(\n|$)", "\n", cleaned)
            cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
            candidates.append(cleaned)

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    if "fixes" in parsed and isinstance(parsed.get("fixes"), list):
                        return parsed
                    return {"fixes": [parsed]}
                elif isinstance(parsed, list):
                    return {"fixes": parsed}
            except json.JSONDecodeError:
                continue

        logger.warning("Não foi possível parsear resposta do LLM para correção")
        return None
    
    def _fix_basic(
        self,
        file_manager: FileManager,
        fix_plan: dict,
        project_path: str
    ) -> list[str]:
        """Aplica correções básicas sem LLM."""
        files_modified = []
        all_files = file_manager.list_files(".")
        
        for pattern in fix_plan.get("patterns_to_fix", []):
            logger.info(f"  Verificando padrão: {pattern}")
            
            if pattern == "docker":
                docker_compose_path = "docker-compose.yml"
                if docker_compose_path not in all_files:
                    content = self._generate_docker_compose()
                    if file_manager.create_file(docker_compose_path, content):
                        files_modified.append(docker_compose_path)
                        logger.info(f"  Criado: {docker_compose_path}")
        
        files_modified.extend(self._fix_init_files_smart(file_manager, project_path))
        files_modified.extend(self._complete_basic_templates(file_manager, project_path))
        
        return files_modified
    
    def _fix_init_files_smart(self, file_manager: FileManager, project_path: str) -> list[str]:
        """Cria arquivos __init__.py de forma inteligente."""
        modified = []
        all_files = file_manager.list_files(".")
        
        python_dirs = set()
        for f in all_files:
            if f.endswith('.py') and f != '__init__.py':
                dir_path = '/'.join(f.split('/')[:-1])
                if dir_path:
                    python_dirs.add(dir_path)
        
        for dir_path in python_dirs:
            init_file = f"{dir_path}/__init__.py"
            existing = file_manager.read_file(init_file)
            if existing is not None:
                if self._is_init_placeholder(existing):
                    proper_content = self._generate_proper_init(dir_path)
                    if file_manager.create_file(init_file, proper_content):
                        modified.append(init_file)
                        logger.info(f"  Completado: {init_file}")
                continue
            
            dir_files = [f for f in all_files if f.startswith(dir_path + '/') and f != init_file]
            if dir_files:
                proper_content = self._generate_proper_init(dir_path)
                if file_manager.create_file(init_file, proper_content):
                    modified.append(init_file)
                    logger.info(f"  Criado: {init_file}")
        
        return modified
    
    def _is_init_placeholder(self, content: str) -> bool:
        """Verifica se o conteúdo do __init__.py é apenas um placeholder."""
        if not content:
            return True
        cleaned = ''.join(c for c in content if not c.isspace())
        if not cleaned:
            return True
        placeholder_patterns = ['# TODO', '# Placeholder', '# Add your code', 'pass  #', 'pass\n', '# Module']
        content_lower = content.lower()
        lines = content.strip().split('\n')
        non_empty_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
        if len(non_empty_lines) == 1 and non_empty_lines[0] == 'pass':
            return True
        return any(pattern.lower() in content_lower for pattern in placeholder_patterns)
    
    def _generate_proper_init(self, dir_path: str) -> str:
        """Gera conteúdo adequado para __init__.py baseado no diretório."""
        module_name = dir_path.split('/')[-1] if '/' in dir_path else dir_path
        if 'domain' in dir_path.lower():
            return f'''"""{module_name.title()} Domain Layer - Domain entities, value objects, and domain services."""
__all__ = []'''
        elif 'application' in dir_path.lower():
            return f'''"""{module_name.title()} Application Layer - Use cases, DTOs, and application services."""
__all__ = []'''
        elif 'infrastructure' in dir_path.lower():
            return f'''"""{module_name.title()} Infrastructure Layer - Database, repositories, and external services."""
__all__ = []'''
        elif 'api' in dir_path.lower():
            return f'''"""{module_name.title()} API Layer - Routes, controllers, and schemas."""
__all__ = []'''
        else:
            return f'''"""{module_name.title()} - Module initialization."""
__all__ = []'''
    
    def _complete_basic_templates(self, file_manager: FileManager, project_path: str) -> list[str]:
        """Completa templates básicos existentes com lógica de negócio."""
        modified = []
        all_files = file_manager.list_files(".")
        
        for file_path in all_files:
            if not file_path.endswith('_entities.py') and not file_path.endswith('/entities.py'):
                continue
            
            content = file_manager.read_file(file_path)
            if not content:
                continue
            
            if self._is_basic_entity_template(content):
                entity_name = self._extract_main_entity_name(content)
                if entity_name:
                    completed_content = self._complete_entity_template(content, entity_name, file_path)
                    if completed_content and completed_content != content:
                        if file_manager.create_file(file_path, completed_content):
                            modified.append(file_path)
                            logger.info(f"  Completo: {file_path} ({entity_name})")
        
        return modified
    
    def _is_basic_entity_template(self, content: str) -> bool:
        """Verifica se o conteúdo é um template básico que precisa de completamento."""
        if not content:
            return False
        basic_indicators = ['pass  #', '# TODO', 'pass\n\n\n', 'def create(', 'def update(', 'def to_dict(']
        indicator_count = sum(1 for ind in basic_indicators if ind in content)
        has_business_methods = any(method in content for method in [
            'authenticate', 'verify', 'activate', 'deactivate',
            'add_item', 'remove_item', 'calculate_', 'cancel',
            'process', 'approve', 'reject', 'refund',
            'is_available', 'decrease_stock', 'apply_discount',
        ])
        return indicator_count >= 2 and not has_business_methods
    
    def _extract_main_entity_name(self, content: str) -> str | None:
        """Extrai o nome da entidade principal do conteúdo."""
        match = re.search(r'class\s+(\w+)\s*[:\(]', content)
        if match:
            return match.group(1)
        return None
    
    def _complete_entity_template(self, content: str, entity_name: str, file_path: str) -> str | None:
        """Completa um template básico de entidade com métodos de negócio."""
        entity_lower = entity_name.lower()
        
        if 'user' in entity_lower or 'usuario' in entity_lower:
            business_methods = '''
    def authenticate(self, password: str) -> bool:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, self.senha_hash)
    
    def verify_email(self):
        self.is_verified = True
        self.updated_at = datetime.now()
    
    def deactivate(self):
        self.is_active = False
        self.updated_at = datetime.now()
'''
        elif 'order' in entity_lower or 'pedido' in entity_lower:
            business_methods = '''
    def add_item(self, item: dict):
        self.itens.append(item)
        self.total += item.get("preco", 0) * item.get("quantidade", 1)
        self.updated_at = datetime.now()
    
    def calculate_total(self) -> float:
        return sum(item.get("preco", 0) * item.get("quantidade", 1) for item in self.itens)
    
    def can_cancel(self) -> bool:
        return self.status in ["PENDING", "CONFIRMED"]
    
    def cancel(self):
        if self.can_cancel():
            self.status = "CANCELLED"
            self.updated_at = datetime.now()
'''
        elif 'product' in entity_lower or 'produto' in entity_lower:
            business_methods = '''
    def is_available(self) -> bool:
        return self.estoque > 0
    
    def decrease_stock(self, quantity: int) -> bool:
        if self.estoque >= quantity:
            self.estoque -= quantity
            self.updated_at = datetime.now()
            return True
        return False
    
    def apply_discount(self, percentage: float) -> float:
        self.preco = self.preco * (1 - percentage / 100)
        self.updated_at = datetime.now()
        return self.preco
'''
        else:
            business_methods = '''
    def activate(self):
        self.updated_at = datetime.now()
    
    def deactivate(self):
        self.updated_at = datetime.now()
'''
        
        lines = content.split('\n')
        insert_idx = len(lines)
        
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith('def ') and not lines[i].strip().startswith('def __'):
                insert_idx = i + 1
                break
        
        lines.insert(insert_idx, business_methods)
        
        if 'from datetime import datetime' not in content:
            for i, line in enumerate(lines):
                if line.startswith('class ') or line.startswith('@'):
                    lines.insert(i, 'from datetime import datetime')
                    break
            else:
                lines.insert(0, 'from datetime import datetime')
        
        return '\n'.join(lines)
    
    def _generate_docker_compose(self) -> str:
        """Gera um docker-compose.yml básico."""
        return '''version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/mydb
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
'''
    
    def _generate_fix_report(
        self,
        issues: list[str],
        fix_plan: dict,
        files_modified: list[str]
    ) -> str:
        """Gera relatório das correções aplicadas."""
        report_lines = [
            "=" * 60,
            "RELATÓRIO DE CORREÇÕES - FIX AGENT V2",
            "=" * 60,
            f"Problemas identificados: {len(issues)}",
            "-" * 60,
            "Problemas:",
        ]
        for issue in issues:
            report_lines.append(f"  - {issue}")
        report_lines.extend(["", "-" * 60, "Ações realizadas:"])
        for action in fix_plan.get("actions", []):
            report_lines.append(f"  ✓ {action}")
        if not fix_plan.get("actions"):
            report_lines.append("  (nenhuma ação específica)")
        report_lines.extend(["", "-" * 60, "Arquivos modificados:"])
        if files_modified:
            for file in files_modified:
                report_lines.append(f"  - {file}")
        else:
            report_lines.append("  (nenhum arquivo modificado)")
        report_lines.extend(["", "=" * 60])
        return "\n".join(report_lines)


class FixManager:
    """Gerenciador de correções - coordena múltiplas tentativas."""
    
    def __init__(self, llm_provider: OllamaProvider = None):
        self.fix_agent = FixAgent(llm_provider)
        self.error_logger = get_error_logger()

