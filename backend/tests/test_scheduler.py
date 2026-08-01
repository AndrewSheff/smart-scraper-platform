"""Тесты планировщика — парсинг cron, управление джобами."""

import pytest

from app.tasks.scheduler import _parse_cron


class TestCronParser:
    """Тесты парсинга cron-выражений."""

    def test_every_hour(self):
        """Каждый час — '0 * * * *'."""
        result = _parse_cron("0 * * * *")
        assert result["minute"] == "0"
        assert result["hour"] == "*"

    def test_every_6_hours(self):
        """Каждые 6 часов — '0 */6 * * *'."""
        result = _parse_cron("0 */6 * * *")
        assert result["minute"] == "0"
        assert result["hour"] == "*/6"

    def test_every_5_minutes(self):
        """Каждые 5 минут — '*/5 * * * *'."""
        result = _parse_cron("*/5 * * * *")
        assert result["minute"] == "*/5"

    def test_specific_time(self):
        """Конкретное время — '30 14 * * *' (14:30 каждый день)."""
        result = _parse_cron("30 14 * * *")
        assert result["minute"] == "30"
        assert result["hour"] == "14"
        assert result["day"] == "*"

    def test_weekly(self):
        """Еженедельно по понедельникам — '0 9 * * 1'."""
        result = _parse_cron("0 9 * * 1")
        assert result["minute"] == "0"
        assert result["hour"] == "9"
        assert result["day_of_week"] == "1"

    def test_daily_at_midnight(self):
        """Ежедневно в полночь — '0 0 * * *'."""
        result = _parse_cron("0 0 * * *")
        assert result["minute"] == "0"
        assert result["hour"] == "0"

    def test_invalid_cron_raises(self):
        """Невалидное cron-выражение должно вызвать ошибку."""
        with pytest.raises((ValueError, IndexError)):
            _parse_cron("invalid")

    def test_too_few_parts(self):
        """Меньше 5 частей — ошибка."""
        with pytest.raises((ValueError, IndexError)):
            _parse_cron("* * *")
