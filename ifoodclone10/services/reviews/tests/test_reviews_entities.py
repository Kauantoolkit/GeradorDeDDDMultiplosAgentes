"""
Tests - reviews Domain
======================
Testes unitários para entidades de reviews.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestReview:
    """Testes para Review."""
    
    def test_create_review(self):
        """Testa criação de Review."""
        from ..services.service.domain import Review
        
        entity = Review.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_review(self):
        """Testa atualização de Review."""
        from ..services.service.domain import Review
        
        entity = Review.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Review
        
        entity = Review.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
