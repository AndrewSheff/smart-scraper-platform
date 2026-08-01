"""Тесты diff-движка — сравнение результатов между запусками."""

from unittest.mock import MagicMock

from app.services.diff_service import compute_diff


def _make_result(field_name, field_value, field_index=0):
    """Хелпер для мок-результата."""
    r = MagicMock()
    r.field_name = field_name
    r.field_value = field_value
    r.field_index = field_index
    return r


def _make_field(name, is_list=False):
    """Хелпер для мок-поля."""
    f = MagicMock()
    f.name = name
    f.is_list = is_list
    return f


class TestDiffService:
    """Тесты вычисления diff между запусками."""

    def test_no_changes(self):
        """Если данные не изменились — пустой diff."""
        prev = [_make_result("title", "Hello")]
        curr = {"title": "Hello"}
        fields = [_make_field("title")]
        changes = compute_diff(prev, curr, fields)
        assert changes == []

    def test_modified_value(self):
        """Измененное значение должно детектиться как modified."""
        prev = [_make_result("price", "$100")]
        curr = {"price": "$85"}
        fields = [_make_field("price")]
        changes = compute_diff(prev, curr, fields)
        assert len(changes) == 1
        assert changes[0]["change_type"] == "modified"
        assert changes[0]["old_value"] == "$100"
        assert changes[0]["new_value"] == "$85"

    def test_added_field(self):
        """Новое поле должно детектиться как added."""
        prev = []
        curr = {"title": "New Item"}
        fields = [_make_field("title")]
        changes = compute_diff(prev, curr, fields)
        assert len(changes) == 1
        assert changes[0]["change_type"] == "added"
        assert changes[0]["new_value"] == "New Item"

    def test_removed_field(self):
        """Удаленное поле должно детектиться как removed."""
        prev = [_make_result("title", "Old Item")]
        curr = {}
        fields = [_make_field("title")]
        changes = compute_diff(prev, curr, fields)
        assert len(changes) == 1
        assert changes[0]["change_type"] == "removed"
        assert changes[0]["old_value"] == "Old Item"

    def test_list_added_items(self):
        """Новые элементы в списке должны быть added."""
        prev = [
            _make_result("name", "Item A", 0),
            _make_result("name", "Item B", 1),
        ]
        curr = {"name": ["Item A", "Item B", "Item C"]}
        fields = [_make_field("name", is_list=True)]
        changes = compute_diff(prev, curr, fields)
        assert any(c["change_type"] == "added" and c["new_value"] == "Item C" for c in changes)

    def test_list_removed_items(self):
        """Удаленные элементы списка должны быть removed."""
        prev = [
            _make_result("name", "Item A", 0),
            _make_result("name", "Item B", 1),
            _make_result("name", "Item C", 2),
        ]
        curr = {"name": ["Item A", "Item B"]}
        fields = [_make_field("name", is_list=True)]
        changes = compute_diff(prev, curr, fields)
        assert any(c["change_type"] == "removed" and c["old_value"] == "Item C" for c in changes)

    def test_list_modified_items(self):
        """Измененные элементы списка должны быть modified."""
        prev = [
            _make_result("price", "$100", 0),
            _make_result("price", "$200", 1),
        ]
        curr = {"price": ["$100", "$150"]}
        fields = [_make_field("price", is_list=True)]
        changes = compute_diff(prev, curr, fields)
        assert len(changes) == 1
        assert changes[0]["change_type"] == "modified"
        assert changes[0]["old_value"] == "$200"
        assert changes[0]["new_value"] == "$150"

    def test_empty_prev_and_curr(self):
        """Пустые данные с обеих сторон — пустой diff."""
        changes = compute_diff([], {}, [])
        assert changes == []

    def test_multiple_fields(self):
        """Diff по нескольким полям одновременно."""
        prev = [
            _make_result("title", "Old Title"),
            _make_result("price", "$100"),
        ]
        curr = {"title": "New Title", "price": "$100"}
        fields = [_make_field("title"), _make_field("price")]
        changes = compute_diff(prev, curr, fields)
        assert len(changes) == 1
        assert changes[0]["field_name"] == "title"
