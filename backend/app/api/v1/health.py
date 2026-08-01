"""Роутер хелсчека — проверяем что база и Redis живы.

Используется мониторингом и балансировщиком для проверки здоровья сервиса.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Общий хелсчек — проверяем PostgreSQL и Redis."""
    result = {
        "status": "healthy",
        "services": {
            "database": await _check_database(db),
            "redis": await _check_redis(),
        },
    }

    # если хоть один сервис лег — статус unhealthy
    all_ok = all(s["status"] == "ok" for s in result["services"].values())
    if not all_ok:
        result["status"] = "unhealthy"

    return result


async def _check_database(db: AsyncSession) -> dict:
    """Проверяем что база отвечает — простой SELECT 1."""
    try:
        await db.execute(text("select 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


async def _check_redis() -> dict:
    """Проверяем что Redis живой — пингуем через aioredis."""
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            await r.ping()
            return {"status": "ok"}
        finally:
            await r.aclose()
    except Exception as e:
        return {"status": "error", "detail": str(e)}
