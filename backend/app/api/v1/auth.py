"""Роутер аутентификации — логин, регистрация, рефреш, смена пароля, текущий юзер.

Пять эндпоинтов — все что нужно для входа в систему.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Регистрация нового юзера — получаем токены сразу."""
    return await auth_service.register(data, db)


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Логин — проверяем email+пароль, отдаем токены + данные юзера."""
    return await auth_service.login(data, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Обновление токенов — передаем refresh, получаем новую пару."""
    return await auth_service.refresh(data, db)


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Смена пароля — нужен текущий пароль для подтверждения."""
    return await auth_service.change_password(current_user.id, data, db)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Текущий юзер — данные из токена, подтянутые из базы."""
    return await auth_service.get_me(current_user.id, db)


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить профиль текущего юзера — имя и прочее."""
    return await auth_service.update_me(current_user.id, data, db)
