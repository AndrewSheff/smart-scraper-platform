"""Схемы полей задачи — селектор, тип данных, порядок."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class SelectorType(StrEnum):
    css = "css"
    xpath = "xpath"


class DataType(StrEnum):
    text = "text"
    number = "number"
    url = "url"
    image = "image"


class TaskFieldCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    selector: str = Field(min_length=1, max_length=500)
    selector_type: SelectorType = SelectorType.css
    data_type: DataType = DataType.text
    is_list: bool = False
    attribute: str | None = None
    position: int = 0


class TaskFieldResponse(BaseModel):
    id: UUID
    name: str
    selector: str
    selector_type: str
    data_type: str
    is_list: bool
    attribute: str | None
    position: int

    model_config = {"from_attributes": True}
