# Architecture Audit Report — task-manager-api

## Scope and independence

This report was produced from the current `task-manager-api` source, dependency file, validation scripts, and runtime probes. The findings were derived independently from source inspection; the README was consulted only after the findings were complete for a rediscovery comparison. `ecommerce-api-legacy` was not analyzed.

## Project profile

- Project: `task-manager-api`
- Stack: Python 3.12.3, Flask 3.0.0, Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0
- Installed validation dependencies: SQLAlchemy 2.0.51, Requests 2.31.0, Marshmallow 3.20.1, python-dotenv 1.0.0
- Database: SQLite, configured as `sqlite:///tasks.db` and materialized under Flask's instance path
- Domain: task management with users, roles, tasks, categories, login, and productivity reports
- Application source files analyzed: 15 Python files
- Public endpoints: 22
- Baseline status: PASSED with an isolated temporary copy/database and the deterministic validator; the pre-existing repository validator failed before boot because `python` is unavailable in the environment

## Executive summary

CRITICAL: 1 | HIGH: 6 | MEDIUM: 3 | LOW: 1

The most urgent risks are unauthenticated destructive operations, insecure password handling, committed credentials, and unsafe runtime defaults. The route modules also combine HTTP parsing, validation, business calculations, persistence, and response mapping. Phase 3 should address security and configuration first, then introduce thin controllers/services/repositories while preserving the current HTTP contract, and finally remove query/validation duplication and make seed writes atomic.

## Phase 1 architecture map

| Area | Observed responsibility |
|---|---|
| `app.py:1-34` | Flask bootstrap, fixed configuration, CORS, extension initialization, blueprint registration, schema creation at import time, health/root routes, and development-server startup |
| `routes/task_routes.py:1-299` | Task HTTP routes, input validation, ORM queries, task serialization, overdue calculations, search, statistics, commits, rollbacks, and console output |
| `routes/user_routes.py:1-211` | User HTTP routes, validation, ORM queries, password workflow, cascading task deletion, commits, rollbacks, and login response mapping |
| `routes/report_routes.py:1-223` | Report calculations plus category CRUD, ORM queries, validation, commits, rollbacks, and response mapping |
| `models/*.py` | SQLAlchemy entities, serialization, password hashing/checking, and local task rules |
| `database.py:1-3` | Global SQLAlchemy extension object |
| `services/notification_service.py:1-48` | SMTP configuration and email/in-memory notification behavior; no application reference was found in the analyzed runtime paths |
| `utils/helpers.py:1-116` | Date, email, string, task-data helpers, and scattered validation constants; `process_task_data` is not referenced by the routes |
| `seed.py:1-99` | Destructive seed reset plus user/category/task inserts with three separate commits |

## Endpoint inventory

The following inventory was derived from route decorators and verified against the isolated HTTP baseline. JSON shapes show representative top-level keys or array item keys.

| Method | Path | Handler | Success | Response shape |
|---|---|---|---:|---|
| GET | `/health` | `app.health` | 200 | object: `status`, `timestamp` |
| GET | `/` | `app.index` | 200 | object: `message`, `version` |
| GET | `/users` | `user_routes.get_users` | 200 | array: user summary fields, `task_count` |
| GET | `/users/<int:user_id>` | `user_routes.get_user` | 200 | object: user fields including `password`, plus `tasks` |
| POST | `/users` | `user_routes.create_user` | 201 | object: user fields including `password` |
| PUT | `/users/<int:user_id>` | `user_routes.update_user` | 200 | object: user fields including `password` |
| DELETE | `/users/<int:user_id>` | `user_routes.delete_user` | 200 | object: `message` |
| GET | `/users/<int:user_id>/tasks` | `user_routes.get_user_tasks` | 200 | array: task summary fields and `overdue` |
| POST | `/login` | `user_routes.login` | 200 | object: `message`, `user`, `token` |
| GET | `/tasks` | `task_routes.get_tasks` | 200 | array: task fields, `overdue`, `user_name`, `category_name` |
| GET | `/tasks/<int:task_id>` | `task_routes.get_task` | 200 | object: task fields and `overdue` |
| POST | `/tasks` | `task_routes.create_task` | 201 | object: task fields |
| PUT | `/tasks/<int:task_id>` | `task_routes.update_task` | 200 | object: task fields |
| DELETE | `/tasks/<int:task_id>` | `task_routes.delete_task` | 200 | object: `message` |
| GET | `/tasks/search` | `task_routes.search_tasks` | 200 | array: task fields |
| GET | `/tasks/stats` | `task_routes.task_stats` | 200 | object: totals, status counts, `overdue`, `completion_rate` |
| GET | `/reports/summary` | `report_routes.summary_report` | 200 | object: overview, status/priority, overdue, recent activity, productivity |
| GET | `/reports/user/<int:user_id>` | `report_routes.user_report` | 200 | object: `user`, `statistics` |
| GET | `/categories` | `report_routes.get_categories` | 200 | array: category fields and `task_count` |
| POST | `/categories` | `report_routes.create_category` | 201 | object: category fields |
| PUT | `/categories/<int:cat_id>` | `report_routes.update_category` | 200 | object: category fields |
| DELETE | `/categories/<int:cat_id>` | `report_routes.delete_category` | 200 | object: `message` |

## Findings

### [CRITICAL] SEC-002 — Destructive endpoints have no authentication or authorization

- File: `routes/user_routes.py:134-151`
- File: `routes/task_routes.py:225-238`
- File: `routes/report_routes.py:211-223`
- Evidence: the three DELETE handlers load and delete users/tasks/categories and commit without checking an authenticated principal, role, or permission. `delete_user` also deletes all tasks owned by the user at `routes/user_routes.py:140-146`.
- Impact: any network client that can reach the API can destroy task-manager data, including a user's related tasks, without credentials or an authorization decision.
- Recommendation: introduce authentication and explicit authorization at a controller/service boundary; keep deletion and cascade behavior inside a transactional use case; preserve the current success body only for authorized requests.
- Validation: in an isolated database, issue anonymous DELETE requests to each destructive endpoint, assert 401/403 and unchanged row counts, then issue an authorized request and assert the intended deletion and response contract. The current baseline showed anonymous DELETE requests returning 200.

### [HIGH] SEC-004 — MD5 password hashes and password fields are serialized to clients

- File: `models/user.py:16-32`
- File: `routes/user_routes.py:33-40`
- File: `routes/user_routes.py:74-90`
- File: `routes/user_routes.py:127-132`
- File: `routes/user_routes.py:207-211`
- Evidence: `set_password` and `check_password` use unsalted MD5, while `User.to_dict()` includes the stored password hash. The user GET, create, update, and login response paths use that serializer. Baseline response shapes for `GET /users/4`, `POST /users`, `PUT /users/4`, and `POST /login` confirmed a `password` key.
- Impact: MD5 is unsuitable for password storage, and exposing the stored verifier enables offline cracking and leaks a credential-derived secret through ordinary API responses.
- Recommendation: use a work-factor password-hashing function supported by the application, migrate existing hashes deliberately, and define a public user serializer that never includes password material.
- Validation: create a user and inspect the database representation for the approved password-hash format; assert that every user/login response omits `password`; verify valid and invalid login behavior and that a database dump cannot be used as a direct password comparison.

### [HIGH] SEC-003 — Usable credentials and secret keys are committed in source

- File: `app.py:11-13`
- File: `services/notification_service.py:7-10`
- Evidence: the application sets `SECRET_KEY` to `super-secret-key-123`; the notification service stores `taskmanager@gmail.com` and `senha123` as SMTP credentials.
- Impact: repository readers can forge framework-signed values or reuse SMTP credentials; rotation and environment separation are impossible while values remain committed.
- Recommendation: load secrets from environment/secret storage, reject missing production secrets, rotate any exposed credentials, and inject notification configuration through the composition root.
- Validation: run a repository secret scan that rejects these literals, start a production-configured app with missing secrets and assert fail-closed behavior, then verify configured values are not present in HTTP responses or logs.

### [HIGH] OPS-001 — Unsafe runtime and deployment defaults

- File: `app.py:8-15`
- File: `app.py:20-34`
- Evidence: the app hardcodes a SQLite database URI, enables unrestricted `CORS(app)`, binds the development server to `0.0.0.0`, and starts with `debug=True` on a fixed port 5000. Schema creation also runs during module import at `app.py:20-21`.
- Impact: debug behavior and broad cross-origin access can expose internals or widen attack surface; fixed local configuration is unsafe for deployment and makes isolation difficult; import-time persistence mutation surprises tests and tooling.
- Recommendation: use an application factory and environment-backed configuration, disable debug by default, allowlist CORS, require an explicit production server, and move schema setup to a separate command/migration path.
- Validation: boot with production settings and assert debug is false, CORS is allowlisted, the database path comes from configuration, and importing the application does not create or mutate a database; separately verify the supported server startup path.

### [HIGH] ARCH-001 — Cross-domain route modules act as god modules

- File: `routes/task_routes.py:11-299`
- File: `routes/report_routes.py:12-223`
- Evidence: the task route module owns seven task/list/search/statistics endpoints and their validation, calculations, ORM access, serialization, transactions, and prints. The report route module combines report aggregation with all category CRUD and its persistence/error handling.
- Impact: unrelated use cases change together, responsibilities cannot be unit-tested without Flask/SQLAlchemy context, and route files become the de facto service/repository layer.
- Recommendation: split category and report concerns, then extract domain services/controllers and repositories incrementally while retaining the existing blueprints and contracts.
- Validation: assert route modules contain only transport mapping and controller calls, exercise each endpoint through the existing smoke validator, and unit-test extracted services/repositories without a Flask request context.

### [HIGH] ARCH-002 — Business validation and workflows live in HTTP handlers

- File: `routes/task_routes.py:85-154`
- File: `routes/task_routes.py:156-223`
- File: `routes/task_routes.py:273-299`
- File: `routes/report_routes.py:12-165`
- Evidence: handlers validate title/status/priority/date values, resolve related entities, calculate overdue state and completion statistics, build productivity reports, and own multi-step request workflows before returning JSON.
- Impact: business rules are coupled to transport, duplicated across create/update/report paths, and difficult to reuse or test independently; changing HTTP shape risks changing domain behavior.
- Recommendation: move request validation to schemas, orchestration to use-case services, and response mapping to thin controllers while preserving status codes and JSON keys.
- Validation: add direct service/schema tests for valid, invalid, missing-related-entity, overdue, and report cases; then run the full endpoint baseline and compare status/body shape.

### [HIGH] ARCH-003 — Persistence and transaction operations are coupled to routes

- File: `routes/task_routes.py:14-56`
- File: `routes/task_routes.py:117-148`
- File: `routes/task_routes.py:158-218`
- File: `routes/user_routes.py:12-23`
- File: `routes/user_routes.py:67-82`
- File: `routes/user_routes.py:140-146`
- File: `routes/report_routes.py:15-68`
- File: `routes/report_routes.py:159-219`
- Evidence: route handlers directly call `Model.query`, `db.or_`, `db.session.add/delete/commit/rollback`, and ORM relationship loading while also handling HTTP input/output.
- Impact: database technology and transaction boundaries leak into transport code; persistence failures, query behavior, and rollback semantics cannot be tested at a stable repository boundary.
- Recommendation: introduce repositories for queries/mapping and a service/unit-of-work boundary for commits and rollback; controllers should call those abstractions and map outcomes.
- Validation: static inspection must find no ORM queries or session commit/rollback calls in route/controller modules; repository tests must cover query results and transaction failure paths, followed by the endpoint smoke suite.

### [MEDIUM] PERF-001 — Query-in-loop patterns create N+1 behavior

- File: `routes/task_routes.py:41-56`
- File: `routes/report_routes.py:53-68`
- File: `routes/report_routes.py:157-165`
- Evidence: `GET /tasks` queries each task's user and category individually; summary reports query tasks for each user; category listing counts tasks with one query per category.
- Impact: response latency and database load grow with the number of tasks/users/categories rather than with a bounded batch of queries.
- Recommendation: use joins, eager loading, grouped aggregates, or repository batch methods and keep report calculations over already-loaded data.
- Validation: instrument SQLAlchemy query events against fixtures with increasing entity counts, assert query count does not grow per item, and compare response shapes and values.

### [MEDIUM] QUAL-001 — Validation and domain constants are duplicated across layers

- File: `routes/task_routes.py:92-114`
- File: `routes/task_routes.py:166-184`
- File: `routes/user_routes.py:54-72`
- File: `routes/user_routes.py:102-122`
- File: `utils/helpers.py:57-108`
- Evidence: title, status, priority, date, email, role, and password rules are repeated in route handlers; `process_task_data` contains a parallel task-validation path and shared constants are defined separately at `utils/helpers.py:110-116`.
- Impact: rule changes can produce inconsistent create/update behavior, and the unused helper can diverge silently from the reachable route logic.
- Recommendation: centralize typed request schemas and domain constants, remove or connect dead validation paths, and have both create/update use the same validator.
- Validation: run a table-driven validation matrix through both create and update use cases and assert identical accepted/rejected values and stable error mapping.

### [MEDIUM] DATA-002 — Seed workflow commits related data in separate phases

- File: `seed.py:11-14`
- File: `seed.py:37`
- File: `seed.py:63`
- File: `seed.py:92`
- Evidence: the seed script deletes existing rows and commits, commits users, commits categories, and only then commits tasks. A failure after any earlier commit leaves a partially seeded database.
- Impact: rerunning or failing halfway through initialization can leave inconsistent users/categories/tasks and make later endpoint results depend on where the seed failed.
- Recommendation: own the whole seed operation in one explicit transaction, or make each phase independently idempotent with a documented consistency strategy.
- Validation: inject a deterministic failure after user/category writes and assert all related tables return to their pre-seed state; run the success path and assert all three entity sets commit together.

### [LOW] QUAL-004 — Dead imports and debugging residue remain in runtime modules

- File: `app.py:7`
- File: `models/task.py:3`
- File: `routes/task_routes.py:7`
- File: `routes/user_routes.py:6`
- File: `routes/report_routes.py:7-8`
- File: `utils/helpers.py:3-7`
- File: `routes/task_routes.py:149-153,219,234`
- File: `routes/user_routes.py:83-89,147`
- Evidence: multiple imported modules are not used by their files, and request handlers print task/user operations and exception text to standard output.
- Impact: noise obscures operational signals, increases maintenance cost, and can expose sensitive exception details in collected logs.
- Recommendation: remove unused imports, replace ad-hoc prints with structured logging, and avoid logging secrets or raw exception details.
- Validation: run the configured linter/static checker with unused-import and logging rules enabled, then trigger expected and unexpected failures and inspect logs for sensitive values.

## README comparison

After the independent findings were completed, `README.md` was compared as a manual-analysis source. The historical comparison recorded zero concrete findings because the manual section was absent at that point. The final documentary correction restores the original eight-finding baseline at `README.md:64-79` without changing this audit's independent findings, evidence, or dispositions. No finding was copied from the README or the stale report.

## Proposed Phase 3 plan

1. Establish an application factory/configuration boundary and security baseline: authenticate and authorize destructive operations (SEC-002), replace password handling and serializers (SEC-004), externalize/rotate secrets (SEC-003), and make runtime defaults safe (OPS-001). Add negative security probes before changing routes.
2. Preserve blueprints while extracting thin controllers, domain services, repositories, and an explicit unit-of-work boundary (ARCH-001, ARCH-002, ARCH-003). Keep current paths, success statuses, JSON keys, and documented failure responses unless a deliberate security change is approved.
3. Consolidate validation/constants (QUAL-001), replace query loops with batch/eager operations (PERF-001), make seed writes atomic (DATA-002), and remove dead/debug residue (QUAL-004). Run the baseline, failure-path checks, query-count checks, and rollback checks after each milestone.

## Contract risks

- Current DELETE endpoints return 200 without credentials; adding authorization will deliberately change unauthorized responses to 401/403.
- User serializers currently expose a `password` key; removing it is a deliberate security contract change that must be documented and approved.
- Preserve all 22 paths, methods, successful status codes, response envelopes, and field names not explicitly changed for security.
- The application currently relies on a fixed port 5000 and `python app.py`; the safe replacement must provide an explicit supported startup/configuration path.
- Dynamic timestamps, generated IDs, seeded counts, and report values are data-dependent and should be compared by shape and invariants rather than literal timestamp equality.

## Approval gate

No Phase 3 implementation was executed. No final finding disposition is assigned before implementation and finding-specific validation.

Proceed with Phase 3 refactoring? [y/n]

## Phase 3 — Implementation result

The approved refactoring was executed incrementally. The composition root now uses `create_app()` in `app.py:13-38`, configuration is environment-backed in `config.py:11-35`, and production exposes `wsgi:app` through `wsgi.py:1-4`. Routes are transport-only wrappers in `routes/task_routes.py:19-59`, `routes/user_routes.py:19-52`, `routes/report_routes.py:10-17`, and `routes/category_routes.py:16-34`; repositories own ORM access in `repositories/*.py`, services own workflows, and `controllers/response.py:6-13` centralizes expected/unexpected error mapping.

Security and contract changes intentionally approved in Phase 3:

- anonymous DELETE requests now fail with 401; admin bearer-token requests retain 200 success responses;
- login tokens are signed with `itsdangerous` and expire according to `TOKEN_MAX_AGE`;
- user create/get/update/login responses no longer contain `password`;
- production requires `SECRET_KEY`, forces debug off, and refuses `python app.py`; production should load `wsgi:app` through a WSGI server;
- CORS defaults to an explicit localhost allowlist and host/port/database settings are configurable.

## Post-refactor validation

- `PYTHON_BIN=/tmp/task-manager-api-phase3.oZMGVh/venv/bin/python bash scripts/validation/validate-task-manager-api.sh`: exit 0 on port 5000; all endpoint probes, anonymous 401 checks, authorized 200 checks, and cleanup passed.
- `PYTHON_BIN=/tmp/task-manager-api-phase3.oZMGVh/venv/bin/python PORT=5053 bash scripts/validation/validate-task-manager-api.sh`: exit 0; configurable-port boot and the same endpoint contract passed.
- `PYTHONPATH=. /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python scripts/validation/validate-findings.py`: exit 0; password, authorization, rollback, seed, and query-count checks passed with `{'task': 1, 'report': 5, 'category': 2}`.
- `/tmp/task-manager-api-phase3.oZMGVh/venv/bin/ruff check app.py auth.py config.py controllers models repositories routes services utils seed.py wsgi.py`: exit 0.
- `python3 -m compileall -q .`: exit 0.
- `APP_ENV=production SECRET_KEY=validation-secret /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python -c "from wsgi import app; assert app.debug is False"`: exit 0.
- `APP_ENV=production SECRET_KEY=validation-secret /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python app.py`: exit 1 as the intentional production guard; no development server was started.
- `APP_ENV=production SECRET_KEY= /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python -c "from app import app"`: exit 1 as the intentional fail-closed secret guard.
- Static review after implementation found no ORM/session calls in `routes/` or `controllers/`, no old MD5/committed-secret literals in application Python, exactly one seed commit, and no runtime `print()` calls in routes/controllers/services/utils.

## Final finding disposition

| Finding | Disposition | Final implementation evidence | Validation evidence | Remaining risk |
|---|---|---|---|---|
| `SEC-002` — unauthenticated destructive endpoints | `RESOLVED` | `auth.py:31-42`; protected DELETE routes at `routes/task_routes.py:39-42`, `routes/user_routes.py:39-42`, `routes/category_routes.py:31-34` | `scripts/validation/validate-findings.py:61-77`; main validator anonymous DELETE -> 401 and admin DELETE -> 200 | Authorization is admin-only; broader per-resource ownership policy is not implemented |
| `SEC-004` — MD5/password disclosure | `RESOLVED` | `models/user.py:16-30` uses Werkzeug password hashing and omits `password` from `to_dict()` | `scripts/validation/validate-findings.py:32-52`; all user/login smoke shapes omit `password` | Existing databases containing legacy MD5 hashes require a password-reset/migration procedure; the final app no longer generates, verifies, or emits MD5 material |
| `SEC-003` — committed secrets | `RESOLVED` | `config.py:11-35` loads secret/SMTP values from environment; `services/notification_service.py:5-28` has no literals | old-literal `rg` scan exit 0; production missing-secret import exit 1 | Secret rotation must still be performed for any credentials exposed by the old revision |
| `OPS-001` — unsafe runtime defaults | `RESOLVED` | `config.py:17-30`; `app.py:13-48`; `wsgi.py:1-4` | production WSGI import exit 0, production `app.py` guard exit 1, smoke passed on ports 5000 and 5053, factory import created no database | A production WSGI server/deployment process must be supplied externally |
| `ARCH-001` — god route modules | `RESOLVED` | split category/report routes plus `controllers/`, `services/`, and `repositories/` boundaries | smoke passed all 22 route patterns; direct service/repository finding checks passed | Controllers/services are intentionally lightweight and share the existing global SQLAlchemy extension |
| `ARCH-002` — business logic in routes | `RESOLVED` | validation/workflows in `utils/validation.py:6-114` and `services/task_service.py:22-99`, `services/user_service.py:22-105`, `services/report_service.py` | route inspection found only request parsing/delegation; full smoke and finding-specific tests passed | No dedicated external test suite was added; deterministic scripts cover the audited behaviors |
| `ARCH-003` — persistence coupled to routes | `RESOLVED` | ORM access in `repositories/task_repository.py:7-34`, `repositories/user_repository.py:7-21`, `repositories/category_repository.py:7-18`; `repositories/unit_of_work.py:8-18` owns commits | `rg` for ORM/session calls in `routes controllers` returned no matches; smoke passed | Repository abstractions still use the global Flask-SQLAlchemy extension |
| `PERF-001` — N+1 query loops | `RESOLVED` | joined/select-in loading in `repositories/task_repository.py:7-9`, `repositories/user_repository.py:7-9`, `repositories/category_repository.py:7-9`; aggregate calculations in `services/report_service.py` | finding-specific query counts: task 1, report 5, category 2 | Counts should be re-baselined if new report dimensions are added |
| `QUAL-001` — duplicated validation/constants | `RESOLVED` | centralized rules in `utils/validation.py:6-114`; services call the same normalizers; `models/task.py` reuses `VALID_STATUSES` | finding-specific validation and full Ruff exit 0 | Validation compatibility helper remains for callers of the old `utils.helpers.process_task_data` name |
| `DATA-002` — non-atomic seed | `RESOLVED` | one transaction with flushes and rollback in `seed.py:13-57` | injected post-flush seed failure preserved pre-seed counts; source contains exactly one `db.session.commit()` | SQLite schema creation remains a separate idempotent setup step before the transaction |
| `QUAL-004` — dead imports/debug residue | `RESOLVED` | cleaned imports and structured logging in `utils/helpers.py`, `services/notification_service.py`, and `controllers/response.py:11-13`; routes have no ad-hoc prints | full Ruff exit 0, compileall exit 0, and runtime static print scan passed | Logging policy is minimal and can be expanded for deployment observability |

No CRITICAL or HIGH finding remains partially resolved or unaddressed. The final closure gate passed with application boot, endpoint validation, negative/failure-path validation, and cleanup all successful.
