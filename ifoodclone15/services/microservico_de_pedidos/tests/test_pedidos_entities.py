"""
Tests - pedidos Domain
======================
Testes unitários para entidades de pedidos.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestPedidosEntity:
    """Testes para PedidosEntity."""
    
    def test_create_pedidosentity(self):
        """Testa criação de PedidosEntity."""
        from ..services.service.domain import PedidosEntity
        
        entity = PedidosEntity.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_pedidosentity(self):
        """Testa atualização de PedidosEntity."""
        from ..services.service.domain import PedidosEntity
        
        entity = PedidosEntity.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import PedidosEntity
        
        entity = PedidosEntity.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
