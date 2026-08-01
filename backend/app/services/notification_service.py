"""Сервис уведомлений — отправка в Telegram через aiogram.

Все ошибки глотаем — уведомления не должны ломать основной процесс.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.models.scraping_task import ScrapingTask
    from app.models.user import User

log = get_logger(__name__)


async def send_change_notification(user: User, task: ScrapingTask, summary: str) -> None:
    """Отправляет уведомление об изменениях на странице."""
    if not user.telegram_bot_token or not user.telegram_chat_id:
        log.info(
            "telegram_not_configured",
            user_id=str(user.id),
            msg="Телега не настроена, пропускаем",
        )
        return

    text = (
        f"🔔 *Изменения обнаружены*\n\n"
        f"📋 Задача: {_escape_md(task.name)}\n"
        f"🌐 URL: {_escape_md(task.url)}\n\n"
        f"📝 Резюме:\n{_escape_md(summary)}"
    )

    await _send_telegram(user.telegram_bot_token, user.telegram_chat_id, text)


async def send_error_notification(user: User, task: ScrapingTask, error: str) -> None:
    """Отправляет уведомление об ошибке выполнения задачи."""
    if not user.telegram_bot_token or not user.telegram_chat_id:
        log.info(
            "telegram_not_configured",
            user_id=str(user.id),
            msg="Телега не настроена, пропускаем",
        )
        return

    text = (
        f"❌ *Ошибка при выполнении задачи*\n\n"
        f"📋 Задача: {_escape_md(task.name)}\n"
        f"🌐 URL: {_escape_md(task.url)}\n\n"
        f"💥 Ошибка:\n{_escape_md(error[:500])}"
    )

    await _send_telegram(user.telegram_bot_token, user.telegram_chat_id, text)


async def send_test_notification(bot_token: str, chat_id: str) -> dict:
    """Тестовая отправка — проверяем что токен и чат-айди рабочие."""
    text = "✅ *Тестовое сообщение*\n\nSmart Scraper Platform успешно подключен к Telegram\\!"

    try:
        await _send_telegram(bot_token, chat_id, text)
        return {"success": True, "message": "Тестовое сообщение отправлено"}
    except Exception as e:
        log.warning("test_notification_failed", error=str(e))
        return {"success": False, "message": f"Ошибка отправки: {e!s}"}


def _escape_md(text: str) -> str:
    """Экранирует спецсимволы MarkdownV2 — телеграм тут привередлив."""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    escaped = text
    for char in special_chars:
        escaped = escaped.replace(char, f"\\{char}")
    return escaped


async def _send_telegram(bot_token: str, chat_id: str, text: str) -> None:
    """Отправляет сообщение в телеграм через aiogram, закрывает сессию после."""
    try:
        from aiogram import Bot

        bot = Bot(token=bot_token)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="MarkdownV2",
            )
            log.info("telegram_message_sent", chat_id=chat_id)
        finally:
            # обязательно закрываем сессию, а то утечет
            await bot.session.close()
    except Exception as e:
        log.error("telegram_send_failed", chat_id=chat_id, error=str(e))
        raise
