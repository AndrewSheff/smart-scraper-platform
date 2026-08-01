"""Модель поля для извлечения — CSS/XPath селектор, тип данных, порядок."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskField(Base):
    __tablename__ = "task_fields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scraping_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    selector: Mapped[str] = mapped_column(String(500), nullable=False)
    selector_type: Mapped[str] = mapped_column(String(10), nullable=False, default="css")  # css | xpath
    data_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text")  # text | number | url | image
    is_list: Mapped[bool] = mapped_column(Boolean, default=False)

    # Атрибут элемента — href, src и т.д. Если null — берем innerText
    attribute: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Порядок отображения полей
    position: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Связь
    task = relationship("ScrapingTask", back_populates="fields")
