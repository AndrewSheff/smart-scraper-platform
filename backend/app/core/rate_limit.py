"""Rate limiting — защита от спама запросами через slowapi + Redis."""

from slowapi import Limiter
from slowapi.util import get_remote_address as _get_remote_address
from starlette.requests import Request

from app.config import settings


def get_remote_address(request: Request) -> str:
    """Достает IP клиента — сначала из X-Forwarded-For (если за прокси), потом из request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Берем первый IP из цепочки — это реальный клиент
        return forwarded.split(",")[0].strip()
    return _get_remote_address(request)


# Лимитер с Redis-бекендом — состояние шарится между воркерами
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"],
)
