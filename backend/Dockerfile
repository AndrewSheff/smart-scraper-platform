# ─── Сборка бэкенда Smart Scraper Platform ───
# Мультистейдж: сначала ставим зависимости, потом копируем код.
# Так кэш слоев не ломается при каждом изменении в app/

# --- стадия зависимостей ---
FROM python:3.13-slim AS dependencies

WORKDIR /opt/app

# ставим системные пакеты, которые нужны для сборки некоторых pip-пакетов
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- финальный образ ---
FROM python:3.13-slim AS runtime

WORKDIR /opt/app

# только рантаймовая зависимость — libpq для asyncpg
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# забираем установленные пакеты из стадии dependencies
COPY --from=dependencies /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# копируем исходники приложения
COPY app/ ./app/
COPY alembic/ ./alembic/

# непривилегированный пользователь — не бегаем от рута
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# запускаем uvicorn, хост 0.0.0.0 чтоб докер мог достучаться
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
