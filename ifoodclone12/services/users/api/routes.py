"""
Routes - API Layer
==================
Definição de rotas para users.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import UserDTO, CreateUserDTO, UpdateUserDTO
from application.use_cases import (
    CreateUserUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
)
from infrastructure.repositories import UserRepositoryImpl
from api.schemas import UserSchema, CreateUserSchema
from api.controllers import get_user_repository


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: CreateUserSchema,
    repository: UserRepositoryImpl = Depends(get_user_repository)
):
    """Cria um novo User."""
    use_case = CreateUserUseCase(repository)
    entity = await use_case.execute(data.dict())
    return UserSchema.from_orm(entity)


@router.get("/users", response_model=List[UserSchema])
async def list_users(
    repository: UserRepositoryImpl = Depends(get_user_repository)
):
    """Lista todos os Users."""
    entities = await repository.get_all()
    return [UserSchema.from_orm(e) for e in entities]


@router.get("/users/{id}", response_model=UserSchema)
async def get_user(
    id: UUID,
    repository: UserRepositoryImpl = Depends(get_user_repository)
):
    """Busca User por ID."""
    use_case = GetUserByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="User não encontrado")
    return UserSchema.from_orm(entity)


@router.put("/users/{id}", response_model=UserSchema)
async def update_user(
    id: UUID,
    data: UpdateUserDTO,
    repository: UserRepositoryImpl = Depends(get_user_repository)
):
    """Atualiza User."""
    use_case = UpdateUserUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="User não encontrado")
    return UserSchema.from_orm(entity)


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: UUID,
    repository: UserRepositoryImpl = Depends(get_user_repository)
):
    """Deleta User."""
    use_case = DeleteUserUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="User não encontrado")
