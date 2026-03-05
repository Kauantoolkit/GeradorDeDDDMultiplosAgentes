"""
Tests - product_domain Domain
======================
Testes unitários para entidades de product_domain.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestProduct:
    """Testes para Product."""
    
    def test_create_product(self):
        """Testa criação de Product."""
        from ..services.service.domain import Product
        
        entity = Product.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_product(self):
        """Testa atualização de Product."""
        from ..services.service.domain import Product
        
        entity = Product.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Product
        
        entity = Product.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
