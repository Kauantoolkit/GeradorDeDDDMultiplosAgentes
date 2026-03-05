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
