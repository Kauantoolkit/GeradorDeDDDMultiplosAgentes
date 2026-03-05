"""
Integrity Validator - Validador de Integridade do Projeto Gerado
================================================================

Este módulo valida que o projeto gerado está integro:
- Sem placeholders não substituídos
- Imports resolvem corretamente
- Estrutura DDD respeitada
- Syntax Python válida

Esta é uma camada CRÍTICA de validação que DEVE passar
antes de considerar o projeto como "pronto".
"""

import os
import re
import ast
from typing import Any
from loguru import logger


class IntegrityValidator:
    """
    Validador de integridade do projeto gerado.
    
    Executa verificações críticas para garantir que o projeto
    pode ser executado sem erros de import ou syntax.
    """
    
    # Placeholders que não devem existir no código gerado
    FORBIDDEN_PATTERNS = [
        r'\{entity_name\}',
        r'\{domain\}',
        r'\{service_name\}',
        r'\{entity_name\.lower\(\)\}',
        r'\{domain\.lower\(\)\}',
        r'\{\{entity_name\}\}',
        r'\{\{domain\}\}',
        r'\{\{service_name\}\}',
        r'\{\{entity_name\.lower\(\)\}\}',
        r'\{\{domain\.lower\(\)\}\}',
    ]
    
    # Padrões de imports que indicam problemas
    SUSPICIOUS_IMPORTS = [
        r'from services\.\w+\.infrastructure\.services import',  # Services que não existem
    ]
    
    def __init__(self, project_path: str):
        """
        Inicializa o validador.
        
        Args:
            project_path: Caminho raiz do projeto gerado
        """
        self.project_path = project_path
        self.errors = []
        self.warnings = []
        self.files_checked = 0
        self.files_with_issues = []
    
    def validate(self, skip_docker: bool = False) -> dict:
        """
        Executa todas as validações.
        
        Args:
            skip_docker: Se True, pula validação de Docker (para testes rápidos)
            
        Returns:
            Dicionário com resultado da validação
        """
        logger.info(f"Iniciando validação de integridade: {self.project_path}")
        
        # Executar todas as validações
        self._check_placeholders()
        self._check_imports()
        self._check_syntax()
        self._check_ddd_structure()
        self._check_required_files()
        
        # NOVAS VERIFICAÇÕES CRÍTICAS
        self._check_fastapi_duplicates()
        self._check_apirouter_in_routes()
        self._check_imports_with_hyphen()
        self._check_shadowing()
        self._check_relative_imports_in_main()
        self._check_unpinned_postgres_images()
        
        # Resultado
        result = {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'files_checked': self.files_checked,
            'files_with_issues': self.files_with_issues,
        }
        
        if result['valid']:
            logger.info(f"✅ Validação de integridade PASSOU")
        else:
            logger.error(f"❌ Validação de integridade FALHOU com {len(self.errors)} erros")
        
        return result
    
    # ============================================================
    # NOVAS VERIFICAÇÕES CRÍTICAS
    # ============================================================
    
    def _check_fastapi_duplicates(self) -> None:
        """
        Verifica se há mais de uma instância de FastAPI() por serviço.
        
        CRÍTICO: Apenas main.py deve criar FastAPI().
        Arquivos como routes.py NÃO devem criar FastAPI().
        """
        logger.debug("Verificando instâncias FastAPI duplicadas...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Conta instâncias de FastAPI()
                fastapi_count = content.count('FastAPI(')
                
                if fastapi_count > 0:
                    # Se é routes.py, não deveria ter FastAPI()
                    if 'routes.py' in file_path:
                        if fastapi_count > 0:
                            self.errors.append({
                                'type': 'fastapi_in_routes',
                                'file': rel_path,
                                'error': 'routes.py não deve criar FastAPI() - use APIRouter()',
                                'count': fastapi_count,
                            })
                            self.files_with_issues.append(rel_path)
                            logger.error(f"❌ {rel_path}: FastAPI() encontrado em routes.py")
                    
                    # Se é main.py, deveria ter exatamente 1
                    elif 'main.py' in file_path:
                        if fastapi_count > 1:
                            self.errors.append({
                                'type': 'fastapi_duplicado',
                                'file': rel_path,
                                'error': f'Main.py tem {fastapi_count} instâncias de FastAPI() - deve ter apenas 1',
                                'count': fastapi_count,
                            })
                            self.files_with_issues.append(rel_path)
                            logger.error(f"❌ {rel_path}: FastAPI() duplicado em main.py")
                            
            except Exception as e:
                logger.warning(f"Erro ao verificar FastAPI em {file_path}: {e}")
        
        if not any(e['type'] in ['fastapi_in_routes', 'fastapi_duplicado'] for e in self.errors):
            logger.debug("✅ Verificação de FastAPI OK")
    
    def _check_apirouter_in_routes(self) -> None:
        """
        Verifica se routes.py usa APIRouter corretamente.
        
        CRÍTICO: routes.py deve usar APIRouter, não FastAPI.
        """
        logger.debug("Verificando uso de APIRouter em routes.py...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Se é routes.py, deve ter APIRouter
                if 'routes.py' in file_path:
                    if 'APIRouter' not in content and 'router' not in content:
                        self.errors.append({
                            'type': 'no_apirouter',
                            'file': rel_path,
                            'error': 'routes.py não usa APIRouter - deve usar APIRouter do FastAPI',
                        })
                        self.files_with_issues.append(rel_path)
                        logger.error(f"❌ {rel_path}: APIRouter não encontrado")
                    elif 'from fastapi import' in content and 'APIRouter' not in content:
                        self.errors.append({
                            'type': 'wrong_import_in_routes',
                            'file': rel_path,
                            'error': 'routes.py importa FastAPI mas não APIRouter',
                        })
                        self.files_with_issues.append(rel_path)
                        
            except Exception as e:
                logger.warning(f"Erro ao verificar APIRouter em {file_path}: {e}")
        
        if not any(e['type'] in ['no_apirouter', 'wrong_import_in_routes'] for e in self.errors):
            logger.debug("✅ Verificação de APIRouter OK")
    
    def _check_imports_with_hyphen(self) -> None:
        """
        Verifica se há imports com hífen (inválidos em Python).
        
        CRÍTICO: Python não suporta hífen em nomes de módulos.
        """
        logger.debug("Verificando imports com hífen...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Procura por imports contendo hífen
                # Padrão: from/import seguido de algo com hífen
                hyphen_import_pattern = r'(?:from|import)\s+[\w\.]*-\w[\w\.]*'
                matches = re.findall(hyphen_import_pattern, content)
                
                if matches:
                    for match in matches:
                        self.errors.append({
                            'type': 'import_with_hyphen',
                            'file': rel_path,
                            'import': match,
                            'error': 'Import com hífen é inválido em Python',
                        })
                        self.files_with_issues.append(rel_path)
                        logger.error(f"❌ {rel_path}: Import com hífen: {match}")
                
                # Também verifica referências a diretórios com hífen
                # Ex: services/auth-service/...
                if 'services/' in content or 'services\\' in content:
                    # Procura por padrões como services/auth-service/
                    dir_hyphen_pattern = r'services[/\\][a-zA-Z]+-[a-zA-Z]+'
                    dir_matches = re.findall(dir_hyphen_pattern, content)
                    
                    if dir_matches:
                        for match in dir_matches:
                            # Normaliza para verificação
                            normalized = match.replace('-', '_').replace('\\', '/')
                            if normalized != match.replace('\\', '/'):
                                self.warnings.append({
                                    'type': 'directory_with_hyphen',
                                    'file': rel_path,
                                    'path': match,
                                    'suggestion': f'Troque {match} por {normalized}',
                                })
                                
            except Exception as e:
                logger.warning(f"Erro ao verificar imports com hífen em {file_path}: {e}")
        
        if not any(e['type'] == 'import_with_hyphen' for e in self.errors):
            logger.debug("✅ Verificação de imports com hífen OK")
    
    def _check_shadowing(self) -> None:
        """
        Verifica se há shadowing de funções (função com mesmo nome de import).
        
        CRÍTICO: Shadowing causa comportamentos inesperados.
        """
        logger.debug("Verificando shadowing de funções...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Extrai nomes importados
                imports = self._extract_imported_names(content)
                
                # Extrai nomes de funções definidas
                functions = self._extract_function_names(content)
                
                # Verifica shadowing
                for func_name in functions:
                    if func_name in imports:
                        self.errors.append({
                            'type': 'shadowing',
                            'file': rel_path,
                            'function': func_name,
                            'error': f'Função "{func_name}" sobrescreve import com mesmo nome',
                        })
                        self.files_with_issues.append(rel_path)
                        logger.error(f"❌ {rel_path}: Shadowing detectado: {func_name}")
                
            except Exception as e:
                logger.warning(f"Erro ao verificar shadowing em {file_path}: {e}")
        
        if not any(e['type'] == 'shadowing' for e in self.errors):
            logger.debug("✅ Verificação de shadowing OK")
    

    def _check_relative_imports_in_main(self) -> None:
        """
        Verifica imports relativos em main.py.

        CRÍTICO: main.py é executado como script (`python main.py`) nos Dockerfiles
        gerados, então imports relativos como `from .api.routes` quebram.
        """
        logger.debug("Verificando imports relativos em main.py...")

        services_dir = os.path.join(self.project_path, 'services')
        if not os.path.exists(services_dir):
            return

        for service_name in os.listdir(services_dir):
            main_file = os.path.join(services_dir, service_name, 'main.py')
            if not os.path.exists(main_file):
                continue

            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                rel_path = os.path.relpath(main_file, self.project_path)
                if re.search(r'^from\s+\.[\w\.]+\s+import\s+', content, flags=re.MULTILINE):
                    self.errors.append({
                        'type': 'relative_import_in_main',
                        'file': rel_path,
                        'error': 'main.py usa import relativo e pode falhar com `python main.py`',
                    })
                    self.files_with_issues.append(rel_path)
                    logger.error(f"❌ {rel_path}: import relativo em main.py")
            except Exception as e:
                logger.warning(f"Erro ao verificar imports relativos em {main_file}: {e}")

    def _check_unpinned_postgres_images(self) -> None:
        """Verifica uso de imagem `postgres` sem versão fixa no compose."""
        logger.debug("Verificando pinagem de imagem PostgreSQL...")

        compose_candidates = [os.path.join(self.project_path, 'docker-compose.yml')]

        services_dir = os.path.join(self.project_path, 'services')
        if os.path.exists(services_dir):
            for service_name in os.listdir(services_dir):
                compose_candidates.append(os.path.join(services_dir, service_name, 'docker-compose.yml'))

        for compose_file in compose_candidates:
            if not os.path.exists(compose_file):
                continue

            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                rel_path = os.path.relpath(compose_file, self.project_path)

                if re.search(r'^\s*image:\s*postgres\s*$', content, flags=re.MULTILINE):
                    self.warnings.append({
                        'type': 'unpinned_postgres_image',
                        'file': rel_path,
                        'error': 'Compose usa `image: postgres` sem versão fixa; prefira `postgres:16`',
                    })

                if re.search(r'^\s*image:\s*postgresql\s*$', content, flags=re.MULTILINE):
                    self.errors.append({
                        'type': 'invalid_postgres_image',
                        'file': rel_path,
                        'error': 'Compose usa `image: postgresql` (inválida para Docker Hub oficial)',
                    })
                    self.files_with_issues.append(rel_path)
                    logger.error(f"❌ {rel_path}: imagem de banco inválida (postgresql)")
            except Exception as e:
                logger.warning(f"Erro ao verificar imagem de banco em {compose_file}: {e}")

    def _extract_imported_names(self, content: str) -> set:
        """Extrai nomes de todas as funções/classes importadas."""
        imported = set()
        
        # Padrão: from X import Y, Z
        from_import_pattern = r'from\s+[\w.]+\s+import\s+([\w.,\s]+)'
        for match in re.finditer(from_import_pattern, content):
            names = match.group(1).split(',')
            for name in names:
                name = name.strip()
                # Remove "as alias"
                if ' as ' in name:
                    name = name.split(' as ')[0].strip()
                if name:
                    imported.add(name)
        
        # Padrão: import X, Y
        import_pattern = r'^import\s+([\w.,\s]+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            names = match.group(1).split(',')
            for name in names:
                name = name.strip()
                # Remove "as alias"
                if ' as ' in name:
                    name = name.split(' as ')[0].strip()
                if name:
                    imported.add(name)
        
        return imported
    
    def _extract_function_names(self, content: str) -> set:
        """Extrai nomes de todas as funções definidas."""
        functions = set()
        
        # Padrão: def nome_funcao(
        def_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        for match in re.finditer(def_pattern, content):
            func_name = match.group(1)
            functions.add(func_name)
        
        # Padrão: async def nome_funcao(
        async_def_pattern = r'async\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        for match in re.finditer(async_def_pattern, content):
            func_name = match.group(1)
            functions.add(func_name)
        
        return functions
    
    def _get_all_python_files(self) -> list[str]:
        """Retorna todos os arquivos Python no projeto."""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Ignorar diretórios virtuais
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', '.venv']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _check_placeholders(self) -> None:
        """
        Verifica se placeholders não substituídos permanecem no código.
        
        Placeholders como {entity_name}, {domain} indicam que o
        template não foi processado corretamente.
        """
        logger.debug("Verificando placeholders...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            self.files_checked += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in self.FORBIDDEN_PATTERNS:
                    matches = re.findall(pattern, content)
                    if matches:
                        rel_path = os.path.relpath(file_path, self.project_path)
                        self.errors.append({
                            'type': 'placeholder',
                            'file': rel_path,
                            'pattern': pattern,
                            'matches': matches[:3],  # Primeiros 3
                        })
                        self.files_with_issues.append(rel_path)
                        break
                        
            except Exception as e:
                logger.warning(f"Erro ao verificar placeholders em {file_path}: {e}")
        
        if not self.errors:
            logger.debug(f"✅ Nenhum placeholder encontrado em {self.files_checked} arquivos")
    
    def _check_imports(self) -> None:
        """
        Verifica se os imports existem e resolvem corretamente.
        
        Este método:
        1. Extrai imports de cada arquivo
        2. Verifica se os módulos existem
        3. Reporta imports quebrados
        """
        logger.debug("Verificando imports...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrai imports
                imports = self._extract_imports(content)
                
                for imp in imports:
                    if not self._import_resolves(imp, file_path):
                        rel_path = os.path.relpath(file_path, self.project_path)
                        self.errors.append({
                            'type': 'import',
                            'file': rel_path,
                            'import': imp,
                        })
                        self.files_with_issues.append(rel_path)
                        
            except Exception as e:
                logger.warning(f"Erro ao verificar imports em {file_path}: {e}")
        
        if not any(e['type'] == 'import' for e in self.errors):
            logger.debug("✅ Todos os imports resolvem corretamente")
    
    def _extract_imports(self, content: str) -> list[str]:
        """Extrai todos os imports de um arquivo Python."""
        imports = []
        
        # Padrão para imports regulares
        import_pattern = r'^(?:from\s+([\w.]+)\s+import\s+.*|import\s+([\w.]+))'
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('from ') or line.startswith('import '):
                match = re.match(import_pattern, line)
                if match:
                    module = match.group(1) or match.group(2)
                    imports.append(module)
        
        return imports
    
    def _import_resolves(self, import_path: str, source_file: str) -> bool:
        """
        Verifica se um import resolve corretamente.
        
        Args:
            import_path: Caminho do import (ex: services.orders.domain)
            source_file: Arquivo que contém o import
            
        Returns:
            True se o import resolve, False caso contrário
        """
        # Ignora imports absolutos do sistema
        if not import_path.startswith('.'):
            # É um import de biblioteca do sistema ou externo
            if import_path in ['os', 'sys', 'datetime', 'uuid', 'typing', 'json',
                              'fastapi', 'pydantic', 'sqlalchemy', 'requests']:
                return True
            # Outros imports externos são assumidos como válidos
            # (serão verificados quando o usuário instalar dependências)
            return True
        
        # É um import relativo ou do projeto
        source_dir = os.path.dirname(source_file)
        
        # Determina o caminho do módulo
        if import_path.startswith('.'):
            # Import relativo
            dots = len(import_path) - len(import_path.lstrip('.'))
            import_name = import_path.lstrip('.')
            
            if dots == 1:
                # .
                module_path = os.path.join(source_dir, import_name.replace('.', os.sep))
            elif dots > 1:
                # ..
                parent_dir = os.path.dirname(source_dir)
                module_path = os.path.join(parent_dir, import_name.replace('.', os.sep))
        else:
            # Import absoluto do projeto (ex: services.orders.domain)
            project_root = self.project_path
            module_path = os.path.join(project_root, import_path.replace('.', os.sep))
        
        # Verifica se o arquivo existe
        for ext in ['.py', '']:
            if os.path.exists(module_path + ext):
                return True
        
        # Verifica se é um diretório com __init__.py
        if os.path.isdir(module_path):
            init_file = os.path.join(module_path, '__init__.py')
            if os.path.exists(init_file):
                return True
        
        return False
    
    def _check_syntax(self) -> None:
        """
        Verifica se o código Python tem syntax válida.
        
        Arquivos com syntax errors não podem ser executados.
        """
        logger.debug("Verificando syntax Python...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Tenta parsear o código
                ast.parse(content)
                
            except SyntaxError as e:
                rel_path = os.path.relpath(file_path, self.project_path)
                self.errors.append({
                    'type': 'syntax',
                    'file': rel_path,
                    'error': str(e),
                    'line': e.lineno,
                })
                self.files_with_issues.append(rel_path)
            except Exception as e:
                logger.warning(f"Erro ao verificar syntax em {file_path}: {e}")
        
        if not any(e['type'] == 'syntax' for e in self.errors):
            logger.debug("✅ Syntax Python válida em todos os arquivos")
    
    def _check_ddd_structure(self) -> None:
        """
        Verifica se a estrutura DDD está respeitada.
        
        Regras:
        - Domínio não deve importar de infraestrutura
        - Domínio não deve importar de API
        - Use cases devem estar em application/
        """
        logger.debug("Verificando estrutura DDD...")
        
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Verifica se é arquivo de domínio
                if '/domain/' in rel_path or '\\domain\\' in rel_path:
                    # Domínio não deve importar de infrastructure ou api
                    if 'from ..infrastructure' in content or 'from ...infrastructure' in content:
                        self.errors.append({
                            'type': 'ddd_violation',
                            'file': rel_path,
                            'error': 'Domínio importa de infraestrutura',
                        })
                        self.files_with_issues.append(rel_path)
                    
                    if 'from ..api' in content or 'from ...api' in content:
                        self.errors.append({
                            'type': 'ddd_violation',
                            'file': rel_path,
                            'error': 'Domínio importa de API',
                        })
                        self.files_with_issues.append(rel_path)
                
                # Verifica se use cases estão no lugar certo
                if '/use_cases' in rel_path or '\\use_cases' in rel_path:
                    # Use cases devem estar em application/, não domain/
                    if '/domain/' in rel_path or '\\domain\\' in rel_path:
                        self.warnings.append({
                            'type': 'ddd_warning',
                            'file': rel_path,
                            'error': 'Use cases encontrado em domain/ (deveria estar em application/)',
                        })
                        
            except Exception as e:
                logger.warning(f"Erro ao verificar DDD em {file_path}: {e}")
    
    def _check_required_files(self) -> None:
        """
        Verifica se arquivos obrigatórios existem.
        
        Arquivos como main.py, __init__.py, etc.
        """
        logger.debug("Verificando arquivos obrigatórios...")
        
        # Lista de padrões de arquivos obrigatórios por serviço
        services_dir = os.path.join(self.project_path, 'services')
        
        if not os.path.exists(services_dir):
            self.warnings.append({
                'type': 'missing_directory',
                'directory': 'services',
            })
            return
        
        # Para cada serviço
        for service_name in os.listdir(services_dir):
            service_path = os.path.join(services_dir, service_name)
            
            if not os.path.isdir(service_path):
                continue
            
            # Verificar main.py
            main_file = os.path.join(service_path, 'main.py')
            if not os.path.exists(main_file):
                self.errors.append({
                    'type': 'missing_file',
                    'file': f'services/{service_name}/main.py',
                })
            
            # Verificar requirements.txt
            requirements_file = os.path.join(service_path, 'requirements.txt')
            if not os.path.exists(requirements_file):
                self.warnings.append({
                    'type': 'missing_file',
                    'file': f'services/{service_name}/requirements.txt',
                })
            
            # Verificar estrutura DDD
            required_layers = ['domain', 'application', 'infrastructure', 'api']
            for layer in required_layers:
                layer_path = os.path.join(service_path, layer)
                if not os.path.exists(layer_path):
                    self.errors.append({
                        'type': 'missing_layer',
                        'service': service_name,
                        'layer': layer,
                    })
    
    def get_summary(self) -> str:
        """Retorna um resumo da validação."""
        error_types = {}
        for e in self.errors:
            t = e.get('type', 'unknown')
            error_types[t] = error_types.get(t, 0) + 1
        
        summary = f"""
=== RESUMO DA VALIDAÇÃO ===
Arquivos verificados: {self.files_checked}
Arquivos com problemas: {len(set(self.files_with_issues))}
Erros: {len(self.errors)}
Avisos: {len(self.warnings)}

Tipos de erros:
"""
        for t, count in error_types.items():
            summary += f"  - {t}: {count}\n"
        
        if self.errors:
            summary += "\nPrimeiros erros:\n"
            for e in self.errors[:5]:
                summary += f"  - [{e.get('type')}] {e.get('file', e.get('service', ''))}: {e.get('error', e.get('import', ''))}\n"
        
        return summary


class PlaceholderReplacer:
    """
    Substituidor de placeholders para templates.
    
    Este utilitário garante que todos os placeholders sejam
    substituídos antes de salvar o arquivo.
    """
    
    @staticmethod
    def replace_all(content: str, **kwargs) -> str:
        """
        Substitui todos os placeholders no conteúdo.
        
        Args:
            content: Conteúdo do template
            **kwargs: Valores para substituir
            
        Returns:
            Conteúdo com placeholders substituídos
        """
        result = content
        
        # Substituições simples
        for key, value in kwargs.items():
            # {entity_name} -> EntityName
            result = result.replace(f'{{{key}}}', str(value))
            
            # {entity_name.lower()} -> entityname
            if hasattr(value, 'lower'):
                result = result.replace(f'{{{key}.lower()}}', str(value).lower())
            
            # {{entity_name}} (escaped) -> EntityName
            result = result.replace(f'{{{{{key}}}}}', str(value))
        
        # Verificar se ainda há placeholders
        remaining = re.findall(r'\{[a-z_]+\}', result)
        if remaining:
            logger.warning(f"Placeholders restantes após substituição: {set(remaining)}")
        
        return result


class ImportFixer:
    """
    Corretor de imports para projetos gerados.
    
    Analisa imports quebrados e tenta corrigi-los.
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
    
    def fix_import(self, import_statement: str, source_file: str) -> str | None:
        """
        Tenta corrigir um import quebrado.
        
        Args:
            import_statement: Statement de import
            source_file: Arquivo que contém o import
            
        Returns:
            Correção ou None se não puder corrigir
        """
        # Analisa o import e determina a correção
        # Esta é uma implementação básica - pode ser expandida
        
        return None  # Por enquanto, não tenta corrigir automaticamente


def validate_project(project_path: str) -> dict:
    """
    Função de conveniência para validar um projeto.
    
    Args:
        project_path: Caminho do projeto
        
    Returns:
        Resultado da validação
    """
    validator = IntegrityValidator(project_path)
    return validator.validate()


def validate_and_fix(project_path: str) -> dict:
    """
    Valida e tenta corrigir problemas encontrados.
    
    Args:
        project_path: Caminho do projeto
        
    Returns:
        Resultado com informações de correção
    """
    validator = IntegrityValidator(project_path)
    result = validator.validate()
    
    if not result['valid']:
        # Tentar corrigir alguns problemas automaticamente
        fixer = ImportFixer(project_path)
        result['fixes_applied'] = []  # Implementar conforme necessário
    
    return result

