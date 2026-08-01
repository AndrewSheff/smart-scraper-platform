"""Сервис запусков — полный пайплайн: скрапинг, сохранение, диф, AI, уведомления.

Тут самая мясная логика — координирует весь процесс от запуска до результата.
"""

import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.run_result import RunResult
from app.models.scraping_task import ScrapingTask
from app.models.task_change import TaskChange
from app.models.task_run import TaskRun
from app.schemas.scraping_task import PreviewRequest, PreviewResponse
from app.schemas.task_run import TaskRunDetailResponse, TaskRunListResponse, TaskRunResponse
from app.services import ai_service, diff_service, notification_service, scraper_service

log = get_logger(__name__)


async def execute_task(task_id: uuid.UUID, db: AsyncSession) -> TaskRunResponse:
    """Полный пайплайн выполнения задачи скрапинга.

    1. Создаем TaskRun со статусом pending
    2. Запускаем скрапер
    3. Сохраняем результаты
    4. Сравниваем с предыдущим запуском
    5. Генерим AI-саммари если есть изменения
    6. Отправляем уведомление
    """
    # достаем задачу с полями и юзером
    result = await db.execute(
        select(ScrapingTask)
        .options(
            selectinload(ScrapingTask.fields),
            selectinload(ScrapingTask.user),
        )
        .where(ScrapingTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundError("Задача не найдена")

    # создаем запись о запуске
    run = TaskRun(task_id=task.id, status="running")
    db.add(run)
    await db.flush()

    start_time = time.time()

    try:
        # скрапим
        scraped_data = await scraper_service.scrape(
            url=task.url,
            fields=list(task.fields),
            headers=task.headers,
            timeout=task.timeout_seconds,
        )

        # сохраняем результаты
        items_count = 0
        for field_name, value in scraped_data.items():
            if isinstance(value, list):
                for idx, v in enumerate(value):
                    db.add(
                        RunResult(
                            run_id=run.id,
                            field_name=field_name,
                            field_value=v,
                            field_index=idx,
                        )
                    )
                    items_count += 1
            else:
                db.add(
                    RunResult(
                        run_id=run.id,
                        field_name=field_name,
                        field_value=value,
                        field_index=0,
                    )
                )
                items_count += 1

        # достаем предыдущий успешный запуск для сравнения
        prev_run_result = await db.execute(
            select(TaskRun)
            .options(selectinload(TaskRun.results))
            .where(
                TaskRun.task_id == task.id,
                TaskRun.status == "success",
                TaskRun.id != run.id,
            )
            .order_by(TaskRun.started_at.desc())
            .limit(1)
        )
        prev_run = prev_run_result.scalar_one_or_none()

        has_changes = False
        changes_list: list[dict] = []

        if prev_run and prev_run.results:
            # считаем разницу
            changes_list = diff_service.compute_diff(
                prev_results=list(prev_run.results),
                curr_data=scraped_data,
                fields=list(task.fields),
            )

            if changes_list:
                has_changes = True
                for change in changes_list:
                    db.add(
                        TaskChange(
                            run_id=run.id,
                            change_type=change["change_type"],
                            field_name=change["field_name"],
                            old_value=change.get("old_value"),
                            new_value=change.get("new_value"),
                            item_index=change.get("item_index", 0),
                        )
                    )

        # генерим AI-саммари если есть изменения и есть что суммаризировать
        ai_summary = None
        if has_changes:
            try:
                ai_summary = await ai_service.generate_summary(
                    task_name=task.name,
                    url=task.url,
                    changes=changes_list,
                    custom_prompt=task.ai_prompt,
                )
            except Exception as e:
                log.warning("ai_summary_failed", error=str(e))

        # финализируем запуск
        duration_ms = int((time.time() - start_time) * 1000)
        run.status = "success"
        run.finished_at = datetime.now(UTC)
        run.duration_ms = duration_ms
        run.items_count = items_count
        run.has_changes = has_changes
        run.ai_summary = ai_summary

        # обновляем статистику задачи
        task.last_run_at = datetime.now(UTC)
        task.last_status = "success"
        task.total_runs += 1
        task.success_runs += 1

        await db.flush()

        # отправляем уведомление если есть изменения
        if has_changes and task.notify_on_change and task.user:
            try:
                await notification_service.send_change_notification(
                    user=task.user,
                    task=task,
                    summary=ai_summary or "Обнаружены изменения на странице",
                )
            except Exception as e:
                log.warning("notification_failed", error=str(e))

        log.info(
            "task_executed",
            task_id=str(task.id),
            duration_ms=duration_ms,
            items_count=items_count,
            has_changes=has_changes,
        )

    except Exception as e:
        # ошибка — фиксируем в запуске
        duration_ms = int((time.time() - start_time) * 1000)
        run.status = "failed"
        run.finished_at = datetime.now(UTC)
        run.duration_ms = duration_ms
        run.error_message = str(e)

        task.last_run_at = datetime.now(UTC)
        task.last_status = "failed"
        task.total_runs += 1

        await db.flush()

        # уведомляем об ошибке
        if task.notify_on_error and task.user:
            try:
                await notification_service.send_error_notification(
                    user=task.user,
                    task=task,
                    error=str(e),
                )
            except Exception as notify_err:
                log.warning("error_notification_failed", error=str(notify_err))

        log.error("task_execution_failed", task_id=str(task.id), error=str(e))

    return TaskRunResponse.model_validate(run)


async def get_runs(
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    page: int,
    per_page: int,
    db: AsyncSession,
) -> TaskRunListResponse:
    """Список запусков задачи с пагинацией — проверяем владельца."""
    # проверяем что задача принадлежит юзеру
    task_result = await db.execute(
        select(ScrapingTask.id).where(ScrapingTask.id == task_id, ScrapingTask.user_id == user_id)
    )
    if task_result.scalar_one_or_none() is None:
        raise NotFoundError("Задача не найдена")

    # считаем общее количество
    count_result = await db.execute(select(func.count(TaskRun.id)).where(TaskRun.task_id == task_id))
    total = count_result.scalar() or 0

    # берем нужную страницу
    offset = (page - 1) * per_page
    runs_result = await db.execute(
        select(TaskRun)
        .where(TaskRun.task_id == task_id)
        .order_by(TaskRun.started_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    runs = runs_result.scalars().all()

    return TaskRunListResponse(
        items=[TaskRunResponse.model_validate(r) for r in runs],
        total=total,
        page=page,
        per_page=per_page,
    )


async def get_run_detail(run_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> TaskRunDetailResponse:
    """Детали запуска — с результатами и изменениями."""
    result = await db.execute(
        select(TaskRun)
        .options(
            selectinload(TaskRun.results),
            selectinload(TaskRun.changes),
            selectinload(TaskRun.task),
        )
        .where(TaskRun.id == run_id)
    )
    run = result.scalar_one_or_none()

    if run is None:
        raise NotFoundError("Запуск не найден")

    # проверяем что задача принадлежит юзеру
    if run.task.user_id != user_id:
        raise NotFoundError("Запуск не найден")

    return TaskRunDetailResponse.model_validate(run)


async def preview_task(data: PreviewRequest) -> PreviewResponse:
    """Предпросмотр — запускаем скрапер без сохранения, полезно при настройке."""
    from app.models.task_field import TaskField as TaskFieldModel

    start_time = time.time()

    # превращаем pydantic-схемы полей в объекты, которые понимает скрапер
    mock_fields = []
    for f in data.fields:
        field = TaskFieldModel(
            name=f.name,
            selector=f.selector,
            selector_type=f.selector_type,
            data_type=f.data_type,
            is_list=f.is_list,
            attribute=f.attribute,
            position=f.position,
        )
        mock_fields.append(field)

    try:
        scraped_data = await scraper_service.scrape(
            url=data.url,
            fields=mock_fields,
            headers=data.headers,
            timeout=data.timeout_seconds,
        )
        duration_ms = int((time.time() - start_time) * 1000)

        return PreviewResponse(
            success=True,
            data=scraped_data,
            duration_ms=duration_ms,
        )
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return PreviewResponse(
            success=False,
            error=str(e),
            duration_ms=duration_ms,
        )
