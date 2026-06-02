# AGENTS.md

Guidelines for AI coding agents working in this repository.

## Project Overview

This repository is a reusable Flask API shell. It provides generic application
startup, Flask-RESTful routing, SQLAlchemy setup, Alembic migration foundation,
request/response helpers, repository base classes, domain entity base classes,
configuration loading, security primitives, optional APM/cache/cloud adapters,
and an empty Celery worker foundation.

## Architectural Rules

Allowed dependency direction:

api -> resources -> domain -> repository

Do not bypass intermediate layers.

Domain code must stay framework-independent and must not depend on Flask,
HTTP request/response objects, Celery task decorators, or infrastructure-specific
classes.

Repositories handle persistence only. Repositories must not contain business
rules and must not call `commit()`.

Transaction ownership belongs at entrypoints. Write HTTP resources, CLI commands,
and background task entrypoints must use `@database.atomic`.

Do not introduce business domains into the base shell. Add only generic
infrastructure or template behavior unless a product repository is created from
this template.

## Import Style

Prefer package imports over direct class imports when following existing package
patterns.

Correct:

```python
from base_api.infrastructure import database
```

Incorrect:

```python
from base_api.infrastructure.database import transaction
```

## Commands

```bash
# Install
python -m pip install -e .

# Install with dev tools
python -m pip install -e '.[dev]'

# Run the Flask app
flask --app base_api.initialize:web_app run

# Run Celery worker
# BASE_API_OPTIONAL: celery
celery -A base_api.initialize:celery_app worker

# Database migrations
# BASE_API_OPTIONAL: postgresql
flask --app base_api.initialize:web_app db migrate -m "description"
flask --app base_api.initialize:web_app db upgrade

# Lint
ruff check base_api/
```

## Environment

Configuration is selected with `APP_SETTINGS`, defaulting to
`base_api.infrastructure.config.DevelopmentConfig`.

Required generic variables:

- `SECRET_KEY`
- `API_TOKEN`
- `API_TOKEN_HEADER`
- `DATABASE_URL`

Optional generic variables:

- `COOKIE_TOKEN`
- `COOKIE_USER`
- `COOKIE_DOMAIN`
- `REDIS_URL`
- `APM_SERVICE_NAME`
- `APM_SECRET_TOKEN`
- `APM_SERVER_URL`
- `CLOUD_REGION`
- `SNS_PLATFORM_APPLICATION_ARN`
- `API_RESPONSE_LOGGING`

## Testing

Use `.env.test` for tests.

```bash
pytest tests/ -v
```
