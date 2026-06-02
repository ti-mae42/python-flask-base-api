# Base API

Reusable Flask API template for starting RESTful JSON service projects. It
provides a small generic shell with Flask-RESTful routing, camelCase JSON
request/response helpers, configuration loading, security primitives,
SQLAlchemy and Alembic foundation, optional Celery worker setup, and optional
AWS adapters.

The template is intentionally business-domain free. New projects should add
their own domain modules, repositories, resources, schemas, validators, and
migrations after the scaffold step.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the layered design, component
responsibilities, and fit guidance.

## Included

- Flask app factory and `web_app` entrypoint.
- Healthcheck endpoint at `/api/healthcheck`.
- Generic API resource, schema, and validator bases.
- Generic domain entity and repository bases.
- Optional PostgreSQL or MySQL database support with Flask-SQLAlchemy and Flask-Migrate.
- Optional Celery worker foundation.
- Optional AWS adapter foundation.
- Generic password, JWT, and API-token security helpers.
- Alembic migration scaffolding with no application tables.
- Focused tests for the reusable shell.

## Template Features

Optional feature boundaries are documented in `TEMPLATE_FEATURES.md`. The
future scaffold CLI is expected to use those markers and docs to keep, remove,
or configure optional parts of the template.

The default template keeps all optional features enabled for now.

## Python dependency management (phased migration)

- Source of truth for direct dependencies: `pyproject.toml`

### Install

```bash
python -m pip install -e .
```

### Install with development tools

```bash
python -m pip install -e '.[dev]'
```

### Configure

Create a local `.env` from `.env.sample` and replace placeholder values.

```bash
cp .env.sample .env
```

Use a SQLAlchemy-compatible database URL. Examples:

```env
DATABASE_URL=postgresql+psycopg2://user:pass@host/dbname
DATABASE_URL=mysql+pymysql://user:pass@host/dbname
```

### Run the API

```bash
flask --app base_api.initialize:web_app run
```

### Run the worker

```bash
celery -A base_api.initialize:celery_app worker
```

### Run tests

```bash
pytest tests/ -v
```

### Migrations

```bash
flask --app base_api.initialize:web_app db migrate -m "description"
flask --app base_api.initialize:web_app db upgrade
```
