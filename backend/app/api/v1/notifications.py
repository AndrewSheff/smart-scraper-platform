"""Роутер уведомлений — настройки Telegram, тестовая отправка.

Три эндпоинта: получить настройки, обновить, отправить тестовое.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationSettings,
    NotificationSettingsUpdate,
    TestNotificationResponse,
)
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
):
    """Получить текущие настройки уведомлений — токен бота и чат-айди."""
    return NotificationSettings(
        telegram_bot_token=current_user.telegram_bot_token,
        telegram_chat_id=current_user.telegram_chat_id,
    )


@router.put("/settings", response_model=NotificationSettings)
async def update_notification_settings(
    data: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить настройки уведомлений — токен бота и/или чат-айди."""
    # перечитываем юзера в текущей сессии
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("Пользователь не найден")

    if data.telegram_bot_token is not None:
        user.telegram_bot_token = data.telegram_bot_token
    if data.telegram_chat_id is not None:
        user.telegram_chat_id = data.telegram_chat_id

    await db.flush()

    return NotificationSettings(
        telegram_bot_token=user.telegram_bot_token,
        telegram_chat_id=user.telegram_chat_id,
    )


@router.post("/test", response_model=TestNotificationResponse)
async def test_notification(
    current_user: User = Depends(get_current_user),
):
    """Тестовая отправка — проверяем что бот работает и чат-айди верный."""
    if not current_user.telegram_bot_token or not current_user.telegram_chat_id:
        return TestNotificationResponse(
            success=False,
            message="Настройки Telegram не заполнены — укажите bot_token и chat_id",
        )

    result = await notification_service.send_test_notification(
        bot_token=current_user.telegram_bot_token,
        chat_id=current_user.telegram_chat_id,
    )
    return TestNotificationResponse(**result)
