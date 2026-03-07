"""
Tests - restaurant Domain
======================
Testes unitários para entidades de restaurant.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestRestaurant:
    """Testes para Restaurant."""
    
    def test_create_restaurant(self):
        """Testa criação de Restaurant."""
        from ..services.service.domain import Restaurant
        
        entity = Restaurant.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_restaurant(self):
        """Testa atualização de Restaurant."""
        from ..services.service.domain import Restaurant
        
        entity = Restaurant.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Restaurant
        
        entity = Restaurant.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
