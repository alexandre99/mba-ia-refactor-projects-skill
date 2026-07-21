# Project Analysis Heuristics

## Scope exclusions

Ignore `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, coverage output, caches, binary databases, and generated lock artifacts except when dependency versions are required.

## Stack detection

### Python

Signals: `requirements.txt`, `pyproject.toml`, `Pipfile`, `.py` entrypoints.

- Flask: imports from `flask`, `Flask(...)`, blueprints, `app.route`.
- SQLAlchemy: `flask_sqlalchemy`, `sqlalchemy`, model base declarations.
- SQLite: `sqlite3`, `sqlite:///`, `.db` configuration.
- Tests: `pytest`, `unittest`, test modules.

### Node.js

Signals: `package.json`, `.js`, `.cjs`, `.mjs`, `.ts`.

- Express: dependency/import `express`, `express()`, router declarations.
- SQLite: `sqlite3`, `better-sqlite3`, database file setup.
- Tests: scripts or dependencies for Jest, Mocha, Vitest, Supertest.

## Architecture mapping

For each source file, record its actual responsibilities, not merely its folder name:

- application bootstrap and dependency wiring;
- route declaration and HTTP transport;
- use-case orchestration;
- business rules;
- data models and invariants;
- persistence and queries;
- cross-cutting middleware;
- configuration and secrets;
- notifications or other external effects.

A file named `controller` may still contain persistence and domain logic. A file named `model` may be a procedural god module.

## Endpoint inventory

Capture method, path, handler, request input, usual success status, and response shape. Include administrative and health endpoints. This inventory is the contract baseline for Phase 3.

## Domain inference

Use entity names, routes, SQL tables, request payloads, and README language. State uncertainty explicitly. Do not invent business rules.

## Phase 1 output

Include:

- project name;
- language/runtime;
- framework and key dependencies;
- database;
- inferred domain;
- current architecture summary;
- source file count;
- endpoint count;
- startup command;
- test/validation availability;
- immediate blockers.
