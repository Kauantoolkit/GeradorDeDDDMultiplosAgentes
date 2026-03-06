"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio pedidos.
"""

from uuid import UUID
from domain.pedidos_entities import PedidosEntity


class CreatePedidosEntityUseCase:
    """Use case para criar PedidosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> PedidosEntity:
        entity = PedidosEntity.create(**data)
        return await self.repository.save(entity)


class GetPedidosEntityByIdUseCase:
    """Use case para buscar PedidosEntity por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> PedidosEntity | None:
        return await self.repository.get_by_id(id)


class UpdatePedidosEntityUseCase:
    """Use case para atualizar PedidosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> PedidosEntity | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeletePedidosEntityUseCase:
    """Use case para deletar PedidosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
