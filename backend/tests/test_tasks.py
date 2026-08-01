"""Тесты сервиса задач — CRUD, валидация URL, переключение."""

import pytest

from app.schemas.scraping_task import TaskCreate, TaskUpdate
from app.schemas.task_field import TaskFieldCreate


class TestTaskValidation:
    """Тесты валидации задач."""

    def test_valid_url(self):
        """Валидный URL должен пройти проверку."""
        task = TaskCreate(
            name="Test",
            url="https://example.com/page",
            schedule_cron="0 * * * *",
            fields=[TaskFieldCreate(name="title", selector="h1")],
        )
        assert task.url == "https://example.com/page"

    def test_localhost_url_blocked(self):
        """localhost URL должен быть заблокирован (SSRF)."""
        with pytest.raises(ValueError, match="localhost"):
            TaskCreate(
                name="Test",
                url="http://localhost:8080/secret",
                schedule_cron="0 * * * *",
                fields=[TaskFieldCreate(name="title", selector="h1")],
            )

    def test_private_ip_blocked(self):
        """Приватный IP должен быть заблокирован."""
        with pytest.raises(ValueError, match="приватный"):
            TaskCreate(
                name="Test",
                url="http://192.168.1.1/admin",
                schedule_cron="0 * * * *",
                fields=[TaskFieldCreate(name="title", selector="h1")],
            )

    def test_ftp_scheme_blocked(self):
        """FTP-схема должна быть заблокирована."""
        with pytest.raises(ValueError, match="http"):
            TaskCreate(
                name="Test",
                url="ftp://example.com/file",
                schedule_cron="0 * * * *",
                fields=[TaskFieldCreate(name="title", selector="h1")],
            )

    def test_loopback_ip_blocked(self):
        """127.0.0.1 должен быть заблокирован."""
        with pytest.raises(ValueError, match="localhost"):
            TaskCreate(
                name="Test",
                url="http://127.0.0.1:3000/api",
                schedule_cron="0 * * * *",
                fields=[TaskFieldCreate(name="title", selector="h1")],
            )

    def test_empty_fields_blocked(self):
        """Задача без полей не должна создаваться."""
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test",
                url="https://example.com",
                schedule_cron="0 * * * *",
                fields=[],
            )

    def test_timeout_range(self):
        """Timeout должен быть в допустимом диапазоне."""
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test",
                url="https://example.com",
                schedule_cron="0 * * * *",
                timeout_seconds=300,  # > 120
                fields=[TaskFieldCreate(name="title", selector="h1")],
            )


class TestTaskUpdate:
    """Тесты обновления задачи."""

    def test_partial_update(self):
        """Частичное обновление — только переданные поля."""
        update = TaskUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.url is None
        assert update.fields is None

    def test_update_with_fields(self):
        """Обновление с заменой полей."""
        update = TaskUpdate(
            fields=[
                TaskFieldCreate(name="new_field", selector=".new"),
            ]
        )
        assert len(update.fields) == 1
        assert update.fields[0].name == "new_field"
