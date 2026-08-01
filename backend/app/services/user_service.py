"""Сервис управления юзерами — CRUD для админов.

Админ может создавать, редактировать, блокировать юзеров и все такое.
"""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.core.security import generate_temporary_password, hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

log = get_logger(__name__)


def _escape_like(value: str) -> str:
    """Экранирует спецсимволы LIKE — %, _, \\ — чтоб не ломали поиск."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def list_users(
    page: int,
    per_page: int,
    search: str | None,
    db: AsyncSession,
) -> UserListResponse:
    """Список юзеров с пагинацией и поиском по имени/email."""
    query = select(User)
    count_query = select(func.count(User.id))

    # поиск по имени или email (ilike — регистронезависимый)
    if search:
        escaped = _escape_like(search)
        pattern = f"%{escaped}%"
        search_filter = or_(
            User.name.ilike(pattern),
            User.email.ilike(pattern),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # общее количество
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # пагинация
    offset = (page - 1) * per_page
    query = query.order_by(User.created_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        per_page=per_page,
    )


async def get_user(user_id: uuid.UUID, db: AsyncSession) -> UserResponse:
    """Получить юзера по id — если нет, кидаем 404."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    return UserResponse.model_validate(user)


async def create_user(data: UserCreate, db: AsyncSession) -> dict:
    """Создать юзера — если пароль не передан, генерим временный.

    Возвращает юзера + временный пароль (если был сгенерирован).
    """
    # проверка на дубль email
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("Пользователь с таким email уже существует")

    # если пароль не передали — генерим временный
    temp_password = None
    if data.password:
        password_hash = hash_password(data.password)
    else:
        temp_password = generate_temporary_password()
        password_hash = hash_password(temp_password)

    user = User(
        email=data.email,
        hashed_password=password_hash,
        name=data.name,
        role=data.role,
        must_change_password=True,
    )
    db.add(user)
    await db.flush()

    log.info("user_created_by_admin", user_id=str(user.id), email=user.email)

    result = {"user": UserResponse.model_validate(user)}
    if temp_password:
        result["temporary_password"] = temp_password

    return result


async def update_user(user_id: uuid.UUID, data: UserUpdate, db: AsyncSession) -> UserResponse:
    """Обновить поля юзера — только те, что переданы (не None)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    log.info("user_updated", user_id=str(user.id))
    return UserResponse.model_validate(user)


async def block_user(user_id: uuid.UUID, is_active: bool, db: AsyncSession) -> UserResponse:
    """Блокировка/разблокировка юзера — ставим is_active."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("Пользователь не найден")

    user.is_active = is_active
    await db.flush()

    action = "unblocked" if is_active else "blocked"
    log.info(f"user_{action}", user_id=str(user.id))
    return UserResponse.model_validate(user)
