"""Сервис дашборда — статистика, графики, последние запуски.

Собирает данные для главной страницы, чтоб юзер видел общую картину.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import Date, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.scraping_task import ScrapingTask
from app.models.task_run import TaskRun
from app.schemas.dashboard import (
    ChartDataPoint,
    ChartResponse,
    DashboardStats,
    RecentRunItem,
    RecentRunsResponse,
)

log = get_logger(__name__)


async def get_stats(user_id: uuid.UUID, db: AsyncSession) -> DashboardStats:
    """Общая статистика юзера — задачи, запуски за сегодня, процент успеха."""
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

    # считаем задачи
    tasks_result = await db.execute(
        select(
            func.count(ScrapingTask.id).label("total"),
            func.count(
                case((ScrapingTask.is_active == True, ScrapingTask.id))  # noqa: E712
            ).label("active"),
        ).where(ScrapingTask.user_id == user_id)
    )
    tasks_row = tasks_result.one()
    total_tasks = tasks_row.total or 0
    active_tasks = tasks_row.active or 0

    # запуски за сегодня — через подзапрос по задачам юзера
    user_task_ids = select(ScrapingTask.id).where(ScrapingTask.user_id == user_id)

    runs_result = await db.execute(
        select(
            func.count(TaskRun.id).label("total_runs"),
            func.count(case((TaskRun.status == "failed", TaskRun.id))).label("errors"),
            func.count(case((TaskRun.status == "success", TaskRun.id))).label("successes"),
        ).where(
            TaskRun.task_id.in_(user_task_ids),
            TaskRun.started_at >= today_start,
        )
    )
    runs_row = runs_result.one()
    runs_today = runs_row.total_runs or 0
    errors_today = runs_row.errors or 0
    successes_today = runs_row.successes or 0

    # процент успеха
    success_rate = (successes_today / runs_today) if runs_today > 0 else 0.0

    return DashboardStats(
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        runs_today=runs_today,
        errors_today=errors_today,
        success_rate=round(success_rate, 2),
    )


async def get_chart_data(user_id: uuid.UUID, period_days: int, db: AsyncSession) -> ChartResponse:
    """Данные для графика — количество запусков по дням за период."""
    start_date = datetime.now(UTC) - timedelta(days=period_days)

    user_task_ids = select(ScrapingTask.id).where(ScrapingTask.user_id == user_id)

    # группируем по дате
    result = await db.execute(
        select(
            cast(TaskRun.started_at, Date).label("run_date"),
            func.count(TaskRun.id).label("total"),
            func.count(case((TaskRun.status == "success", TaskRun.id))).label("success"),
            func.count(case((TaskRun.status == "failed", TaskRun.id))).label("failed"),
        )
        .where(
            TaskRun.task_id.in_(user_task_ids),
            TaskRun.started_at >= start_date,
        )
        .group_by(cast(TaskRun.started_at, Date))
        .order_by(cast(TaskRun.started_at, Date))
    )

    rows = result.all()

    # создаем точки данных, заполняя пропуски нулями
    data_map = {str(row.run_date): row for row in rows}
    data_points: list[ChartDataPoint] = []

    for i in range(period_days):
        date = (datetime.now(UTC) - timedelta(days=period_days - 1 - i)).date()
        date_str = str(date)

        if date_str in data_map:
            row = data_map[date_str]
            data_points.append(
                ChartDataPoint(
                    date=date_str,
                    success=row.success,
                    failed=row.failed,
                    total=row.total,
                )
            )
        else:
            data_points.append(
                ChartDataPoint(
                    date=date_str,
                    success=0,
                    failed=0,
                    total=0,
                )
            )

    return ChartResponse(data=data_points, period_days=period_days)


async def get_recent_runs(user_id: uuid.UUID, limit: int, db: AsyncSession) -> RecentRunsResponse:
    """Последние запуски по всем задачам юзера — для виджета на дашборде."""
    user_task_ids = select(ScrapingTask.id).where(ScrapingTask.user_id == user_id)

    result = await db.execute(
        select(TaskRun)
        .options(selectinload(TaskRun.task))
        .where(TaskRun.task_id.in_(user_task_ids))
        .order_by(TaskRun.started_at.desc())
        .limit(limit)
    )
    runs = result.scalars().unique().all()

    items = [
        RecentRunItem(
            id=run.id,
            task_id=run.task_id,
            task_name=run.task.name if run.task else "Неизвестная задача",
            status=run.status,
            started_at=run.started_at,
            duration_ms=run.duration_ms,
            has_changes=run.has_changes,
            items_count=run.items_count,
        )
        for run in runs
    ]

    return RecentRunsResponse(items=items)
