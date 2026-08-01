"""Схемы запуска задачи — статус, результаты, изменения."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class RunStatus(StrEnum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    timeout = "timeout"


class ChangeType(StrEnum):
    added = "added"
    removed = "removed"
    modified = "modified"


class RunResultResponse(BaseModel):
    id: UUID
    field_name: str
    field_value: str | None
    field_index: int

    model_config = {"from_attributes": True}


class TaskChangeResponse(BaseModel):
    id: UUID
    change_type: str
    field_name: str
    old_value: str | None
    new_value: str | None
    item_index: int

    model_config = {"from_attributes": True}


class TaskRunResponse(BaseModel):
    id: UUID
    task_id: UUID
    status: str
    started_at: datetime
    finished_at: datetime | None
    duration_ms: int | None
    items_count: int
    error_message: str | None
    ai_summary: str | None
    has_changes: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskRunDetailResponse(TaskRunResponse):
    results: list[RunResultResponse]
    changes: list[TaskChangeResponse]


class TaskRunListResponse(BaseModel):
    items: list[TaskRunResponse]
    total: int
    page: int
    per_page: int
