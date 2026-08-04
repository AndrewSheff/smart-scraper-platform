<div align="center">

# Smart Scraper Platform

### Web Scraping SaaS with Scheduling, Change Detection & AI Summaries

[![CI/CD](https://github.com/AndrewSheff/smart-scraper-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AndrewSheff/smart-scraper-platform/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript 5.7](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Monitor any website for changes automatically.**
Define CSS/XPath selectors, set a cron schedule, and get Telegram notifications with AI-powered change summaries when data changes.

[Quick Start](#-quick-start) &bull; [Features](#-features) &bull; [Architecture](#-architecture) &bull; [API](#-api-documentation) &bull; [Screenshots](#-screenshots)

</div>

---

## The Problem

> Businesses manually check competitor prices, product availability, regulatory updates, and job listings -- spending **hours on repetitive copy-paste work**. When critical changes happen (price drops, new regulations, stock availability), the delay costs money. Existing scraping tools are either too technical (Scrapy, Puppeteer) or too expensive (SaaS at $100+/month).

**Smart Scraper Platform** solves this with a visual, self-hosted scraping SaaS. Users configure what to scrape through a web UI (no code needed), set a cron schedule, and receive intelligent notifications when data changes -- complete with AI-generated summaries of what exactly changed and why it matters.

**Key metrics:**
- 10,400+ lines of production-ready code
- 31 API endpoints with Swagger documentation
- 6 database models with Alembic migrations
- 13 admin panel pages
- 48+ automated tests across 12 test files
- Built-in diff engine for change detection
- AI summaries via Claude / GPT
- Telegram notifications
- CI/CD pipeline with GitHub Actions
- Docker Compose: one command to deploy

---

## Screenshots

| Login | Dashboard | Tasks |
|:-----:|:---------:|:-----:|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) | ![Tasks](screenshots/tasks.png) |

| Task Detail | Run Results | Notifications |
|:-----------:|:-----------:|:-------------:|
| ![Task](screenshots/task-detail.png) | ![Run](screenshots/run-detail.png) | ![Notifications](screenshots/notifications.png) |

---

## Features

### Visual Task Builder
Create scraping tasks through a web UI -- no coding required. Define the target URL, add fields with CSS or XPath selectors, set custom headers, and preview results before saving.

### Cron Scheduling
Set flexible cron schedules (every 5 minutes to once a month). APScheduler runs tasks in the background. View execution history, success/failure status, and retry on errors.

### Intelligent Change Detection
Built-in diff engine compares new results with previous runs. Detects added, removed, and modified values. Tracks changes over time with full history.

### AI-Powered Summaries
After each run, Claude or GPT analyzes the extracted data and generates a human-readable summary: what changed, what's important, and recommended actions. Configurable prompts per task.

### Telegram Notifications
Get instant Telegram alerts when monitored data changes. Includes the AI summary, specific field changes, and a link to the full report. Configurable per-task (notify on all changes, errors only, or never).

### Excel Export
Export task results and change history to Excel (XLSX). Summary reports across all tasks or detailed per-task exports with charts.

### Multi-User & RBAC
User registration with email. Admin role manages users, views all tasks. Regular users see only their own data. JWT authentication with refresh tokens.

### Production Infrastructure
Multi-stage Docker builds, Nginx reverse proxy with security headers (CSP, HSTS, X-Frame-Options), Redis rate limiting, structured JSON logging, health checks on all services.

---

## Architecture

```
                          +------------------+
                          |   Nginx:80       |
                          |  Reverse Proxy   |
                          |  Security Headers|
                          +--------+---------+
                                   |
                    +--------------+--------------+
                    |                             |
            +-------+-------+           +--------+--------+
            | Frontend:3000 |           |  Backend:8000   |
            |  React 19 SPA |           |  FastAPI        |
            |  Radix UI     |           +---+----+----+---+
            +---------------+               |    |    |
                                +-----------+    |    +----------+
                                |                |               |
                       +--------+---+   +--------+-----+  +-----+------+
                       | PostgreSQL |   |    Redis     |  | APScheduler|
                       |   :5432    |   |    :6379     |  | Cron Jobs  |
                       |  6 models  |   |  Rate Limit  |  +-----+------+
                       +------------+   +--------------+        |
                                                          +-----+------+
                                                          | Scraper    |
                                                          | httpx +    |
                                                          | BeautifulSoup
                                                          +-----+------+
                                                                |
                                                          +-----+------+
                                                          | Diff Engine|
                                                          | AI Summary |
                                                          | Telegram   |
                                                          +------------+
```

### Scraping Pipeline

```
Task scheduled (cron)
        |
        v
  [httpx fetch URL] -- custom headers, User-Agent, follow redirects
        |
        v
  [BeautifulSoup / lxml parse HTML]
        |
        v
  [Extract fields] -- CSS selectors or XPath, text or attributes
        |
        v
  [Diff engine] -- compare with previous run results
        |                    |
        |               No changes --> save run, done
        |
  Changes detected
        |
        v
  [AI summary] -- Claude/GPT analyzes changes, generates human-readable report
        |
        v
  [Telegram notification] -- send alert with summary and link to details
        |
        v
  [Save to DB] -- run result, changes, AI summary
```

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Python, FastAPI, SQLAlchemy (async), Alembic | 3.13, 0.115, 2.0 |
| **Scraping** | httpx, BeautifulSoup, lxml | Async HTTP + parsing |
| **Frontend** | React, TypeScript, Vite, TailwindCSS, Radix UI | 19, 5.7, 8.2, 4.3 |
| **Database** | PostgreSQL | 16 |
| **Cache** | Redis | 7 |
| **Scheduling** | APScheduler | Cron triggers |
| **AI** | Anthropic Claude, OpenAI GPT | Latest |
| **Notifications** | aiogram (Telegram Bot API) | 3.x |
| **Auth** | JWT (access + refresh) + bcrypt | HS256 |
| **Export** | openpyxl | XLSX generation |
| **Infra** | Docker Compose, Nginx, GitHub Actions | Multi-stage |
| **Logging** | structlog (JSON) | Request tracing |
| **Testing** | Pytest (async), 48+ tests | 12 test files |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose v2+
- (Optional) Anthropic or OpenAI API key for AI summaries
- (Optional) Telegram bot token for notifications

### 1. Clone and configure

```bash
git clone https://github.com/AndrewSheff/smart-scraper-platform.git
cd smart-scraper-platform
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-random-64-char-secret-key-here
ADMIN_DEFAULT_PASSWORD=SecurePass123
ANTHROPIC_API_KEY=sk-ant-...     # optional, for AI summaries
OPENAI_API_KEY=sk-...            # optional, alternative AI provider
```

### 2. Launch

```bash
docker compose up -d
```

### 3. Access

| Service | URL |
|---------|-----|
| Application | http://localhost |
| API Docs (Swagger) | http://localhost/docs |
| Health Check | http://localhost/api/v1/health |

Login with `admin@company.com` / password from `.env`.

### 4. Create your first scraping task

1. Go to **Tasks** and click **New Task**
2. Enter a URL to monitor (e.g., a product page)
3. Add fields with CSS selectors (e.g., `.price`, `h1.title`)
4. Click **Preview** to test selectors
5. Set a cron schedule (e.g., every hour)
6. Enable Telegram notifications (optional)
7. Save and watch the results come in

---

## API Documentation

Interactive Swagger documentation at `/docs`. **31 endpoints** across 8 groups:

| Group | Prefix | Description |
|-------|--------|-------------|
| **Auth** | `/api/v1/auth` | Register, login, refresh, change password, profile |
| **Tasks** | `/api/v1/tasks` | CRUD, preview, run now, toggle active |
| **Runs** | `/api/v1/runs` | Run history, results, changes |
| **Users** | `/api/v1/users` | Admin user management |
| **Dashboard** | `/api/v1/dashboard` | Stats, charts, recent runs |
| **Export** | `/api/v1/export` | Excel export (per-task, summary) |
| **Notifications** | `/api/v1/notifications` | Telegram settings, test send |
| **Health** | `/api/v1/health` | Liveness and readiness probe |

All endpoints use Pydantic v2 validation, structured error responses, and Redis-backed rate limiting.

---

## Project Structure

```
smart-scraper-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app with lifespan
│   │   ├── config.py                # Pydantic settings from .env
│   │   ├── database.py              # Async SQLAlchemy engine
│   │   ├── api/v1/                  # 8 REST API routers
│   │   ├── models/                  # 6 SQLAlchemy models
│   │   ├── schemas/                 # Pydantic v2 schemas
│   │   ├── services/                # Business logic (11 files)
│   │   │   ├── scraper_service.py   # httpx + BeautifulSoup extraction
│   │   │   ├── diff_service.py      # Change detection algorithm
│   │   │   ├── ai_service.py        # Claude/GPT integration
│   │   │   ├── run_service.py       # Scraping pipeline orchestrator
│   │   │   └── notification_service.py  # Telegram alerts
│   │   ├── tasks/                   # APScheduler cron jobs
│   │   └── core/                    # Security, logging, exceptions
│   ├── tests/                       # 48+ pytest tests (12 files)
│   ├── alembic/                     # Database migrations
│   └── Dockerfile                   # Multi-stage Python build
├── frontend/
│   ├── src/
│   │   ├── api/                     # 9 Axios API client modules
│   │   ├── hooks/                   # 7 React Query custom hooks
│   │   ├── contexts/                # Auth context provider
│   │   ├── components/              # Radix UI components + layout
│   │   ├── pages/                   # 13 page components
│   │   ├── types/                   # TypeScript interfaces
│   │   └── lib/                     # Utilities
│   └── Dockerfile                   # Node build + Nginx serve
├── docker/nginx/                    # Reverse proxy + security headers
├── .github/workflows/               # CI (lint+test+build) + CD (GHCR push)
├── docker-compose.yml               # 5 services with health checks
└── .env.example
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | -- | JWT signing key (min 32 chars) |
| `ADMIN_DEFAULT_PASSWORD` | Yes | -- | Initial admin password |
| `DATABASE_URL` | No | Auto-configured | PostgreSQL async connection |
| `REDIS_URL` | No | Auto-configured | Redis connection |
| `AI_PROVIDER` | No | `claude` | AI provider (`claude` or `openai`) |
| `ANTHROPIC_API_KEY` | No | -- | Anthropic API key |
| `OPENAI_API_KEY` | No | -- | OpenAI API key |
| `CORS_ORIGINS` | No | `localhost` | Allowed CORS origins |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `DEBUG` | No | `false` | Debug mode (SQL echo) |

---

## Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d postgres redis
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

### Testing

```bash
cd backend && pytest tests/ -v
```

48+ tests across 12 files covering scraper extraction, diff algorithm, authentication, tasks, runs, and notifications.

### Linting

```bash
ruff check backend/             # Python
cd frontend && npx oxlint src/  # TypeScript
npx tsc --noEmit                # Type check
```

---

## License

[MIT](LICENSE) -- free for commercial use.
