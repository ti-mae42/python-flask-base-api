# Architecture

`base-api` is a reusable Flask shell for building a specific kind of backend: a
RESTful API that receives JSON requests and returns JSON responses using
camelCase keys as the public contract. Internally, application code uses
snake_case names and the resource layer translates between the two conventions.

The shell is intentionally business-domain free: product repositories created
from this template add their own entities, repositories, resources, schemas,
validators, commands, migrations, and background tasks.

The shell is a good fit when a project needs a RESTful JSON API with request
validation, response serialization, relational persistence,
transaction-controlled write entrypoints, optional background workers, and
simple infrastructure adapters. It is less useful for projects that are
primarily event-sourced, heavily asynchronous from the start, built around a
different web framework, use a non-REST interface as the primary contract, or
intentionally avoid a layered domain model.

## Dependency Direction

Application code should follow this dependency direction:

```text
api -> resources -> domain -> repositories
```

Do not skip layers for normal application behavior. HTTP resources should call
domain objects or domain services instead of reaching into repositories
directly. Domain code can use repositories for persistence, but it must stay
independent from Flask, HTTP request/response objects, Celery decorators, and
infrastructure-specific clients. Repositories should only know about
persistence.

Infrastructure code sits beside these layers and provides adapters for
configuration, database sessions, external connections, cache clients, cloud
clients, security primitives, APM, and worker setup. Product code should call
those adapters from entrypoints or domain-facing services when needed, while
keeping infrastructure details out of pure domain rules.

## Request Flow

A typical HTTP request moves through the system like this:

1. `base_api.initialize.create_app` creates the Flask app, loads config,
   registers SQLAlchemy, Alembic, APM, commands, routes, and request hooks.
2. Request hooks authenticate the generic API token and attach request-scoped
   state to Flask `g`.
3. Flask-RESTful routes dispatch to API resources.
4. Resources read payload data, normalize external camelCase keys to internal
   snake_case keys, validate input with Pydantic validators, and call domain
   behavior.
5. Domain entities and services apply project-specific rules and coordinate
   repository access.
6. Repositories query, add, update, delete, flush, and refresh ORM models.
7. Write entrypoints wrapped with `@database.atomic` commit or roll back the
   transaction.
8. Resources serialize domain or repository-backed objects with schemas,
   convert response keys back to camelCase, and return HTTP responses.

The base shell only ships a healthcheck route, but product APIs are expected to
register their own resources in `api.create_api`.

## Layers

### API Package

`base_api/api/__init__.py` owns Flask-RESTful API registration and generic
decorators such as `login_required` and `not_allowed`.

Use this layer for:

- Route registration.
- HTTP authentication decorators.
- HTTP-only response shortcuts.

Avoid putting business rules here. The route table should describe the public
API surface, not implement use cases.

### Resources

`base_api/api/resources/__init__.py` provides `ResourceBase` and
`HealthCheckResource`.

Resources are the HTTP boundary. They are responsible for:

- Reading JSON, form, query string, and file payloads.
- Converting inbound camelCase names to internal snake_case names.
- Selecting create/update validators based on HTTP method.
- Returning consistent error responses.
- Serializing output through schemas.
- Converting outbound snake_case names to camelCase names.

Write resource methods should use `@database.atomic`. That keeps transaction
ownership at the entrypoint where request success or failure is known.

### Validators

`base_api/api/validators/__init__.py` provides a Pydantic base model configured
to forbid unknown fields and strip string whitespace.

Use validators for request shape, type conversion, and request-level input
rules. Keep domain invariants in domain objects when they are not merely input
format checks.

### Schemas

`base_api/api/schemas/__init__.py` provides `SchemaBase`, a small serializer
that supports:

- Compact and full field sets.
- Audience-specific field sets.
- Object and dict sources.
- Primitive serialization for dates, datetimes, decimals, UUIDs, enums, sets,
  tuples, lists, and dicts.
- Per-field custom serializer methods.

Schemas define the API response contract. They should not query the database or
make business decisions.

### Domain

`base_api/domain/__init__.py` provides `Entity` and `ValueEntity` base classes.
`base_api/domain/services.py` provides a minimal service base.

Product repositories should place business concepts and rules in this layer.
Domain objects wrap repository instances, expose meaningful behavior, enforce
business invariants, and coordinate persistence through repository APIs.

Entities are the main components for business rules. An `Entity` should own the
decisions, policies, validations, permissions, and state transitions for the
business concept it represents. An `Entity` should never directly instantiate
another `Entity`, because that couples independent business concepts to each
other. When an entity needs another entity, call that entity's module service
factory instead.

`ValueEntity` represents a concept that only exists through a parent `Entity`.
A `ValueEntity` must always be accessed by an `Entity` and must always declare
an `Entity` as its parent. An `Entity` may instantiate one of its own
`ValueEntity` objects directly, because that coupling is already part of the
business model. For example, if a bet only makes sense for a modality, the bet
can be modeled as a value entity accessed through the modality or another
owning entity.

An `Entity` or `ValueEntity` can have no repository, or one and only one
repository. A repository must belong to an `Entity` or `ValueEntity` and should
not be accessed without going through that domain object. How an entity exposes
repository model fields is left to the product API, but fields that need to be
included in REST responses should usually be exposed as `@property` methods on
the entity or value entity.

Use domain services as a facade when a resource, command, task, or another
domain entity needs a stable entrypoint into a domain module. The most common
use is to call domain entity factory methods without coupling entities directly
to each other.

A service should serve one Python module. For example, if a product API has a
`<your_api>.domain.register` module, `services.py` should expose a
`RegisterService` whose `_domain` attribute points to
`'<your_api>.domain.register'`. That service should contain class methods for
the factory methods of any entity in `register.py` that external callers need,
such as `create_user_with_id`, `create_profile_with_instance`, or
`create_guest_registration`.

Service methods should always be `@classmethod`s. They should not call other
services; needing one service to call another usually means the behavior belongs
in an entity or the entity dependency should be expressed through that module's
own service. Services also should not contain business rules. Any choice,
policy, validation, permission, or state transition that needs to be decided
belongs in entities, not in service methods.

Domain code must remain framework-independent. It should not import Flask,
access request globals, return HTTP responses, or depend on Celery task
decorators.

### Repositories

`base_api/repositories/__init__.py` provides `AbstractModel` and `AuditMixin`
for SQLAlchemy-backed repositories.

Repositories are the SQLAlchemy abstraction layer. They define tables, columns,
relationships, indexes, ordering, and persistence-focused query helpers. Any use
of SQLAlchemy for query construction, selects, filters, joins, ordering,
pagination, inserts, updates, deletes, flushes, or model refreshes should be
contained in repositories instead of leaking into domain entities, resources,
services, commands, or tasks.

`AbstractModel` provides generic helpers for common persistence operations such
as listing, filtering, pagination, counting, getting, creating, updating, and
deleting. Prefer adding intention-revealing class methods to the specific
repository model when a query has business meaning or is reused. For example,
if a `Modality` entity needs active modality models, add a repository method
such as `Modality.list_active()` and call `cls.repository.list_active()` from
the entity. Avoid putting generic filter expressions in the entity, such as
`cls.repository.list_with_filter(active=True)`, when the query represents a
named concept in the domain.

Repositories must not own business rules and must not call `commit()`. They
flush and refresh when necessary, but transaction commit and rollback are owned
by entrypoints through `@database.atomic`.

Repositories should be reached through their owning `Entity` or `ValueEntity`,
not used as general-purpose application services.

### Infrastructure

`base_api/infrastructure/` contains generic adapters and setup code:

- `config.py` loads environment-based configuration selected by `APP_SETTINGS`.
- `database.py` registers SQLAlchemy and Flask-Migrate and provides
  `transaction` and `atomic`.
- `security.py` contains API token comparison, password hashing, JWT helpers,
  recovery code generation, and secret generation.
- `validation.py` contains reusable infrastructure validation helpers such as
  strong password validation.
- `connections.py` contains a simple HTTP connection base around `requests`.
- `cacher.py` contains Redis-backed expiring key storage with a test fallback.
- `cloud.py` contains generic AWS client bases, including SNS.
- `apm.py` installs Elastic APM when enabled and falls back to a no-op monitor.
- `worker.py` creates a Celery app using the Flask app configuration.

Infrastructure is intentionally generic. Product-specific integrations should
extend these adapters in the product repository instead of being added to the
base shell.

### Commands

`base_api/commands/__init__.py` exposes a command registration hook. The base
shell does not ship business commands.

Product CLI commands are entrypoints, like HTTP resources and background tasks.
Commands that write data should use `@database.atomic`, call domain services or
domain objects, and keep persistence details behind the domain/repository
boundary.

### Worker

`base_api.initialize` exports `celery_app` when the optional Celery feature is
kept. The shell only provides the worker foundation.

Product tasks should be treated as entrypoints. A task may call domain services,
but domain modules should not import task decorators or Celery app instances.

### Migrations

The `migrations/` directory contains Alembic scaffolding with no application
tables. Product repositories add concrete SQLAlchemy models and generate
migrations from those models.

## Transaction Ownership

Transaction ownership belongs at entrypoints:

- HTTP resource methods that write data.
- CLI commands that write data.
- Background tasks that write data.

Use `@database.atomic` on those entrypoints. Nested uses are supported through a
transaction depth counter: only the outermost transaction commits, and failures
roll back the session.

Repositories should never commit. Domain objects should not silently commit
either, because callers need one transaction around the whole use case.

## Authentication And Security

The base app includes a generic API token hook. Each request reads the configured
header name, compares it with the configured API token using constant-time
comparison, and stores the result in `g.authenticated`.

This is a shell-level primitive, not a full user authentication system. Product
APIs can build user login, JWT subject handling, permissions, password recovery,
or device registration on top of the security helpers.

## Optional Feature Boundaries

Some components are marked with `BASE_API_OPTIONAL` comments so a future
scaffold process can keep or remove them:

- `database`: SQLAlchemy, Flask-Migrate, repositories, migrations, and
  `DATABASE_URL`.
- `celery`: Celery worker setup and `REDIS_URL` worker configuration.
- `aws`: generic AWS/SNS adapters and AWS-related environment variables.

See `TEMPLATE_FEATURES.md` for the detailed file and dependency boundaries.

## When This Template Fits

Use `base-api` when the project needs:

- A RESTful JSON API with Flask-RESTful resources.
- camelCase request and response keys for API clients, with snake_case inside
  Python code.
- A relational database with SQLAlchemy models and Alembic migrations.
- Clear separation between HTTP handling, domain behavior, and persistence.
- Pydantic request validation without adopting a larger framework.
- Explicit transaction boundaries at write entrypoints.
- Optional Celery, Redis, APM, and AWS adapter foundations.
- A reusable starting point for multiple small or medium backend services.

## When To Choose Something Else

Consider another base when the project needs:

- A framework with native async request handling as the main programming model.
- GraphQL, gRPC, event streaming, or non-JSON payloads as the primary
  interface.
- A service without a relational database or without repository-style
  persistence.
- A very small script-like API where layered structure would add more cost than
  clarity.
- A domain architecture that intentionally couples use cases to a different
  application service or dependency injection pattern.

## Extension Checklist

When creating a product API from this shell:

1. Add product routes in `api.create_api`.
2. Add resource classes for HTTP behavior only.
3. Add Pydantic validators for request payloads.
4. Add schemas for response contracts.
5. Add domain entities and services for business behavior.
6. Add repository models and query helpers for persistence.
7. Add Alembic migrations for new tables.
8. Wrap write resources, commands, and tasks with `@database.atomic`.
9. Keep domain modules free of Flask, Celery, and infrastructure-specific
   request/response objects.
10. Keep repositories focused on persistence and free of commits.
