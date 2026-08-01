"""Конфиг приложения — все настройки тянутся из .env через pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Главный конфиг, собирает переменные окружения в одном месте."""

    # Основное
    APP_NAME: str = "Smart Scraper Platform"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # База и кеш
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/scraper"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Секреты
    SECRET_KEY: str = "change-me-in-production-please"  # noqa: S105
    ADMIN_DEFAULT_PASSWORD: str = "admin123"  # noqa: S105

    # AI — по умолчанию Claude, но можно переключить на OpenAI
    AI_PROVIDER: str = "claude"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # CORS — список разрешенных источников
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Токены авторизации
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Синглтон конфига — импортируй и пользуйся
settings = Settings()
