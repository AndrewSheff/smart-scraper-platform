"""Тесты скрапер-движка — извлечение данных из HTML по селекторам."""

from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from app.services.scraper_service import _extract_css, _extract_xpath

# Тестовый HTML для парсинга
SAMPLE_HTML = """
<html>
<body>
    <div class="product-list">
        <div class="product">
            <h3 class="name">MacBook Pro</h3>
            <span class="price">$1,999</span>
            <a href="/products/1" class="link">Details</a>
        </div>
        <div class="product">
            <h3 class="name">ThinkPad X1</h3>
            <span class="price">$1,449</span>
            <a href="/products/2" class="link">Details</a>
        </div>
        <div class="product">
            <h3 class="name">Dell XPS 15</h3>
            <span class="price">$1,599</span>
            <a href="/products/3" class="link">Details</a>
        </div>
    </div>
    <div class="meta">
        <span id="total">3 items</span>
    </div>
</body>
</html>
"""

SOUP = BeautifulSoup(SAMPLE_HTML, "lxml")


def _make_field(name, selector, selector_type="css", data_type="text", is_list=False, attribute=None):
    """Хелпер для создания мок-поля."""
    field = MagicMock()
    field.name = name
    field.selector = selector
    field.selector_type = selector_type
    field.data_type = data_type
    field.is_list = is_list
    field.attribute = attribute
    return field


class TestCssExtraction:
    """Тесты CSS-селекторов через BeautifulSoup."""

    def test_extract_single_text(self):
        """Извлечение одного текстового элемента."""
        field = _make_field("total", "#total")
        result = _extract_css(SOUP, field)
        assert result == "3 items"

    def test_extract_list_text(self):
        """Извлечение списка текстовых элементов."""
        field = _make_field("names", ".product .name", is_list=True)
        result = _extract_css(SOUP, field)
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == "MacBook Pro"
        assert result[1] == "ThinkPad X1"
        assert result[2] == "Dell XPS 15"

    def test_extract_attribute(self):
        """Извлечение атрибута элемента."""
        field = _make_field("links", ".product .link", is_list=True, attribute="href")
        result = _extract_css(SOUP, field)
        assert result == ["/products/1", "/products/2", "/products/3"]

    def test_extract_prices(self):
        """Извлечение цен как текст."""
        field = _make_field("prices", ".product .price", is_list=True, data_type="number")
        result = _extract_css(SOUP, field)
        assert len(result) == 3
        assert result[0] == "$1,999"

    def test_extract_nonexistent_selector(self):
        """Несуществующий селектор должен вернуть None."""
        field = _make_field("ghost", ".nonexistent")
        result = _extract_css(SOUP, field)
        assert result is None

    def test_extract_nonexistent_list(self):
        """Несуществующий селектор для списка — None (пустой select)."""
        field = _make_field("ghost", ".nonexistent", is_list=True)
        result = _extract_css(SOUP, field)
        assert result is None


class TestXpathExtraction:
    """Тесты XPath-селекторов через lxml."""

    def test_extract_single_xpath(self):
        """Извлечение одного элемента по XPath."""
        field = _make_field("total", "//span[@id='total']", selector_type="xpath")
        result = _extract_xpath(SAMPLE_HTML, field)
        assert result == "3 items"

    def test_extract_list_xpath(self):
        """Извлечение списка по XPath."""
        field = _make_field("names", "//h3[@class='name']", selector_type="xpath", is_list=True)
        result = _extract_xpath(SAMPLE_HTML, field)
        assert isinstance(result, list)
        assert len(result) == 3
        assert "MacBook Pro" in result

    def test_extract_attribute_xpath(self):
        """Извлечение атрибута через XPath."""
        field = _make_field("links", "//a[@class='link']", selector_type="xpath", is_list=True, attribute="href")
        result = _extract_xpath(SAMPLE_HTML, field)
        assert len(result) == 3
        assert result[0] == "/products/1"

    def test_extract_nonexistent_xpath(self):
        """Несуществующий XPath — None."""
        field = _make_field("ghost", "//div[@class='nope']", selector_type="xpath")
        result = _extract_xpath(SAMPLE_HTML, field)
        assert result is None
