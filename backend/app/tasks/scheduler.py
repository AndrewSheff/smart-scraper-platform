"""Планировщик задач — APScheduler поднимает крон-джобы из базы при старте.

Каждая активная задача получает свой CronTrigger, при срабатывании
вызывается execute_task с отдельной сессией (вне контекста запроса).
"""

import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.logging import get_logger

log = get_logger(__name__)

# Глобальный экземпляр планировщика — один на все приложение
scheduler = AsyncIOScheduler()


def _parse_cron(cron_expr: str) -> dict:
    """Разбирает cron-строку на составляющие для CronTrigger.

    Формат: минута час день месяц день_недели
    Пример: '*/30 * * * *' -> каждые 30 минут
    """
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Кривой cron: '{cron_expr}', нужно 5 частей")

    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }


async def _run_task(task_id: str) -> None:
    """Обертка для запуска задачи — создает свою сессию, т.к. мы вне request-контекста."""
    from app.database import async_session
    from app.services.run_service import execute_task

    log.info("scheduler_trigger", task_id=task_id)
    async with async_session() as session:
        try:
            await execute_task(uuid.UUID(task_id), session)
            await session.commit()
        except Exception:
            await session.rollback()
            log.exception("scheduler_task_failed", task_id=task_id)
        finally:
            await session.close()


def add_task_job(task) -> None:
    """Добавляет (или заменяет) крон-джоб для задачи в планировщике."""
    job_id = f"scraping_task_{task.id}"

    try:
        cron_kwargs = _parse_cron(task.schedule_cron)
    except ValueError:
        log.error("invalid_cron", task_id=str(task.id), cron=task.schedule_cron)
        return

    trigger = CronTrigger(**cron_kwargs)

    # replace_existing=True — если джоб уже есть, просто обновим
    scheduler.add_job(
        _run_task,
        trigger=trigger,
        id=job_id,
        args=[str(task.id)],
        replace_existing=True,
        misfire_grace_time=60,
    )

    log.info("job_added", task_id=str(task.id), cron=task.schedule_cron)


def remove_task_job(task_id: str) -> None:
    """Удаляет джоб задачи из планировщика (если он там есть)."""
    job_id = f"scraping_task_{task_id}"
    try:
        scheduler.remove_job(job_id)
        log.info("job_removed", task_id=task_id)
    except Exception:
        # Джоба может и не быть — ничего страшного
        log.debug("job_not_found_for_removal", task_id=task_id)


def reload_task_job(task) -> None:
    """Удобная обертка — просто переключает на add_task_job.

    По сути то же самое, т.к. add_task_job делает replace_existing.
    """
    add_task_job(task)


async def start_scheduler(app=None) -> None:
    """Запуск планировщика — подгружает все активные задачи и стартует.

    Вызывается из lifespan при запуске приложения.
    """
    from app.database import async_session
    from app.models.scraping_task import ScrapingTask
    from app.tasks.cleanup import cleanup_old_runs

    log.info("scheduler_starting")

    # Загружаем все активные задачи и создаем для них джобы
    async with async_session() as session:
        result = await session.execute(
            select(ScrapingTask).where(ScrapingTask.is_active == True)  # noqa: E712
        )
        active_tasks = result.scalars().all()

        for task in active_tasks:
            add_task_job(task)

        log.info("scheduler_tasks_loaded", count=len(active_tasks))

    # Джоб очистки старых запусков — каждый день в 3 утра
    scheduler.add_job(
        cleanup_old_runs,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_old_runs",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.start()
    log.info("scheduler_started")


async def stop_scheduler() -> None:
    """Останавливает планировщик — вызывается при shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        log.info("scheduler_stopped")
