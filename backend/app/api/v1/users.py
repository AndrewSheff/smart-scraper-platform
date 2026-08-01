"""Роутер управления юзерами — только для админов.

CRUD пользователей, блокировка, создание с временным паролем.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Элементов на страницу"),
    search: str | None = Query(None, description="Поиск по имени или email"),
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Список пользователей с пагинацией и поиском — только для админов."""
    return await user_service.list_users(page, per_page, search, db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Получить пользователя по ID — только для админов."""
    return await user_service.get_user(user_id, db)


@router.post("", status_code=201)
async def create_user(
    data: UserCreate,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Создать пользователя — если пароль не указан, генерится временный."""
    return await user_service.create_user(data, db)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Обновить данные пользователя — только для админов."""
    return await user_service.update_user(user_id, data, db)


@router.patch("/{user_id}/block", response_model=UserResponse)
async def block_user(
    user_id: uuid.UUID,
    is_active: bool = Query(..., description="True — разблокировать, False — заблокировать"),
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Блокировка/разблокировка пользователя — только для админов."""
    return await user_service.block_user(user_id, is_active, db)
