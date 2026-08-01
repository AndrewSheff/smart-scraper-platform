"""Тесты выполнения задач — статусы, preview."""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.task_run import RunStatus


class TestRunStatus:
    """Тесты статусов выполнения."""

    def test_valid_statuses(self):
        """Все статусы должны быть валидны."""
        assert RunStatus.pending == "pending"
        assert RunStatus.running == "running"
        assert RunStatus.success == "success"
        assert RunStatus.failed == "failed"
        assert RunStatus.timeout == "timeout"

    def test_status_values(self):
        """Статусы должны быть строками."""
        for status in RunStatus:
            assert isinstance(status.value, str)

    def test_all_statuses_count(self):
        """Должно быть ровно 5 статусов."""
        assert len(list(RunStatus)) == 5


class TestPreview:
    """Тесты preview-функциональности."""

    @pytest.mark.asyncio
    @patch("app.services.run_service.scraper_service")
    async def test_preview_returns_data(self, mock_scraper_mod):
        """Preview должен вернуть данные без сохранения в БД."""
        from app.schemas.scraping_task import PreviewRequest
        from app.schemas.task_field import TaskFieldCreate
        from app.services.run_service import preview_task

        mock_scraper_mod.scrape = AsyncMock(return_value={"title": "Hello World"})

        request = PreviewRequest(
            url="https://example.com",
            fields=[TaskFieldCreate(name="title", selector="h1")],
        )

        result = await preview_task(request)
        assert result.success is True
        assert result.data is not None
        assert result.data["title"] == "Hello World"

    @pytest.mark.asyncio
    @patch("app.services.run_service.scraper_service")
    async def test_preview_handles_error(self, mock_scraper_mod):
        """Preview должен обрабатывать ошибки грациозно."""
        from app.schemas.scraping_task import PreviewRequest
        from app.schemas.task_field import TaskFieldCreate
        from app.services.run_service import preview_task

        mock_scraper_mod.scrape = AsyncMock(side_effect=Exception("Connection refused"))

        request = PreviewRequest(
            url="https://dead-site.example.com",
            fields=[TaskFieldCreate(name="title", selector="h1")],
        )

        result = await preview_task(request)
        assert result.success is False
        assert result.error is not None
        assert "Connection refused" in result.error

    @pytest.mark.asyncio
    @patch("app.services.run_service.scraper_service")
    async def test_preview_measures_duration(self, mock_scraper_mod):
        """Preview должен измерять время выполнения."""
        from app.schemas.scraping_task import PreviewRequest
        from app.schemas.task_field import TaskFieldCreate
        from app.services.run_service import preview_task

        mock_scraper_mod.scrape = AsyncMock(return_value={"x": "y"})

        request = PreviewRequest(
            url="https://example.com",
            fields=[TaskFieldCreate(name="x", selector=".x")],
        )

        result = await preview_task(request)
        assert result.duration_ms >= 0
