"""Схемы задач скрапинга — создание, обновление, ответы, preview."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.task_field import TaskFieldCreate, TaskFieldResponse


class TaskCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    url: str = Field(min_length=1, max_length=2048)
    schedule_cron: str = Field(min_length=1, max_length=100)
    is_active: bool = True
    headers: dict[str, str] | None = None
    timeout_seconds: int = Field(default=30, ge=5, le=120)
    max_retries: int = Field(default=2, ge=0, le=5)
    notify_on_change: bool = True
    notify_on_error: bool = True
    ai_prompt: str | None = None
    fields: list[TaskFieldCreate] = Field(min_length=1)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Проверяем что URL валидный и не ведет на локалхост (SSRF)."""
        import ipaddress
        from urllib.parse import urlparse

        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            msg = "URL должен начинаться с http:// или https://"
            raise ValueError(msg)

        hostname = parsed.hostname or ""
        # Блокируем localhost и приватные адреса
        blocked = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]  # noqa: S104
        if hostname in blocked:
            msg = "URL не может указывать на localhost"
            raise ValueError(msg)

        # Проверяем приватные IP
        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            pass  # Это доменное имя, не IP — все ок
        else:
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                msg = "URL не может указывать на приватный IP-адрес"
                raise ValueError(msg)

        return v

    @field_validator("schedule_cron")
    @classmethod
    def validate_cron(cls, v: str) -> str:
        """Проверяем cron-выражение — должно быть ровно 5 частей, иначе мимо."""
        parts = v.strip().split()
        if len(parts) != 5:
            msg = "Cron-выражение должно содержать ровно 5 частей (минута час день месяц день_недели)"
            raise ValueError(msg)
        return v


class TaskUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    url: str | None = Field(None, min_length=1, max_length=2048)
    schedule_cron: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None
    headers: dict[str, str] | None = None
    timeout_seconds: int | None = Field(None, ge=5, le=120)
    max_retries: int | None = Field(None, ge=0, le=5)
    notify_on_change: bool | None = None
    notify_on_error: bool | None = None
    ai_prompt: str | None = None
    fields: list[TaskFieldCreate] | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        """Проверяем URL на SSRF — только если он вообще передан."""
        if v is None:
            return v

        import ipaddress
        from urllib.parse import urlparse

        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            msg = "URL должен начинаться с http:// или https://"
            raise ValueError(msg)

        hostname = parsed.hostname or ""
        # Блокируем localhost и приватные адреса
        blocked = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]  # noqa: S104
        if hostname in blocked:
            msg = "URL не может указывать на localhost"
            raise ValueError(msg)

        # Проверяем приватные IP
        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            pass  # Доменное имя, не IP — ок
        else:
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                msg = "URL не может указывать на приватный IP-адрес"
                raise ValueError(msg)

        return v

    @field_validator("schedule_cron")
    @classmethod
    def validate_cron(cls, v: str | None) -> str | None:
        """Валидация cron — только если передали, а не None."""
        if v is None:
            return v
        parts = v.strip().split()
        if len(parts) != 5:
            msg = "Cron-выражение должно содержать ровно 5 частей (минута час день месяц день_недели)"
            raise ValueError(msg)
        return v


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str | None
    url: str
    schedule_cron: str
    is_active: bool
    headers: dict[str, str] | None
    timeout_seconds: int
    max_retries: int
    notify_on_change: bool
    notify_on_error: bool
    ai_prompt: str | None
    last_run_at: datetime | None
    last_status: str | None
    total_runs: int
    success_runs: int
    fields: list[TaskFieldResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    per_page: int


class PreviewRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    fields: list[TaskFieldCreate] = Field(min_length=1)
    headers: dict[str, str] | None = None
    timeout_seconds: int = Field(default=30, ge=5, le=120)


class PreviewResponse(BaseModel):
    success: bool
    data: dict[str, list[str] | str] | None = None
    error: str | None = None
    duration_ms: int
