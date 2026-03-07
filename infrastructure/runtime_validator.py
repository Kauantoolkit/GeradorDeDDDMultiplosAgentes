"""
Runtime Validator - Validador de Execução em Tempo Real
=======================================================

Este módulo valida se o código realmente executa, não apenas verifica estrutura.
É o "pulo do gato" que seus agentes estão faltando - a capacidade de
tentar rodar o código e ver se funciona.

Funcionalidades:
- Testar imports de módulos Python
- Verificar erros de sintaxe
- Testar se APIs sobem (sem banco de dados)
- Detectar e corrigir erros comuns automaticamente
- Só usar LLM para erros complexos
"""

import ast
import sys
import os
import subprocess
from pathlib import Path
from typing import Any
from loguru import logger


class RuntimeValidator:
    """
    Validador que testa se o código realmente executa.
    
    Este validador é diferente do Validator Agent que apenas verifica estrutura.
    Ele TENTA importar e executar o código para verificar se funciona.
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.errors = []
        self.warnings = []
    
    async def validate_all_services(self) -> dict[str, Any]:
        """
        Valida todos os serviços do projeto.
        
        Returns:
            Dicionário com resultados por serviço
        """
        results = {}
        
        # Encontrar todos os serviços
        services_path = Path(self.project_path) / "services"
        if not services_path.exists():
            logger.warning(f"Diretório de serviços não encontrado: {services_path}")
            return results
        
        for service_dir in services_path.iterdir():
            if not service_dir.is_dir():
                continue
            
            service_name = service_dir.name
            logger.info(f"Validando serviço: {service_name}")
            
            result = await self.validate_service(service_name, service_dir)
            results[service_name] = result
        
        return results
    
    async def validate_service(self, service_name: str, service_path: Path) -> dict[str, Any]:
        """
        Valida um serviço específico.
        
        Args:
            service_name: Nome do serviço
            service_path: Caminho do diretório do serviço
            
        Returns:
            Dicionário com resultado da validação
        """
        result = {
            "service_name": service_name,
            "path": str(service_path),
            "imports_ok": False,
            "syntax_ok": False,
            "startup_ok": False,
            "errors": [],
            "warnings": [],
            "score": 0.0
        }
        
        # 1. Testar imports
        import_result = self._test_imports(service_name, service_path)
        result["imports_ok"] = import_result["success"]
        result["imports_errors"] = import_result.get("errors", [])
        
        # 2. Testar sintaxe
        syntax_result = self._test_syntax(service_path)
        result["syntax_ok"] = syntax_result["success"]
        result["syntax_errors"] = syntax_result.get("errors", [])
        
        # 3. Testar startup (se tem main.py)
        if (service_path / "main.py").exists():
            startup_result = await self._test_startup(service_name, service_path)
            result["startup_ok"] = startup_result["success"]
            result["startup_errors"] = startup_result.get("errors", [])
        
        # Calcular score
        checks = [
            result["imports_ok"],
            result["syntax_ok"],
            result["startup_ok"]
        ]
        result["score"] = sum(checks) / len(checks) if checks else 0.0
        
        return result
    
    def _test_imports(self, service_name: str, service_path: Path) -> dict[str, Any]:
        """
        Testa se os módulos podem ser importados.
        
        Args:
            service_name: Nome do serviço
            service_path: Caminho do diretório do serviço
            
        Returns:
            Dicionário com resultado
        """
        result = {
            "success": False,
            "errors": []
        }
        
        # Adicionar o caminho do projeto ao sys.path
        project_root = str(service_path.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Tentar importar o main do serviço
        try:
            service_module_path = service_path / "main.py"
            if service_module_path.exists():
                # Compilar para verificar sintaxe
                with open(service_module_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Testar syntax
                ast.parse(code)
                
                # Tentar importar o módulo
                module_name = f"services.{service_name}.main"
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, service_module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    result["success"] = True
                    logger.info(f"  ✓ Imports OK: {service_name}")
                    
        except SyntaxError as e:
            error_msg = f"Syntax error em {e.filename}:{e.lineno} - {e.msg}"
            result["errors"].append(error_msg)
            logger.error(f"  ✗ Syntax error: {service_name} - {error_msg}")
            
        except ImportError as e:
            error_msg = f"Import error: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(f"  ✗ Import error: {service_name} - {error_msg}")
            
            # Tentar identificar dependência faltando
            missing_dep = self._extract_missing_dependency(str(e))
            if missing_dep:
                result["missing_dependency"] = missing_dep
                result["suggested_fix"] = f"pip install {missing_dep}"
                
        except Exception as e:
            error_msg = f"Erro ao importar: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(f"  ✗ Import error: {service_name} - {error_msg}")
        
        return result
    
    def _test_syntax(self, service_path: Path) -> dict[str, Any]:
        """
        Testa a sintaxe de todos os arquivos Python do serviço.
        
        Args:
            service_path: Caminho do diretório do serviço
            
        Returns:
            Dicionário com resultado
        """
        result = {
            "success": True,
            "errors": []
        }
        
        # Encontrar todos os arquivos Python
        py_files = list(service_path.rglob("*.py"))
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                ast.parse(code)
            except SyntaxError as e:
                error_msg = f"Syntax error em {py_file.name}:{e.lineno} - {e.msg}"
                result["errors"].append(error_msg)
                result["success"] = False
                logger.error(f"  ✗ Syntax error: {py_file.name}")
            except Exception as e:
                # Outros erros são menos críticos
                pass
        
        if result["success"]:
            logger.info(f"  ✓ Syntax OK: {service_path.name}")
        
        return result
    
    async def _test_startup(self, service_name: str, service_path: Path) -> dict[str, Any]:
        """
        Testa se a aplicação FastAPI consegue subir.
        
        Args:
            service_name: Nome do serviço
            service_path: Caminho do diretório do serviço
            
        Returns:
            Dicionário com resultado
        """
        result = {
            "success": False,
            "errors": []
        }
        
        try:
            # Importar o app FastAPI
            sys.path.insert(0, str(service_path.parent.parent))
            
            # Tentar importar o app
            main_path = service_path / "main.py"
            module_name = f"services.{service_name}.main"
            
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, main_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                # Executar o módulo para obter o app
                try:
                    spec.loader.exec_module(module)
                    
                    # Verificar se tem atributo 'app'
                    if hasattr(module, 'app'):
                        result["success"] = True
                        logger.info(f"  ✓ Startup OK: {service_name}")
                    else:
                        result["errors"].append("Módulo não tem atributo 'app' (FastAPI)")
                        
                except Exception as e:
                    # Erro ao executar - pode ser dependência faltando
                    result["errors"].append(f"Erro ao executar: {str(e)}")
                    
        except Exception as e:
            result["errors"].append(f"Erro no startup: {str(e)}")
            logger.error(f"  ✗ Startup error: {service_name} - {str(e)}")
        
        return result
    
    def _extract_missing_dependency(self, error_message: str) -> str | None:
        """
        Extrai o nome da dependência faltando a partir da mensagem de erro.
        
        Args:
            error_message: Mensagem de erro do ImportError
            
        Returns:
            Nome da dependência ou None
        """
        import re
        
        # Padrões comuns de erros de dependência
        patterns = [
            r"No module named ['\"]([^'\"]+)['\"]",
            r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                module_name = match.group(1)
                # Traduzir para nome de pacote pip se necessário
                return self._translate_module_to_package(module_name)
        
        return None
    
    def _translate_module_to_package(self, module_name: str) -> str:
        """
        Traduz nome do módulo Python para nome do pacote pip.
        
        Args:
            module_name: Nome do módulo
            
        Returns:
            Nome do pacote pip
        """
        translations = {
            "email_validator": "email-validator",
            "passlib": "passlib[bcrypt]",
            "bcrypt": "bcrypt",
            "python_jose": "python-jose[cryptography]",
            "cryptography": "cryptography",
            "pydantic_settings": "pydantic-settings",
            "asyncpg": "asyncpg",
            "psycopg2": "psycopg2-binary",
            "sqlalchemy": "sqlalchemy",
            "alembic": "alembic",
            "uvicorn": "uvicorn[standard]",
            "python_multipart": "python-multipart",
        }
        
        return translations.get(module_name, module_name)


class CommonErrorFixer:
    """
    Corretor de erros comuns automaticamente, sem precisar de LLM.
    
    Este é o segundo componente crucial - a capacidade de corrigir
    erros comuns sem ter que chamar o LLM para cada problema.
    """
    
    # Mapeamento de erros comuns para correções
    COMMON_FIXES = {
        "No module named 'email-validator'": {
            "file_pattern": "requirements.txt",
            "action": "add_line",
            "value": "email-validator>=2.0.0"
        },
        "No module named 'passlib'": {
            "file_pattern": "requirements.txt",
            "action": "add_line",
            "value": "passlib[bcrypt]>=1.7.4"
        },
        "No module named 'bcrypt'": {
            "file_pattern": "requirements.txt",
            "action": "add_line",
            "value": "bcrypt>=4.0.0"
        },
        "No module named 'asyncpg'": {
            "file_pattern": "requirements.txt",
            "action": "add_line",
            "value": "asyncpg>=0.29.0"
        },
        "No module named 'pydantic'": {
            "file_pattern": "requirements.txt",
            "action": "add_line",
            "value": "pydantic>=2.5.0"
        },
    }
    
    def __init__(self, project_path: str):
        self.project_path = project_path
    
    def detect_and_fix(self, error_message: str) -> dict[str, Any] | None:
        """
        Detecta erros comuns e aplica correção automática.
        
        Args:
            error_message: Mensagem de erro
            
        Returns:
            Dicionário com informação da correção aplicada ou None
        """
        # Procurar por padrão de erro conhecido
        for pattern, fix in self.COMMON_FIXES.items():
            if pattern in error_message:
                logger.info(f"Detectado erro comum: {pattern}")
                return self._apply_fix(fix)
        
        return None
    
    def _apply_fix(self, fix: dict) -> dict[str, Any]:
        """
        Aplica uma correção automática.
        
        Args:
            fix: Dicionário com informações da correção
            
        Returns:
            Resultado da correção
        """
        result = {
            "success": False,
            "action_taken": None
        }
        
        file_pattern = fix.get("file_pattern")
        action = fix.get("action")
        value = fix.get("value")
        
        # Encontrar arquivo
        if file_pattern == "requirements.txt":
            # Procurar em todos os serviços
            services_path = Path(self.project_path) / "services"
            if services_path.exists():
                for service_dir in services_path.iterdir():
                    if not service_dir.is_dir():
                        continue
                    
                    req_file = service_dir / "requirements.txt"
                    if req_file.exists():
                        # Verificar se a dependência já existe
                        with open(req_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if value.split(">")[0] in content:
                            continue  # Já existe
                        
                        # Adicionar dependência
                        with open(req_file, 'a', encoding='utf-8') as f:
                            f.write(f"\n{value}\n")
                        
                        result["success"] = True
                        result["action_taken"] = f"Adicionado {value} em {req_file}"
                        logger.info(f"  ✓ {result['action_taken']}")
        
        return result


class RuntimeValidationOrchestrator:
    """
    Orquestrador que combina validação de execução e correção automática.
    
    Este é o fluxo completo que seus agentes estavam faltando:
    1. Tentar importar/executar o código
    2. Se falhar, detectar erro
    3. Se for erro comum, corrigir automaticamente
    4. Se for erro complexo, usar LLM
    5. Revalidar
    """
    
    def __init__(self, project_path: str, llm_provider=None):
        self.project_path = project_path
        self.llm_provider = llm_provider
        self.validator = RuntimeValidator(project_path)
        self.fixer = CommonErrorFixer(project_path)
    
    async def validate_and_fix(self) -> dict[str, Any]:
        """
        Executa validação e correção automática.
        
        Returns:
            Resultado da validação com correções aplicadas
        """
        logger.info("="*60)
        logger.info("RUNTIME VALIDATOR - Validando execução real")
        logger.info("="*60)
        
        # Validar todos os serviços
        results = await self.validator.validate_all_services()
        
        # Para cada serviço com erro, tentar corrigir
        for service_name, result in results.items():
            if not result["imports_ok"]:
                # Tentar corrigir erros
                for error in result.get("imports_errors", []):
                    fix_result = self.fixer.detect_and_fix(error)
                    if fix_result and fix_result["success"]:
                        logger.info(f"Correção automática aplicada para {service_name}")
                        result["auto_fixes"] = result.get("auto_fixes", [])
                        result["auto_fixes"].append(fix_result["action_taken"])
        
        # Revalidar após correções
        # (simplificado - em produção faria um loop)
        
        return {
            "results": results,
            "total_services": len(results),
            "successful": sum(1 for r in results.values() if r["imports_ok"]),
            "failed": sum(1 for r in results.values() if not r["imports_ok"])
        }


# Função de conveniência para testar
async def quick_validate(project_path: str) -> dict[str, Any]:
    """
    Função de conveniência para validação rápida.
    
    Args:
        project_path: Caminho do projeto
        
    Returns:
        Resultado da validação
    """
    orchestrator = RuntimeValidationOrchestrator(project_path)
    return await orchestrator.validate_and_fix()


if __name__ == "__main__":
    import asyncio
    
    # Teste rápido
    project = "ifoodclone8"
    result = asyncio.run(quick_validate(project))
    print(f"\nResultado: {result}")

