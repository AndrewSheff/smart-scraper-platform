"""Роутер дашборда — статистика, графики, последние запуски.

Три эндпоинта для главной страницы — вся инфа по юзеру.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import ChartResponse, DashboardStats, RecentRunsResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Общая статистика юзера — задачи, запуски, процент успеха."""
    return await dashboard_service.get_stats(current_user.id, db)


@router.get("/chart", response_model=ChartResponse)
async def get_chart_data(
    period_days: int = Query(7, ge=1, le=90, description="Период в днях"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Данные для графика — запуски по дням за указанный период."""
    return await dashboard_service.get_chart_data(current_user.id, period_days, db)


@router.get("/recent-runs", response_model=RecentRunsResponse)
async def get_recent_runs(
    limit: int = Query(10, ge=1, le=50, description="Количество последних запусков"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Последние запуски по всем задачам юзера — для виджета."""
    return await dashboard_service.get_recent_runs(current_user.id, limit, db)
