"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio produtos.
"""

from uuid import UUID
from domain.produtos_entities import ProdutosEntity


class CreateProdutosEntityUseCase:
    """Use case para criar ProdutosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> ProdutosEntity:
        entity = ProdutosEntity.create(**data)
        return await self.repository.save(entity)


class GetProdutosEntityByIdUseCase:
    """Use case para buscar ProdutosEntity por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> ProdutosEntity | None:
        return await self.repository.get_by_id(id)


class UpdateProdutosEntityUseCase:
    """Use case para atualizar ProdutosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> ProdutosEntity | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteProdutosEntityUseCase:
    """Use case para deletar ProdutosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
