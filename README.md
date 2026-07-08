<<<<<<< HEAD
# LeadForge AI

> Business discovery & opportunity analysis platform built with FastAPI, PostgreSQL, Celery, and Redis.

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI 0.115 + Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Queue | Celery 5 + Redis |
| Cache / Broker | Redis 7 |
| Database | PostgreSQL 16 |
| Runtime | Python 3.12 |

## Project Structure

```
app/
├── api/v1/          # FastAPI routers (HTTP delivery layer)
├── core/            # Config, logging, exceptions
├── db/              # Engine, session, base model
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic (use-case layer)
├── repositories/    # DB access (repository pattern)
├── tasks/           # Celery task definitions
└── main.py          # Application entrypoint
alembic/             # Database migrations
tests/               # Pytest test suite
```

## Getting Started

### 1. Copy the environment file

```bash
cp .env.example .env
# Edit .env with your local secrets
```

### 2. Start all services

```bash
docker compose up --build
```

The API will be available at <http://localhost:8000>.  
Interactive docs: <http://localhost:8000/docs> (development only).

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Run tests

```bash
docker compose exec api pytest -v
```

## Development

```bash
# Lint
ruff check app tests

# Type-check
mypy app

# Format
ruff format app tests
```

## Creating a Migration

```bash
# Auto-generate from model changes
docker compose exec api alembic revision --autogenerate -m "describe_change"

# Apply
docker compose exec api alembic upgrade head

# Rollback one step
docker compose exec api alembic downgrade -1
```
=======
# Lead_AI
Building a tool to find lead 
>>>>>>> 47bf47e9da21f36a940ba49e945b3efd7bcef2d1
