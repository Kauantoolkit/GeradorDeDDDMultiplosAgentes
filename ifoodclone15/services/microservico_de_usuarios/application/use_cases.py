"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio usuarios.
"""

from uuid import UUID
from domain.usuarios_entities import UsuariosEntity


class CreateUsuariosEntityUseCase:
    """Use case para criar UsuariosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> UsuariosEntity:
        entity = UsuariosEntity.create(**data)
        return await self.repository.save(entity)


class GetUsuariosEntityByIdUseCase:
    """Use case para buscar UsuariosEntity por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> UsuariosEntity | None:
        return await self.repository.get_by_id(id)


class UpdateUsuariosEntityUseCase:
    """Use case para atualizar UsuariosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> UsuariosEntity | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteUsuariosEntityUseCase:
    """Use case para deletar UsuariosEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
