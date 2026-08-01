"""Кастомные исключения — чтоб не дублировать status_code и detail повсюду."""

from fastapi import HTTPException, status


class AppError(HTTPException):
    """Базовая ошибка приложения — наследуется от HTTPException."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Внутренняя ошибка сервера"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        super().__init__(
            status_code=status_code or self.__class__.status_code,
            detail=detail or self.__class__.detail,
        )


class NotFoundError(AppError):
    """Ресурс не найден — 404, классика."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Ресурс не найден"


class ConflictError(AppError):
    """Конфликт данных — 409, например дублирование email."""

    status_code = status.HTTP_409_CONFLICT
    detail = "Конфликт данных"


class ForbiddenError(AppError):
    """Доступ запрещен — 403, прав не хватает."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "Доступ запрещен"


class UnauthorizedError(AppError):
    """Не авторизован — 401, токен не предоставлен или битый."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Необходима авторизация"

    def __init__(self, detail: str | None = None):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)
        # Добавляем заголовок для Bearer-схемы
        self.headers = {"WWW-Authenticate": "Bearer"}
