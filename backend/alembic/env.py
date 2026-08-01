"""Alembic env — асинхронные миграции для PostgreSQL через asyncpg."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.config import settings
from app.database import Base
from app.models import RunResult, ScrapingTask, TaskChange, TaskField, TaskRun, User  # noqa: F401

# Конфиг alembic из ini-файла
config = context.config

# Подставляем URL из настроек приложения
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метадата для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Оффлайн-режим — генерит SQL без подключения к базе."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Запуск миграций с живым подключением."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Асинхронный запуск миграций — для asyncpg движка."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Онлайн-режим — подключаемся к базе и катим миграции."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
