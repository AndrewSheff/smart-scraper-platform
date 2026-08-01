"""Тесты AI-сервиса — суммаризация изменений."""

from unittest.mock import patch

import pytest

from app.services.ai_service import _format_changes, generate_summary


class TestFormatChanges:
    """Тесты форматирования изменений в текст."""

    def test_format_added(self):
        """Added должен форматироваться с плюсом."""
        text = _format_changes([{"change_type": "added", "field_name": "title", "new_value": "New", "item_index": 0}])
        assert "добавлено" in text
        assert "New" in text

    def test_format_removed(self):
        """Removed должен форматироваться с минусом."""
        text = _format_changes([{"change_type": "removed", "field_name": "title", "old_value": "Old", "item_index": 0}])
        assert "удалено" in text
        assert "Old" in text

    def test_format_modified(self):
        """Modified должен показывать старое и новое значение."""
        text = _format_changes(
            [
                {
                    "change_type": "modified",
                    "field_name": "price",
                    "old_value": "$100",
                    "new_value": "$85",
                    "item_index": 0,
                }
            ]
        )
        assert "$100" in text
        assert "$85" in text

    def test_format_empty(self):
        """Пустой список — пустая строка."""
        assert _format_changes([]) == ""


class TestAISummary:
    """Тесты генерации AI-саммари."""

    @pytest.mark.asyncio
    async def test_summary_empty_changes(self):
        """Пустой список изменений — None без вызова AI."""
        result = await generate_summary(
            task_name="Test",
            url="https://example.com",
            changes=[],
        )
        assert result is None

    @pytest.mark.asyncio
    @patch("app.services.ai_service.settings")
    async def test_summary_no_api_key_claude(self, mock_settings):
        """Без API-ключа Claude — None."""
        mock_settings.AI_PROVIDER = "claude"
        mock_settings.ANTHROPIC_API_KEY = ""
        mock_settings.OPENAI_API_KEY = ""

        result = await generate_summary(
            task_name="Test",
            url="https://example.com",
            changes=[
                {
                    "change_type": "modified",
                    "field_name": "price",
                    "old_value": "$100",
                    "new_value": "$85",
                    "item_index": 0,
                }
            ],
        )
        assert result is None

    @pytest.mark.asyncio
    @patch("app.services.ai_service.settings")
    async def test_summary_no_api_key_openai(self, mock_settings):
        """Без API-ключа OpenAI — None."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.ANTHROPIC_API_KEY = ""
        mock_settings.OPENAI_API_KEY = ""

        result = await generate_summary(
            task_name="Test",
            url="https://example.com",
            changes=[
                {
                    "change_type": "modified",
                    "field_name": "price",
                    "old_value": "$100",
                    "new_value": "$85",
                    "item_index": 0,
                }
            ],
        )
        assert result is None

    @pytest.mark.asyncio
    @patch("app.services.ai_service.settings")
    async def test_summary_unknown_provider(self, mock_settings):
        """Неизвестный провайдер — None."""
        mock_settings.AI_PROVIDER = "gemini"
        result = await generate_summary(
            task_name="Test",
            url="https://example.com",
            changes=[{"change_type": "added", "field_name": "x", "new_value": "y", "item_index": 0}],
        )
        assert result is None
