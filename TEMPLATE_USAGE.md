# Template Usage

This repository is intended to be consumed by a future scaffold CLI, not copied
manually file by file.

## Expected Scaffold Flow

1. Copy the template into a new project directory.
2. Rename the package if the generated project should not use `base_api`.
3. Update project metadata in `pyproject.toml`.
4. Select optional features using `TEMPLATE_FEATURES.md`.
5. Remove files, dependencies, environment variables, and tests for disabled
   optional features.
6. Keep and configure files for enabled optional features.
7. Generate project-specific domain, repository, resource, schema, validator,
   and migration files.
8. Write local environment files from `.env.sample`.
9. Run tests before handing the generated project to the user.

## Package Naming

The template package is `base_api`. A scaffolded application may keep that name
for an internal starter project, but public or product projects should usually
rename it to an application-specific Python package.

When renaming the package, update:

- Python imports.
- `pyproject.toml` package discovery.
- `.flaskenv`.
- CLI commands in docs.
- Test imports.
- Alembic templates.

## Optional Feature Handling

The scaffold CLI should read `TEMPLATE_FEATURES.md` and use
`BASE_API_OPTIONAL` markers as implementation hints.

When a feature is disabled, the CLI should remove the feature's files,
dependencies, environment variables, and tests. When a feature is enabled, the
CLI should keep the generic foundation and configure it with generated project
values.

## Public Template Rules

The template should remain free of:

- Business-domain behavior.
- Private configuration values.
- Local machine paths.
- Product-specific URLs.
- Generated cache files.
- Committed local environment files.

Only `.env.sample` should be committed as an environment example.
