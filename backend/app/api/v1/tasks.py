"""Роутер задач скрапинга — CRUD, запуск, preview, переключение активности.

Юзер видит только свои задачи, если не админ.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.scraping_task import (
    PreviewRequest,
    PreviewResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.schemas.task_run import TaskRunResponse
from app.services import run_service, task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Элементов на страницу"),
    search: str | None = Query(None, description="Поиск по названию или URL"),
    is_active: bool | None = Query(None, description="Фильтр по активности"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список задач текущего юзера с пагинацией и фильтрами."""
    return await task_service.list_tasks(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        search=search,
        is_active=is_active,
        db=db,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить задачу по ID — только свои."""
    return await task_service.get_task(task_id, current_user.id, db)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую задачу скрапинга с полями извлечения."""
    return await task_service.create_task(current_user.id, data, db)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить задачу — можно частично, поля заменяются целиком."""
    return await task_service.update_task(task_id, current_user.id, data, db)


@router.delete("/{task_id}")
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить задачу — каскадом удалятся все запуски и результаты."""
    return await task_service.delete_task(task_id, current_user.id, db)


@router.post("/{task_id}/run", response_model=TaskRunResponse)
async def run_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Запустить задачу вручную — полный пайплайн: скрапинг, диф, AI, уведомления."""
    # проверяем что задача принадлежит юзеру
    await task_service.get_task(task_id, current_user.id, db)
    return await run_service.execute_task(task_id, db)


@router.post("/preview", response_model=PreviewResponse)
async def preview_task(data: PreviewRequest):
    """Предпросмотр — пробный скрапинг без сохранения, для настройки селекторов."""
    return await run_service.preview_task(data)


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Переключить активность задачи — active/inactive."""
    return await task_service.toggle_task(task_id, current_user.id, db)
