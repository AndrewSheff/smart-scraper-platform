"""Роутер экспорта — выгрузка данных в Excel.

Отдаем StreamingResponse с xlsx-файлом — качай и радуйся.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.core.security import get_current_user
from app.database import get_db
from app.models.scraping_task import ScrapingTask
from app.models.task_run import TaskRun
from app.models.user import User
from app.services import export_service

router = APIRouter(prefix="/export", tags=["export"])

# content-type для xlsx файлов
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/task/{task_id}")
async def export_task(
    task_id: uuid.UUID,
    date_from: datetime | None = Query(None, description="Начало периода"),
    date_to: datetime | None = Query(None, description="Конец периода"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Экспорт данных задачи в Excel — история запусков с результатами."""
    # достаем задачу с полями
    result = await db.execute(
        select(ScrapingTask)
        .options(selectinload(ScrapingTask.fields))
        .where(ScrapingTask.id == task_id, ScrapingTask.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundError("Задача не найдена")

    # подтягиваем запуски с фильтром по дате
    runs_query = (
        select(TaskRun)
        .options(selectinload(TaskRun.results))
        .where(TaskRun.task_id == task_id, TaskRun.status == "success")
    )

    if date_from:
        runs_query = runs_query.where(TaskRun.started_at >= date_from)
    if date_to:
        runs_query = runs_query.where(TaskRun.started_at <= date_to)

    runs_query = runs_query.order_by(TaskRun.started_at.desc())
    runs_result = await db.execute(runs_query)
    runs = list(runs_result.scalars().unique().all())

    # генерим файл
    output = await export_service.export_task_excel(task, runs, db)

    # формируем безопасное имя файла
    safe_name = task.name.replace('"', "").replace("/", "_")[:50]
    filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        output,
        media_type=XLSX_CONTENT_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/summary")
async def export_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сводный экспорт по всем задачам юзера — общая статистика."""
    # достаем все задачи юзера с полями
    result = await db.execute(
        select(ScrapingTask)
        .options(selectinload(ScrapingTask.fields))
        .where(ScrapingTask.user_id == current_user.id)
        .order_by(ScrapingTask.created_at.desc())
    )
    tasks = list(result.scalars().unique().all())

    # генерим файл
    output = await export_service.export_summary_excel(tasks, db)

    filename = f"scraper_summary_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        output,
        media_type=XLSX_CONTENT_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
