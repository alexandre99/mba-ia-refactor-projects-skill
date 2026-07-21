# Architecture Audit Report — Project 1

## Phase 1 — Project Analysis

- Project: `code-smells-project`
- Language: Python
- Framework: Flask
- Database: SQLite
- Domain: e-commerce API for products, users, orders and sales reports
- Current architecture: route registration in `app.py`, HTTP and business orchestration in `controllers.py`, persistence and domain workflows concentrated in `models.py`
- Source files reviewed: `app.py`, `controllers.py`, `models.py`, `database.py`, `requirements.txt`

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 5 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **12** |

## Findings

### [CRITICAL] Arbitrary SQL execution endpoint

- File: `app.py:61-80`
- Evidence: `/admin/query` accepts a client-provided SQL string and passes it directly to `cursor.execute`.
- Impact: unauthenticated callers can read, modify or destroy the entire database.
- Recommendation: remove the endpoint; administrative operations must be explicit, authenticated use cases using parameterized queries.

### [CRITICAL] SQL injection through string concatenation

- File: `models.py:45-63`, `models.py:107-131`, `models.py:287-301`
- Evidence: product, login, user creation and search queries concatenate request-controlled values into SQL.
- Impact: data disclosure, authentication bypass and destructive database modification.
- Recommendation: parameterize every query and move persistence behind repositories.

### [CRITICAL] Plaintext password storage and comparison

- File: `models.py:74-113`, `models.py:124-131`
- Evidence: password values are returned by user queries, inserted directly and compared directly in SQL.
- Impact: a database leak immediately exposes credentials and password reuse risk.
- Recommendation: hash passwords with a modern adaptive password hasher and never serialize password fields.

### [CRITICAL] Secrets and debug information exposed

- File: `app.py:8-10`, `controllers.py:266-294`
- Evidence: the secret key is hardcoded, debug is enabled, and `/health` returns the secret key, database path and debug state.
- Impact: sensitive configuration disclosure and unsafe production execution.
- Recommendation: environment-based configuration and a minimal health response.

### [CRITICAL] Unauthenticated destructive reset endpoint

- File: `app.py:49-59`
- Evidence: `/admin/reset-db` deletes all business data without authentication or authorization.
- Impact: complete data loss through a single public request.
- Recommendation: remove from the runtime API or isolate behind an authenticated maintenance command.

### [HIGH] God module combines multiple domains and responsibilities

- File: `models.py:1-316`
- Evidence: one module handles products, users, authentication, orders, inventory, reports, SQL and serialization.
- Impact: strong coupling, poor test isolation and high regression risk.
- Recommendation: split by domain into models, repositories and services.

### [HIGH] Fat controllers mix HTTP, validation and side effects

- File: `controllers.py:26-264`
- Evidence: controllers contain validation rules, business status rules and notification side effects.
- Impact: business behavior is coupled to Flask and difficult to unit test.
- Recommendation: keep route adapters thin and move workflows into services.

### [MEDIUM] N+1 database queries when loading orders

- File: `models.py:173-235`
- Evidence: each order triggers an items query and every item triggers a product query.
- Impact: query count grows with orders and items.
- Recommendation: use joins or batch loading and map results once.

### [MEDIUM] Validation duplicated between create and update

- File: `controllers.py:26-98`
- Evidence: product required fields and numeric validations are repeated.
- Impact: rules can diverge and fixes must be made in multiple places.
- Recommendation: centralize product validation in a schema or domain validator.

### [MEDIUM] Broad exception handling leaks internals

- File: `controllers.py:7-294`
- Evidence: most handlers catch `Exception` and return `str(e)` to the client.
- Impact: implementation and database details leak while error behavior becomes inconsistent.
- Recommendation: centralized error handling with stable public error contracts.

### [LOW] Magic values embedded in business logic

- File: `controllers.py:54-56`, `models.py:258-264`
- Evidence: category lists and revenue thresholds are inline literals.
- Impact: business policies are hard to discover and change.
- Recommendation: named policy constants or configuration owned by the domain service.

### [LOW] Print-based logging

- File: `controllers.py:10-13`, `controllers.py:210-212`, `app.py:58`
- Evidence: operational and business events are emitted with `print`.
- Impact: no structured level, context or production observability.
- Recommendation: use structured application logging and avoid sensitive values.

## Deprecated API Check

No framework API was classified as deprecated from static inspection alone. Dependency versions must be resolved during runtime validation before making a final deprecated-API claim.

## Phase Gate

Phase 2 complete. Application files must not be modified until Phase 3 is explicitly approved.
