"""
Tests - notification Domain
======================
Testes unitários para entidades de notification.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestNotification:
    """Testes para Notification."""
    
    def test_create_notification(self):
        """Testa criação de Notification."""
        from ..services.service.domain import Notification
        
        entity = Notification.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_notification(self):
        """Testa atualização de Notification."""
        from ..services.service.domain import Notification
        
        entity = Notification.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Notification
        
        entity = Notification.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
