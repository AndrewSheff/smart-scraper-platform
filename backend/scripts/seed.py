"""Скрипт для создания демо-данных — задачи скрапинга, запуски, результаты.

Запускать из корня бэкенда: python -m scripts.seed
"""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.security import hash_password
from app.models.run_result import RunResult
from app.models.scraping_task import ScrapingTask
from app.models.task_change import TaskChange
from app.models.task_field import TaskField
from app.models.task_run import TaskRun
from app.models.user import User


async def seed() -> None:
    """Закидываем демо-данные в базу — юзеры, задачи, запуски, результаты."""
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        # Проверяем, есть ли уже юзеры
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("База уже содержит данные, пропускаем seed")
            return

        await _create_seed_data(db)
        await db.commit()
        print("Демо-данные успешно созданы!")

    await engine.dispose()


async def _create_seed_data(db: AsyncSession) -> None:
    """Создаем набор демо-данных — мониторинг цен, вакансий, погоды."""
    # Админ
    admin = User(
        id=uuid.uuid4(),
        email="admin@admin.com",
        hashed_password=hash_password("admin123"),
        name="Admin",
        role="admin",
        is_active=True,
        must_change_password=False,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )
    db.add(admin)

    # Обычный юзер
    demo_user = User(
        id=uuid.uuid4(),
        email="demo@example.com",
        hashed_password=hash_password("demo1234"),
        name="Demo User",
        role="user",
        is_active=True,
        must_change_password=False,
    )
    db.add(demo_user)

    now = datetime.now(UTC)

    # --- Задача 1: Мониторинг цен на электронику ---
    task1 = ScrapingTask(
        id=uuid.uuid4(),
        user_id=demo_user.id,
        name="Electronics Price Monitor",
        description="Tracking laptop prices on a tech store to catch deals",
        url="https://example.com/laptops",
        schedule_cron="0 */6 * * *",
        is_active=True,
        timeout_seconds=30,
        max_retries=2,
        notify_on_change=True,
        notify_on_error=True,
        last_run_at=now - timedelta(hours=2),
        last_status="success",
        total_runs=48,
        success_runs=45,
    )
    db.add(task1)

    # Поля задачи 1
    fields1 = [
        TaskField(
            task_id=task1.id,
            name="product_name",
            selector=".product-card h3",
            selector_type="css",
            data_type="text",
            is_list=True,
            position=0,
        ),
        TaskField(
            task_id=task1.id,
            name="price",
            selector=".product-card .price",
            selector_type="css",
            data_type="number",
            is_list=True,
            position=1,
        ),
        TaskField(
            task_id=task1.id,
            name="availability",
            selector=".product-card .stock-status",
            selector_type="css",
            data_type="text",
            is_list=True,
            position=2,
        ),
        TaskField(
            task_id=task1.id,
            name="product_url",
            selector=".product-card a",
            selector_type="css",
            data_type="url",
            is_list=True,
            attribute="href",
            position=3,
        ),
    ]
    for f in fields1:
        db.add(f)

    # --- Задача 2: Мониторинг вакансий ---
    task2 = ScrapingTask(
        id=uuid.uuid4(),
        user_id=demo_user.id,
        name="Python Developer Jobs",
        description="Monitoring new Python/FastAPI job postings",
        url="https://example.com/jobs/python",
        schedule_cron="0 */2 * * *",
        is_active=True,
        timeout_seconds=30,
        max_retries=2,
        notify_on_change=True,
        notify_on_error=False,
        last_run_at=now - timedelta(hours=1),
        last_status="success",
        total_runs=120,
        success_runs=118,
    )
    db.add(task2)

    fields2 = [
        TaskField(
            task_id=task2.id,
            name="title",
            selector=".job-listing h2",
            selector_type="css",
            data_type="text",
            is_list=True,
            position=0,
        ),
        TaskField(
            task_id=task2.id,
            name="company",
            selector=".job-listing .company-name",
            selector_type="css",
            data_type="text",
            is_list=True,
            position=1,
        ),
        TaskField(
            task_id=task2.id,
            name="salary",
            selector=".job-listing .salary",
            selector_type="css",
            data_type="text",
            is_list=True,
            position=2,
        ),
        TaskField(
            task_id=task2.id,
            name="link",
            selector=".job-listing a.apply-link",
            selector_type="css",
            data_type="url",
            is_list=True,
            attribute="href",
            position=3,
        ),
    ]
    for f in fields2:
        db.add(f)

    # --- Задача 3: Статус сервисов ---
    task3 = ScrapingTask(
        id=uuid.uuid4(),
        user_id=demo_user.id,
        name="Service Status Page",
        description="Monitoring uptime status of critical services",
        url="https://example.com/status",
        schedule_cron="*/10 * * * *",
        is_active=True,
        timeout_seconds=15,
        max_retries=3,
        notify_on_change=True,
        notify_on_error=True,
        last_run_at=now - timedelta(minutes=5),
        last_status="success",
        total_runs=432,
        success_runs=430,
    )
    db.add(task3)

    fields3 = [
        TaskField(
            task_id=task3.id,
            name="service_name",
            selector="//div[@class='service']/span[@class='name']",
            selector_type="xpath",
            data_type="text",
            is_list=True,
            position=0,
        ),
        TaskField(
            task_id=task3.id,
            name="status",
            selector="//div[@class='service']/span[@class='status']",
            selector_type="xpath",
            data_type="text",
            is_list=True,
            position=1,
        ),
    ]
    for f in fields3:
        db.add(f)

    # --- Задача 4: Неактивная (для разнообразия) ---
    task4 = ScrapingTask(
        id=uuid.uuid4(),
        user_id=demo_user.id,
        name="Crypto Prices (Paused)",
        description="Was tracking BTC/ETH prices, paused for now",
        url="https://example.com/crypto",
        schedule_cron="*/5 * * * *",
        is_active=False,
        timeout_seconds=20,
        max_retries=1,
        notify_on_change=True,
        notify_on_error=False,
        last_run_at=now - timedelta(days=3),
        last_status="success",
        total_runs=200,
        success_runs=195,
    )
    db.add(task4)

    fields4 = [
        TaskField(
            task_id=task4.id,
            name="coin",
            selector=".crypto-row .name",
            selector_type="css",
            data_type="text",
            is_list=True,
            position=0,
        ),
        TaskField(
            task_id=task4.id,
            name="price_usd",
            selector=".crypto-row .price",
            selector_type="css",
            data_type="number",
            is_list=True,
            position=1,
        ),
    ]
    for f in fields4:
        db.add(f)

    # --- Запуски для задачи 1 (последние 5) ---
    product_names = ["MacBook Pro 14", "ThinkPad X1 Carbon", "Dell XPS 15", "ASUS ROG Zephyrus"]
    prices_history = [
        ["$1,999", "$1,449", "$1,599", "$1,899"],
        ["$1,999", "$1,449", "$1,549", "$1,899"],  # Dell подешевел
        ["$1,949", "$1,449", "$1,549", "$1,899"],  # MacBook подешевел
        ["$1,949", "$1,449", "$1,549", "$1,849"],  # ASUS подешевел
        ["$1,949", "$1,399", "$1,549", "$1,849"],  # ThinkPad подешевел
    ]

    prev_run = None
    for i in range(5):
        run_time = now - timedelta(hours=(4 - i) * 6)
        has_changes = i > 0
        run = TaskRun(
            id=uuid.uuid4(),
            task_id=task1.id,
            status="success",
            started_at=run_time,
            finished_at=run_time + timedelta(seconds=2),
            duration_ms=2100 + i * 100,
            items_count=4,
            has_changes=has_changes,
            ai_summary=f"Price changes detected: {'1 item dropped in price' if has_changes else 'No changes'}"
            if has_changes
            else None,
        )
        db.add(run)

        for j, name in enumerate(product_names):
            db.add(RunResult(run_id=run.id, field_name="product_name", field_value=name, field_index=j))
            db.add(RunResult(run_id=run.id, field_name="price", field_value=prices_history[i][j], field_index=j))
            db.add(RunResult(run_id=run.id, field_name="availability", field_value="In Stock", field_index=j))
            db.add(
                RunResult(
                    run_id=run.id,
                    field_name="product_url",
                    field_value=f"https://example.com/laptops/{j + 1}",
                    field_index=j,
                )
            )

        # Добавляем изменения для запусков с has_changes
        if has_changes and i == 1:
            db.add(
                TaskChange(
                    run_id=run.id,
                    change_type="modified",
                    field_name="price",
                    old_value="$1,599",
                    new_value="$1,549",
                    item_index=2,
                )
            )
        elif has_changes and i == 2:
            db.add(
                TaskChange(
                    run_id=run.id,
                    change_type="modified",
                    field_name="price",
                    old_value="$1,999",
                    new_value="$1,949",
                    item_index=0,
                )
            )

        prev_run = run  # noqa: F841

    # --- Пара фейловых запусков для задачи 2 ---
    failed_run = TaskRun(
        id=uuid.uuid4(),
        task_id=task2.id,
        status="failed",
        started_at=now - timedelta(hours=5),
        finished_at=now - timedelta(hours=5) + timedelta(seconds=31),
        duration_ms=31000,
        items_count=0,
        error_message="Connection timeout after 30s",
        has_changes=False,
    )
    db.add(failed_run)

    success_run = TaskRun(
        id=uuid.uuid4(),
        task_id=task2.id,
        status="success",
        started_at=now - timedelta(hours=1),
        finished_at=now - timedelta(hours=1) + timedelta(seconds=3),
        duration_ms=3200,
        items_count=6,
        has_changes=True,
        ai_summary=(
            "2 new Python developer positions posted: Senior FastAPI Developer"
            " at TechCorp ($150k-180k) and Backend Lead at StartupXYZ ($130k-160k)."
        ),
    )
    db.add(success_run)

    jobs = [
        ("Senior FastAPI Developer", "TechCorp", "$150k-180k"),
        ("Backend Lead", "StartupXYZ", "$130k-160k"),
        ("Python Engineer", "DataFlow Inc", "$120k-150k"),
        ("Django Developer", "WebAgency", "$100k-130k"),
        ("ML Engineer (Python)", "AI Labs", "$160k-200k"),
        ("DevOps + Python", "CloudScale", "$140k-170k"),
    ]
    for j, (title, company, salary) in enumerate(jobs):
        db.add(RunResult(run_id=success_run.id, field_name="title", field_value=title, field_index=j))
        db.add(RunResult(run_id=success_run.id, field_name="company", field_value=company, field_index=j))
        db.add(RunResult(run_id=success_run.id, field_name="salary", field_value=salary, field_index=j))
        db.add(
            RunResult(
                run_id=success_run.id, field_name="link", field_value=f"https://example.com/jobs/{j + 1}", field_index=j
            )
        )

    # Новые вакансии
    db.add(
        TaskChange(
            run_id=success_run.id,
            change_type="added",
            field_name="title",
            old_value=None,
            new_value="Senior FastAPI Developer",
            item_index=0,
        )
    )
    db.add(
        TaskChange(
            run_id=success_run.id,
            change_type="added",
            field_name="title",
            old_value=None,
            new_value="Backend Lead",
            item_index=1,
        )
    )

    # --- Задача админа ---
    admin_task = ScrapingTask(
        id=uuid.uuid4(),
        user_id=admin.id,
        name="System Health Monitor",
        description="Admin monitoring task for internal services",
        url="https://example.com/health-dashboard",
        schedule_cron="*/5 * * * *",
        is_active=True,
        timeout_seconds=10,
        max_retries=3,
        total_runs=1000,
        success_runs=998,
        last_run_at=now - timedelta(minutes=2),
        last_status="success",
    )
    db.add(admin_task)

    db.add(
        TaskField(
            task_id=admin_task.id,
            name="status",
            selector=".health-status",
            selector_type="css",
            data_type="text",
            position=0,
        )
    )
    db.add(
        TaskField(
            task_id=admin_task.id,
            name="uptime",
            selector=".uptime-value",
            selector_type="css",
            data_type="text",
            position=1,
        )
    )

    print("  Создано 2 пользователя (admin, demo)")
    print("  Создано 5 задач скрапинга (4 у demo, 1 у admin)")
    print("  Создано 7 запусков с результатами и изменениями")


if __name__ == "__main__":
    asyncio.run(seed())
