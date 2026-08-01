"""Точка входа FastAPI — lifespan, роутеры, мидлвари, обработка ошибок."""

import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select

from app.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger, setup_logging
from app.core.rate_limit import limiter
from app.database import async_session

log = get_logger(__name__)


async def _create_admin_if_not_exists() -> None:
    """Создает дефолтного админа если его еще нет — вызывается при старте."""
    from app.core.security import hash_password
    from app.models.user import User

    async with async_session() as session:
        try:
            result = await session.execute(select(User).where(User.email == "admin@admin.com"))
            existing = result.scalar_one_or_none()

            if existing is None:
                admin = User(
                    email="admin@admin.com",
                    hashed_password=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                    name="Admin",
                    role="admin",
                    is_active=True,
                    must_change_password=True,
                )
                session.add(admin)
                await session.commit()
                log.info("admin_created", email="admin@admin.com")
            else:
                log.debug("admin_already_exists", email="admin@admin.com")
        except Exception:
            await session.rollback()
            log.exception("admin_creation_failed")
        finally:
            await session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения — стартуем все что нужно, при выходе тушим."""
    from app.tasks.scheduler import start_scheduler, stop_scheduler

    # Настраиваем логирование первым делом
    setup_logging()
    log.info("app_starting", app_name=settings.APP_NAME)

    # Накатываем миграции — alembic upgrade head
    try:
        subprocess.run(  # noqa: S603
            ["alembic", "upgrade", "head"],  # noqa: S607
            check=True,
            capture_output=True,
            text=True,
        )
        log.info("migrations_applied")
    except subprocess.CalledProcessError as e:
        log.error("migrations_failed", stderr=e.stderr)

    # Создаем админа если нет
    await _create_admin_if_not_exists()

    # Запускаем планировщик
    await start_scheduler(app)

    yield

    # Останавливаем планировщик при выходе
    await stop_scheduler()
    log.info("app_stopped")


# Создаем приложение
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

# CORS — разрешаем фронту стучаться
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter — slowapi
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Обработчик AppError — возвращает JSON с кодом и деталями
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Ловим наши кастомные ошибки и красиво отдаем клиенту."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# --- Подключаем роутеры ---
from app.api.v1 import auth, dashboard, export, health, notifications, runs, tasks, users  # noqa: E402

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(runs.router, prefix="/api/v1/runs", tags=["Runs"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
