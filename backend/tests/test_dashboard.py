"""Тесты дашборда — статистика, графики."""

from app.schemas.dashboard import DashboardStats


class TestDashboardStats:
    """Тесты схемы статистики."""

    def test_stats_creation(self):
        """Статистика должна создаваться с корректными полями."""
        stats = DashboardStats(
            total_tasks=10,
            active_tasks=7,
            runs_today=45,
            errors_today=3,
            success_rate=0.93,
        )
        assert stats.total_tasks == 10
        assert stats.active_tasks == 7
        assert stats.success_rate == 0.93

    def test_stats_zero_values(self):
        """Нулевые значения должны быть допустимы."""
        stats = DashboardStats(
            total_tasks=0,
            active_tasks=0,
            runs_today=0,
            errors_today=0,
            success_rate=0.0,
        )
        assert stats.total_tasks == 0
        assert stats.success_rate == 0.0

    def test_stats_perfect_rate(self):
        """100% успешность — success_rate=1.0."""
        stats = DashboardStats(
            total_tasks=5,
            active_tasks=5,
            runs_today=100,
            errors_today=0,
            success_rate=1.0,
        )
        assert stats.success_rate == 1.0
