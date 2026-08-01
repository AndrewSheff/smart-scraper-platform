"""Схемы экспорта — параметры фильтрации для Excel."""

from datetime import datetime

from pydantic import BaseModel


class ExportParams(BaseModel):
    date_from: datetime | None = None
    date_to: datetime | None = None
