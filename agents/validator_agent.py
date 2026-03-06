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
import re
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

            # Aplica guardrails determinísticos para evitar aprovações indevidas
            self._apply_guardrails(requirement, execution_result, result)
            
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

    def _apply_guardrails(
        self,
        requirement: Requirement,
        execution_result: ExecutionResult,
        result: ValidationResult,
    ) -> None:
        """Aplica validações determinísticas e força reprovação quando necessário."""
        issues = self._run_guardrail_checks(requirement, execution_result)
        if not issues:
            return

        for issue in issues:
            if issue not in result.issues:
                result.issues.append(issue)
            if issue not in result.rejected_items:
                result.rejected_items.append(issue)

        result.score = min(result.score, 0.4)
        result.reject(
            "Guardrails de qualidade detectaram inconsistências críticas: "
            + "; ".join(issues)
        )
        logger.warning(f"❌ Guardrails reprovaram validação: {issues}")

    def _run_guardrail_checks(
        self,
        requirement: Requirement,
        execution_result: ExecutionResult,
    ) -> list[str]:
        """Executa verificações objetivas para reduzir falsos positivos na validação."""
        issues: list[str] = []
        project_path = requirement.project_config.output_directory
        file_manager = FileManager(project_path)

        service_names = self._extract_service_names(execution_result.files_created)
        for service_name in service_names:
            entity_issue = self._check_service_entity_consistency(service_name, file_manager)
            if entity_issue:
                issues.append(entity_issue)

            dependency_issue = self._check_service_email_dependency(service_name, file_manager)
            if dependency_issue:
                issues.append(dependency_issue)

        frontend_issue = self._check_frontend_requirement(requirement, file_manager)
        if frontend_issue:
            issues.append(frontend_issue)

        return issues

    def _extract_service_names(self, files_created: list[str]) -> list[str]:
        services = []
        for file_path in files_created or []:
            normalized = file_path.replace("\\", "/")
            parts = normalized.split("/")
            if "services" not in parts:
                continue
            try:
                service_index = parts.index("services") + 1
                service_name = parts[service_index]
                if service_name and service_name not in services:
                    services.append(service_name)
            except (ValueError, IndexError):
                continue
        return services

    def _check_service_entity_consistency(self, service_name: str, file_manager: FileManager) -> str | None:
        entity_candidates = [
            f"services/{service_name}/domain/{service_name}_entities.py",
            f"services/{service_name}/domain/entities.py",
        ]

        entity_content = None
        entity_file = None
        for candidate in entity_candidates:
            content = file_manager.read_file(candidate)
            if content:
                entity_content = content
                entity_file = candidate
                break

        if not entity_content:
            return None

        expected_entities = self._expected_entities_for_service(service_name)
        if not expected_entities:
            return None

        defined_classes = set(re.findall(r"class\s+(\w+)\s*[(:]", entity_content))
        if any(entity in defined_classes for entity in expected_entities):
            return None

        return (
            f"Serviço '{service_name}' sem entidade coerente em {entity_file}. "
            f"Esperado uma das classes: {', '.join(expected_entities)}"
        )

    def _expected_entities_for_service(self, service_name: str) -> list[str]:
        name = service_name.lower().replace("-", "_")
        mapping = {
            "user": ["User"],
            "usuario": ["Usuario", "User"],
            "product": ["Product", "Produto"],
            "produto": ["Produto", "Product"],
            "order": ["Order", "Pedido"],
            "pedido": ["Pedido", "Order"],
            "payment": ["Payment", "Pagamento"],
            "pagamento": ["Pagamento", "Payment"],
        }

        expected = []
        for token, entities in mapping.items():
            if token in name:
                expected.extend(entities)
        return list(dict.fromkeys(expected))

    def _check_service_email_dependency(self, service_name: str, file_manager: FileManager) -> str | None:
        schema_candidates = [
            f"services/{service_name}/api/schemas.py",
            f"services/{service_name}/api/schema.py",
        ]
        schema_content = None
        for candidate in schema_candidates:
            schema_content = file_manager.read_file(candidate)
            if schema_content:
                break

        if not schema_content or "EmailStr" not in schema_content:
            return None

        requirements_content = file_manager.read_file(f"services/{service_name}/requirements.txt") or ""
        normalized = requirements_content.lower()
        has_dependency = "email-validator" in normalized or "pydantic[email]" in normalized

        if has_dependency:
            return None

        return (
            f"Serviço '{service_name}' usa EmailStr em api/schemas.py sem dependência "
            "'email-validator' ou 'pydantic[email]' no requirements.txt"
        )

    def _check_frontend_requirement(self, requirement: Requirement, file_manager: FileManager) -> str | None:
        description = (requirement.description or "").lower()
        frontend_keywords = [
            "frontend", "react", "vue", "angular", "ui", "interface web", "tela", "spa"
        ]
        if not any(keyword in description for keyword in frontend_keywords):
            return None

        frontend_signals = [
            "frontend/package.json",
            "frontend/src/main.jsx",
            "frontend/src/main.tsx",
            "web/package.json",
            "client/package.json",
            "index.html",
        ]

        for signal in frontend_signals:
            if file_manager.read_file(signal):
                return None

        return "Requisito menciona frontend, mas nenhum artefato de frontend foi gerado"
    
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
    
    # Patterns that indicate domain anemia (entities without behavior)
    ANEMIC_PATTERNS = [
        r'def\s+get_\w+\(self\)',  # Only getters
        r'def\s+set_\w+\(self',     # Only setters
        r'pass\s*$',                # Empty methods
    ]
    
    # Frameworks that should NOT be in domain layer
    FORBIDDEN_IN_DOMAIN = [
        'sqlalchemy',
        'fastapi',
        'pydantic',
        'flask',
        'django',
        'orm',
        'Column',
        'Table',
    ]
    
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
    
    # ============================================================
    # DDD-SPECIFIC VALIDATION RULES
    # ============================================================
    
    @staticmethod
    def detect_domain_anemia(code: str) -> list[str]:
        """
        Detecta se há anemia de domínio no código.
        
        Args:
            code: Código a ser analisado
            
        Returns:
            Lista de problemas encontrados
        """
        import re
        issues = []
        
        # Check for empty classes or classes with only getters/setters
        class_pattern = r'class\s+(\w+).*?:'
        classes = re.findall(class_pattern, code)
        
        for cls in classes:
            # Check if class has only data attributes and getters/setters
            class_block = re.search(rf'class\s+{cls}.*?(?=\nclass|\Z)', code, re.DOTALL)
            if class_block:
                block = class_block.group(0)
                
                # Count meaningful methods (not __init__, getters/setters)
                methods = re.findall(r'def\s+(\w+)\(', block)
                meaningful_methods = [m for m in methods 
                                     if not m.startswith('_') 
                                     and not m.startswith('get_') 
                                     and not m.startswith('set_')
                                     and m not in ['to_dict', 'to_dict']]
                
                if len(meaningful_methods) == 0:
                    issues.append(f"Entidade '{cls}' parece ser anêmica (sem comportamento)")
        
        return issues
    
    @staticmethod
    def check_domain_layer_purity(code: str) -> list[str]:
        """
        Verifica se a camada de domínio está pura (sem dependências de frameworks).
        
        Args:
            code: Código do domínio
            
        Returns:
            Lista de problemas encontrados
        """
        issues = []
        
        for forbidden in ValidationRules.FORBIDDEN_IN_DOMAIN:
            if forbidden.lower() in code.lower():
                # Check if it's an import (not just a comment)
                import re
                if re.search(rf'^\s*(from|import)\s+.*{forbidden}', code, re.MULTILINE):
                    issues.append(f"Dependência de framework '{forbidden}' encontrada no domínio")
        
        return issues
    
    @staticmethod
    def check_aggregate_root_exists(files: list[str]) -> bool:
        """Verifica se há aggregate roots definidos."""
        aggregate_files = [f for f in files if "aggregate" in f.lower()]
        return len(aggregate_files) > 0
    
    @staticmethod
    def check_value_objects_exist(files: list[str]) -> bool:
        """Verifica se há value objects definidos."""
        vo_files = [f for f in files if "value_object" in f.lower() or "valueobject" in f.lower()]
        return len(vo_files) > 0
    
    @staticmethod
    def check_domain_events_exist(files: list[str]) -> bool:
        """Verifica se há domain events definidos."""
        event_files = [f for f in files if "event" in f.lower() and "domain" in f.lower()]
        return len(event_files) > 0
    
    @staticmethod
    def check_repository_interface_separation(files: list[str]) -> dict[str, bool]:
        """
        Verifica se interfaces de repositório estão separadas das implementações.
        
        Returns:
            dict com 'interface_in_domain' e 'implementation_in_infrastructure'
        """
        result = {
            'interface_in_domain': False,
            'implementation_in_infrastructure': False
        }
        
        for f in files:
            if '/domain/' in f and 'repository' in f.lower():
                result['interface_in_domain'] = True
            if '/infrastructure/' in f and 'repository' in f.lower():
                result['implementation_in_infrastructure'] = True
        
        return result
    
    @staticmethod
    def check_layer_dependencies(files: list[str], code_contents: dict[str, str]) -> list[str]:
        """
        Verifica se as dependências entre camadas estão corretas.
        
        Args:
            files: Lista de caminhos de arquivos
            code_contents: Dicionário {caminho: conteúdo}
            
        Returns:
            Lista de violações encontradas
        """
        violations = []
        
        # Domain should not import from infrastructure or api
        domain_files = [f for f in files if '/domain/' in f]
        
        for file_path in domain_files:
            code = code_contents.get(file_path, '')
            
            # Check for imports from other layers
            if '/infrastructure/' in code:
                violations.append(f"{file_path}: Domínio importa de infraestrutura")
            if '/api/' in code:
                violations.append(f"{file_path}: Domínio importa de API")
        
        return violations
    
    @staticmethod
    def run_full_ddd_validation(files: list[str], code_contents: dict[str, str]) -> dict:
        """
        Executa validação completa de DDD.
        
        Args:
            files: Lista de arquivos
            code_contents: Conteúdo dos arquivos
            
        Returns:
            Dicionário com resultado da validação
        """
        result = {
            'has_ddd_structure': False,
            'has_aggregates': False,
            'has_value_objects': False,
            'has_domain_events': False,
            'domain_is_pure': True,
            'repository_separation': False,
            'layer_violations': [],
            'anemia_issues': [],
            'score': 0.0
        }
        
        # Check structure
        structure = ValidationRules.check_ddd_structure(files)
        result['has_ddd_structure'] = all(structure.values())
        
        # Check aggregates
        result['has_aggregates'] = ValidationRules.check_aggregate_root_exists(files)
        
        # Check value objects
        result['has_value_objects'] = ValidationRules.check_value_objects_exist(files)
        
        # Check domain events
        result['has_domain_events'] = ValidationRules.check_domain_events_exist(files)
        
        # Check repository separation
        repo_sep = ValidationRules.check_repository_interface_separation(files)
        result['repository_separation'] = all(repo_sep.values())
        
        # Check domain purity
        domain_files = [f for f in files if '/domain/' in f]
        domain_purity_issues = []
        for f in domain_files:
            issues = ValidationRules.check_domain_layer_purity(code_contents.get(f, ''))
            domain_purity_issues.extend(issues)
        result['domain_is_pure'] = len(domain_purity_issues) == 0
        result['layer_violations'] = domain_purity_issues
        
        # Check for domain anemia
        anemia_issues = []
        for f in files:
            if '/domain/' in f:
                issues = ValidationRules.detect_domain_anemia(code_contents.get(f, ''))
                anemia_issues.extend(issues)
        result['anemia_issues'] = anemia_issues
        
        # Calculate score
        checks = [
            result['has_ddd_structure'],
            result['has_aggregates'],
            result['has_value_objects'],
            result['domain_is_pure'],
            result['repository_separation'],
            len(result['anemia_issues']) == 0
        ]
        
        result['score'] = sum(checks) / len(checks)
        
        return result
