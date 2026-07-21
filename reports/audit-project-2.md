# Architecture Audit Report — ecommerce-api-legacy

## Project profile

- Stack: Node.js `v20.20.2`, npm `10.8.2`, Express `4.22.1`, SQLite3 `5.1.7`
- Database: SQLite in-memory (`:memory:`)
- Domain: LMS/e-commerce de cursos, checkout, matrículas, pagamentos e relatório financeiro
- Source files analyzed: 3 (`src/app.js`, `src/AppManager.js`, `src/utils.js`)
- Public endpoints: 3 declarados (`POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`)
- Baseline status: failed; the official script booted the process but tested undeclared `GET /`, which returned 404

## Executive summary

CRITICAL: 2 | HIGH: 4 | MEDIUM: 2 | LOW: 2

The current implementation exposes destructive administration without authorization, commits production-looking credentials, and stores passwords through a non-cryptographic routine. The same `AppManager` class combines database setup, route declaration, HTTP parsing, business workflows, persistence, reporting, and deletion. The first refactoring order should isolate configuration/secrets and authorization, then extract use cases and repositories while preserving the observed route contracts. The official baseline is not a passing behavioral safety net because its readiness probe targets a route that does not exist.

This report was produced from the current source and configuration files before consulting the repository's manual Project 2 analysis. Findings are facts observed in the cited lines; impacts and recommendations are architectural/security inferences from those facts.

## Findings

### [CRITICAL] SEC-002 — Destructive user deletion is publicly reachable

- File: `src/AppManager.js:131-136`
- Evidence: The application declares `DELETE /api/users/:id`, reads the caller-controlled path parameter, executes `DELETE FROM users WHERE id = ?`, and sends a success response without authentication, authorization, confirmation, or checking the database callback error.
- Impact: Any caller who can reach the API can delete arbitrary users by identifier. The response itself acknowledges that related enrollments and payments remain inconsistent.
- Recommendation: Remove this route from the public contract or protect it with explicit administrative authorization, audit logging, safe deletion semantics, and a deliberate compatibility decision.
- Validation: Exercise authorized and unauthorized deletion attempts against an isolated database; verify status codes, authorization, referential integrity, and audit records.

### [CRITICAL] SEC-003 — Usable-looking credentials and live payment key are committed

- File: `src/utils.js:1-7`
- Evidence: `config` contains `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, and an SMTP identity as source literals. The payment key is used in the checkout log at `src/AppManager.js:43-46`.
- Impact: Repository access exposes credentials/configuration presented as production-like, and the payment key is reachable in normal checkout execution. Rotation, disclosure, or accidental use against an external system can compromise data or payment operations.
- Recommendation: Rotate any real values immediately, remove secrets from source history, load configuration from the environment/secret store through a composition root, and fail closed for production when required secrets are absent.
- Validation: Scan tracked source for secret literals, run with injected test configuration, and verify that production startup rejects missing required secrets without printing values.

### [HIGH] SEC-004 — Passwords use reversible/truncated base64 rather than password hashing

- File: `src/utils.js:17-23`
- Evidence: `badCrypto` repeatedly base64-encodes the password and returns only the first 10 characters; base64 is encoding, not a password hashing function. The path is reachable from `src/AppManager.js:66-72`, and the seed inserts the literal password `123` at `src/AppManager.js:18`.
- Impact: A database disclosure does not receive password protection designed for credential storage; the routine is deterministic, weak, and unsuitable for authentication. The checkout path can create users using this routine.
- Recommendation: Use a maintained password-hashing algorithm with a per-password salt and a verified comparison API; remove plaintext seed credentials and eliminate the fallback password.
- Validation: Create a user through checkout in an isolated database, assert the stored value is a modern password hash, verify correct/incorrect comparisons, and confirm no plaintext/default password is accepted.

### [HIGH] ARCH-001 — `AppManager` is a cross-domain god module

- File: `src/AppManager.js:4-138`
- Evidence: One class initializes the SQLite connection and schema/seed data (`10-23`), registers all HTTP routes (`25-138`), parses request payloads, creates users, decides payment status, writes enrollments/payments/audit logs, updates cache, builds financial reports, and deletes users.
- Impact: Changes to transport, persistence, checkout, reporting, or administration are coupled in one module, making independent testing and safe incremental changes difficult. A failure or change in one concern can affect unrelated routes.
- Recommendation: Keep a small composition root, then split routers/controllers, checkout and reporting services, repositories, configuration, and domain models incrementally while preserving route contracts.
- Validation: Unit-test extracted services/repositories independently and run the same endpoint probes before and after each extraction.

### [HIGH] ARCH-002 — Checkout and reporting workflows run inside route handlers

- File: `src/AppManager.js:28-78` and `src/AppManager.js:80-129`
- Evidence: The checkout handler validates fields, queries the course/user, creates a user, derives a password value, decides payment status from the card prefix, inserts enrollment/payment/audit rows, updates cache, and maps responses. The report handler calculates revenue and assembles student data while traversing database callbacks.
- Impact: Business policy and multi-step workflows are tied to Express callbacks, which makes transaction boundaries, error handling, reuse, and isolated testing unclear. Partial writes can leave enrollment/payment state inconsistent.
- Recommendation: Move checkout orchestration to a service and reporting calculation to a query/service boundary; let controllers parse input and map expected outcomes only, with explicit transaction ownership.
- Validation: Test service outcomes for accepted/denied/missing-course cases and force persistence failures to verify rollback and stable HTTP mapping.

### [HIGH] ARCH-003 — HTTP handlers are directly coupled to SQLite persistence

- File: `src/AppManager.js:37-63`, `src/AppManager.js:83-128`, and `src/AppManager.js:131-136`
- Evidence: Route callbacks call `this.db.get`, `this.db.all`, and `this.db.run` directly for course/user lookup, user creation, enrollment, payment, audit logging, report queries, and deletion. No repository boundary or explicit transaction is present.
- Impact: Transport code depends on SQLite APIs and SQL schema details, preventing persistence substitution and making database error/transaction behavior part of every handler's control flow.
- Recommendation: Introduce repositories for users, courses, enrollments, payments, audit logs, and reporting; keep parameterized SQL and transaction ownership below the controller/service boundary.
- Validation: Test repository behavior independently, inject a repository into the service/controller, and verify all existing status codes and response shapes through HTTP probes.

### [MEDIUM] PERF-001 — Financial report performs query-in-loop / N+1 access

- File: `src/AppManager.js:83-128`
- Evidence: The report first loads all courses, then for each course loads enrollments (`92`), and for each enrollment separately loads the user (`104`) and payment (`106`).
- Impact: Query count grows with the number of courses and enrollments, increasing latency and database load; the callback aggregation also increases the risk of incomplete or inconsistent report assembly.
- Recommendation: Move reporting to a repository query using joins/aggregation or bounded batch queries, then map rows to the existing response shape in a service.
- Validation: Run a fixture with multiple courses/enrollments, measure query count, and compare totals, student ordering, and response shape with the baseline.

### [MEDIUM] TEST-001 — No executable endpoint safety net covers the contract

- File: `package.json:6-8` and `../scripts/validation/validate-ecommerce-legacy.sh:21-32`
- Evidence: The package exposes only `start` and no test script. The repository has no project test files in the analyzed inventory. The available validator probes only `GET /` and explicitly prints `endpoint inventory still pending`; that probe fails because the application has no `/` route.
- Impact: Architectural changes have no deterministic automated check for checkout outcomes, report shape, deletion behavior, or failure paths. A passing boot alone would not prove observable behavior preservation.
- Recommendation: Add a deterministic, isolated endpoint validator in the validation area before Phase 3, covering boot, success, validation failure, not-found, payment denial, report, and protected administration behavior.
- Validation: Execute the validator from a clean dependency state and require non-zero exit on startup, status, response-shape, or cleanup failures.

### [LOW] QUAL-002 — Domain and transport constants are embedded in handlers

- File: `src/AppManager.js:35-48` and `src/utils.js:1-7`
- Evidence: Required field names, payment decision prefix `"4"`, statuses `"PAID"`/`"DENIED"`, fallback password `"123456"`, and port `3000` are embedded as literals across transport/configuration code.
- Impact: Policy changes require editing route code and can produce inconsistent behavior or accidental contract changes.
- Recommendation: Centralize domain statuses, checkout input mapping, and environment-backed runtime settings in named configuration/domain modules without changing the external payload contract.
- Validation: Test the same payloads and statuses while changing only the injected configuration/constants.

### [LOW] QUAL-005 — Response construction is inconsistent across routes

- File: `src/AppManager.js:35-60`, `src/AppManager.js:80-129`, and `src/AppManager.js:131-136`
- Evidence: Checkout failure and deletion return plain text with `send`, successful checkout returns `{msg,enrollment_id}` JSON, and the report returns a bare JSON array. There is no shared response/error policy.
- Impact: Clients must handle unrelated response media/types and future handlers can drift further; centralizing this without a baseline could accidentally break consumers.
- Recommendation: First capture and preserve the current route/status/shape contract, then introduce a documented response/error mapper only if compatibility requirements allow it.
- Validation: Compare content type, status, field names, nesting, and representative bodies for every existing endpoint before and after the mapper extraction.

## Proposed Phase 3 plan

1. Externalize/rotate secrets and add explicit authorization for destructive administration (`SEC-002`, `SEC-003`), then replace the password routine and seed/default credentials (`SEC-004`).
2. Add deterministic endpoint validation and capture the current contract (`TEST-001`, `QUAL-005`).
3. Extract a composition root, routers/controllers, checkout/reporting services, and repositories in small steps (`ARCH-001`, `ARCH-002`, `ARCH-003`); preserve parameterized queries and route contracts.
4. Replace the report's query-in-loop with a repository query/aggregation (`PERF-001`) and centralize named constants (`QUAL-002`).

## Contract risks

- `GET /` is not a public application endpoint, although the official validator assumes it exists; changing this would be a deliberate validation-script or compatibility decision.
- `POST /api/checkout` currently uses `usr`, `eml`, `pwd`, `c_id`, and `card`, returns plain-text failures for several cases, and returns `{msg, enrollment_id}` on success.
- `GET /api/admin/financial-report` is reachable without an authorization check and returns course revenue and student names; this is an observed exposure to resolve during security design even though the catalog rule used here is scoped to destructive administration.
- `DELETE /api/users/:id` returns success regardless of the database callback error and explicitly leaves related records; any correction must define whether deletion is restricted, transactional, or removed.
- The database is in-memory and seeded at startup, so endpoint observations are disposable and do not establish production persistence behavior.

## Approval gate

Proceed with Phase 3 refactoring? [y/n]
