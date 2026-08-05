<!--
  BANNER: см. github_resume/DESIGN_SYSTEM.md — Smart Scraper Platform
  Сохранить как assets/banner.png и раскомментировать:
-->
<!-- <img src="assets/banner.png" alt="Smart Scraper Platform" width="100%"> -->

> **[Русская версия / Russian version](README.md)**

<div align="center">

# Smart Scraper Platform

### Web Scraping SaaS with AI-Powered Change Detection

[![CI/CD](https://github.com/AndrewSheff/smart-scraper-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AndrewSheff/smart-scraper-platform/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Monitor any website on a schedule. Detect changes automatically. Get AI-powered summaries and Telegram alerts.**

[Quick Start](#-quick-start) · [Features](#-features) · [Screenshots](#-screenshots) · [Architecture](#-architecture) · [API](#-api-documentation)

</div>

---

> **The Problem:** Marketing teams check competitor prices manually every morning — 10 sites x 30 minutes. Legal departments miss regulatory updates and face fines. Procurement monitors supplier catalogs by hand. Existing solutions are either too complex (Scrapy) or too expensive ($100+/month).

**Smart Scraper Platform** is a self-hosted SaaS for automated web monitoring. Configure CSS/XPath selectors through a visual interface, set a schedule, and receive Telegram notifications with AI-generated summaries when data changes.

<div align="center">

| Lines of Code | API Endpoints | DB Models | Pages | Tests | Docker Services |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **10,400+** | **31** | **6** | **13** | **48+** | **5** |

</div>

---

## Screenshots

| Monitoring Tasks |
|:----------------:|
| ![Tasks](screenshots/dashboard.png) |

---

## Features

**Visual Task Builder** — enter a URL, add CSS or XPath selectors, and click Preview to see extracted values instantly. No coding required.

**Cron Scheduling** — run tasks from every 5 minutes to once a month. Human-readable schedule display. Manual "Run Now" for instant checks.

**Change Detection Engine** — diff comparison between runs. See exactly what changed (old value vs new value) with highlighted differences.

**AI-Powered Summaries** — Claude or GPT analyzes changes and explains what happened and why it matters. Custom AI prompts per task for domain-specific insights.

**Telegram Notifications** — instant alerts when changes are detected. Configurable per task. Includes change summary and AI analysis.

**Multi-Field Extraction** — extract multiple data points per page (price, title, stock status, etc.). Each field has its own selector and label.

**Run History** — full log of every task execution with timestamps, extracted data, and change indicators. Track trends over time.

**Excel Export** — download extracted data and change history as XLSX for reporting and analysis.

**Role-Based Access** — Admin and User roles. Users manage their own tasks; admins see everything.

**Enterprise Security** — JWT + bcrypt, rate limiting, CORS, structured logging, request tracing.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    Nginx :80                      │
│          Reverse Proxy + Security Headers         │
├──────────────────┬───────────────────────────────┤
│  Frontend :3000  │        Backend :8000           │
│  React 19 + Vite │     FastAPI + Uvicorn          │
│  TailwindCSS v4  │     SQLAlchemy 2.0 (async)     │
│  13 pages        │   ┌────────────────────────┐   │
│                  │   │   Scraping Pipeline     │   │
│                  │   │  httpx → BS4 → Diff     │   │
│                  │   │  → AI Summary → Alert   │   │
│                  │   └────────────────────────┘   │
├──────────────────┴───────────────────────────────┤
│   PostgreSQL 16              Redis 7              │
│   6 models, Alembic          Rate Limiting        │
│   Run history                Session Cache        │
│                                                    │
│              APScheduler (cron tasks)              │
└──────────────────────────────────────────────────┘
```

### Scraping Pipeline

```
Cron trigger (or manual "Run Now")
        |
        v
  [httpx GET target URL]
        |
        v
  [BeautifulSoup parse HTML]
        |
        v
  [Extract values by CSS/XPath selectors]
        |
        v
  [Compare with previous run (diff engine)]
        |
        +---> No changes --> Store result, done
        |
        +---> Changes detected:
                |
                v
          [AI summary (Claude/GPT)]
                |
                v
          [Telegram notification]
                |
                v
          [Store result + diff]
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose v2+
- (Optional) Telegram bot token for notifications
- (Optional) Anthropic or OpenAI API key for AI summaries

### 1. Clone and configure

```bash
git clone https://github.com/AndrewSheff/smart-scraper-platform.git
cd smart-scraper-platform
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-random-32-char-string    # required
ADMIN_PASSWORD=SecurePass123             # required
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...    # optional
TELEGRAM_CHAT_ID=your_chat_id           # optional
ANTHROPIC_API_KEY=sk-ant-...             # optional
```

### 2. Launch

```bash
docker compose up -d
```

### 3. Access

| Service | URL |
|:--------|:----|
| Application | http://localhost |
| API Docs (Swagger) | http://localhost/docs |

Login with admin credentials, create your first scraping task.

---

## Tech Stack

| Layer | Technology | Version |
|:------|:-----------|:--------|
| **Backend** | Python, FastAPI, SQLAlchemy (async), Alembic | 3.13, 0.115, 2.0 |
| **Scraping** | httpx, BeautifulSoup4, lxml | Async HTTP |
| **Scheduling** | APScheduler | Cron expressions |
| **Frontend** | React, TypeScript, Vite, TailwindCSS, shadcn/ui | 19, 5+, 6, v4 |
| **Database** | PostgreSQL | 16 |
| **Cache** | Redis | 7 |
| **AI** | Anthropic Claude, OpenAI GPT | Latest |
| **Notifications** | Telegram Bot API (aiogram) | Instant alerts |
| **Auth** | JWT + bcrypt | HS256 |
| **Infra** | Docker Compose, Nginx, GitHub Actions CI/CD | Multi-stage |

---

## API Documentation

Interactive Swagger at `/docs`. **31 endpoints** across 8 groups:

| Group | Prefix | Endpoints |
|:------|:-------|:----------|
| Auth | `/api/v1/auth` | Register, login, token refresh |
| Tasks | `/api/v1/tasks` | CRUD, run now, pause/resume |
| Runs | `/api/v1/runs` | Run history, results, diffs |
| Fields | `/api/v1/fields` | Selector management per task |
| Notifications | `/api/v1/notifications` | Telegram setup, test message |
| Dashboard | `/api/v1/dashboard` | Stats and activity charts |
| Users | `/api/v1/users` | User management |
| Health | `/api/v1/health` | Liveness probe |

---

## Project Structure

```
smart-scraper-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with lifespan
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── api/v1/              # 8 REST API routers
│   │   ├── models/              # 6 SQLAlchemy models
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── services/            # Scraping, diff, AI, notifications
│   │   ├── workers/             # APScheduler task runner
│   │   └── core/                # Security, logging, exceptions
│   ├── tests/                   # 48+ pytest tests
│   ├── alembic/                 # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API clients
│   │   ├── components/          # UI components + layout
│   │   ├── contexts/            # Auth context
│   │   ├── pages/               # 13 page components
│   │   └── lib/                 # Utilities
│   └── Dockerfile
├── docker/nginx/
├── .github/workflows/           # CI/CD
├── docker-compose.yml           # 5 services
└── .env.example
```

---

## Environment Variables

| Variable | Required | Default | Description |
|:---------|:---------|:--------|:------------|
| `SECRET_KEY` | Yes | -- | JWT signing key |
| `ADMIN_PASSWORD` | Yes | -- | Initial admin password |
| `DATABASE_URL` | No | Auto | PostgreSQL connection |
| `REDIS_URL` | No | Auto | Redis connection |
| `TELEGRAM_BOT_TOKEN` | No | -- | For Telegram alerts |
| `TELEGRAM_CHAT_ID` | No | -- | Telegram notification target |
| `ANTHROPIC_API_KEY` | No | -- | For Claude AI summaries |
| `OPENAI_API_KEY` | No | -- | For GPT AI summaries |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d postgres redis
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && pytest tests/ -v

# Lint
ruff check backend/
cd frontend && npm run lint && npx tsc --noEmit
```

---

## License

[MIT](LICENSE) — free for commercial use.
