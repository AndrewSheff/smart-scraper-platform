"""Сервис скрапинга — загружает страницу, парсит по селекторам, отдает данные.

Поддерживает CSS и XPath селекторы, умеет доставать текст и атрибуты.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from bs4 import BeautifulSoup
from lxml import etree

from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.models.task_field import TaskField

log = get_logger(__name__)

# Юзер-агент чтоб не банили сходу
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


async def scrape(
    url: str,
    fields: list[TaskField],
    headers: dict[str, str] | None = None,
    timeout: int = 30,
) -> dict[str, str | list[str]]:
    """Загружает страницу и извлекает данные по селекторам.

    Возвращает словарь: имя_поля -> значение (строка или список строк).
    """
    # собираем заголовки — дефолтный UA + кастомные
    request_headers = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        request_headers.update(headers)

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        verify=False,  # noqa: S501 — некоторые сайты с кривыми сертификатами
    ) as client:
        response = await client.get(url, headers=request_headers)
        response.raise_for_status()

    html_content = response.text
    soup = BeautifulSoup(html_content, "lxml")

    result: dict[str, str | list[str]] = {}

    for field in fields:
        try:
            if field.selector_type == "css":
                value = _extract_css(soup, field)
            elif field.selector_type == "xpath":
                value = _extract_xpath(html_content, field)
            else:
                log.warning("unknown_selector_type", selector_type=field.selector_type)
                value = None

            if value is not None:
                result[field.name] = value
            else:
                result[field.name] = [] if field.is_list else ""
        except Exception as e:
            log.warning(
                "field_extraction_failed",
                field_name=field.name,
                selector=field.selector,
                error=str(e),
            )
            result[field.name] = [] if field.is_list else ""

    return result


def _extract_css(soup: BeautifulSoup, field: TaskField) -> str | list[str] | None:
    """Извлекает данные по CSS-селектору — текст или атрибут элемента."""
    elements = soup.select(field.selector)

    if not elements:
        return None

    def _get_value(el) -> str:
        """Достает значение из элемента — атрибут или текст."""
        if field.attribute:
            return el.get(field.attribute, "").strip()
        return el.get_text(strip=True)

    if field.is_list:
        return [_get_value(el) for el in elements]

    return _get_value(elements[0])


def _extract_xpath(html_str: str, field: TaskField) -> str | list[str] | None:
    """Извлекает данные по XPath — для тех случаев когда CSS не хватает."""
    tree = etree.HTML(html_str)
    if tree is None:
        return None

    elements = tree.xpath(field.selector)

    if not elements:
        return None

    def _get_value(el) -> str:
        """Достаем значение из XPath-элемента — тут чуть сложнее чем с CSS."""
        if isinstance(el, str):
            return el.strip()
        if field.attribute:
            return (el.get(field.attribute) or "").strip()
        # текстовое содержимое — tostring с method="text" работает для всех типов элементов
        text = etree.tostring(el, method="text", encoding="unicode")
        return text.strip()

    if field.is_list:
        return [_get_value(el) for el in elements]

    return _get_value(elements[0])
