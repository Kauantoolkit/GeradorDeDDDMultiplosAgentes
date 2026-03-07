"""
Gerenciador de Arquivos
=======================

Responsável por todas as operações de arquivo no sistema:
- Criar arquivos e diretórios
- Ler arquivos
- Remover arquivos (para rollback)
- Listar estrutura gerada
"""

import os
import shutil
from pathlib import Path
from typing import Any
from loguru import logger


class FileManager:
    """
    Gerencia operações de arquivo para o sistema de agentes.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Inicializa o gerenciador de arquivos.
        
        Args:
            base_path: Caminho base para operações
        """
        self.base_path = Path(base_path)
        self._base_name = self.base_path.name
        logger.info(f"FileManager inicializado em: {self.base_path}")

    def _normalize_relative_path(self, file_path: str) -> Path:
        """
        Normaliza caminhos vindos do LLM para evitar duplicação de diretórios.

        Exemplos corrigidos automaticamente:
        - generated/services/x.py -> services/x.py (quando base_path == generated)
        - ./services/x.py -> services/x.py
        - /services/x.py -> services/x.py
        """
        normalized = file_path.replace('\\', '/').strip()
        normalized = normalized.lstrip('./').lstrip('/')

        parts = [part for part in normalized.split('/') if part and part != '.']

        # Remove prefixo duplicado quando o LLM devolve caminho já incluindo base_path
        if self._base_name and parts and parts[0] == self._base_name:
            parts = parts[1:]

        return Path(*parts) if parts else Path(file_path)
    
    def create_file(self, file_path: str, content: str) -> bool:
        """
        Cria um arquivo com o conteúdo especificado.
        
        Args:
            file_path: Caminho do arquivo (relativo ao base_path)
            content: Conteúdo do arquivo
            
        Returns:
            True se criado com sucesso, False caso contrário
        """
        try:
            safe_path = self._normalize_relative_path(file_path)
            full_path = self.base_path / safe_path
            
            # Cria diretórios pais se não existirem
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escreve o conteúdo
            full_path.write_text(content, encoding='utf-8')
            
            logger.info(f"Arquivo criado: {safe_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar arquivo {file_path}: {e}")
            return False
    
    def read_file(self, file_path: str) -> str | None:
        """
        Lê o conteúdo de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Conteúdo do arquivo ou None se erro
        """
        ##problematico, as llms ficam mandando de uma pra outra diretórios e quando n bate da erro aqui, tem um problema sério de inconsistencia
        #entre as partes hard coded da aplicação e as gerenciadas por llm
        try:
            full_path = self.base_path / self._normalize_relative_path(file_path)
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Deleta um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            full_path = self.base_path / self._normalize_relative_path(file_path)
            
            if full_path.exists():
                full_path.unlink()
                logger.info(f"Arquivo removido: {file_path}")
                return True
            else:
                logger.warning(f"Arquivo não encontrado: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo {file_path}: {e}")
            return False
    
    def delete_directory(self, dir_path: str) -> bool:
        """
        Deleta um diretório e todo seu conteúdo.
        
        Args:
            dir_path: Caminho do diretório
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            full_path = self.base_path / dir_path
            
            if full_path.exists() and full_path.is_dir():
                shutil.rmtree(full_path)
                logger.info(f"Diretório removido: {dir_path}")
                return True
            else:
                logger.warning(f"Diretório não encontrado: {dir_path}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao deletar diretório {dir_path}: {e}")
            return False
    
    def list_files(self, dir_path: str = ".") -> list[str]:
        """
        Lista todos os arquivos em um diretório.
        
        Args:
            dir_path: Caminho do diretório
            
        Returns:
            Lista de caminhos de arquivos
        """
        try:
            full_path = self.base_path / dir_path
            files = []
            
            for root, _, filenames in os.walk(full_path):
                for filename in filenames:
                    full_file_path = Path(root) / filename
                    relative_path = full_file_path.relative_to(self.base_path)
                    files.append(str(relative_path))
            
            return files
            
        except Exception as e:
            logger.error(f"Erro ao listar arquivos em {dir_path}: {e}")
            return []
    
    def create_structure(self, structure: dict[str, str]) -> list[str]:
        """
        Cria uma estrutura completa de arquivos.
        
        Args:
            structure: Dicionário com {caminho: conteúdo}
            
        Returns:
            Lista de arquivos criados com sucesso
        """
        created_files = []
        
        for file_path, content in structure.items():
            if self.create_file(file_path, content):
                created_files.append(file_path)
        
        logger.info(f"Estrutura criada: {len(created_files)} arquivos")
        return created_files
    
    def rollback_files(self, files: list[str]) -> dict[str, bool]:
        """
        Remove uma lista de arquivos (para rollback).
        
        Args:
            files: Lista de caminhos de arquivos
            
        Returns:
            Dicionário com {caminho: status}
        """
        results = {}
        
        for file_path in files:
            results[file_path] = self.delete_file(file_path)
        
        # Tenta remover diretórios vazios
        dirs_to_check = set()
        for file_path in files:
            parent = Path(file_path).parent
            if parent != Path('.'):
                dirs_to_check.add(str(parent))
        
        for dir_path in dirs_to_check:
            try:
                full_path = self.base_path / dir_path
                if full_path.exists() and not any(full_path.iterdir()):
                    full_path.rmdir()
                    logger.info(f"Diretório vazio removido: {dir_path}")
            except Exception as e:
                pass  # Não é crítico se falhar
        
        return results
    
    def get_structure_tree(self, dir_path: str = ".") -> str:
        """
        Retorna uma representação em árvore da estrutura de diretórios.
        
        Args:
            dir_path: Caminho do diretório
            
        Returns:
            String com a estrutura em árvore
        """
        full_path = self.base_path / dir_path
        
        if not full_path.exists():
            return "Diretório não existe"
        
        tree = []
        
        def _build_tree(path: Path, prefix: str = "", is_last: bool = True):
            """Função recursiva para construir a árvore."""
            if path.is_file():
                tree.append(f"{prefix}📄 {path.name}")
                return
            
            # É diretório
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            
            for i, item in enumerate(items):
                is_last_item = i == len(items) - 1
                current_prefix = "└── " if is_last_item else "├── "
                tree.append(f"{prefix}{current_prefix}{'📁 ' if item.is_dir() else '📄 '}{item.name}")
                
                if item.is_dir():
                    extension = "    " if is_last_item else "│   "
                    _build_tree(item, prefix + extension, is_last_item)
        
        tree.append(f"📁 {full_path.name}")
        _build_tree(full_path)
        
        return "\n".join(tree)

    def find_file_with_patterns(self, base_dir: str, filename_patterns: list[str]) -> str | None:
        """
        Encontra um arquivo verificando múltiplos padrões de nome.
        
        Útil para encontrar arquivos de entidade que podem ter nomes diferentes
        dependendo de como foram gerados pelo LLM.
        
        Args:
            base_dir: Diretório base (ex: "services/order_service/domain")
            filename_patterns: Lista de padrões de nome (ex: ["order_entities.py", "entities.py"])
            
        Returns:
            Caminho do primeiro arquivo encontrado, ou None
        """
        for pattern in filename_patterns:
            full_path = self.base_path / base_dir / pattern
            if full_path.exists():
                return f"{base_dir}/{pattern}"
        
        return None
    
    def find_entity_file(self, service_name: str) -> str | None:
        """
        Encontra o arquivo de entidade de um serviço tentando múltiplos padrões.

        Args:
            service_name: Nome do serviço (ex: "order_service")
            
        Returns:
            Caminho do arquivo de entidade encontrado, ou None
        """
        # Normalizar nome do serviço
        normalized_service = service_name.lower().replace('-', '_')
        
        # Tentar derivar domain a partir do service_name
        domain = normalized_service
        if normalized_service.endswith('_service'):
            domain = normalized_service[:-8]  # Remove "_service"
        
        # Padrões de busca para arquivos de entidade
        patterns = [
            f"services/{service_name}/domain/{domain}_entities.py",
            f"services/{service_name}/domain/{normalized_service}_entities.py",
            f"services/{service_name}/domain/entities.py",
            f"domain/{domain}_entities.py",
            f"domain/entities.py",
        ]
        
        for pattern in patterns:
            full_path = self.base_path / pattern
            if full_path.exists():
                return pattern
        
        return None

    def find_file_with_flexible_search(self, file_path: str) -> str | None:
        """
        Encontra um arquivo tentando múltiplos padrões de caminho.
        
        Problema: O LLM pode retornar caminhos inconsistentes entre agentes.
        Exemplo: O Executor gera 'services/order_service/main.py' mas o FixAgent
        tenta acessar 'order_service/main.py' ou 'services/order_service/domain/entities.py'
        
        Esta função tenta normalizar e encontrar o arquivo em múltiplos locais.

        Args:
            file_path: Caminho original retornado pelo LLM
            
        Returns:
            Caminho válido do arquivo encontrado, ou None
        """
        # CORREÇÃO CRÍTICA: Primeiro normalizar o caminho
        # Remover prefixos duplicados como "ifoodclone3/" se já estamos no diretório
        normalized = file_path.replace('\\', '/').strip()
        
        # Remove prefixos de projeto conhecidos (ex: linkedinclone/, myproject/, ifoodclone3/, etc)
        # Isso resolve o problema de caminhos como "ifoodclone3/services/..."
        normalized = self._strip_project_prefix(normalized)
        
        # Primeiro, tenta o caminho original normalizado
        if (self.base_path / normalized).exists():
            return normalized
        
        # Tenta sem prefixo services/
        if normalized.startswith('services/'):
            without_services = normalized[9:]  # Remove 'services/'
            if (self.base_path / without_services).exists():
                return without_services
        
        # Tenta com prefixo services/
        if not normalized.startswith('services/') and not normalized.startswith('frontend/'):
            with_services = f"services/{normalized}"
            if (self.base_path / with_services).exists():
                return with_services
        
        # Tenta normalizar hífen para underscore (common case: order-service vs order_service)
        if '-' in normalized:
            with_underscore = normalized.replace('-', '_')
            if (self.base_path / with_underscore).exists():
                return with_underscore
        
        # Tenta o inverso: underscore para hífen
        if '_' in normalized:
            with_hyphen = normalized.replace('_', '-')
            if (self.base_path / with_hyphen).exists():
                return with_hyphen
        
        # Tenta buscar em services/*/domain/
        if '/domain/' in normalized or '/application/' in normalized or '/api/' in normalized:
            return self._find_in_all_services(normalized)
        
        # Busca genérica em todo o projeto pelo nome do arquivo
        return self._find_file_anywhere(normalized)
    
    def _strip_project_prefix(self, file_path: str) -> str:
        """
        Remove o prefixo do diretório do projeto do caminho.
        
        O problema é que o LLM às vezes retorna caminhos como:
        - "linkedinclone/services/user_service/main.py"
        - "myproject/domain/entities.py"
        
        Mas o FileManager já está configurado com base_path="linkedinclone"
        então devemos usar apenas "services/user_service/main.py"
        
        Args:
            file_path: Caminho com potencial prefixo
            
        Returns:
            Caminho sem o prefixo do projeto
        """
        # Obtém o nome do diretório base
        base_name = self.base_path.name
        
        # Se o caminho começa com o nome do projeto, remove
        if file_path.startswith(f"{base_name}/"):
            return file_path[len(base_name) + 1:]
        
        # Tenta encontrar e remover qualquer prefixo de diretório que não seja válido
        parts = file_path.split('/')
        
        # Lista de prefixes válidos Known valid prefixes
        valid_prefixes = ['services', 'frontend', 'api', 'domain', 'infrastructure', 
                          'application', 'linkedinclone', 'examples', 'tests', 'logs']
        
        # Se a primeira parte não é um prefixo válido, tenta remover
        if parts and parts[0] not in valid_prefixes:
            # Pode ser um prefixo de projeto, tenta remover
            # Mas verifica se o resto do caminho faz sentido
            remaining = '/'.join(parts[1:])
            if remaining.startswith('services/') or remaining.startswith('frontend/'):
                return remaining
        
        return file_path
    
    def _find_in_all_services(self, path_pattern: str) -> str | None:
        """
        Busca um arquivo em todos os serviços.
        
        Args:
            path_pattern: Padrão do caminho (ex: 'domain/entities.py')
            
        Returns:
            Caminho encontrado ou None
        """
        services_dir = self.base_path / 'services'
        if not services_dir.exists():
            return None
        
        # Extrai a parte do caminho após domain/application/api
        parts = path_pattern.split('/')
        try:
            layer_idx = next(i for i, p in enumerate(parts) if p in ['domain', 'application', 'infrastructure', 'api'])
            filename = '/'.join(parts[layer_idx:])
        except StopIteration:
            filename = path_pattern
        
        # Busca em todos os serviços
        for service_dir in services_dir.iterdir():
            if not service_dir.is_dir():
                continue
            
            candidate = service_dir / filename
            if candidate.exists():
                return str(candidate.relative_to(self.base_path))
            
            # Tenta com _services removido
            if service_dir.name.endswith('_service'):
                alt_service_name = service_dir.name[:-8]
                alt_candidate = services_dir / alt_service_name / filename
                if alt_candidate.exists():
                    return str(alt_candidate.relative_to(self.base_path))
        
        return None
    
    def _find_file_anywhere(self, filename: str) -> str | None:
        """
        Busca um arquivo em qualquer lugar do projeto pelo nome.
        
        Útil quando não sabemos o caminho exato, apenas o nome do arquivo.
        
        Args:
            filename: Nome do arquivo (ex: 'entities.py', 'user_entities.py')
            
        Returns:
            Caminho completo do arquivo encontrado, ou None
        """
        # Obtém apenas o nome do arquivo se um caminho for passado
        just_filename = filename.split('/')[-1]
        
        # Busca em todo o projeto
        for root, _, filenames in os.walk(self.base_path):
            if just_filename in filenames:
                full_path = Path(root) / just_filename
                return str(full_path.relative_to(self.base_path))
        
        # Se não encontrou pelo nome exato, tenta encontrar arquivos similares
        # Remove extensão e tenta encontrar arquivos que contenham o nome
        base_name = just_filename.replace('.py', '')
        
        # Tenta encontrar variações de nome (ex: user_entities -> users_entities)
        variations = [
            base_name,
            base_name.replace('_', ''),
            base_name.replace('ies', 'y'),  # entities -> entity
            base_name.replace('y', 'ies'),  # entity -> entities
        ]
        
        for root, _, filenames in os.walk(self.base_path):
            for f in filenames:
                f_base = f.replace('.py', '')
                for var in variations:
                    if var in f_base or f_base in var:
                        full_path = Path(root) / f
                        return str(full_path.relative_to(self.base_path))
        
        return None
    
    def read_file_flexible(self, file_path: str) -> str | None:
        """
        Lê um arquivo tentando múltiplos padrões de caminho.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Conteúdo do arquivo ou None se não encontrado
        """
        # Primeiro tenta caminho direto
        content = self.read_file(file_path)
        if content is not None:
            return content
        
        # Tenta com busca flexível
        found_path = self.find_file_with_flexible_search(file_path)
        if found_path:
            return self.read_file(found_path)
        
        return None
    
    def normalize_path(self, file_path: str) -> str:
        """
        Normaliza um caminho para o formato padrão do projeto.
        
        Args:
            file_path: Caminho a normalizar
            
        Returns:
            Caminho normalizado
        """
        normalized = file_path.replace('\\', '/').strip()
        
        # Remove prefixos duplicados
        parts = [p for p in normalized.split('/') if p and p != '.']
        
        # Remove base_name se estiver no início (evita duplicação)
        if self._base_name and parts and parts[0] == self._base_name:
            parts = parts[1:]
        
        # Garante que serviços têm o prefixo services/
        if parts and not parts[0] in ['services', 'frontend', 'api', 'domain', 'infrastructure', 'application']:
            # Verificar se é um nome de serviço válido
            if len(parts) >= 2 and parts[0] == 'services':
                pass  # Já tem prefixo
            elif len(parts) >= 1:
                # Assume que é um serviço se tem apenas 1-2 níveis
                if len(parts) <= 2:
                    parts.insert(0, 'services')
        
        return '/'.join(parts)

