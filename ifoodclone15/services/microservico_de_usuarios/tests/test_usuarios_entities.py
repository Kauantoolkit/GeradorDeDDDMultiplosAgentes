"""
Tests - usuarios Domain
======================
Testes unitários para entidades de usuarios.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestUsuariosEntity:
    """Testes para UsuariosEntity."""
    
    def test_create_usuariosentity(self):
        """Testa criação de UsuariosEntity."""
        from ..services.service.domain import UsuariosEntity
        
        entity = UsuariosEntity.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_usuariosentity(self):
        """Testa atualização de UsuariosEntity."""
        from ..services.service.domain import UsuariosEntity
        
        entity = UsuariosEntity.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import UsuariosEntity
        
        entity = UsuariosEntity.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
