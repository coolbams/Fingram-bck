# Copilot instructions for fingram

## Project overview

This repository is a small Python package managed with `uv` and packaged via a `src/` layout. The package root lives in `src/fingram`, and the project entry point is defined in `pyproject.toml`:

- package name: `fingram`
- console script: `fingram`
- package entry: `fingram:main`
- runtime dependency: `fastapi[standard]`

The repo is intentionally minimal right now: there is no larger application structure, no separate services, and no tests/lint tooling yet. Future changes should keep the same simple shape unless the project grows beyond a single package.

## Build, test, and lint commands

Use `uv` as the project’s package runner; the repo is configured for it via `pyproject.toml` and `uv_build`.

```bash
# install/update dependencies
uv sync

# run the app entry point
uv run fingram
```

There is currently no dedicated test or lint configuration in this repository (`pytest`, `ruff`, `mypy`, etc. are not configured yet). If the project adds tests later, prefer a focused command such as:

```bash
uv run pytest path/to/test_file.py -q
```

and keep linting in the same style as the project’s selected toolchain if/when it is introduced.

## Architecture and code layout

The project is organized around a single Python package rather than a multi-service or monorepo layout:

- `pyproject.toml`: project metadata, Python version, package config, and the console script entry point
- `src/fingram/__init__.py`: package-level entry function currently exposed as `main`
- `src/fingram/main.py`: the module that is intended to hold the app logic or initialization entry point

The key architectural point is that all code should remain under `src/fingram` unless there is a clear reason to broaden the package structure. Keep the project’s runtime entry point and package API aligned with the `pyproject.toml` script definition.

## Key conventions

- Use `uv` instead of direct `pip` commands for project setup and execution.
- Keep the package layout consistent with the `src/` convention already in use.
- If new functionality is added, prefer extending the existing `src/fingram` package before introducing new top-level packages or services.
- Treat `pyproject.toml` as the source of truth for runtime configuration, dependencies, and script registration.
- Preserve the minimal package structure unless work definitely requires a larger app layout.

## Working style for this repo

Because the repo is so small, prefer surgical edits that stay within the existing package boundary. Avoid adding framework, tooling, or directory structure churn unless the change clearly requires it. When introducing new capabilities, keep the setup consistent with the current `uv`-based packaging model.
