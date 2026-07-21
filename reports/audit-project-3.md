# Architecture Audit Report — Project 3

## Phase 1 — Project Analysis

- Project: `task-manager-api`
- Language: Python
- Framework: Flask + Flask-SQLAlchemy
- Database: SQLite
- Domain: users, tasks, categories and reports
- Current architecture: partially layered with models, blueprints/routes, services and utilities, but route modules still contain persistence, validation, serialization and business rules
- Source files reviewed: `app.py`, `routes/task_routes.py`, `routes/user_routes.py` and supporting project structure

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 1 |
| HIGH | 2 |
| MEDIUM | 4 |
| LOW | 2 |
| **Total** | **9** |

## Findings

### [CRITICAL] Authentication returns a predictable fake token

- File: `routes/user_routes.py:187-213`
- Evidence: successful login returns `fake-jwt-token-<user id>` without signing, expiry or verification.
- Impact: any caller can forge a token for another user and impersonate that identity if downstream code trusts it.
- Recommendation: use a signed, expiring authentication token or server-side session and enforce authorization on protected routes.

### [HIGH] Hardcoded secret and debug mode enabled

- File: `app.py:13-16`, `app.py:35-36`
- Evidence: application secret is committed in source and the development debugger is enabled on all interfaces.
- Impact: configuration disclosure and unsafe execution outside development.
- Recommendation: environment-specific configuration with debug disabled by default.

### [HIGH] Routes remain fat despite partial layering

- File: `routes/task_routes.py:13-301`, `routes/user_routes.py:12-213`
- Evidence: route functions perform validation, business policy, ORM queries, persistence, serialization and logging.
- Impact: Flask transport is tightly coupled to domain and persistence behavior, reducing testability and reuse.
- Recommendation: introduce controllers/services and repositories while preserving existing good model boundaries.

### [MEDIUM] N+1 queries while listing tasks

- File: `routes/task_routes.py:13-61`
- Evidence: all tasks are loaded, then each task may query its user and category separately.
- Impact: query count grows linearly with tasks and relationships.
- Recommendation: eager-load relationships or issue a joined/batched query.

### [MEDIUM] Deprecated SQLAlchemy query APIs

- File: `routes/task_routes.py:44`, `routes/task_routes.py:53`, `routes/task_routes.py:69`, `routes/user_routes.py:31`, `routes/user_routes.py:96`
- Evidence: repeated use of `Model.query.get(...)`; in SQLAlchemy 2.x the modern primary-key lookup is `Session.get(Model, id)`.
- Impact: legacy API usage complicates upgrades and generates deprecation/legacy warnings.
- Recommendation: migrate primary-key lookups to `db.session.get(...)`.

### [MEDIUM] Validation and serialization are duplicated

- File: `routes/task_routes.py:18-61`, `routes/task_routes.py:67-83`, `routes/user_routes.py:155-185`
- Evidence: task-to-response mapping and overdue calculation are implemented in multiple route handlers.
- Impact: inconsistent response behavior and maintenance drift.
- Recommendation: centralize serialization and overdue policy in a presenter/model method or service.

### [MEDIUM] Broad bare exception handlers hide defects

- File: `routes/task_routes.py:64-65`, `routes/task_routes.py:136-140`, `routes/task_routes.py:238-240`, `routes/user_routes.py:132-134`, `routes/user_routes.py:151-153`
- Evidence: `except:` catches every exception, including programming and process-control exceptions.
- Impact: defects become generic 500 responses without diagnostic classification.
- Recommendation: catch expected exceptions and use a centralized error handler with structured logging.

### [LOW] Unused imports and mixed import declarations

- File: `app.py:9`, `routes/task_routes.py:8-9`, `routes/user_routes.py:7-8`
- Evidence: modules import unrelated or unused standard-library packages.
- Impact: increases noise and obscures actual dependencies.
- Recommendation: remove unused imports and keep one import per responsibility group.

### [LOW] Magic literals duplicate domain policies

- File: `routes/task_routes.py:112-116`, `routes/task_routes.py:178-185`, `routes/user_routes.py:73-74`, `routes/user_routes.py:121-124`
- Evidence: allowed statuses, priority limits and roles are repeated inline.
- Impact: domain policies can diverge across create/update paths.
- Recommendation: move these values to named domain policies or validation schemas.

## Deprecated API Check

A deprecated/legacy API finding applies: `Model.query.get(...)` should be migrated to `Session.get(...)` for SQLAlchemy 2.x compatibility. Exact installed versions must still be confirmed during runtime validation.

## Phase Gate

Phase 2 complete. Application files must not be modified until Phase 3 is explicitly approved.
