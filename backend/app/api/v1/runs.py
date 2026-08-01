"""Роутер запусков — история, детали, результаты, изменения.

Юзер смотрит запуски только своих задач.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.task_run import (
    RunResultResponse,
    TaskChangeResponse,
    TaskRunDetailResponse,
    TaskRunListResponse,
)
from app.services import run_service

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/task/{task_id}", response_model=TaskRunListResponse)
async def list_runs(
    task_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Элементов на страницу"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список запусков задачи с пагинацией — проверяем владельца."""
    return await run_service.get_runs(task_id, current_user.id, page, per_page, db)


@router.get("/{run_id}", response_model=TaskRunDetailResponse)
async def get_run_detail(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Детали запуска — результаты и изменения."""
    return await run_service.get_run_detail(run_id, current_user.id, db)


@router.get("/{run_id}/results", response_model=list[RunResultResponse])
async def get_run_results(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Только результаты запуска — без изменений, для таблички."""
    detail = await run_service.get_run_detail(run_id, current_user.id, db)
    return detail.results


@router.get("/{run_id}/changes", response_model=list[TaskChangeResponse])
async def get_run_changes(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Только изменения запуска — что поменялось по сравнению с предыдущим."""
    detail = await run_service.get_run_detail(run_id, current_user.id, db)
    return detail.changes
