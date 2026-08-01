"""Фикстуры для тестов — мокаем БД, юзера и клиент."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.security import create_access_token, hash_password


@pytest.fixture
def mock_user():
    """Фейковый юзер для тестов."""
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.name = "Test User"
    user.role = "user"
    user.is_active = True
    user.must_change_password = False
    user.hashed_password = hash_password("testpass123")
    user.telegram_bot_token = None
    user.telegram_chat_id = None
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    return user


@pytest.fixture
def mock_admin():
    """Фейковый админ для тестов."""
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "admin@admin.com"
    user.name = "Admin"
    user.role = "admin"
    user.is_active = True
    user.must_change_password = False
    user.hashed_password = hash_password("admin123")
    user.telegram_bot_token = None
    user.telegram_chat_id = None
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    return user


@pytest.fixture
def auth_token(mock_user):
    """JWT-токен для тестов."""
    return create_access_token(
        {
            "sub": str(mock_user.id),
            "email": mock_user.email,
            "name": mock_user.name,
            "role": mock_user.role,
        }
    )


@pytest.fixture
def admin_token(mock_admin):
    """JWT-токен для админа."""
    return create_access_token(
        {
            "sub": str(mock_admin.id),
            "email": mock_admin.email,
            "name": mock_admin.name,
            "role": mock_admin.role,
        }
    )


@pytest.fixture
def mock_db():
    """Мок БД-сессии — чтоб не поднимать реальную базу."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def mock_task(mock_user):
    """Фейковая задача скрапинга."""
    task = MagicMock()
    task.id = uuid.uuid4()
    task.user_id = mock_user.id
    task.name = "Test Task"
    task.description = "Test description"
    task.url = "https://example.com/test"
    task.schedule_cron = "0 */6 * * *"
    task.is_active = True
    task.headers = None
    task.timeout_seconds = 30
    task.max_retries = 2
    task.notify_on_change = True
    task.notify_on_error = True
    task.ai_prompt = None
    task.last_run_at = None
    task.last_status = None
    task.total_runs = 0
    task.success_runs = 0
    task.fields = []
    task.created_at = datetime.now(UTC)
    task.updated_at = datetime.now(UTC)
    return task


@pytest.fixture
def mock_field(mock_task):
    """Фейковое поле задачи."""
    field = MagicMock()
    field.id = uuid.uuid4()
    field.task_id = mock_task.id
    field.name = "title"
    field.selector = "h1.title"
    field.selector_type = "css"
    field.data_type = "text"
    field.is_list = False
    field.attribute = None
    field.position = 0
    return field


@pytest.fixture
def mock_run(mock_task):
    """Фейковый запуск задачи."""
    run = MagicMock()
    run.id = uuid.uuid4()
    run.task_id = mock_task.id
    run.status = "success"
    run.started_at = datetime.now(UTC)
    run.finished_at = datetime.now(UTC)
    run.duration_ms = 1500
    run.items_count = 3
    run.error_message = None
    run.ai_summary = None
    run.has_changes = False
    run.results = []
    run.changes = []
    run.created_at = datetime.now(UTC)
    return run
