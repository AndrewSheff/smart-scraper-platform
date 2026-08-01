"""Схемы дашборда — статистика, графики, последние запуски."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_tasks: int
    active_tasks: int
    runs_today: int
    errors_today: int
    success_rate: float  # 0.0 — 1.0


class ChartDataPoint(BaseModel):
    date: str
    success: int
    failed: int
    total: int


class ChartResponse(BaseModel):
    data: list[ChartDataPoint]
    period_days: int


class RecentRunItem(BaseModel):
    id: UUID
    task_id: UUID
    task_name: str
    status: str
    started_at: datetime
    duration_ms: int | None
    has_changes: bool
    items_count: int


class RecentRunsResponse(BaseModel):
    items: list[RecentRunItem]
