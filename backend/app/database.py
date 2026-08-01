"""Подключение к базе — async SQLAlchemy, сессии и базовый класс моделей."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings

# Движок — echo=True для дебага, в проде выключаем
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Фабрика сессий — expire_on_commit=False чтоб объекты жили после коммита
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для всех моделей
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Зависимость FastAPI — выдает сессию и аккуратно закрывает после запроса."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
