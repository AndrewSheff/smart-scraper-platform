"""Безопасность — JWT-токены, хеширование паролей, зависимости для авторизации.

Используем bcrypt напрямую, без passlib — он нам тут не нужен.
"""

import secrets
import string
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

# Схема авторизации — Bearer token
bearer_scheme = HTTPBearer(auto_error=False)

# Параметры JWT
ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    """Создает access-токен с коротким временем жизни."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Создает refresh-токен — живет подольше, для обновления access."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Проверяет и декодирует JWT. Кидает HTTPException если токен битый."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен невалиден или просрочен",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return payload


def hash_password(password: str) -> str:
    """Хеширует пароль через bcrypt — просто и надежно."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Сверяет пароль с хешом — True если совпал."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def generate_temporary_password() -> str:
    """Генерирует временный пароль — 12 символов, буквы + цифры."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(12))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Зависимость FastAPI — достает юзера из JWT-токена.

    Проверяет что токен валидный, юзер существует и не заблокирован.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)

    # Достаем sub из токена — это user_id
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен — нет sub",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Импорт тут чтоб избежать циклических зависимостей
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован",
        )

    return user


def require_role(role: str):
    """Фабрика зависимостей — проверяет что у юзера нужная роль.

    Использование: Depends(require_role("admin"))
    """

    async def role_checker(
        current_user=Depends(get_current_user),
    ):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Нужна роль '{role}', а у тебя '{current_user.role}'",
            )
        return current_user

    return role_checker
