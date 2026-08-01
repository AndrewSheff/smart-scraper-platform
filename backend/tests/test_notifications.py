"""Тесты уведомлений — отправка в Telegram."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.notification_service import (
    _escape_md,
    send_change_notification,
    send_error_notification,
    send_test_notification,
)


class TestEscapeMarkdown:
    """Тесты экранирования Markdown V2."""

    def test_escape_special_chars(self):
        """Спецсимволы должны экранироваться."""
        result = _escape_md("Hello *world* [link](url)")
        assert "\\*" in result
        assert "\\[" in result
        assert "\\(" in result

    def test_plain_text_unchanged(self):
        """Обычный текст без спецсимволов не меняется."""
        result = _escape_md("Simple text 123")
        assert result == "Simple text 123"

    def test_escape_underscores(self):
        """Подчеркивания экранируются."""
        result = _escape_md("some_variable_name")
        assert "\\_" in result


class TestNotificationService:
    """Тесты Telegram-уведомлений."""

    @pytest.mark.asyncio
    @patch("app.services.notification_service._send_telegram", new_callable=AsyncMock)
    async def test_change_notification_sent(self, mock_send):
        """Уведомление об изменениях должно отправляться."""
        user = MagicMock()
        user.id = "user-123"
        user.telegram_bot_token = "fake-token"
        user.telegram_chat_id = "12345"

        task = MagicMock()
        task.name = "Price Monitor"
        task.url = "https://example.com"

        await send_change_notification(user, task, "Prices dropped by 10%")
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.notification_service._send_telegram", new_callable=AsyncMock)
    async def test_error_notification_sent(self, mock_send):
        """Уведомление об ошибке должно отправляться."""
        user = MagicMock()
        user.id = "user-123"
        user.telegram_bot_token = "fake-token"
        user.telegram_chat_id = "12345"

        task = MagicMock()
        task.name = "Job Monitor"
        task.url = "https://example.com"

        await send_error_notification(user, task, "Connection timeout")
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_notification_skipped_without_token(self):
        """Без токена уведомление не отправляется и не падает."""
        user = MagicMock()
        user.id = "user-123"
        user.telegram_bot_token = None
        user.telegram_chat_id = None

        task = MagicMock()
        task.name = "Test"
        task.url = "https://example.com"

        # Не должно упасть
        await send_change_notification(user, task, "Test")

    @pytest.mark.asyncio
    @patch("app.services.notification_service._send_telegram", new_callable=AsyncMock)
    async def test_test_notification(self, mock_send):
        """Тестовое уведомление должно вернуть success."""
        result = await send_test_notification("fake-token", "12345")
        assert result["success"] is True
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.notification_service._send_telegram", new_callable=AsyncMock)
    async def test_test_notification_failure(self, mock_send):
        """Ошибка при тестовом уведомлении — success=False."""
        mock_send.side_effect = Exception("Bot token invalid")
        result = await send_test_notification("bad-token", "12345")
        assert result["success"] is False
        assert "Ошибка" in result["message"]
