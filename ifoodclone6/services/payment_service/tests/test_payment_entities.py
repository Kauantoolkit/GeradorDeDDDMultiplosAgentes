"""
Tests - payment Domain
======================
Testes unitários para entidades de payment.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestPayment:
    """Testes para Payment."""
    
    def test_create_payment(self):
        """Testa criação de Payment."""
        from ..services.service.domain import Payment
        
        entity = Payment.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_payment(self):
        """Testa atualização de Payment."""
        from ..services.service.domain import Payment
        
        entity = Payment.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Payment
        
        entity = Payment.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
