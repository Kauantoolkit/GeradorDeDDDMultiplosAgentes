"""
Executor Agent - Agente Executor
================================

Este agente é responsável por:
- Analisar os requisitos recebidos
- Identificar os microserviços necessários
- Gerar a estrutura DDD completa
- Criar os arquivos de código fonte

Trabalha em conjunto com o Validator Agent para garantir
que o código gerado atende aos requisitos.

MUDANÇAS IMPLEMENTADAS:
- Sistema de substituição de placeholders (PlaceholderReplacer)
- Validação de integridade após geração
- Geração na ordem correta DDD
- Correção de templates com placeholders não substituídos
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
    MicroserviceSpec
)
from infrastructure.llm_provider import OllamaProvider, PromptBuilder
from infrastructure.file_manager import FileManager


class PlaceholderReplacer:
    """
    Substituidor de placeholders para templates.
    
    Garante que TODOS os placeholders sejam substituídos
    antes de salvar o arquivo.
    """
    
    @staticmethod
    def replace(content: str, entity_name: str = None, domain: str = None, service_name: str = None) -> str:
        """
        Substitui todos os placeholders no conteúdo.
        
        Args:
            content: Conteúdo do template
            entity_name: Nome da entidade (ex: Order, User)
            domain: Nome do domínio (ex: orders, users)
            service_name: Nome do serviço (ex: orders)
            
        Returns:
            Conteúdo com placeholders substituídos
        """
        result = content
        
        # Substituições para entity_name
        if entity_name:
            result = result.replace('{entity_name}', entity_name)
            result = result.replace('{{entity_name}}', entity_name)
            result = result.replace('{entity_name.lower()}', entity_name.lower())
            result = result.replace('{{entity_name.lower()}}', entity_name.lower())
            # Corrige placeholders em f-strings quebradas
            result = result.replace("'{entity_name.lower()}'s", f"'{entity_name.lower()}'s")
            result = result.replace("{entity_name.lower()}s", f"{entity_name.lower()}s")
        
        # Substituições para domain
        if domain:
            result = result.replace('{domain}', domain)
            result = result.replace('{{domain}}', domain)
            result = result.replace('{domain.lower()}', domain.lower())
            result = result.replace('{{domain.lower()}}', domain.lower())
        
        # Substituições para service_name
        if service_name:
            result = result.replace('{service_name}', service_name)
            result = result.replace('{{service_name}}', service_name)
        
        # Verificar se ainda há placeholders perigosos
        remaining = re.findall(r'\{[a-z_]+\}', result)
        if remaining:
            logger.warning(f"Placeholders restantes após substituição: {set(remaining)}")
        
        return result
    
    @staticmethod
    def has_placeholders(content: str) -> bool:
        """Verifica se o conteúdo ainda tem placeholders não substituídos."""
        patterns = [
            r'\{entity_name\}',
            r'\{domain\}',
            r'\{service_name\}',
            r'\{entity_name\.lower\(\)\}',
            r'\{domain\.lower\(\)\}',
            r'\{\{entity_name\}\}',
            r'\{\{domain\}\}',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False


class ExecutorAgent:
    """
    Agente Executor - Gera código baseado em requisitos.
    
    Este agente recebe um Requirement e gera:
    - Estrutura de microserviços
    - Arquivos de código DDD
    - Configurações (Docker, etc.)
    """
    
    def __init__(self, llm_provider: OllamaProvider):
        """
        Inicializa o Executor Agent.
        
        Args:
            llm_provider: Provedor de LLM para geração de código
        """
        self.llm_provider = llm_provider
        self.name = "Executor Agent"
        logger.info(f"{self.name} inicializado")
    
    async def execute(self, requirement: Requirement) -> ExecutionResult:
        """
        Executa a geração de código.
        
        Args:
            requirement: Requisito do projeto
            
        Returns:
            ExecutionResult com os arquivos gerados
        """
        start_time = datetime.now()
        result = ExecutionResult(
            agent_type=AgentType.EXECUTOR,
            status=ExecutionStatus.IN_PROGRESS,
            started_at=start_time
        )
        
        try:
            logger.info("="*60)
            logger.info("EXECUTOR AGENT - Iniciando geração de código")
            logger.info("="*60)
            
            # Constrói o prompt
            prompt = PromptBuilder.build_executor_prompt(requirement)
            logger.debug(f"Prompt construído ({len(prompt)} chars)")
            
            # Chama o LLM para gerar o código
            logger.info("Chamando LLM para geração de código...")
            llm_output = await self.llm_provider.generate(
                prompt=prompt,
                temperature=0.3,  # Menos criativo, mais preciso
                max_tokens=8000
            )
            
            result.output = llm_output
            logger.info(f"Resposta do LLM recebida ({len(llm_output)} chars)")
            
            # Log the first part of the LLM output for debugging
            logger.info(f"LLM Output preview (first 500 chars): {llm_output[:500]}")
            
            # Parseia o JSON retornado
            parsed_data = self._parse_llm_output(llm_output)
            generated_data = self._normalize_llm_data(parsed_data)
            
            if not generated_data:
                raise ValueError("Não foi possível parsear a resposta do LLM")
            
            # Cria os arquivos
            file_manager = FileManager(requirement.project_config.output_directory)
            created_files = self._create_project_files(
                file_manager, 
                generated_data,
                requirement.project_config
            )
            
            result.files_created = created_files
            result.status = ExecutionStatus.SUCCESS
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            logger.info(f"{self.name} - Concluído em {result.execution_time:.2f}s")
            logger.info(f"Arquivos criados: {len(created_files)}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Erro no {self.name}: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.finished_at = datetime.now()
            result.execution_time = (result.finished_at - start_time).total_seconds()
            
            return result
    
    def _normalize_llm_data(self, data: Any) -> dict[str, Any]:
        """
        Normaliza a estrutura retornada pelo LLM para o formato esperado.

        Regras:
        - list -> {"microservices": list}
        - dict -> garante chaves obrigatórias
        - outros tipos -> erro explícito
        """
        logger.info(f"Tipo de estrutura retornada pelo LLM: {type(data).__name__}")

        if isinstance(data, list):
            logger.warning(
                "Formato de resposta inesperado (list). Aplicando normalização automática para {'microservices': [...]}"
            )
            data = {"microservices": data}

        if not isinstance(data, dict):
            logger.error(
                f"Formato inválido retornado pelo LLM: {type(data).__name__}. Esperado: dict ou list"
            )
            raise ValueError(
                f"Formato inválido retornado pelo LLM: {type(data).__name__}. Esperado JSON object ou array"
            )

        normalized = dict(data)
        for required_key in ("microservices", "files", "bounded_contexts"):
            normalized.setdefault(required_key, [])

        return normalized

    def _parse_llm_output(self, llm_output: str) -> Any | None:
        """
        Parseia a saída do LLM em JSON.

        Args:
            llm_output: Texto retornado pelo LLM

        Returns:
            Dicionário com os dados parseados ou None
        """
        
        # PRIMEIRO: Salvar o output original para debugging
        self._save_llm_output_for_debug(llm_output)
        
        # Tentativa 1: Limpar e parsear diretamente
        try:
            cleaned_output = self._clean_llm_output(llm_output)
            logger.debug(f"Tentativa 1 - Output limpo: {cleaned_output[:500]}...")
            return json.loads(cleaned_output)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Tentativa 1 falhou: {e}")

        # Tentativa 2: Tentar corrigir problemas comuns de JSON
        try:
            cleaned_output = self._clean_llm_output(llm_output)
            fixed_output = self._fix_common_json_issues(cleaned_output)
            logger.debug(f"Tentativa 2 - Output corrigido: {fixed_output[:500]}...")
            return json.loads(fixed_output)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Tentativa 2 falhou: {e}")

        # Tentativa 3: Usar método de extração com balanceamento de chaves
        try:
            extracted = self._extract_json_with_braces(llm_output)
            if extracted:
                logger.debug(f"Tentativa 3 - Extraído: {extracted[:500]}...")
                fixed = self._fix_common_json_issues(extracted)
                return json.loads(fixed)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Tentativa 3 falhou: {e}")

        # Tentativa 4: Balancear chaves e tentar novamente
        try:
            cleaned_output = self._clean_llm_output(llm_output)
            balanced = self._balance_braces(cleaned_output)
            logger.debug(f"Tentativa 4 - Balanceado: {balanced[:500]}...")
            fixed = self._fix_common_json_issues(balanced)
            return json.loads(fixed)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Tentativa 4 falhou: {e}")

        # Tentativa 5: Último recurso - extrair do texto completo
        try:
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}')
            if json_start >= 0 and json_end >= json_start:
                json_str = llm_output[json_start:json_end+1]
                logger.debug(f"Tentativa 5 - Extraído direto: {json_str[:500]}...")
                fixed = self._fix_common_json_issues(json_str)
                return json.loads(fixed)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Tentativa 5 falhou: {e}")

        # Tentativa 6: Tentar extrair array JSON
        try:
            json_start = llm_output.find('[')
            json_end = llm_output.rfind(']')
            if json_start >= 0 and json_end >= json_start:
                json_str = llm_output[json_start:json_end+1]
                logger.debug(f"Tentativa 6 - Array: {json_str[:500]}...")
                fixed = self._fix_common_json_issues(json_str)
                return json.loads(fixed)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Tentativa 6 falhou: {e}")

        # Tentativa 7: Usar regex para encontrar JSON mais aggressivamente
        try:
            json_str = self._extract_json_aggressive(llm_output)
            if json_str:
                logger.debug(f"Tentativa 7 - Regex: {json_str[:500]}...")
                fixed = self._fix_common_json_issues(json_str)
                return json.loads(fixed)
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Tentativa 7 falhou: {e}")

        # Todas as tentativas falharam
        logger.error(f"Erro ao parsear JSON após múltiplas tentativas")
        logger.error(f"Output original (primeiros 1000 chars): {llm_output[:1000]}")
        return None

    def _save_llm_output_for_debug(self, llm_output: str) -> None:
        """
        Salva o output do LLM em um arquivo para debugging.
        
        Args:
            llm_output: Output original do LLM
        """
        try:
            import os
            from datetime import datetime
            
            debug_dir = "logs/debug"
            os.makedirs(debug_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = os.path.join(debug_dir, f"llm_output_{timestamp}.txt")
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write(f"LLM Output - {timestamp}\n")
                f.write("="*60 + "\n\n")
                f.write(llm_output)
                f.write("\n\n" + "="*60 + "\n")
                f.write(f"Total chars: {len(llm_output)}\n")
                f.write(f"Primeiro char: {repr(llm_output[0]) if llm_output else 'N/A'}\n")
                f.write(f"Último char: {repr(llm_output[-1]) if llm_output else 'N/A'}\n")
            
            logger.info(f"LLM output salvo para debug: {debug_file}")
        except Exception as e:
            logger.warning(f"Não foi possível salvar output para debug: {e}")

    def _extract_json_aggressive(self, text: str) -> str | None:
        """
        Extrai JSON usando múltiplas estratégias agressivas.
        
        Args:
            text: Texto contendo JSON
            
        Returns:
            String JSON extraída ou None
        """
        import re
        
        # Estratégia 1: Encontrar qualquer objeto ou array JSON
        # Procura por { ... } ou [ ... ]
        patterns = [
            # Objeto JSON completo
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            # Array JSON completo
            r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                if len(match) > 50:  # Ignora matches muito pequenos
                    try:
                        # Tenta verificar se é JSON válido
                        json.loads(match)
                        return match
                    except:
                        continue
        
        # Estratégia 2: Remover markdown e tentar extrair
        # Remove ```json e ```wrapper
        cleaned = re.sub(r'^```json\s*', '', text)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'```$', '', cleaned)
        
        # Procura por { ou [ 
        json_match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        return None

    def _fix_common_json_issues(self, json_str: str) -> str:
        """
        Corrige problemas comuns em JSON gerado por LLM.
        
        Args:
            json_str: String JSON potencialmente com problemas
            
        Returns:
            String JSON corrigida
        """
        result = json_str
        
        # Remove comentários (LLMs às vezes adicionam comentários)
        result = re.sub(r'//.*?(\n|$)', '\n', result)
        result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
        
        # Remove trailing commas (vírgulas antes de })
        result = re.sub(r',(\s*[}\]])', r'\1', result)
        
        # Corrige aspas simples para aspas duplas em valores de string
        result = re.sub(r"'([^'\\]*(\\.[^'\\]*)*)'", r'"\1"', result)
        
        # Remove vírgulas extras entre elementos
        result = re.sub(r',,\s*', ',', result)
        
        # Corrige缺少 aspas em nomes de chaves
        result = re.sub(r'(\s|^)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', result)
        
        # Remove quebras de linha dentro de strings
        result = re.sub(r'"\s*\n\s*"', ' ', result)
        
        return result

    def _extract_json_with_braces(self, text: str) -> str | None:
        """
        Extrai JSON contando chaves e colchetes.
        
        Args:
            text: Texto contendo JSON
            
        Returns:
            String JSON extraída ou None
        """
        # Encontra o primeiro {
        start = text.find('{')
        if start == -1:
            return None
            
        # Conta chaves para encontrar o JSON completo
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start, len(text)):
            char = text[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"':
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    
                if brace_count == 0 and bracket_count == 0 and i > start:
                    return text[start:i+1]
        
        return None

    def _clean_llm_output(self, llm_output: str) -> str:
        """
        Limpa a saída do LLM para extrair apenas o JSON válido.

        Args:
            llm_output: Texto retornado pelo LLM

        Returns:
            String JSON limpa
        """
        # Define markers usando chr para evitar problemas com backticks
        # 96 = backtick
        backtick = chr(96)
        triple_backtick = backtick * 3  

        # Procura por code block with json marker
        marker_json = triple_backtick + "json"
        if marker_json in llm_output:
            start = llm_output.find(marker_json) + len(marker_json)
            end = llm_output.find(triple_backtick, start)
            if end > start:
                return llm_output[start:end].strip()

        # Procura por generic code block
        if triple_backtick in llm_output:
            start = llm_output.find(triple_backtick) + len(triple_backtick)
            end = llm_output.find(triple_backtick, start)
            if end > start:
                return llm_output[start:end].strip()

        # Remove texto antes da primeira { e depois da última }
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}')

        if json_start >= 0 and json_end >= json_start:
            json_str = llm_output[json_start:json_end+1]
            # Tenta balancear chaves para garantir JSON válido
            return self._balance_braces(json_str)

        return llm_output.strip()

    def _balance_braces(self, json_str: str) -> str:
        """
        Balanceia chaves e colchetes para garantir JSON válido.

        Args:
            json_str: String JSON potencialmente incompleta

        Returns:
            String JSON balanceada
        """
        brace_count = 0
        bracket_count = 0
        result = ""

        for char in json_str:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1

            result += char

            # Para se as contagens voltarem a zero (JSON completo)
            if brace_count == 0 and bracket_count == 0 and result.strip().endswith('}'):
                break

        return result
    
    def _create_project_files(
        self, 
        file_manager: FileManager, 
        data: dict,
        config: Any
    ) -> list[str]:
        """
        Cria os arquivos do projeto baseados nos dados gerados.
        
        Args:
            file_manager: Gerenciador de arquivos
            data: Dados retornados pelo LLM
            config: Configurações do projeto
            
        Returns:
            Lista de arquivos criados
        """
        if not isinstance(data, dict):
            logger.error(
                f"Dados inválidos em _create_project_files: esperado dict, recebido {type(data).__name__}"
            )
            raise ValueError(
                f"Dados inválidos para criação de arquivos: {type(data).__name__}"
            )

        created_files = []
        seen_paths: set[str] = set()

        def register_created(path: str) -> None:
            normalized = path.replace('\\', '/').strip()
            if normalized in seen_paths:
                logger.warning(f"Arquivo duplicado detectado na geração: {normalized} (mantendo última versão gravada)")
                return
            seen_paths.add(normalized)
            created_files.append(normalized)
        
        # Extrai os microserviços (modo legado)
        microservices = data.get("microservices", [])
        
        # Gera arquivos da estrutura DDD para cada microserviço
        for microservice in microservices:
            service_name = microservice.get("name", "service")
            domain = microservice.get("domain", service_name)
            
            # Cria estrutura DDD
            ddd_structure = self._generate_ddd_structure(
                service_name,
                domain,
                microservice,
                config
            )
            
            for file_path, content in ddd_structure.items():
                guarded_content = self._apply_generation_guards(file_path, content)
                if file_manager.create_file(file_path, guarded_content):
                    register_created(file_path)
        
        # Modo DDD estratégico: bounded_contexts já trazem arquivos prontos
        bounded_contexts = data.get("bounded_contexts", [])
        for context in bounded_contexts:
            context_name = context.get("name", "unknown")
            for file_data in context.get("files", []):
                path = file_data.get("path")
                content = self._apply_generation_guards(path, file_data.get("content", ""))
                if path and file_manager.create_file(path, content):
                    register_created(path)
            logger.info(f"Bounded context processado: {context_name}")
        
        # Cria arquivos adicionais definidos pelo LLM
        extra_files = data.get("files", [])
        for file_data in extra_files:
            path = file_data.get("path")
            if not self._is_allowed_extra_file_path(path):
                logger.warning(f"Ignorando arquivo extra fora do escopo permitido: {path}")
                continue

            content = self._apply_generation_guards(path, file_data.get("content", ""))

            if path and file_manager.create_file(path, content):
                register_created(path)
        
        # Cria arquivos raiz do projeto
        root_files = self._generate_root_files(config, microservices)
        for file_path, content in root_files.items():
            guarded_content = self._apply_generation_guards(file_path, content)
            if file_manager.create_file(file_path, guarded_content):
                register_created(file_path)
        
        # VALIDAÇÃO: Verificar arquivos gerados para detectar problemas
        validation_summary = self._validate_generated_files(created_files, file_manager)
        if validation_summary["critical_issues"]:
            raise ValueError(
                "Falha nos guardrails de geração: "
                + "; ".join(validation_summary["critical_issues"])
            )
        
        logger.info(f"Criados {len(created_files)} arquivos")
        return created_files
    
    def _is_allowed_extra_file_path(self, file_path: str | None) -> bool:
        """Restringe arquivos extras do LLM para evitar lixo fora da estrutura esperada."""
        if not file_path or not isinstance(file_path, str):
            return False

        normalized = file_path.replace('\\', '/').strip().lstrip('./').lstrip('/')
        if not normalized:
            return False

        allowed_prefixes = (
            'services/',
            'frontend/',
        )
        allowed_root_files = {
            'README.md',
            'docker-compose.yml',
            '.env',
            '.env.example',
            '.gitignore',
        }

        if normalized in allowed_root_files:
            return True

        return normalized.startswith(allowed_prefixes)

    def _sanitize_generated_content(self, file_path: str, content: str) -> str:
        """Corrige padrões críticos conhecidos em código gerado pelo LLM."""
        if not file_path.endswith('.py') or not content:
            return content

        fixed = content

        if file_path.endswith('domain/__init__.py'):
            fixed = re.sub(r'^from\s+domain\s+import\s+.+$', '# Corrigido: evitar import circular em domain/__init__.py', fixed, flags=re.MULTILINE)

        fixed = fixed.replace('from . import User', 'from .users_entities import User')
        fixed = fixed.replace('from . import Product', 'from .products_entities import Product')
        fixed = fixed.replace('from . import Order', 'from .orders_entities import Order')

        fixed = re.sub(r'from\s+\.\s+import\s+([A-Z][A-Za-z0-9_]*)', r'from .\1_entities import \1', fixed)

        return fixed

    def _apply_generation_guards(self, file_path: str, content: str) -> str:
        """Aplica correções preventivas em arquivos críticos gerados por LLM."""
        if not file_path or not content:
            return content

        fixed = self._sanitize_generated_content(file_path, content)

        if file_path.endswith("requirements.txt"):
            fixed = self._ensure_runtime_dependencies(fixed)

        if file_path.endswith("Dockerfile"):
            fixed = self._normalize_docker_cmd_syntax(fixed)

        return fixed

    def _ensure_runtime_dependencies(self, content: str) -> str:
        """Garante dependências mínimas para subir APIs FastAPI em Docker."""
        required = [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.5.0",
            "sqlalchemy>=2.0.0",
            "asyncpg>=0.29.0",
            "python-dotenv>=1.0.0",
        ]

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        existing_pkgs = {
            re.split(r"[<>=~!]", line, maxsplit=1)[0].strip().lower()
            for line in lines
            if not line.startswith("#")
        }

        merged = list(content.rstrip("\n").splitlines())
        if merged and merged[-1].strip():
            merged.append("")

        for dep in required:
            dep_name = re.split(r"[<>=~!]", dep, maxsplit=1)[0].lower()
            if dep_name not in existing_pkgs:
                merged.append(dep)

        return "\n".join(merged).rstrip() + "\n"

    def _normalize_docker_cmd_syntax(self, content: str) -> str:
        """Corrige CMD inválido em Dockerfile quando gerado com aspas simples."""
        fixed = content

        invalid_cmd_pattern = r"CMD\s*\['uvicorn',\s*'main:app',\s*'--host',\s*'0\.0\.0\.0',\s*'--port',\s*'8000'\]"
        fixed = re.sub(
            invalid_cmd_pattern,
            'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]',
            fixed,
        )

        return fixed

    def _validate_generated_files(self, created_files: list, file_manager: FileManager) -> dict[str, list[str]]:
        """
        Valida os arquivos gerados para detectar problemas comuns.
        
        Args:
            created_files: Lista de arquivos criados
            file_manager: Gerenciador de arquivos para ler conteúdo
        """
        logger.info("="*60)
        logger.info("VALIDAÇÃO - Verificando arquivos gerados...")
        
        issues_found = False
        critical_issues: list[str] = []
        warnings: list[str] = []
        route_registry: dict[tuple[str, str, str], str] = {}
        
        for file_path in created_files:
            try:
                content = file_manager.read_file(file_path)
                if not content:
                    logger.warning(f"Arquivo vazio: {file_path}")
                    warnings.append(f"Arquivo vazio: {file_path}")
                    continue
                
                # Verifica placeholders não substituídos
                if PlaceholderReplacer.has_placeholders(content):
                    logger.error(f"PLACEHOLDER encontrado em: {file_path}")
                    issues_found = True
                    critical_issues.append(f"Placeholder não substituído em {file_path}")
                
                # Verifica padrões comuns de código vazio/incompleto
                if 'pass\n' in content and content.count('pass\n') > 3:
                    # Mais de 3 'pass' pode indicar código incompleto
                    logger.warning(f"Muitos 'pass' em: {file_path} - possível código incompleto")
                    warnings.append(f"Possível código incompleto em {file_path}")
                
                # Verifica se há imports faltando para arquivos Python
                if file_path.endswith('.py'):
                    # Verifica se o arquivo tem pelo menos uma função ou classe definida
                    if file_path.endswith('__init__.py'):
                        pass
                    elif 'def ' not in content and 'class ' not in content:
                        logger.warning(f"Arquivo Python sem definições: {file_path}")
                        warnings.append(f"Arquivo Python sem definições: {file_path}")

                    # Verifica sintaxe Python
                    try:
                        ast.parse(content)
                    except SyntaxError as syntax_error:
                        issues_found = True
                        issue = f"Erro de sintaxe em {file_path}: {syntax_error.msg}"
                        critical_issues.append(issue)
                        logger.error(issue)

                    if '/main.py' in file_path.replace('\\', '/'):
                        undefined_issue = self._check_undefined_handler_symbols(file_path, content)
                        if undefined_issue:
                            issues_found = True
                            critical_issues.append(undefined_issue)
                            logger.error(undefined_issue)

                    duplicate_route_issues = self._check_duplicate_routes(file_path, content, route_registry)
                    if duplicate_route_issues:
                        issues_found = True
                        critical_issues.extend(duplicate_route_issues)
                        for issue in duplicate_route_issues:
                            logger.error(issue)

                if file_path.endswith('requirements.txt'):
                    required_runtime = ['fastapi', 'uvicorn']
                    requirements_lower = content.lower()
                    for dependency in required_runtime:
                        if dependency not in requirements_lower:
                            logger.error(f"Dependência obrigatória ausente ({dependency}) em: {file_path}")
                            issues_found = True
                            critical_issues.append(f"Dependência obrigatória ausente ({dependency}) em {file_path}")

                if file_path.endswith('Dockerfile') and "CMD ['" in content:
                    logger.error(f"Sintaxe CMD inválida (aspas simples) em: {file_path}")
                    issues_found = True
                    critical_issues.append(f"Sintaxe CMD inválida em {file_path}")

                if '/infrastucture/' in file_path.replace('\\', '/'):
                    issues_found = True
                    issue = f"Diretório suspeito detectado (typo): {file_path}"
                    critical_issues.append(issue)
                    logger.error(issue)
                        
            except Exception as e:
                logger.warning(f"Erro ao validar {file_path}: {e}")
                warnings.append(f"Erro ao validar {file_path}: {e}")
        
        if issues_found:
            logger.error("VALIDAÇÃO - Problemas encontrados nos arquivos gerados!")
            logger.error("Recomendação: Revise os templates de geração")
        else:
            logger.info("VALIDAÇÃO - Todos os arquivos passaram na verificação!")
        
        logger.info("="*60)
        return {
            "critical_issues": list(dict.fromkeys(critical_issues)),
            "warnings": list(dict.fromkeys(warnings)),
        }

    def _check_undefined_handler_symbols(self, file_path: str, content: str) -> str | None:
        """Detecta símbolos frequentemente esquecidos em handlers FastAPI."""
        request_used = bool(re.search(r"\brequest\s*:\s*Request\b", content))
        request_imported = bool(re.search(r"from\s+fastapi\s+import[^\n]*\bRequest\b", content))

        if request_used and not request_imported:
            return f"Request usado sem import em {file_path}"

        imported_symbols = set(re.findall(r"from\s+[^\n]+\s+import\s+([^\n]+)", content))
        imported_names: set[str] = set()
        for symbols in imported_symbols:
            for token in symbols.split(','):
                imported_names.add(token.strip().split(' as ')[0])

        used_calls = set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(\)", content))
        allowed_builtins = {"FastAPI"}
        missing = sorted(name for name in used_calls if name not in imported_names and name not in allowed_builtins)
        if missing:
            return f"Possíveis símbolos não importados em {file_path}: {', '.join(missing)}"

        return None

    def _check_duplicate_routes(
        self,
        file_path: str,
        content: str,
        route_registry: dict[tuple[str, str, str], str],
    ) -> list[str]:
        """Detecta rotas duplicadas de FastAPI (mesmo método+path no mesmo serviço)."""
        normalized = file_path.replace('\\', '/')
        parts = normalized.split('/')
        service = "unknown"
        if len(parts) > 2 and parts[0] == 'services':
            service = parts[1]

        route_pattern = r"@app\.(get|post|put|patch|delete)\((['\"])([^'\"]+)\2"
        issues: list[str] = []
        for method, _, path in re.findall(route_pattern, content):
            key = (service, method.lower(), path)
            if key in route_registry:
                issues.append(
                    f"Rota duplicada detectada em serviço '{service}': {method.upper()} {path} ({file_path} e {route_registry[key]})"
                )
            else:
                route_registry[key] = file_path

        return issues
    
    def _generate_ddd_structure(
        self, 
        service_name: str, 
        domain: str,
        microservice: dict,
        config: Any
    ) -> dict[str, str]:
        """
        Gera a estrutura DDD para um microserviço.
        
        Args:
            service_name: Nome do serviço
            domain: Nome do domínio
            microservice: Dados do microserviço
            config: Configurações do projeto
            
        Returns:
            Dicionário {caminho: conteúdo}
        """
        # ============================================================
        # CORREÇÃO CRÍTICA: Normalizar nomes de serviços
        # Isso garante que auth-service -> auth_service
        # ============================================================
        normalized_service_name = service_name.replace('-', '_')
        
        files = {}
        base_path = f"services/{normalized_service_name}"
        
        entities = microservice.get("entities", [])
        
        # Normalizar domain também
        normalized_domain = domain.replace('-', '_').lower()
        
        # Domain Layer - CORRIGIDO: Usar normalized_domain
        files[f"{base_path}/domain/__init__.py"] = f"""# {normalized_service_name} - Domain Layer
from .{normalized_domain}_entities import {entities[0] if entities else "Entity"}, {entities[0] if entities else "Entity"}Repository
from .{normalized_domain}_value_objects import Address, Email, Money
from .{normalized_domain}_aggregates import {normalized_domain.capitalize()}Aggregate
"""
        
        # Entities
        for entity in entities:
            files[f"{base_path}/domain/{normalized_domain}_entities.py"] = self._generate_entity(entity, normalized_domain)
        
        # Value Objects - CORRIGIDO: Usar normalized_domain
        files[f"{base_path}/domain/{normalized_domain}_value_objects.py"] = self._generate_value_objects(normalized_domain)
        
        # Aggregates - CORRIGIDO: Usar normalized_domain
        files[f"{base_path}/domain/{normalized_domain}_aggregates.py"] = self._generate_aggregates(normalized_domain, entities)
        
        # Application Layer - CORRIGIDO: Usar normalized_service_name
        files[f"{base_path}/application/__init__.py"] = self._generate_application_init(normalized_service_name)
        files[f"{base_path}/application/use_cases.py"] = self._generate_use_cases(normalized_domain, entities)
        files[f"{base_path}/application/dtos.py"] = self._generate_dtos(entities)
        files[f"{base_path}/application/mappers.py"] = self._generate_mappers(normalized_domain, entities)
        
        # Infrastructure Layer
        files[f"{base_path}/infrastructure/__init__.py"] = self._generate_infrastructure_init()
        # Pass entity_name to database generation to avoid placeholders
        entity_name = entities[0] if entities else "Entity"
        files[f"{base_path}/infrastructure/repositories.py"] = self._generate_repositories(normalized_domain, entities)
        files[f"{base_path}/infrastructure/database.py"] = self._generate_database(config.database, entity_name)
        
        # API Layer - CORRIGIDO: Usar normalized_service_name
        files[f"{base_path}/api/__init__.py"] = self._generate_api_init()
        files[f"{base_path}/api/routes.py"] = self._generate_routes(normalized_service_name, normalized_domain, entities)
        files[f"{base_path}/api/controllers.py"] = self._generate_controllers(normalized_service_name, entities)
        files[f"{base_path}/api/schemas.py"] = self._generate_schemas(entities)
        
        # Main - CORRIGIDO: Usar normalized_service_name
        files[f"{base_path}/main.py"] = self._generate_main(normalized_service_name, config)
        files[f"{base_path}/requirements.txt"] = self._generate_requirements()
        
        # Docker
        if config.include_docker:
            files[f"{base_path}/Dockerfile"] = self._generate_dockerfile(normalized_service_name)
            files[f"{base_path}/docker-compose.yml"] = self._generate_docker_compose(normalized_service_name, config.database)
        
        # Tests
        if config.include_tests:
            files[f"{base_path}/tests/__init__.py"] = ""
            files[f"{base_path}/tests/test_{normalized_domain}_entities.py"] = self._generate_test_entities(normalized_domain, entities)
        
        return files
    
    def _generate_entity(self, entity_name: str, domain: str) -> str:
        """Gera código de Entity."""
        return f'''"""
{entity_name} Entity - Domain Layer
=================================
Entidade representando {entity_name} no domínio {domain}.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class {entity_name}:
    """
    Entidade {entity_name} - Agrega regras de negócio e identidade.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "{entity_name}":
        """Factory method para criar uma nova {entity_name}."""
        now = datetime.now()
        return {entity_name}(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}}
        )
    
    def update(self, **kwargs):
        """Atualiza os atributos da entidade."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte a entidade para dicionário."""
        return {{
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }}


# Repositório (interface)
class {entity_name}Repository:
    """Interface para repositório de {entity_name}."""
    
    async def get_by_id(self, id: UUID) -> {entity_name} | None:
        raise NotImplementedError
    
    async def get_all(self) -> list[{entity_name}]:
        raise NotImplementedError
    
    async def save(self, entity: {entity_name}) -> {entity_name}:
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        raise NotImplementedError
'''
    
    def _generate_value_objects(self, domain: str) -> str:
        """Gera código de Value Objects."""
        return f'''"""
Value Objects - Domain Layer
===========================
Objetos de valor para o domínio {domain}.
Objetos de valor são imutáveis e equality por valor.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Address:
    """Value Object para endereço."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "Brasil"
    
    def __str__(self) -> str:
        return f"{{self.street}}, {{self.city}} - {{self.state}}"


@dataclass(frozen=True)
class Email:
    """Value Object para email com validação."""
    value: str
    
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Email inválido")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Money:
    """Value Object para valores monetários."""
    amount: float
    currency: str = "BRL"
    
    def __str__(self) -> str:
        return f"R$ {{self.amount:.2f}}"
'''
    
    def _generate_aggregates(self, domain: str, entities: list) -> str:
        """Gera código de Aggregates."""
        entity_name = entities[0] if entities else "Entity"
        return f'''"""
Aggregates - Domain Layer
=========================
Agregados para o domínio {domain}.
Agregado é um cluster de entidades e value objects com raiz (root entity).
"""

from uuid import UUID
from .{domain}_entities import {entity_name}


class {domain.capitalize()}Aggregate:
    """
    Agregado raiz para o domínio {domain}.
    Controla invariantes de negócio e transações.
    """
    
    def __init__(self, root: {entity_name}):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> {entity_name}:
        return self._root
    
    def add_entity(self, entity):
        """Adiciona uma entidade ao agregado."""
        self._entities.append(entity)
    
    def remove_entity(self, entity_id: UUID) -> bool:
        """Remove uma entidade do agregado."""
        for i, e in enumerate(self._entities):
            if e.id == entity_id:
                self._entities.pop(i)
                return True
        return False
    
    def get_all_entities(self):
        """Retorna todas as entidades do agregado."""
        return self._entities.copy()
'''
    
    def _generate_application_init(self, service_name: str) -> str:
        return f'''"""
{service_name} - Application Layer
=================================
Camada de aplicação com Use Cases e DTOs.
"""
'''
    
    def _generate_use_cases(self, domain: str, entities: list) -> str:
        entity_name = entities[0] if entities else "Entity"
        return f'''"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio {domain}.
"""

from uuid import UUID
from domain.{domain}_entities import {entity_name}


class Create{entity_name}UseCase:
    """Use case para criar {entity_name}."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> {entity_name}:
        entity = {entity_name}.create(**data)
        return await self.repository.save(entity)


class Get{entity_name}ByIdUseCase:
    """Use case para buscar {entity_name} por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> {entity_name} | None:
        return await self.repository.get_by_id(id)


class Update{entity_name}UseCase:
    """Use case para atualizar {entity_name}."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> {entity_name} | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class Delete{entity_name}UseCase:
    """Use case para deletar {entity_name}."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
'''
    
    def _generate_dtos(self, entities: list) -> str:
        """
        Gera código de DTOs com campos properiados.
        
        Args:
            entities: Lista de nomes de entidades
            
        Returns:
            Conteúdo do arquivo dtos.py
        """
        entity_name = entities[0] if entities else "Entity"
        
        # Define campos padrão baseados no tipo de entidade
        # Esses campos serão usados se não forem especificados pelo LLM
        default_fields = self._get_default_dto_fields(entity_name)
        
        return f'''"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class {entity_name}DTO:
    """DTO para {entity_name}."""
    id: UUID | None = None
    {default_fields["dto_fields"]}
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Create{entity_name}DTO:
    """DTO para criação de {entity_name}."""
    {default_fields["create_fields"]}


@dataclass
class Update{entity_name}DTO:
    """DTO para atualização de {entity_name}."""
    {default_fields["update_fields"]}
'''
    
    def _get_default_dto_fields(self, entity_name: str) -> dict:
        """
        Retorna campos padrão para DTOs baseados no nome da entidade.
        
        Args:
            entity_name: Nome da entidade
            
        Returns:
            Dicionário com campos para cada tipo de DTO
        """
        entity_lower = entity_name.lower()
        
        # Campos específicos por tipo de entidade
        if 'user' in entity_lower or 'usuario' in entity_lower:
            return {
                "dto_fields": "nome: str | None = None\n    email: str | None = None",
                "create_fields": "nome: str\n    email: str\n    senha: str",
                "update_fields": "nome: str | None = None\n    email: str | None = None"
            }
        elif 'post' in entity_lower:
            return {
                "dto_fields": "usuario_id: UUID | None = None\n    conteudo: str | None = None",
                "create_fields": "usuario_id: UUID\n    conteudo: str",
                "update_fields": "conteudo: str | None = None"
            }
        elif 'comment' in entity_lower or 'comentario' in entity_lower:
            return {
                "dto_fields": "post_id: UUID | None = None\n    usuario_id: UUID | None = None\n    conteudo: str | None = None",
                "create_fields": "post_id: UUID\n    usuario_id: UUID\n    conteudo: str",
                "update_fields": "conteudo: str | None = None"
            }
        elif 'order' in entity_lower or 'pedido' in entity_lower:
            return {
                "dto_fields": "usuario_id: UUID | None = None\n    total: float | None = None\n    status: str | None = None",
                "create_fields": "usuario_id: UUID\n    itens: list",
                "update_fields": "status: str | None = None"
            }
        elif 'product' in entity_lower or 'produto' in entity_lower:
            return {
                "dto_fields": "nome: str | None = None\n    preco: float | None = None\n    descricao: str | None = None",
                "create_fields": "nome: str\n    preco: float\n    descricao: str | None = None",
                "update_fields": "nome: str | None = None\n    preco: float | None = None\n    descricao: str | None = None"
            }
        else:
            # Campos genéricos para outras entidades
            return {
                "dto_fields": "nome: str | None = None",
                "create_fields": "nome: str",
                "update_fields": "nome: str | None = None"
            }
    
    def _generate_mappers(self, domain: str, entities: list) -> str:
        entity_name = entities[0] if entities else "Entity"
        return f'''"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import {entity_name}DTO, Create{entity_name}DTO
from domain.{domain}_entities import {entity_name}


class {entity_name}Mapper:
    """Mapper para {entity_name}."""
    
    @staticmethod
    def to_dto(entity: {entity_name}) -> {entity_name}DTO:
        return {entity_name}DTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: {entity_name}DTO) -> {entity_name}:
        return {entity_name}(**{{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        }})
    
    @staticmethod
    def to_create_dict(dto: Create{entity_name}DTO) -> dict:
        return {{k: v for k, v in dto.__dict__.items() if v is not None}}
'''
    
    def _generate_infrastructure_init(self) -> str:
        return '''"""
Infrastructure Layer
====================
Camada de infraestrutura com repositórios e banco de dados.
"""
'''
    
    def _generate_repositories(self, domain: str, entities: list) -> str:
        entity_name = entities[0] if entities else "Entity"
        db_type = "sqlalchemy"  # Padrão
        # Apply placeholder replacements first
        content = f'''"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para {domain}.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.{domain}_entities import {entity_name}, {entity_name}Repository
from infrastructure.database import get_db


class {entity_name}RepositoryImpl({entity_name}Repository):
    """Implementação do repositório de {entity_name}."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[{entity_name}]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM {entity_name.lower()}s WHERE id = $1", str(id)
        )
        if row:
            return {entity_name}(**row)
        return None
    
    async def get_all(self) -> list[{entity_name}]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM {entity_name.lower()}s")
        return [{entity_name}(**row) for row in rows]
    
    async def save(self, entity: {entity_name}) -> {entity_name}:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${{i+1}} = ${{i+2}}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE {entity_name.lower()}s SET {{set_clause}} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${{i+1}}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO {entity_name.lower()}s ({{columns}}) VALUES ({{values}})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM {entity_name.lower()}s WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_{entity_name.lower()}_repository() -> {entity_name}RepositoryImpl:
    """Dependência para obter repositório de {entity_name}."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = {entity_name}RepositoryImpl()
    return _repository_instance
'''
        # Apply replacements to fix any remaining placeholders
        result = content.replace('{entity_name}', entity_name)
        result = result.replace('{entity_name.lower()}', entity_name.lower())
        result = result.replace('{domain}', domain)
        result = result.replace('{set_clause}', ', '.join([f'{{k}} = ${{i+2}}' for i, k in enumerate(['nome', 'email', 'created_at', 'updated_at'])]))
        result = result.replace('{{set_clause}}', ', '.join([f'{k} = ${i+2}' for i, k in enumerate(['nome', 'email', 'created_at', 'updated_at'])]))
        return result
    
    def _generate_database(self, db_type: str, entity_name: str = "Entity") -> str:
        """
        Gera código de Database Configuration usando asyncpg.
        
        Args:
            db_type: Tipo de banco (postgresql, mysql, etc)
            entity_name: Nome da entidade principal
            
        Returns:
            Conteúdo do arquivo database.py
        """
        # Gera template usando asyncpg (async)
        content = f'''"""
Database Configuration - Infrastructure Layer
=============================================
Configuração de banco de dados ({db_type}) - Async version.
"""

import asyncpg
import os
from typing import Optional


# Database connection pool
_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Obtém o pool de conexões do banco."""
    global _pool
    if _pool is None:
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:postgres@localhost:5432/dbname"
        )
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10
        )
    return _pool


async def close_db_pool():
    """Fecha o pool de conexões."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def init_db():
    """Inicializa o banco de dados criando as tabelas."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Create {entity_name.lower()}s table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS {entity_name.lower()}s (
                id UUID PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)


def get_db():
    """Dependência para obter conexão do banco (async)."""
    return get_db_pool()
'''
        # Usa o replacer para garantir que não há placeholders restantes
        return PlaceholderReplacer.replace(content, entity_name=entity_name)
    
    def _generate_api_init(self) -> str:
        return '''"""
API Layer
=========
Camada de API com controllers e rotas.
"""
'''
    
    def _generate_routes(self, service_name: str, domain: str, entities: list) -> str:
        """
        Gera código de Routes com APIRouter.
        
        Args:
            service_name: Nome do serviço (normalizado)
            domain: Nome do domínio (normalizado)
            entities: Lista de entidades
            
        Returns:
            Conteúdo do arquivo routes.py
        """
        entity_name = entities[0] if entities else "Entity"
        return f'''"""
Routes - API Layer
==================
Definição de rotas para {service_name}.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import {entity_name}DTO, Create{entity_name}DTO, Update{entity_name}DTO
from application.use_cases import (
    Create{entity_name}UseCase,
    Get{entity_name}ByIdUseCase,
    Update{entity_name}UseCase,
    Delete{entity_name}UseCase,
)
from infrastructure.repositories import {entity_name}RepositoryImpl
from api.schemas import {entity_name}Schema, Create{entity_name}Schema
from api.controllers import get_{entity_name.lower()}_repository


router = APIRouter(prefix="/api/{service_name}", tags=["{service_name}"])


@router.post("/{entity_name.lower()}s", response_model={entity_name}Schema, status_code=status.HTTP_201_CREATED)
async def create_{entity_name.lower()}(
    data: Create{entity_name}Schema,
    repository: {entity_name}RepositoryImpl = Depends(get_{entity_name.lower()}_repository)
):
    """Cria um novo {entity_name}."""
    use_case = Create{entity_name}UseCase(repository)
    entity = await use_case.execute(data.dict())
    return {entity_name}Schema.from_orm(entity)


@router.get("/{entity_name.lower()}s", response_model=List[{entity_name}Schema])
async def list_{entity_name.lower()}s(
    repository: {entity_name}RepositoryImpl = Depends(get_{entity_name.lower()}_repository)
):
    """Lista todos os {entity_name}s."""
    entities = await repository.get_all()
    return [{entity_name}Schema.from_orm(e) for e in entities]


@router.get("/{entity_name.lower()}s/{{id}}", response_model={entity_name}Schema)
async def get_{entity_name.lower()}(
    id: UUID,
    repository: {entity_name}RepositoryImpl = Depends(get_{entity_name.lower()}_repository)
):
    """Busca {entity_name} por ID."""
    use_case = Get{entity_name}ByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="{entity_name} não encontrado")
    return {entity_name}Schema.from_orm(entity)


@router.put("/{entity_name.lower()}s/{{id}}", response_model={entity_name}Schema)
async def update_{entity_name.lower()}(
    id: UUID,
    data: Update{entity_name}DTO,
    repository: {entity_name}RepositoryImpl = Depends(get_{entity_name.lower()}_repository)
):
    """Atualiza {entity_name}."""
    use_case = Update{entity_name}UseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="{entity_name} não encontrado")
    return {entity_name}Schema.from_orm(entity)


@router.delete("/{entity_name.lower()}s/{{id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{entity_name.lower()}(
    id: UUID,
    repository: {entity_name}RepositoryImpl = Depends(get_{entity_name.lower()}_repository)
):
    """Deleta {entity_name}."""
    use_case = Delete{entity_name}UseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="{entity_name} não encontrado")
'''
    
    def _generate_controllers(self, service_name: str, entities: list) -> str:
        entity_name = entities[0] if entities else "Entity"
        return f'''"""
Controllers - API Layer
=======================
Controladores para {service_name}.
"""

from fastapi import Depends
from infrastructure.repositories import {entity_name}RepositoryImpl


def get_{entity_name.lower()}_repository() -> {entity_name}RepositoryImpl:
    """Dependência para obter repositório de {entity_name}."""
    return {entity_name}RepositoryImpl()
'''
    
    def _generate_schemas(self, entities: list) -> str:
        """
        Gera código de Schemas com campos e validação.
        
        Args:
            entities: Lista de nomes de entidades
            
        Returns:
            Conteúdo do arquivo schemas.py
        """
        entity_name = entities[0] if entities else "Entity"
        
        # Get default fields based on entity type
        default_fields = self._get_default_schema_fields(entity_name)
        
        return f'''"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class {entity_name}Schema(BaseModel):
    """Schema para {entity_name}."""
    id: UUID
    {default_fields["schema_fields"]}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Create{entity_name}Schema(BaseModel):
    """Schema para criação de {entity_name}."""
    {default_fields["create_fields"]}


class Update{entity_name}Schema(BaseModel):
    """Schema para atualização de {entity_name}."""
    {default_fields["update_fields"]}
'''
    
    def _get_default_schema_fields(self, entity_name: str) -> dict:
        """
        Retorna campos padrão para Schemas Pydantic baseados no nome da entidade.
        
        Args:
            entity_name: Nome da entidade
            
        Returns:
            Dicionário com campos para cada tipo de Schema
        """
        entity_lower = entity_name.lower()
        
        # Campos específicos por tipo de entidade
        if 'user' in entity_lower or 'usuario' in entity_lower:
            return {
                "schema_fields": "nome: str\n    email: str",
                "create_fields": "nome: str = Field(..., min_length=2, max_length=100)\n    email: EmailStr\n    senha: str = Field(..., min_length=6)",
                "update_fields": "nome: str | None = Field(None, min_length=2, max_length=100)\n    email: EmailStr | None = None"
            }
        elif 'post' in entity_lower:
            return {
                "schema_fields": "usuario_id: UUID\n    conteudo: str",
                "create_fields": "usuario_id: UUID\n    conteudo: str = Field(..., min_length=1)",
                "update_fields": "conteudo: str | None = Field(None, min_length=1)"
            }
        elif 'comment' in entity_lower or 'comentario' in entity_lower:
            return {
                "schema_fields": "post_id: UUID\n    usuario_id: UUID\n    conteudo: str",
                "create_fields": "post_id: UUID\n    usuario_id: UUID\n    conteudo: str = Field(..., min_length=1)",
                "update_fields": "conteudo: str | None = Field(None, min_length=1)"
            }
        elif 'order' in entity_lower or 'pedido' in entity_lower:
            return {
                "schema_fields": "usuario_id: UUID\n    total: float\n    status: str",
                "create_fields": "usuario_id: UUID\n    itens: list",
                "update_fields": "status: str | None = None"
            }
        elif 'product' in entity_lower or 'produto' in entity_lower:
            return {
                "schema_fields": "nome: str\n    preco: float\n    descricao: str",
                "create_fields": "nome: str = Field(..., min_length=2, max_length=100)\n    preco: float = Field(..., gt=0)\n    descricao: str | None = None",
                "update_fields": "nome: str | None = Field(None, min_length=2, max_length=100)\n    preco: float | None = Field(None, gt=0)\n    descricao: str | None = None"
            }
        else:
            # Campos genéricos para outras entidades
            return {
                "schema_fields": "nome: str",
                "create_fields": "nome: str = Field(..., min_length=2, max_length=100)",
                "update_fields": "nome: str | None = Field(None, min_length=2, max_length=100)"
            }
    
    def _generate_main(self, service_name: str, config: Any) -> str:
        return f'''"""
{service_name} - Main Application
================================
Ponto de entrada do microserviço {service_name}.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router


app = FastAPI(
    title="{service_name}",
    description="Microserviço {service_name} - DDD Architecture",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{service_name}"}}


@app.get("/")
async def root():
    """Root endpoint."""
    return {{"message": "{service_name} API", "version": "1.0.0"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_requirements(self) -> str:
        return """# Requirements
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
python-dotenv>=1.0.0
"""
    
    def _generate_dockerfile(self, service_name: str) -> str:
        return f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
'''

    def _resolve_database_image(self, database: str) -> str:
        """Normaliza a imagem do banco para evitar tags incompatíveis."""
        db = (database or "").strip().lower()

        if db in {"postgres", "postgresql", "postgres:latest", "postgresql:latest", ""}:
            return "postgres:16"

        return database
    
    def _generate_docker_compose(self, service_name: str, database: str) -> str:
        # NOTA: Não usamos mais 'version' pois está obsoleto nas versões recentes do Docker Compose
        db_image = self._resolve_database_image(database)
        return f'''services:
  {service_name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/{service_name}
    depends_on:
      - db

  db:
    image: {db_image}
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={service_name}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
'''
    
    def _generate_test_entities(self, domain: str, entities: list) -> str:
        entity_name = entities[0] if entities else "Entity"
        return f'''"""
Tests - {domain} Domain
======================
Testes unitários para entidades de {domain}.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class Test{entity_name}:
    """Testes para {entity_name}."""
    
    def test_create_{entity_name.lower()}(self):
        """Testa criação de {entity_name}."""
        from ..services.service.domain import {entity_name}
        
        entity = {entity_name}.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_{entity_name.lower()}(self):
        """Testa atualização de {entity_name}."""
        from ..services.service.domain import {entity_name}
        
        entity = {entity_name}.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import {entity_name}
        
        entity = {entity_name}.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
'''
    
    def _generate_root_files(self, config: Any, microservices: list) -> dict:
        """Gera arquivos na raiz do projeto."""
        files = {}
        
        # README
        service_names = [s.get("name", "service") for s in microservices]
        files["README.md"] = f'''# Generated Project

Generated microservices using DDD architecture.

## Services
{chr(10).join(f"- {name}" for name in service_names)}

## Configuration
- Framework: {config.framework}
- Database: {config.database}

## Running
```
bash
cd services/<service-name>
pip install -r requirements.txt
python main.py
```
'''
        
        # Gera frontend para o primeiro serviço (se houver)
        # GENERIC: O nome do serviço e entidades devem vir do requirement
        if microservices:
            service_name = microservices[0].get("name", "service")
            entities = microservices[0].get("entities", ["Entity"])
            files[f"services/{service_name}/static/index.html"] = self._generate_frontend(service_name, entities)
        
        # docker-compose principal se houver múltiplos serviços
        if len(microservices) > 1:
            files["docker-compose.yml"] = '''services:
  # Add your microservices here
'''
        
        return files
    
    def _generate_frontend(self, service_name: str, entities: list) -> str:
        """Gera um frontend moderno com login e CRUD."""
        # GENERIC: entity name should come from the requirement, not hardcoded
        entity_name = entities[0] if entities else "Entity"
        
        return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{service_name.title()} - Sistema de Gestão</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
        
        :root {{
            --primary: #ff6b35;
            --secondary: #004e89;
            --dark: #1a1a2e;
            --light: #f7f7f7;
            --gray: #666;
        }}
        
        body {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; }}
        
        .login-container {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
        
        .login-box {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 25px 50px rgba(0,0,0,0.3); width: 100%; max-width: 400px; animation: slideUp 0.5s ease; }}
        
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        .logo {{ text-align: center; margin-bottom: 30px; }}
        .logo-icon {{ font-size: 60px; margin-bottom: 10px; }}
        .logo h1 {{ color: var(--primary); font-size: 28px; font-weight: 700; }}
        .logo p {{ color: var(--gray); font-size: 14px; }}
        
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; color: var(--dark); font-weight: 500; }}
        .form-group input {{ width: 100%; padding: 14px 16px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 15px; transition: all 0.3s; }}
        .form-group input:focus {{ outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1); }}
        
        .btn {{ width: 100%; padding: 14px; background: linear-gradient(135deg, var(--primary) 0%, #ff8f5a 100%); color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(255, 107, 53, 0.3); }}
        
        .app-container {{ display: none; min-height: 100vh; }}
        
        .sidebar {{ position: fixed; left: 0; top: 0; width: 260px; height: 100vh; background: white; padding: 20px; box-shadow: 4px 0 20px rgba(0,0,0,0.1); z-index: 100; }}
        .sidebar-logo {{ display: flex; align-items: center; gap: 12px; margin-bottom: 40px; padding: 10px; }}
        .sidebar-logo span {{ font-size: 28px; }}
        .sidebar-logo h2 {{ color: var(--primary); font-size: 22px; }}
        
        .nav-menu {{ list-style: none; }}
        .nav-item {{ margin-bottom: 8px; }}
        .nav-link {{ display: flex; align-items: center; gap: 12px; padding: 14px 16px; color: var(--gray); text-decoration: none; border-radius: 10px; transition: all 0.3s; font-weight: 500; }}
        .nav-link:hover, .nav-link.active {{ background: linear-gradient(135deg, var(--primary) 0%, #ff8f5a 100%); color: white; }}
        
        .main-content {{ margin-left: 260px; padding: 30px; background: var(--light); min-height: 100vh; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .header h1 {{ color: var(--dark); font-size: 28px; }}
        
        .user-info {{ display: flex; align-items: center; gap: 12px; }}
        .user-avatar {{ width: 45px; height: 45px; background: linear-gradient(135deg, var(--primary) 0%, #ff8f5a 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 18px; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 4px solid var(--primary); }}
        .stat-card h3 {{ color: var(--gray); font-size: 14px; font-weight: 500; margin-bottom: 10px; }}
        .stat-card .value {{ color: var(--dark); font-size: 32px; font-weight: 700; }}
        
        .card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        .card h2 {{ color: var(--dark); margin-bottom: 20px; font-size: 20px; }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 14px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ color: var(--gray); font-weight: 600; font-size: 13px; text-transform: uppercase; }}
        
        .btn-danger {{ background: #dc3545; padding: 8px 14px; font-size: 13px; }}
        
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center; }}
        .modal.active {{ display: flex; }}
        .modal-content {{ background: white; padding: 30px; border-radius: 15px; width: 100%; max-width: 500px; }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        
        .toast {{ position: fixed; top: 20px; right: 20px; padding: 15px 25px; border-radius: 10px; color: white; font-weight: 500; z-index: 2000; display: none; }}
        .toast.show {{ display: block; }}
        .toast.success {{ background: #28a745; }}
        .toast.error {{ background: #dc3545; }}
        
        .btn-logout {{ background: #dc3545; padding: 8px 20px; margin-left: 15px; }}
        .btn-secondary {{ background: #6c757d; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="login-container" id="loginScreen">
        <div class="login-box">
            <div class="logo">
                <div class="logo-icon">🏋️</div>
                <h1>{service_name.title()}</h1>
                <p>Sistema de Gestão</p>
            </div>
            <div id="loginMessage"></div>
            <form id="loginForm">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="loginEmail" placeholder="seu@email.com" required>
                </div>
                <div class="form-group">
                    <label>Senha</label>
                    <input type="password" id="loginPassword" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn">Entrar</button>
            </form>
            <p style="text-align: center; margin-top: 20px; color: var(--gray); font-size: 13px;">
                Use: admin@{service_name}.com / admin123
            </p>
        </div>
    </div>
    
    <div class="app-container" id="appScreen">
        <nav class="sidebar">
            <div class="sidebar-logo">
                <span>🏋️</span>
                <h2>{service_name.title()}</h2>
            </div>
            <ul class="nav-menu">
                <li class="nav-item"><a href="#" class="nav-link active" onclick="showSection('dashboard')"><span>📊</span> Dashboard</a></li>
                <li class="nav-item"><a href="#" class="nav-link" onclick="showSection('{entity_name.lower()}s')"><span>👥</span> {entity_name}s</a></li>
            </ul>
        </nav>
        
        <main class="main-content">
            <div class="header">
                <h1 id="pageTitle">Dashboard</h1>
                <div class="user-info">
                    <div class="user-avatar">A</div>
                    <span class="user-name" id="userName">Admin</span>
                    <button class="btn btn-logout" onclick="logout()">Sair</button>
                </div>
            </div>
            
            <div id="dashboard">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total de {entity_name}s</h3>
                        <div class="value" id="total{entity_name}s">0</div>
                    </div>
                    <div class="stat-card">
                        <h3>Ativos</h3>
                        <div class="value" id="ativos">0</div>
                    </div>
                </div>
            </div>
            
            <div id="{entity_name.lower()}s" style="display: none;">
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2>Gerenciar {entity_name}s</h2>
                        <button class="btn" onclick="openModal()">+ Novo {entity_name}</button>
                    </div>
                    <table>
                        <thead><tr><th>Nome</th><th>Email</th><th>Data</th><th>Ações</th></tr></thead>
                        <tbody id="{entity_name.lower()}TableBody"></tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
    
    <div class="modal" id="{entity_name.lower()}Modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Novo {entity_name}</h2>
                <button onclick="closeModal()">&times;</button>
            </div>
            <form id="{entity_name.lower()}Form">
                <input type="hidden" id="{entity_name.lower()}Id">
                <div class="form-group">
                    <label>Nome</label>
                    <input type="text" id="{entity_name.lower()}Nome" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="{entity_name.lower()}Email" required>
                </div>
                <button type="submit" class="btn">Salvar</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancelar</button>
            </form>
        </div>
    </div>
    
    <div class="toast" id="toast"></div>
    
    <script>
        const API_URL = 'http://localhost:8000/api/{service_name}/{entity_name.lower()}s';
        const USERS = [{{ email: 'admin@{service_name}.com', password: 'admin123', nome: 'Administrador' }}];
        
        let currentUser = null;
        
        document.getElementById('loginForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const user = USERS.find(u => u.email === email && u.password === password);
            if (user) {{
                currentUser = user;
                document.getElementById('loginScreen').style.display = 'none';
                document.getElementById('appScreen').style.display = 'block';
                document.getElementById('userName').textContent = user.nome;
                load{entity_name}s();
            }} else {{
                alert('Email ou senha incorretos');
            }}
        }});
        
        function logout() {{
            currentUser = null;
            document.getElementById('loginScreen').style.display = 'flex';
            document.getElementById('appScreen').style.display = 'none';
            document.getElementById('loginForm').reset();
        }}
        
        function showSection(section) {{
            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            event.target.closest('.nav-link').classList.add('active');
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('{entity_name.lower()}s').style.display = 'none';
            document.getElementById(section).style.display = 'block';
            document.getElementById('pageTitle').textContent = section === 'dashboard' ? 'Dashboard' : '{entity_name}s';
            if (section === '{entity_name.lower()}s') load{entity_name}s();
        }}
        
        async function load{entity_name}s() {{
            try {{
                const response = await fetch(API_URL);
                const data = await response.json();
                document.getElementById('total{entity_name}s').textContent = data.length;
                document.getElementById('ativos').textContent = Math.floor(data.length * 0.8);
                const tbody = document.getElementById('{entity_name.lower()}TableBody');
                if (data.length === 0) {{
                    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px;">Nenhum {entity_name.lower()} cadastrado</td></tr>';
                    return;
                }}
                tbody.innerHTML = data.map(item => `
                    <tr>
                        <td>${{item.nome}}</td>
                        <td>${{item.email}}</td>
                        <td>${{new Date(item.created_at).toLocaleDateString('pt-BR')}}</td>
                        <td><button class="btn btn-danger" onclick="delete{entity_name}('${{item.id}}')">Excluir</button></td>
                    </tr>
                `).join('');
            }} catch (e) {{ console.error('Error:', e); }}
        }}
        
        function openModal() {{
            document.getElementById('{entity_name.lower()}Modal').classList.add('active');
            document.getElementById('modalTitle').textContent = 'Novo {entity_name}';
            document.getElementById('{entity_name.lower()}Id').value = '';
            document.getElementById('{entity_name.lower()}Form').reset();
        }}
        
        function closeModal() {{
            document.getElementById('{entity_name.lower()}Modal').classList.remove('active');
        }}
        
        document.getElementById('{entity_name.lower()}Form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            const id = document.getElementById('{entity_name.lower()}Id').value;
            const nome = document.getElementById('{entity_name.lower()}Nome').value;
            const email = document.getElementById('{entity_name.lower()}Email').value;
            try {{
                let response;
                if (id) {{
                    response = await fetch(`${{API_URL}}/${{id}}`, {{ method: 'PUT', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ nome, email }}) }});
                }} else {{
                    response = await fetch(API_URL, {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ nome, email }}) }});
                }}
                if (response.ok) {{
                    showToast('{entity_name} salvo com sucesso!', 'success');
                    closeModal();
                    load{entity_name}s();
                }} else {{
                    showToast('Erro ao salvar', 'error');
                }}
            }} catch (e) {{ showToast('Erro ao conectar', 'error'); }}
        }});
        
        async function delete{entity_name}(id) {{
            if (!confirm('Tem certeza que deseja excluir?')) return;
            try {{
                const response = await fetch(`${{API_URL}}/${{id}}`, {{ method: 'DELETE' }});
                if (response.ok) {{
                    showToast('{entity_name} excluído!', 'success');
                    load{entity_name}s();
                }} else {{
                    showToast('Erro ao excluir', 'error'); }}
            }} catch (e) {{ showToast('Erro ao conectar', 'error'); }}
        }}
        
        function showToast(message, type) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast ' + type + ' show';
            setTimeout(() => toast.classList.remove('show'), 3000);
        }}
    </script>
</body>
</html>
'''
