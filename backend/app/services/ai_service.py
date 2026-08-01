"""Сервис AI-суммаризации — генерит человекопонятное описание изменений.

Поддерживает Claude и OpenAI, переключается через настройки.
Если API-ключ не задан — молча возвращает None, не паникуем.
"""

from __future__ import annotations

from app.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)

# дефолтный промпт для суммаризации изменений
DEFAULT_PROMPT = """Ты — аналитик данных. Тебе дан список изменений, обнаруженных при мониторинге веб-страницы.
Составь краткое, понятное резюме на русском языке.
Укажи ключевые изменения и их возможное значение.
Будь лаконичен — максимум 3-5 предложений."""


async def generate_summary(
    task_name: str,
    url: str,
    changes: list[dict],
    custom_prompt: str | None = None,
) -> str | None:
    """Генерирует AI-саммари по списку изменений.

    Возвращает текст или None если что-то пошло не так (нет ключа, ошибка API и т.д.).
    """
    if not changes:
        return None

    # формируем описание изменений для AI
    changes_text = _format_changes(changes)
    system_prompt = custom_prompt or DEFAULT_PROMPT

    user_message = f"Задача мониторинга: {task_name}\nURL: {url}\n\nОбнаруженные изменения:\n{changes_text}"

    provider = settings.AI_PROVIDER.lower()

    if provider == "claude":
        return await _call_claude(system_prompt, user_message)
    elif provider == "openai":
        return await _call_openai(system_prompt, user_message)
    else:
        log.warning("unknown_ai_provider", provider=provider)
        return None


def _format_changes(changes: list[dict]) -> str:
    """Форматирует список изменений в текст для AI."""
    lines = []
    for ch in changes:
        change_type = ch.get("change_type", "unknown")
        field_name = ch.get("field_name", "?")
        old_val = ch.get("old_value", "—")
        new_val = ch.get("new_value", "—")
        idx = ch.get("item_index", 0)

        if change_type == "added":
            lines.append(f'+ [{field_name}][{idx}]: добавлено значение "{new_val}"')
        elif change_type == "removed":
            lines.append(f'- [{field_name}][{idx}]: удалено значение "{old_val}"')
        elif change_type == "modified":
            lines.append(f'~ [{field_name}][{idx}]: "{old_val}" -> "{new_val}"')

    return "\n".join(lines)


async def _call_claude(system_prompt: str, user_message: str) -> str | None:
    """Вызов Claude API через anthropic SDK."""
    if not settings.ANTHROPIC_API_KEY:
        log.info("anthropic_api_key_not_set", msg="Пропускаем AI-суммаризацию")
        return None

    try:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        # достаем текстовый контент из ответа
        return message.content[0].text if message.content else None

    except Exception as e:
        log.error("claude_api_error", error=str(e))
        return None


async def _call_openai(system_prompt: str, user_message: str) -> str | None:
    """Вызов OpenAI API через openai SDK."""
    if not settings.OPENAI_API_KEY:
        log.info("openai_api_key_not_set", msg="Пропускаем AI-суммаризацию")
        return None

    try:
        import openai

        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        choice = response.choices[0] if response.choices else None
        return choice.message.content if choice else None

    except Exception as e:
        log.error("openai_api_error", error=str(e))
        return None
