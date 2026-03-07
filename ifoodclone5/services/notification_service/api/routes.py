"""
Routes - API Layer
==================
Definição de rotas para notification_service.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import NotificationDTO, CreateNotificationDTO, UpdateNotificationDTO
from application.use_cases import (
    CreateNotificationUseCase,
    GetNotificationByIdUseCase,
    UpdateNotificationUseCase,
    DeleteNotificationUseCase,
)
from infrastructure.repositories import NotificationRepositoryImpl
from api.schemas import NotificationSchema, CreateNotificationSchema
from api.controllers import get_notification_repository


router = APIRouter(prefix="/api/notification_service", tags=["notification_service"])


@router.post("/notifications", response_model=NotificationSchema, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: CreateNotificationSchema,
    repository: NotificationRepositoryImpl = Depends(get_notification_repository)
):
    """Cria um novo Notification."""
    use_case = CreateNotificationUseCase(repository)
    entity = await use_case.execute(data.dict())
    return NotificationSchema.from_orm(entity)


@router.get("/notifications", response_model=List[NotificationSchema])
async def list_notifications(
    repository: NotificationRepositoryImpl = Depends(get_notification_repository)
):
    """Lista todos os Notifications."""
    entities = await repository.get_all()
    return [NotificationSchema.from_orm(e) for e in entities]


@router.get("/notifications/{id}", response_model=NotificationSchema)
async def get_notification(
    id: UUID,
    repository: NotificationRepositoryImpl = Depends(get_notification_repository)
):
    """Busca Notification por ID."""
    use_case = GetNotificationByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Notification} não encontrado")
    return NotificationSchema.from_orm(entity)


@router.put("/notifications/{id}", response_model=NotificationSchema)
async def update_notification(
    id: UUID,
    data: UpdateNotificationDTO,
    repository: NotificationRepositoryImpl = Depends(get_notification_repository)
):
    """Atualiza Notification."""
    use_case = UpdateNotificationUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Notification} não encontrado")
    return NotificationSchema.from_orm(entity)


@router.delete("/notifications/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    id: UUID,
    repository: NotificationRepositoryImpl = Depends(get_notification_repository)
):
    """Deleta Notification."""
    use_case = DeleteNotificationUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"{Notification} não encontrado")
