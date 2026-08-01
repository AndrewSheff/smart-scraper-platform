"""Схемы уведомлений — настройки Telegram, тестовое сообщение."""

from pydantic import BaseModel, Field


class NotificationSettings(BaseModel):
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    model_config = {"from_attributes": True}


class NotificationSettingsUpdate(BaseModel):
    telegram_bot_token: str | None = Field(None, max_length=255)
    telegram_chat_id: str | None = Field(None, max_length=100)


class TestNotificationResponse(BaseModel):
    success: bool
    message: str
