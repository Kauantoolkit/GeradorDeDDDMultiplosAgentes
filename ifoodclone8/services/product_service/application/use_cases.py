"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio product.
"""

from uuid import UUID
from domain.product_entities import Product


class CreateProductUseCase:
    """Use case para criar Product."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Product:
        entity = Product.create(**data)
        return await self.repository.save(entity)


class GetProductByIdUseCase:
    """Use case para buscar Product por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Product | None:
        return await self.repository.get_by_id(id)


class UpdateProductUseCase:
    """Use case para atualizar Product."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Product | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteProductUseCase:
    """Use case para deletar Product."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
