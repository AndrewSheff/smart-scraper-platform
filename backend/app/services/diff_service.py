"""Сервис сравнения результатов — находит разницу между двумя запусками.

Умеет определять добавленные, удаленные и измененные значения.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.run_result import RunResult
    from app.models.task_field import TaskField


def compute_diff(
    prev_results: list[RunResult],
    curr_data: dict[str, str | list[str]],
    fields: list[TaskField],
) -> list[dict]:
    """Сравнивает предыдущие результаты с текущими данными.

    Возвращает список изменений в формате:
    [{"change_type": "modified", "field_name": "...", "old_value": "...", "new_value": "...", "item_index": 0}]
    """
    changes: list[dict] = []

    # собираем предыдущие результаты в удобную структуру: field_name -> {index: value}
    prev_map: dict[str, dict[int, str | None]] = {}
    for r in prev_results:
        if r.field_name not in prev_map:
            prev_map[r.field_name] = {}
        prev_map[r.field_name][r.field_index] = r.field_value

    # карта полей для быстрого поиска
    field_map = {f.name: f for f in fields}

    for field_name, curr_value in curr_data.items():
        field = field_map.get(field_name)
        if field is None:
            continue

        prev_field_data = prev_map.get(field_name, {})

        if field.is_list and isinstance(curr_value, list):
            # для списковых полей сравниваем поэлементно
            _diff_list(changes, field_name, prev_field_data, curr_value)
        else:
            # для скалярных — простое сравнение
            curr_str = curr_value if isinstance(curr_value, str) else str(curr_value)
            old_str = prev_field_data.get(0)

            if old_str is None and curr_str:
                changes.append(
                    {
                        "change_type": "added",
                        "field_name": field_name,
                        "old_value": None,
                        "new_value": curr_str,
                        "item_index": 0,
                    }
                )
            elif old_str is not None and not curr_str:
                changes.append(
                    {
                        "change_type": "removed",
                        "field_name": field_name,
                        "old_value": old_str,
                        "new_value": None,
                        "item_index": 0,
                    }
                )
            elif old_str != curr_str:
                changes.append(
                    {
                        "change_type": "modified",
                        "field_name": field_name,
                        "old_value": old_str,
                        "new_value": curr_str,
                        "item_index": 0,
                    }
                )

    # проверяем поля которые были раньше, но пропали из текущих данных
    for field_name, prev_values in prev_map.items():
        if field_name not in curr_data:
            for idx, old_val in prev_values.items():
                changes.append(
                    {
                        "change_type": "removed",
                        "field_name": field_name,
                        "old_value": old_val,
                        "new_value": None,
                        "item_index": idx,
                    }
                )

    return changes


def _diff_list(
    changes: list[dict],
    field_name: str,
    prev_data: dict[int, str | None],
    curr_list: list[str],
) -> None:
    """Сравнивает списковое поле — поэлементно по индексу."""
    max_len = max(len(curr_list), max(prev_data.keys(), default=-1) + 1)

    for idx in range(max_len):
        old_val = prev_data.get(idx)
        new_val = curr_list[idx] if idx < len(curr_list) else None

        if old_val is None and new_val is not None:
            changes.append(
                {
                    "change_type": "added",
                    "field_name": field_name,
                    "old_value": None,
                    "new_value": new_val,
                    "item_index": idx,
                }
            )
        elif old_val is not None and new_val is None:
            changes.append(
                {
                    "change_type": "removed",
                    "field_name": field_name,
                    "old_value": old_val,
                    "new_value": None,
                    "item_index": idx,
                }
            )
        elif old_val != new_val:
            changes.append(
                {
                    "change_type": "modified",
                    "field_name": field_name,
                    "old_value": old_val,
                    "new_value": new_val,
                    "item_index": idx,
                }
            )
