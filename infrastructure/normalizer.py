"""
Normalizer - Utilitário de Normalização de Nomes
================================================

Este módulo fornece funções para normalizar nomes de serviços,
domínios e entidades para garantir que sejam válidos em Python.

PROBLEMAS RESOLVIDOS:
- Hífens em nomes de serviços (auth-service → auth_service)
- Nomes inválidos para módulos Python
- Consistência na nomenclatura
"""

import re
from typing import Any


class ServiceNameNormalizer:
    """
    Normalizador de nomes de serviços.
    
    Garante que todos os nomes de serviços sejam válidos
    como nomes de módulos Python (sem hífen, etc).
    """
    
    @staticmethod
    def normalize(service_name: str) -> str:
        """
        Normaliza nome de serviço para Python válido.
        
        Args:
            service_name: Nome com possível hífen (ex: "auth-service")
            
        Returns:
            Nome normalizado com underscore (ex: "auth_service")
            
        Examples:
            >>> ServiceNameNormalizer.normalize("auth-service")
            'auth_service'
            >>> ServiceNameNormalizer.normalize("user-service")
            'user_service'
            >>> ServiceNameNormalizer.normalize("auth_service")
            'auth_service'
        """
        if not service_name:
            return service_name
            
        # Substitui hífen por underscore
        result = service_name.replace('-', '_')
        
        # Remove caracteres inválidos para identificadores Python
        result = re.sub(r'[^a-zA-Z0-9_]', '', result)
        
        # Garante que não comece com número
        if result and result[0].isdigit():
            result = '_' + result
            
        return result
    
    @staticmethod
    def is_valid(service_name: str) -> bool:
        """
        Verifica se nome de serviço é válido em Python.
        
        Args:
            service_name: Nome a verificar
            
        Returns:
            True se válido, False caso contrário
        """
        if not service_name:
            return False
            
        # Padrão para identificador Python válido
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, service_name))
    
    @staticmethod
    def validate(service_name: str) -> tuple[bool, str]:
        """
        Valida e normaliza nome de serviço.
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Tupla (foi_normalizado, nome_normalizado)
        """
        original = service_name
        normalized = ServiceNameNormalizer.normalize(service_name)
        
        # Verifica se houve mudança (hífen encontrado)
        was_normalized = original != normalized
        
        return was_normalized, normalized


class DomainNameNormalizer:
    """
    Normalizador de nomes de domínio.
    """
    
    @staticmethod
    def normalize(domain_name: str) -> str:
        """
        Normaliza nome de domínio para Python válido.
        
        Args:
            domain_name: Nome do domínio
            
        Returns:
            Nome normalizado
        """
        if not domain_name:
            return domain_name
            
        # Substitui hífen por underscore
        result = domain_name.replace('-', '_')
        
        # Garante lowercase
        result = result.lower()
        
        return result
    
    @staticmethod
    def is_valid(domain_name: str) -> bool:
        """Verifica se nome de domínio é válido."""
        if not domain_name:
            return False
        # Apenas letras, números e underscore
        return bool(re.match(r'^[a-zA-Z0-9_]+$', domain_name))


class EntityNameNormalizer:
    """
    Normalizador de nomes de entidades.
    """
    
    @staticmethod
    def normalize(entity_name: str) -> str:
        """
        Normaliza nome de entidade para Python válido.
        
        Args:
            entity_name: Nome da entidade
            
        Returns:
            Nome normalizado (PascalCase)
        """
        if not entity_name:
            return entity_name
            
        # Remove caracteres especiais
        result = re.sub(r'[^a-zA-Z0-9]', '', entity_name)
        
        # Garante que primeira letra seja maiúscula
        if result:
            result = result[0].upper() + result[1:]
            
        return result
    
    @staticmethod
    def to_snake_case(entity_name: str) -> str:
        """
        Converte nome de entidade para snake_case.
        
        Args:
            entity_name: Nome em PascalCase
            
        Returns:
            Nome em snake_case
        """
        if not entity_name:
            return entity_name
            
        # PascalCase to snake_case
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', entity_name)
        return snake.lower()
    
    @staticmethod
    def to_kebab_case(entity_name: str) -> str:
        """
        Converte nome de entidade para kebab-case.
        
        Args:
            entity_name: Nome em PascalCase
            
        Returns:
            Nome em kebab-case
        """
        snake = EntityNameNormalizer.to_snake_case(entity_name)
        return snake.replace('_', '-')


def normalize_service_name(name: str) -> str:
    """
    Função de conveniência para normalizar nome de serviço.
    
    Alias para ServiceNameNormalizer.normalize()
    
    Args:
        name: Nome do serviço
        
    Returns:
        Nome normalizado
    """
    return ServiceNameNormalizer.normalize(name)


def validate_and_normalize_service_name(name: str) -> tuple[bool, str]:
    """
    Valida e normaliza nome de serviço.
    
    Args:
        name: Nome do serviço
        
    Returns:
        Tupla (foi_normalizado, nome_normalizado)
    """
    return ServiceNameNormalizer.validate(name)


# ============================================================
# VALIDAÇÕES DE INTEGRIDADE
# ============================================================

class NameValidator:
    """
    Validador de nomes para garantir código Python válido.
    """
    
    # Caracteres válidos para identificadores Python
    VALID_IDENTIFIER_PATTERN = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    
    @staticmethod
    def is_valid_python_identifier(name: str) -> bool:
        """Verifica se nome é identificador Python válido."""
        if not name:
            return False
        return bool(re.match(NameValidator.VALID_IDENTIFIER_PATTERN, name))
    
    @staticmethod
    def has_hyphen(name: str) -> bool:
        """Verifica se nome contém hífen."""
        return '-' in name
    
    @staticmethod
    def validate_import_path(import_path: str) -> tuple[bool, str]:
        """
        Valida caminho de import.
        
        Args:
            import_path: Caminho de import (ex: "services.auth-service.api")
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not import_path:
            return False, "Caminho vazio"
            
        # Verifica se contém hífen
        if '-' in import_path:
            return False, f"Import contém hífen inválido: {import_path}"
            
        # Verifica se cada parte é identificador válido
        parts = import_path.split('.')
        for part in parts:
            if not NameValidator.is_valid_python_identifier(part):
                return False, f"Parte inválida no import: {part}"
                
        return True, ""
    
    @staticmethod
    def validate_service_directory(dir_name: str) -> tuple[bool, str]:
        """
        Valida nome de diretório de serviço.
        
        Args:
            dir_name: Nome do diretório
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not dir_name:
            return False, "Nome de diretório vazio"
            
        if NameValidator.has_hyphen(dir_name):
            return False, f"Diretório contém hífen inválido: {dir_name}"
            
        if not NameValidator.is_valid_python_identifier(dir_name):
            return False, f"Diretório não é identificador Python válido: {dir_name}"
            
        return True, ""


def validate_service_structure(service_name: str) -> dict:
    """
    Valida estrutura completa de nome de serviço.
    
    Args:
        service_name: Nome do serviço
        
    Returns:
        Dicionário com resultados da validação
    """
    result = {
        'original': service_name,
        'has_hyphen': NameValidator.has_hyphen(service_name),
        'is_valid': NameValidator.is_valid_python_identifier(service_name),
        'normalized': ServiceNameNormalizer.normalize(service_name),
        'needs_normalization': service_name != ServiceNameNormalizer.normalize(service_name),
    }
    
    return result

