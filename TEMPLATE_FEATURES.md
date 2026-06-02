# Template Features

This file documents optional template boundaries for a future scaffold CLI. The
default template currently keeps all listed features enabled.

## PostgreSQL Database Support

Feature marker: `BASE_API_OPTIONAL: postgresql`

Files involved:

- `base_api/initialize.py`
- `base_api/infrastructure/config.py`
- `base_api/infrastructure/database.py`
- `base_api/repositories/__init__.py`
- `migrations/README`
- `migrations/alembic.ini`
- `migrations/env.py`
- `migrations/script.py.mako`
- `migrations/versions/`
- `pyproject.toml`
- `.env.sample`
- `AGENTS.md`
- `tests/conftest.py`
- `tests/unit/test_app.py`

Environment variables involved:

- `DATABASE_URL`

Dependencies involved:

- `SQLAlchemy`
- `Flask-SQLAlchemy`
- `Flask-Migrate`
- `alembic`
- `psycopg2-binary`

When disabled:

- Remove SQLAlchemy and Flask-Migrate registration from `create_app`.
- Remove `base_api/infrastructure/database.py`.
- Remove `base_api/repositories/` unless another enabled feature needs it.
- Remove `migrations/`.
- Remove `DATABASE_URL` from environment files and config loading.
- Remove database dependencies from `pyproject.toml`.
- Replace database-backed tests with app-only tests.

When enabled:

- Keep `DATABASE_URL` configured.
- Keep database registration and migration registration in `create_app`.
- Keep Alembic migration scaffolding.
- Keep repository base classes available for generated domain modules.
- Generate or keep migration versions only for concrete tables added by the scaffolded application.

## Celery Support

Feature marker: `BASE_API_OPTIONAL: celery`

Files involved:

- `base_api/initialize.py`
- `base_api/infrastructure/config.py`
- `base_api/infrastructure/worker.py`
- `pyproject.toml`
- `.env.sample`
- `AGENTS.md`

Environment variables involved:

- `REDIS_URL`

Dependencies involved:

- `celery`
- `redis` when Redis is used as the Celery broker/backend

When disabled:

- Remove `base_api/infrastructure/worker.py`.
- Remove `celery_app = worker.create_worker(web_app)` from `base_api/initialize.py`.
- Remove the `worker` import from `base_api/initialize.py`.
- Remove Celery commands from docs.
- Remove `celery` from `pyproject.toml`.
- Remove `REDIS_URL` only if no other enabled feature uses Redis.

When enabled:

- Keep `celery_app` exported from `base_api.initialize`.
- Keep `REDIS_URL` or replace it with the selected broker/backend configuration.
- Add generated task modules only when the scaffolded application needs background work.

## AWS Integration Support

Feature marker: `BASE_API_OPTIONAL: aws`

Files involved:

- `base_api/infrastructure/cloud.py`
- `base_api/infrastructure/config.py`
- `pyproject.toml`
- `.env.sample`

Environment variables involved:

- `CLOUD_REGION`
- `SNS_PLATFORM_APPLICATION_ARN`

Dependencies involved:

- `boto3`

When disabled:

- Remove `base_api/infrastructure/cloud.py`.
- Remove AWS environment variables from config and environment files.
- Remove `boto3` from `pyproject.toml`.
- Remove generated code that imports cloud adapters.

When enabled:

- Keep the generic `CloudClient` and `SnsClient` adapters.
- Keep AWS environment variables configured.
- Add product-specific AWS clients in application code, not in the base shell.
