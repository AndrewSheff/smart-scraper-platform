"""Модель задачи скрапинга — URL, селекторы, расписание, настройки уведомлений."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScrapingTask(Base):
    __tablename__ = "scraping_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # Cron-расписание — формат: "*/30 * * * *" (каждые 30 мин)
    schedule_cron: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Дополнительные настройки HTTP-запроса
    headers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
    max_retries: Mapped[int] = mapped_column(Integer, default=2)

    # Уведомления
    notify_on_change: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_error: Mapped[bool] = mapped_column(Boolean, default=True)

    # Кастомный промпт для AI-суммаризации (если null — дефолтный)
    ai_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Статистика — обновляется после каждого запуска
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    total_runs: Mapped[int] = mapped_column(Integer, default=0)
    success_runs: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Связи
    user = relationship("User", back_populates="scraping_tasks")
    fields = relationship(
        "TaskField", back_populates="task", cascade="all, delete-orphan", order_by="TaskField.position"
    )
    runs = relationship("TaskRun", back_populates="task", cascade="all, delete-orphan")
