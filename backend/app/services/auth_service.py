"""Сервис аутентификации — регистрация, логин, рефреш токенов, смена пароля.

Тут вся логика, роутер просто дергает эти методы.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError, UnauthorizedError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse

log = get_logger(__name__)


def _build_token_payload(user: User) -> dict:
    """Собирает payload для JWT — стандартный набор полей юзера."""
    return {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "must_change_password": user.must_change_password,
    }


def _make_tokens(user: User) -> TokenResponse:
    """Генерит пару access + refresh токенов для юзера."""
    payload = _build_token_payload(user)
    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
    )


async def register(data: RegisterRequest, db: AsyncSession) -> TokenResponse:
    """Регистрация нового юзера — проверяем уникальность email, создаем, отдаем токены."""
    # проверим что email не занят
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("Пользователь с таким email уже существует")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        name=data.name,
        role="user",
    )
    db.add(user)
    await db.flush()

    log.info("user_registered", user_id=str(user.id), email=user.email)
    return _make_tokens(user)


async def login(data: LoginRequest, db: AsyncSession) -> dict:
    """Логин — проверяем email + пароль, отдаем токены и данные юзера."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedError("Неверный email или пароль")

    if not user.is_active:
        raise UnauthorizedError("Аккаунт деактивирован")

    log.info("user_logged_in", user_id=str(user.id))

    tokens = _make_tokens(user)
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": tokens.token_type,
        "user": UserResponse.model_validate(user),
    }


async def refresh(data: RefreshRequest, db: AsyncSession) -> TokenResponse:
    """Рефреш — проверяем refresh-токен, генерим новую пару."""
    payload = verify_token(data.refresh_token)

    if payload.get("type") != "refresh":
        raise UnauthorizedError("Это не refresh-токен, братишка")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Невалидный токен")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("Пользователь не найден")

    if not user.is_active:
        raise UnauthorizedError("Аккаунт деактивирован")

    log.info("token_refreshed", user_id=str(user.id))
    return _make_tokens(user)


async def change_password(user_id: uuid.UUID, data: ChangePasswordRequest, db: AsyncSession) -> dict:
    """Смена пароля — проверяем текущий, ставим новый, снимаем флаг must_change_password."""
    if data.new_password != data.confirm_password:
        raise AppError("Пароли не совпадают", status_code=400)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    if not verify_password(data.current_password, user.hashed_password):
        raise UnauthorizedError("Текущий пароль неверный")

    user.hashed_password = hash_password(data.new_password)
    user.must_change_password = False
    await db.flush()

    log.info("password_changed", user_id=str(user.id))
    return {"message": "Пароль успешно изменен"}


async def get_me(user_id: uuid.UUID, db: AsyncSession) -> UserResponse:
    """Получить текущего юзера по id из токена."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    return UserResponse.model_validate(user)


async def update_me(user_id: uuid.UUID, data: dict, db: AsyncSession) -> UserResponse:
    """Обновить профиль текущего юзера — пока только имя можно менять."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    if "name" in data and data["name"]:
        user.name = data["name"]

    await db.flush()
    log.info("profile_updated", user_id=str(user.id))
    return UserResponse.model_validate(user)
