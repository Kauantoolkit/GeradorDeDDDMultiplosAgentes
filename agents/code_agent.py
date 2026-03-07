"""
Code Agent - Unified Code Generation and Fixing
================================================

This agent combines the functionality of ExecutorAgent and FixAgent:
- Generates initial DDD project code
- Fixes runtime errors with full project context
- Receives all project files when fixing

Key Principles:
1. Full project context for both generation and fixing
2. Objective feedback from RuntimeRunner drives fixes
3. Edit existing files instead of creating duplicates
"""

import json
import re
import ast
from datetime import datetime
from typing import Any, Optional
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    Requirement
)
from infrastructure.llm_provider import OllamaProvider, PromptBuilder
from infrastructure.file_manager import FileManager

# Import agent logger for structured logging
from agents.agent_logger import (
    get_logger,
    log_execution,
    log_error,
    log_communication,
    AgentExecutionContext
)


class CodeAgent:
    """
    Unified Agent for code generation and fixing.
    
    This agent is responsible for:
    1. Initial DDD project generation
    2. Fixing runtime errors with full project context
    
    Key difference from previous agents:
    - Receives ALL project files when fixing (not just validation feedback)
    - Uses objective runtime errors (not LLM judgment)
    - Edit existing files instead of creating duplicates
    """
    
    def __init__(self, llm_provider: OllamaProvider):
        """
        Initialize the Code Agent.
        
        Args:
            llm_provider: LLM provider for code generation
        """
        self.llm_provider = llm_provider
        self.name = "Code Agent"
        logger.info(f"{self.name} initialized - Generation + Fixing")
    
    async def generate(
        self,
        requirement: Requirement,
        trace_id: str = None
    ) -> ExecutionResult:
        """
        Generate initial DDD project code.
        
        Args:
            requirement: Project requirements
            trace_id: Unique execution ID
            
        Returns:
            ExecutionResult with generated files
        """
        start_time = datetime.now()
        
        # Get or create logger with trace_id
        agent_logger = get_logger()
        if trace_id is None:
            trace_id = agent_logger.create_trace_id()
        
        # Create execution context
        context = AgentExecutionContext(
            agent_name=self.name,
            trace_id=trace_id,
            input_data={
                "requirement": requirement.description[:500] if requirement.description else "",
                "output_directory": requirement.project_config.output_directory,
                "framework": requirement.project_config.framework,
                "database": requirement.project_config.database,
                "mode": "generation"
            }
        )
        context.start()
        
        result = ExecutionResult(
            agent_type=AgentType.CODE,
            status=ExecutionStatus.IN_PROGRESS,
            started_at=start_time
        )
        
        try:
            logger.info("="*60)
            logger.info("CODE AGENT - Generating initial code")
            logger.info(f"trace_id: {trace_id[:8]}...")
            logger.info("="*60)
            
            file_manager = FileManager(requirement.project_config.output_directory)
            base_prompt = PromptBuilder.build_executor_prompt(requirement)
            
            logger.info("Calling LLM for code generation...")
            
            llm_output = await self.llm_provider.generate(
                prompt=base_prompt,
                temperature=0.3,
                max_tokens=8000
            )
            
            result.output = llm_output
            logger.info(f"LLM response received ({len(llm_output)} chars)")
            
            # Parse and create files
            created_files = self._generate_and_create_files(
                file_manager,
                llm_output,
                requirement.project_config
            )
            
            result.files_created = created_files
            result.status = ExecutionStatus.SUCCESS
            
            logger.info(f"Code generated: {len(created_files)} files created")
            
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            context.end(
                output_data={
                    "files_created": len(created_files),
                    "execution_time": result.execution_time
                },
                status="success"
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error in {self.name}: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            context.end_with_error(e, context={"error": str(e)})
            
            return result
    
    async def fix(
        self,
        requirement: Requirement,
        runtime_errors: list[dict],
        attempt: int = 1,
        trace_id: str = None
    ) -> ExecutionResult:
        """
        Fix runtime errors with full project context.
        
        This is the key improvement: instead of using LLM judgment,
        we use objective runtime errors and provide FULL project context.
        
        Args:
            requirement: Original project requirements
            runtime_errors: List of runtime errors from RuntimeRunner
            attempt: Fix attempt number
            trace_id: Unique execution ID
            
        Returns:
            ExecutionResult with modified files
        """
        start_time = datetime.now()
        
        # Get or create logger with trace_id
        agent_logger = get_logger()
        if trace_id is None:
            trace_id = agent_logger.create_trace_id()
        
        context = AgentExecutionContext(
            agent_name=self.name,
            trace_id=trace_id,
            input_data={
                "requirement_id": requirement.id,
                "attempt": attempt,
                "runtime_errors_count": len(runtime_errors),
                "mode": "fixing"
            }
        )
        context.start()
        
        result = ExecutionResult(
            agent_type=AgentType.CODE,
            status=ExecutionStatus.IN_PROGRESS,
            started_at=start_time
        )
        
        try:
            logger.info("="*60)
            logger.info(f"CODE AGENT - Fixing errors (attempt {attempt})")
            logger.info("="*60)
            
            # Format runtime errors for the LLM
            errors_text = self._format_runtime_errors(runtime_errors)
            logger.info(f"Runtime errors to fix:\n{errors_text}")
            
            # Get FULL project context (key difference from old FixAgent)
            project_path = requirement.project_config.output_directory
            file_manager = FileManager(project_path)
            all_files = file_manager.list_files(".")
            project_context = self._build_full_project_context(file_manager, all_files)
            
            logger.info(f"Full project context loaded: {len(all_files)} files")
            
            # Build fix prompt with full context
            prompt = self._build_fix_prompt(
                requirement=requirement,
                runtime_errors=errors_text,
                project_context=project_context,
                attempt=attempt
            )
            
            logger.info("Calling LLM with full project context...")
            
            llm_output = await self.llm_provider.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=4000
            )
            
            # Parse and apply fixes
            files_modified = self._apply_fixes(
                file_manager,
                llm_output,
                all_files
            )
            
            if not files_modified:
                logger.warning("No files were modified by the fix attempt")
                result.status = ExecutionStatus.FAILED
                result.error_message = "No fixes could be applied"
                return result
            
            result.files_modified = files_modified
            result.status = ExecutionStatus.SUCCESS
            result.output = f"Fixed {len(files_modified)} files"
            
            logger.info(f"Fix applied: {len(files_modified)} files modified")
            
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            context.end(
                output_data={
                    "files_modified": files_modified,
                    "execution_time": result.execution_time
                },
                status="success"
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error in {self.name} fix: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            context.end_with_error(e, context={"error": str(e)})
            
            return result
    
    def _generate_and_create_files(
        self,
        file_manager: FileManager,
        llm_output: str,
        config: Any
    ) -> list[str]:
        """
        Parse LLM output and create project files.
        
        Args:
            file_manager: File manager instance
            llm_output: LLM response
            config: Project configuration
            
        Returns:
            List of created file paths
        """
        created_files = []
        
        try:
            parsed_data = self._parse_llm_output(llm_output)
            if not parsed_data:
                logger.warning("Could not parse LLM output")
                return created_files
            
            normalized_data = self._normalize_llm_data(parsed_data)
            
            # Handle microservices format
            microservices = normalized_data.get("microservices", [])
            for microservice in microservices:
                service_name = microservice.get("name", "service")
                domain = microservice.get("domain", service_name)
                
                # Use the generation logic from ExecutorAgent
                ddd_structure = self._generate_ddd_structure(
                    service_name,
                    domain,
                    microservice,
                    config
                )
                
                for file_path, content in ddd_structure.items():
                    guarded_content = self._apply_generation_guards(file_path, content)
                    if file_manager.create_file(file_path, guarded_content):
                        created_files.append(file_path)
            
            # Handle bounded_contexts format (DDD strategic)
            bounded_contexts = normalized_data.get("bounded_contexts", [])
            for context in bounded_contexts:
                context_name = context.get("name", "unknown")
                for file_data in context.get("files", []):
                    path = file_data.get("path")
                    content = file_data.get("content", "")
                    if path and file_manager.create_file(path, content):
                        created_files.append(path)
                logger.info(f"Bounded context processed: {context_name}")
            
            # Handle extra files
            extra_files = normalized_data.get("files", [])
            for file_data in extra_files:
                path = file_data.get("path")
                content = file_data.get("content", "")
                if path and self._is_allowed_extra_file_path(path):
                    if file_manager.create_file(path, content):
                        created_files.append(path)
            
            # Generate root files
            root_files = self._generate_root_files(config, microservices)
            for file_path, content in root_files.items():
                if file_manager.create_file(file_path, content):
                    created_files.append(file_path)
            
        except Exception as e:
            logger.error(f"Error creating files: {e}")
        
        return created_files
    
    def _format_runtime_errors(self, runtime_errors: list[dict]) -> str:
        """
        Format runtime errors for the LLM prompt.
        
        Args:
            runtime_errors: List of runtime error dictionaries
            
        Returns:
            Formatted error text
        """
        lines = []
        
        for i, error in enumerate(runtime_errors, 1):
            error_type = error.get("type", "unknown")
            file_path = error.get("file", "unknown")
            line = error.get("line", 0)
            message = error.get("message", "No message")
            
            lines.append(f"{i}. {error_type} in {file_path}:{line}")
            lines.append(f"   Error: {message}")
            
            if "missing_dependency" in error:
                lines.append(f"   Missing: {error['missing_dependency']}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_full_project_context(
        self,
        file_manager: FileManager,
        all_files: list[str]
    ) -> str:
        """
        Build full project context for the LLM.
        
        This is the KEY difference from the old FixAgent:
        - We provide ALL project files, not just validation feedback
        - The LLM can see the actual code that needs fixing
        
        Args:
            file_manager: File manager instance
            all_files: List of all project files
            
        Returns:
            Formatted project context
        """
        snippets = []
        
        # Prioritize files that are likely to have errors
        priority_patterns = [
            "main.py",
            "domain/entities.py",
            "domain/__init__.py",
            "application/use_cases.py",
            "infrastructure/repositories.py",
            "api/routes.py",
            "requirements.txt"
        ]
        
        # First add priority files
        priority_files = [
            f for f in all_files
            if any(pattern in f for pattern in priority_patterns)
        ]
        
        for file_path in priority_files[:20]:
            content = file_manager.read_file(file_path)
            if content:
                # Show more content for important files
                snippets.append(f"### {file_path}\n```python\n{content[:1500]}\n```")
        
        # Then add other Python files
        other_files = [
            f for f in all_files
            if f.endswith(".py") and f not in priority_files
        ]
        
        for file_path in other_files[:30]:
            content = file_manager.read_file(file_path)
            if content:
                snippets.append(f"### {file_path}\n```python\n{content[:800]}\n```")
        
        return "\n\n".join(snippets)
    
    def _build_fix_prompt(
        self,
        requirement: Requirement,
        runtime_errors: str,
        project_context: str,
        attempt: int
    ) -> str:
        """
        Build prompt for fixing runtime errors.
        
        Args:
            requirement: Original requirements
            runtime_errors: Formatted runtime errors
            project_context: Full project context
            attempt: Fix attempt number
            
        Returns:
            Fix prompt
        """
        return f"""
You are the CODE AGENT - responsible for fixing runtime errors in generated DDD code.

OBJECTIVE: Fix the runtime errors below using the FULL project context provided.

RUNTIME ERRORS (these are REAL errors from actual execution):
{runtime_errors}

ORIGINAL REQUIREMENTS:
{requirement.description}

PROJECT CONTEXT (ALL project files - use this to understand and fix):
{project_context}

INSTRUCTIONS:

1. Analyze the runtime errors carefully - these are REAL errors from execution
2. Look at the project context to understand the code structure
3. Fix the errors by editing EXISTING files (not creating new ones)
4. Make minimal, targeted fixes

COMMON FIXES:

1. Import errors:
   - Check if module is installed in requirements.txt
   - Check if import path is correct
   - Add missing dependencies

2. Syntax errors:
   - Check for missing colons, parentheses, brackets
   - Check for invalid Python syntax

3. Missing dependencies:
   - Add to requirements.txt (e.g., email-validator, passlib, etc.)

4. Attribute errors:
   - Check if attribute exists in the class
   - Check import paths

Return JSON with fixes:
{{
    "fixes": [
        {{
            "file_path": "path/to/file.py",
            "action": "modify" | "patch",
            "content": "full file content (for modify)",
            "search": "code to find (for patch)",
            "replace": "new code (for patch)",
            "reason": "why this fix resolves the error"
        }}
    ]
}}

IMPORTANT:
- Use "modify" for complete file rewrite
- Use "patch" for small changes (search/replace)
- Make minimal, targeted fixes
- Do NOT create new files - only edit existing ones
- Return ONLY JSON, no markdown
"""
    
    def _apply_fixes(
        self,
        file_manager: FileManager,
        llm_output: str,
        existing_files: list[str]
    ) -> list[str]:
        """
        Apply fixes from LLM output.
        
        Args:
            file_manager: File manager instance
            llm_output: LLM response with fixes
            existing_files: List of existing files
            
        Returns:
            List of modified file paths
        """
        files_modified = []
        
        try:
            fix_data = self._parse_fix_json(llm_output)
            if not fix_data:
                logger.warning("Could not parse fix JSON")
                return files_modified
            
            fixes = fix_data.get("fixes", [])
            
            for fix in fixes:
                file_path = fix.get("file_path")
                if not file_path:
                    continue
                
                action = fix.get("action", "modify")
                
                # Skip placeholder content
                content = fix.get("content", "")
                if self._looks_like_placeholder(content):
                    logger.warning(f"Skipping placeholder: {file_path}")
                    continue
                
                if action == "modify":
                    existing = file_manager.read_file(file_path)
                    if existing is None:
                        # Try to find similar file
                        similar = self._find_similar_file(file_path, existing_files)
                        if similar:
                            file_path = similar
                        else:
                            logger.warning(f"File not found for modification: {file_path}")
                            continue
                    
                    if not self._is_valid_python(file_path, content):
                        logger.warning(f"Invalid Python for {file_path}")
                        continue
                    
                    if file_manager.create_file(file_path, content):
                        files_modified.append(file_path)
                        logger.info(f"Modified: {file_path}")
                
                elif action == "patch":
                    existing = file_manager.read_file(file_path)
                    if existing is None:
                        similar = self._find_similar_file(file_path, existing_files)
                        if similar:
                            file_path = similar
                            existing = file_manager.read_file(similar)
                        else:
                            logger.warning(f"File not found for patch: {file_path}")
                            continue
                    
                    search = fix.get("search", "")
                    replace = fix.get("replace", "")
                    
                    if search and search in existing:
                        new_content = existing.replace(search, replace)
                        if self._is_valid_python(file_path, new_content):
                            if file_manager.create_file(file_path, new_content):
                                files_modified.append(file_path)
                                logger.info(f"Patched: {file_path}")
        
        except Exception as e:
            logger.error(f"Error applying fixes: {e}")
        
        return files_modified
    
    def _parse_llm_output(self, llm_output: str) -> Any:
        """Parse LLM JSON output with multiple strategies."""
        # Strategy 1: Find JSON in markdown
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Find JSON without markdown
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}')
        
        if json_start >= 0 and json_end > json_start:
            json_str = llm_output[json_start:json_end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Try to fix common issues
        try:
            cleaned = self._clean_llm_output(llm_output)
            return json.loads(cleaned)
        except:
            pass
        
        return None
    
    def _normalize_llm_data(self, data: Any) -> dict:
        """Normalize LLM data structure."""
        if isinstance(data, list):
            logger.warning("Converting list to microservices format")
            return {"microservices": data}
        
        if not isinstance(data, dict):
            return {"microservices": []}
        
        # Ensure required keys exist
        for key in ["microservices", "files", "bounded_contexts"]:
            data.setdefault(key, [])
        
        return data
    
    def _clean_llm_output(self, llm_output: str) -> str:
        """Clean common JSON issues in LLM output."""
        # Remove trailing commas
        result = re.sub(r',(\s*[}\]])', r'\1', llm_output)
        # Remove comments
        result = re.sub(r'//.*?(\n|$)', '\n', result)
        result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
        return result
    
    def _parse_fix_json(self, llm_output: str) -> dict:
        """Parse fix JSON from LLM output."""
        try:
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return None
    
    def _looks_like_placeholder(self, content: str) -> bool:
        """Check if content is a placeholder."""
        if not content:
            return True
        lowered = content.lower()
        markers = ["todo", "placeholder", "add your code", "implement here"]
        return any(marker in lowered for marker in markers)
    
    def _is_valid_python(self, file_path: str, content: str) -> bool:
        """Validate Python syntax."""
        if not file_path.endswith('.py'):
            return True
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return False
    
    def _find_similar_file(self, target: str, existing: list[str]) -> Optional[str]:
        """Find similar file path."""
        target_name = target.split('/')[-1]
        
        for f in existing:
            if f.split('/')[-1] == target_name:
                return f
        
        return None
    
    def _is_allowed_extra_file_path(self, file_path: str) -> bool:
        """Check if extra file path is allowed."""
        if not file_path:
            return False
        
        allowed_prefixes = ('services/', 'frontend/')
        allowed_roots = {'README.md', 'docker-compose.yml', '.env', '.gitignore'}
        
        normalized = file_path.lstrip('./')
        
        if normalized in allowed_roots:
            return True
        
        return normalized.startswith(allowed_prefixes)
    
    # ============================================================
    # DDD Structure Generation (from ExecutorAgent)
    # ============================================================
    
    def _generate_ddd_structure(
        self,
        service_name: str,
        domain: str,
        microservice: dict,
        config: Any
    ) -> dict[str, str]:
        """Generate DDD structure for a microservice."""
        normalized_service = service_name.replace('-', '_')
        normalized_domain = domain.replace('-', '_').lower()
        
        files = {}
        base_path = f"services/{normalized_service}"
        entities = microservice.get("entities", [])
        
        # Domain Layer
        entities_import = ", ".join(entities) if entities else "Entity"
        files[f"{base_path}/domain/__init__.py"] = f"""# Domain Layer
from .{normalized_domain}_entities import {entities_import}
from .{normalized_domain}_value_objects import Address, Email, Money
from .{normalized_domain}_aggregates import {normalized_domain.capitalize()}Aggregate
"""
        
        # Entities
        entities_content = "\n\n".join([
            self._generate_entity(e, normalized_domain) for e in entities
        ])
        files[f"{base_path}/domain/{normalized_domain}_entities.py"] = entities_content
        
        # Value Objects
        files[f"{base_path}/domain/{normalized_domain}_value_objects.py"] = self._generate_value_objects(normalized_domain)
        
        # Aggregates
        files[f"{base_path}/domain/{normalized_domain}_aggregates.py"] = self._generate_aggregates(normalized_domain, entities)
        
        # Application Layer
        files[f"{base_path}/application/__init__.py"] = f"Application Layer - {service_name}\n"
        files[f"{base_path}/application/use_cases.py"] = self._generate_use_cases(normalized_domain, entities)
        files[f"{base_path}/application/dtos.py"] = self._generate_dtos(entities)
        files[f"{base_path}/application/mappers.py"] = self._generate_mappers(normalized_domain, entities)
        
        # Infrastructure Layer
        files[f"{base_path}/infrastructure/__init__.py"] = "Infrastructure Layer\n"
        files[f"{base_path}/infrastructure/repositories.py"] = self._generate_repositories(normalized_domain, entities)
        files[f"{base_path}/infrastructure/database.py"] = self._generate_database(config.database, entities[0] if entities else "Entity")
        
        # API Layer
        files[f"{base_path}/api/__init__.py"] = "API Layer\n"
        files[f"{base_path}/api/routes.py"] = self._generate_routes(normalized_service, normalized_domain, entities)
        files[f"{base_path}/api/schemas.py"] = self._generate_schemas(entities)
        
        # Main
        files[f"{base_path}/main.py"] = self._generate_main(normalized_service)
        files[f"{base_path}/requirements.txt"] = self._generate_requirements(entities)
        
        # Dockerfile
        if config.include_docker:
            files[f"{base_path}/Dockerfile"] = self._generate_dockerfile(normalized_service)
        
        return files
    
    def _generate_entity(self, entity_name: str, domain: str) -> str:
        """Generate entity code."""
        return f'''"""Entity: {entity_name}"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class {entity_name}:
    """Domain entity for {domain}."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "{entity_name}":
        now = datetime.now()
        return {entity_name}(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {{
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }}

class {entity_name}Repository:
    """Repository interface for {entity_name}."""
    async def get_by_id(self, id: UUID) -> "{entity_name} | None":
        raise NotImplementedError
    async def get_all(self) -> list["{entity_name}"]:
        raise NotImplementedError
    async def save(self, entity: "{entity_name}") -> "{entity_name}":
        raise NotImplementedError
'''
    
    def _generate_value_objects(self, domain: str) -> str:
        """Generate value objects."""
        return f'''"""Value Objects for {domain}."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Address:
    """Value object for address."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "Brasil"

@dataclass(frozen=True)
class Email:
    """Value object for email."""
    value: str
    
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email")

@dataclass(frozen=True)
class Money:
    """Value object for money."""
    amount: float
    currency: str = "BRL"
'''
    
    def _generate_aggregates(self, domain: str, entities: list) -> str:
        """Generate aggregates."""
        entity = entities[0] if entities else "Entity"
        return f'''"""Aggregates for {domain}."""
from .{domain}_entities import {entity}

class {domain.capitalize()}Aggregate:
    """Aggregate root for {domain}."""
    def __init__(self, root: {entity}):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> {entity}:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
'''
    
    def _generate_use_cases(self, domain: str, entities: list) -> str:
        """Generate use cases."""
        entity = entities[0] if entities else "Entity"
        return f'''"""Use cases for {domain}."""
from uuid import UUID
from domain.{domain}_entities import {entity}

class Create{entity}UseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> {entity}:
        entity = {entity}.create(**data)
        return await self.repository.save(entity)

class Get{entity}ByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> {entity} | None:
        return await self.repository.get_by_id(id)
'''
    
    def _generate_dtos(self, entities: list) -> str:
        """Generate DTOs."""
        entity = entities[0] if entities else "Entity"
        return f'''"""DTOs for {entity}."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class {entity}DTO:
    id: UUID | None = None

@dataclass
class Create{entity}DTO:
    pass
'''
    
    def _generate_mappers(self, domain: str, entities: list) -> str:
        """Generate mappers."""
        entity = entities[0] if entities else "Entity"
        return f'''"""Mappers for {domain}."""
from application.dtos import {entity}DTO
from domain.{domain}_entities import {entity}

class {entity}Mapper:
    @staticmethod
    def to_dto(entity: {entity}) -> {entity}DTO:
        return {entity}DTO(id=entity.id)
'''
    
    def _generate_repositories(self, domain: str, entities: list) -> str:
        """Generate repositories."""
        entity = entities[0] if entities else "Entity"
        entity_lower = entity.lower()
        return f'''"""Repositories for {domain}."""
from uuid import UUID
from typing import Optional
from domain.{domain}_entities import {entity}, {entity}Repository

class {entity}RepositoryImpl({entity}Repository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[{entity}]:
        pass
    
    async def get_all(self) -> list[{entity}]:
        pass
    
    async def save(self, entity: {entity}) -> {entity}:
        return entity

_repository_instance = None

def get_{entity_lower}_repository() -> {entity}RepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = {entity}RepositoryImpl()
    return _repository_instance
'''
    
    def _generate_database(self, db_type: str, entity_name: str = "Entity") -> str:
        """Generate database configuration."""
        return f'''"""Database configuration."""
import asyncpg
import os

_pool = None

async def get_db_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dbname")
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool

async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
'''
    
    def _generate_routes(self, service_name: str, domain: str, entities: list) -> str:
        """Generate routes."""
        entity = entities[0] if entities else "Entity"
        entity_lower = entity.lower()
        return f'''"""Routes for {service_name}."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import {entity}DTO, Create{entity}DTO
from infrastructure.repositories import {entity}RepositoryImpl

router = APIRouter(prefix="/api/{service_name}", tags=["{service_name}"])

@router.post("/{entity_lower}s", status_code=201)
async def create_{entity_lower}(
    data: Create{entity}DTO,
    repository: {entity}RepositoryImpl = Depends(get_{entity_lower}_repository)
):
    return {{"id": "123"}}

@router.get("/{entity_lower}s")
async def list_{entity_lower}s():
    return []
'''
    
    def _generate_schemas(self, entities: list) -> str:
        """Generate schemas."""
        entity = entities[0] if entities else "Entity"
        return f'''"""Schemas for {entity}."""
from pydantic import BaseModel

class {entity}Schema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
'''
    
    def _generate_main(self, service_name: str) -> str:
        """Generate main.py."""
        return f'''"""Main application for {service_name}."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="{service_name}", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_requirements(self, entities: list = None) -> str:
        """Generate requirements.txt."""
        base = [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.5.0",
            "sqlalchemy>=2.0.0",
            "asyncpg>=0.29.0",
            "python-dotenv>=1.0.0",
        ]
        
        if entities:
            entities_str = " ".join(entities).lower()
            if any(e in entities_str for e in ["user", "customer", "email"]):
                base.append("pydantic[email]>=2.5.0")
        
        return "# Requirements\n" + "\n".join(base) + "\n"
    
    def _generate_dockerfile(self, service_name: str) -> str:
        """Generate Dockerfile."""
        return f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
'''
    
    def _generate_root_files(self, config: Any, microservices: list) -> dict:
        """Generate root files."""
        files = {}
        
        service_names = [s.get("name", "service") for s in microservices]
        files["README.md"] = f'''# Generated Project

Services: {", ".join(service_names)}

Run: cd services/<service> && python main.py
'''
        
        return files
    
    def _apply_generation_guards(self, file_path: str, content: str) -> str:
        """Apply generation guards."""
        if not content:
            return content
        
        # Fix common issues
        if file_path.endswith("requirements.txt"):
            if "fastapi" not in content.lower():
                content += "\nfastapi>=0.104.0"
        
        return content

