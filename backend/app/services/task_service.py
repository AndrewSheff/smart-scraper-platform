"""Сервис задач скрапинга — CRUD, пагинация, владелец видит только свое.

Тут управление задачами: создание, редактирование, удаление, переключение.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.scraping_task import ScrapingTask
from app.models.task_field import TaskField
from app.schemas.scraping_task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.tasks.scheduler import add_task_job, remove_task_job

log = get_logger(__name__)


def _escape_like(value: str) -> str:
    """Экранируем спецсимволы LIKE чтоб не было сюрпризов."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def list_tasks(
    user_id: uuid.UUID,
    page: int,
    per_page: int,
    search: str | None,
    is_active: bool | None,
    db: AsyncSession,
) -> TaskListResponse:
    """Список задач юзера с пагинацией, поиском и фильтром по активности."""
    query = select(ScrapingTask).where(ScrapingTask.user_id == user_id)
    count_query = select(func.count(ScrapingTask.id)).where(ScrapingTask.user_id == user_id)

    # поиск по имени или URL
    if search:
        escaped = _escape_like(search)
        pattern = f"%{escaped}%"
        query = query.where(ScrapingTask.name.ilike(pattern) | ScrapingTask.url.ilike(pattern))
        count_query = count_query.where(ScrapingTask.name.ilike(pattern) | ScrapingTask.url.ilike(pattern))

    # фильтр по is_active
    if is_active is not None:
        query = query.where(ScrapingTask.is_active == is_active)
        count_query = count_query.where(ScrapingTask.is_active == is_active)

    # считаем общее количество
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # подтягиваем поля через selectinload (чтоб не было N+1)
    offset = (page - 1) * per_page
    query = (
        query.options(selectinload(ScrapingTask.fields))
        .order_by(ScrapingTask.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )

    result = await db.execute(query)
    tasks = result.scalars().unique().all()

    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        per_page=per_page,
    )


async def get_task(task_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> TaskResponse:
    """Получить задачу по id — проверяем что она принадлежит юзеру."""
    result = await db.execute(
        select(ScrapingTask)
        .options(selectinload(ScrapingTask.fields))
        .where(ScrapingTask.id == task_id, ScrapingTask.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundError("Задача не найдена")

    return TaskResponse.model_validate(task)


async def create_task(user_id: uuid.UUID, data: TaskCreate, db: AsyncSession) -> TaskResponse:
    """Создать задачу с полями — все в одной транзакции."""
    task = ScrapingTask(
        user_id=user_id,
        name=data.name,
        description=data.description,
        url=data.url,
        schedule_cron=data.schedule_cron,
        is_active=data.is_active,
        headers=data.headers,
        timeout_seconds=data.timeout_seconds,
        max_retries=data.max_retries,
        notify_on_change=data.notify_on_change,
        notify_on_error=data.notify_on_error,
        ai_prompt=data.ai_prompt,
    )
    db.add(task)
    await db.flush()

    # создаем поля задачи
    for field_data in data.fields:
        field = TaskField(
            task_id=task.id,
            name=field_data.name,
            selector=field_data.selector,
            selector_type=field_data.selector_type,
            data_type=field_data.data_type,
            is_list=field_data.is_list,
            attribute=field_data.attribute,
            position=field_data.position,
        )
        db.add(field)

    await db.flush()

    # перечитываем с загруженными полями
    result = await db.execute(
        select(ScrapingTask).options(selectinload(ScrapingTask.fields)).where(ScrapingTask.id == task.id)
    )
    task = result.scalar_one()

    log.info("task_created", task_id=str(task.id), user_id=str(user_id))

    # Добавляем джоб в планировщик если задача активна
    if task.is_active:
        add_task_job(task)

    return TaskResponse.model_validate(task)


async def update_task(
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession,
) -> TaskResponse:
    """Обновить задачу — если переданы поля (fields), заменяем все целиком."""
    result = await db.execute(
        select(ScrapingTask)
        .options(selectinload(ScrapingTask.fields))
        .where(ScrapingTask.id == task_id, ScrapingTask.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundError("Задача не найдена")

    # обновляем скалярные поля (кроме fields)
    update_data = data.model_dump(exclude_unset=True, exclude={"fields"})
    for field, value in update_data.items():
        setattr(task, field, value)

    # если переданы новые поля — удаляем старые, создаем новые
    if data.fields is not None:
        # удаляем старые поля
        for old_field in task.fields:
            await db.delete(old_field)

        # создаем новые
        for field_data in data.fields:
            field = TaskField(
                task_id=task.id,
                name=field_data.name,
                selector=field_data.selector,
                selector_type=field_data.selector_type,
                data_type=field_data.data_type,
                is_list=field_data.is_list,
                attribute=field_data.attribute,
                position=field_data.position,
            )
            db.add(field)

    await db.flush()

    # перечитываем с обновленными полями
    result = await db.execute(
        select(ScrapingTask).options(selectinload(ScrapingTask.fields)).where(ScrapingTask.id == task.id)
    )
    task = result.scalar_one()

    log.info("task_updated", task_id=str(task.id))

    # Синхронизируем планировщик — обновляем или убираем джоб
    if task.is_active:
        add_task_job(task)
    else:
        remove_task_job(str(task.id))

    return TaskResponse.model_validate(task)


async def delete_task(task_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict:
    """Удалить задачу — каскад потянет за собой поля и запуски."""
    result = await db.execute(select(ScrapingTask).where(ScrapingTask.id == task_id, ScrapingTask.user_id == user_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundError("Задача не найдена")

    await db.delete(task)
    await db.flush()

    # Убираем джоб из планировщика — задачи больше нет
    remove_task_job(str(task_id))

    log.info("task_deleted", task_id=str(task_id))
    return {"message": "Задача удалена"}


async def toggle_task(task_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> TaskResponse:
    """Переключить статус задачи — active -> inactive и наоборот."""
    result = await db.execute(
        select(ScrapingTask)
        .options(selectinload(ScrapingTask.fields))
        .where(ScrapingTask.id == task_id, ScrapingTask.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundError("Задача не найдена")

    task.is_active = not task.is_active
    await db.flush()

    log.info("task_toggled", task_id=str(task.id), is_active=task.is_active)

    # Включили — добавляем джоб, выключили — убираем
    if task.is_active:
        add_task_job(task)
    else:
        remove_task_job(str(task.id))

    return TaskResponse.model_validate(task)
