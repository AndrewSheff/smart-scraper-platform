"""Очистка старых запусков — удаляем лишние run-ы чтоб база не разбухала.

Оставляем последние 1000 запусков на каждую задачу, остальное в мусорку.
"""

from sqlalchemy import delete, func, select

from app.core.logging import get_logger

log = get_logger(__name__)


async def cleanup_old_runs() -> None:
    """Удаляет task_runs старше 1000-го на каждую задачу.

    Запускается планировщиком ежедневно в 3:00.
    Работает с отдельной сессией — мы вне контекста запроса.
    """
    from app.database import async_session
    from app.models.task_run import TaskRun

    log.info("cleanup_starting")

    async with async_session() as session:
        try:
            # Берем все task_id у которых больше 1000 запусков
            count_query = (
                select(TaskRun.task_id, func.count(TaskRun.id).label("cnt"))
                .group_by(TaskRun.task_id)
                .having(func.count(TaskRun.id) > 1000)
            )
            result = await session.execute(count_query)
            overflowed_tasks = result.all()

            total_deleted = 0

            for task_id, _count in overflowed_tasks:
                # Находим id 1000-го запуска (по дате, от свежих к старым)
                cutoff_query = (
                    select(TaskRun.id)
                    .where(TaskRun.task_id == task_id)
                    .order_by(TaskRun.created_at.desc())
                    .offset(1000)
                    .limit(1)
                )
                cutoff_result = await session.execute(cutoff_query)
                cutoff_run = cutoff_result.scalar_one_or_none()

                if cutoff_run is None:
                    continue

                # Берем created_at этого run-а для удаления
                cutoff_date_query = select(TaskRun.created_at).where(TaskRun.id == cutoff_run)
                date_result = await session.execute(cutoff_date_query)
                cutoff_date = date_result.scalar_one()

                # Удаляем все запуски старше этой даты для данной задачи
                # CASCADE позаботится о run_results и task_changes
                del_query = delete(TaskRun).where(TaskRun.task_id == task_id).where(TaskRun.created_at <= cutoff_date)
                del_result = await session.execute(del_query)
                total_deleted += del_result.rowcount

            await session.commit()
            log.info("cleanup_finished", deleted_runs=total_deleted, tasks_processed=len(overflowed_tasks))

        except Exception:
            await session.rollback()
            log.exception("cleanup_failed")
        finally:
            await session.close()
