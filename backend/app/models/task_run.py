"""Модель запуска задачи — статус, время, результаты, AI-саммари."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskRun(Base):
    __tablename__ = "task_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scraping_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Сколько элементов извлекли
    items_count: Mapped[int] = mapped_column(Integer, default=0)

    # Ошибка, если что-то пошло не так
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI-саммари изменений (генерится если есть diff с предыдущим запуском)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Были ли изменения по сравнению с предыдущим запуском
    has_changes: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Связи
    task = relationship("ScrapingTask", back_populates="runs")
    results = relationship("RunResult", back_populates="run", cascade="all, delete-orphan")
    changes = relationship("TaskChange", back_populates="run", cascade="all, delete-orphan")
