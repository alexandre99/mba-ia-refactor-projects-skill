# Architecture Audit Report — Project 3 (`ecommerce-api-legacy`)

## Project profile

- Stack: Node.js 20.20.2, Express 4.22.1 installed (declared `^4.18.2`), npm 10.8.2
- Database: SQLite via `sqlite3` 5.1.7 installed (declared `^5.1.6`); `:memory:` by default in development and a configured file in production
- Domain: LMS course enrollment and checkout, including payment records, financial reporting, and administrative user deletion
- Source files analyzed: 20 files under `src/`
- Public endpoints: 3 routes
- Baseline status: boot and representative probes passed; no repository validation script or `npm test` command is available

## Executive summary

CRITICAL: 1 | HIGH: 2 | MEDIUM: 3 | LOW: 1

The current code has useful route/controller/service/repository boundaries, checkout writes are wrapped in a database transaction, password creation uses scrypt, and the checkout cache is updated after the transaction. The main risks are an unauthenticated administrative report, orphaned enrollment/payment state after user deletion, and a non-idempotent production bootstrap that fails on restart and seeds demo data into durable storage.

## Endpoint contract inventory

| Method | Path | Handler | Input | Observed success | Response shape |
|---|---|---|---|---|---|
| POST | `/api/checkout` | `CheckoutController.create` | JSON `usr`, `eml`, `pwd`, `c_id`, `card` | `200` | JSON `{ msg, enrollment_id }` |
| GET | `/api/admin/financial-report` | `ReportController.financialReport` | none | `200` | JSON array of `{ course, revenue, students[] }` |
| DELETE | `/api/users/:id` | `UserController.delete` | path `id`, `x-admin-token` header | `200` | text message |

## Phase 1 — Project analysis

- Runtime/package manager: Node.js and npm.
- Framework: Express, constructed in `src/app.js:1,32-39`.
- Database: SQLite wrapper in `src/infrastructure/database.js:1-60`.
- Startup: `npm start` → `node src/server.js`, declared in `package.json:6-8`.
- Configuration: `src/config.js:1-12`; `PORT`, `DATABASE_PATH`, `NODE_ENV`, and `ADMIN_TOKEN` are environment-backed.
- Composition root: `src/app.js:17-44` wires database, repositories, services, controllers, and routes.
- Server entrypoint: `src/server.js:1-31` starts listening and closes the database on signals.
- Routes/controllers: `src/routes.js:1-15` and `src/controllers/*.js` handle HTTP transport and response mapping.
- Services: checkout workflow in `src/services/checkoutService.js:5-46`; report aggregation in `src/services/reportService.js:3-34`; user deletion delegation in `src/services/userService.js:3-11`.
- Repositories: SQL and persistence mapping in `src/repositories/*.js`.
- Domain: LMS users, courses, enrollments, payments, audit logs, checkout, and financial reporting.
- Validation availability: no `scripts/validation/` directory, no test files, and no `test` script. Executed `npm test` failed with `Missing script: "test"`.

The checkout workflow finds an active course, evaluates the card prefix, creates or reuses a user, writes enrollment/payment/audit rows inside `db.transaction` at `src/services/checkoutService.js:28-42`, then updates the cache at lines 44-45. User deletion currently removes only the user row while its response acknowledges that related records remain dirty.

### Baseline evidence

The application was booted on port `4317` with `DATABASE_PATH=:memory:` and `ADMIN_TOKEN=baseline-admin-token`.

- Boot: passed; server printed `Frankenstein LMS rodando na porta 4317...`.
- Financial report without a token: `200` with financial JSON data.
- Financial report with the token: `200` with the same JSON shape.
- Successful checkout: `200`, `{"msg":"Sucesso","enrollment_id":2}`.
- Denied card: `400`, `Pagamento recusado`.
- Missing checkout fields: `400`, `Bad Request`.
- Unknown course: `404`, `Curso não encontrado`.
- User deletion without token: `401`, `Unauthorized`.
- User deletion with token: `200`, legacy dirty-state message.
- Malformed JSON: `400` HTML containing `SyntaxError`, absolute repository paths, and parser stack details.
- Cleanup: spawned process stopped; no listener remained on port `4317`.

## Findings

### [CRITICAL] SEC-002 — Unauthenticated financial administration

- File: `src/routes.js:8-10`; `src/middleware/adminAuth.js:1-7`
- Evidence: `/api/admin/financial-report` at `src/routes.js:9` is registered without `adminOnly`, while deletion at line 10 receives the middleware. An executed request without `x-admin-token` returned `200` and revenue/student data.
- Impact: any caller can read administrative financial and student information.
- Recommendation: apply the existing authorization boundary to the report route and require a non-empty environment-backed administrator credential.
- Validation: assert `401` without the header and `200` with a valid token; assert the denied request does not mutate state.

### [HIGH] DATA-002 — User deletion leaves a partial relational aggregate

- File: `src/services/userService.js:8-10`; `src/repositories/userRepository.js:17-19`; `src/infrastructure/initializeDatabase.js:3-7`
- Evidence: deletion executes only `DELETE FROM users WHERE id = ?`; enrollments/payments have no foreign-key cascade. After an executed deletion of user `1`, direct SQLite counts were `users=0`, `enrollments=1`, `payments=1`, `audit_logs=0`.
- Impact: orphaned rows remain reportable and can distort revenue/student data.
- Recommendation: define retention policy and implement a transactional deletion workflow or documented foreign-key/cascade equivalent covering all related rows.
- Validation: force a failure after the first related write and verify rollback; then verify successful deletion leaves no orphan aggregate.

### [HIGH] OPS-001 — Durable production bootstrap is non-idempotent and seeds demo data

- File: `src/config.js:1-5`; `src/app.js:17-20`; `src/infrastructure/initializeDatabase.js:1-21`
- Evidence: every app construction creates tables and inserts the hardcoded `Leonan` user/courses; schema statements lack `IF NOT EXISTS`. A second boot against the same SQLite file exited with `SQLITE_ERROR: table users already exists` at `initializeDatabase.js:10`.
- Impact: normal restart against durable storage fails, and fresh production storage receives development/demo data.
- Recommendation: use idempotent migrations and gate demo seeds behind an explicit development/test switch.
- Validation: boot twice against one isolated durable database and verify both starts succeed without duplicate seed rows.

### [MEDIUM] ERR-001 — Malformed JSON exposes internal stack details

- File: `src/app.js:32-33`; `src/config.js:1`
- Evidence: `express.json()` is installed without application error middleware. Malformed JSON returned HTML containing `SyntaxError`, absolute paths, and body-parser/raw-body stack frames.
- Impact: clients receive implementation paths and parser internals.
- Recommendation: add terminal parser/unexpected-error mapping with stable generic responses and server-side detailed logging only.
- Validation: send malformed JSON and inject an infrastructure error; assert stable bodies without stack traces, paths, SQL, or secrets.

### [MEDIUM] TEST-001 — No deterministic behavioral safety net

- File: `package.json:6-8`; missing `scripts/validation/` and test files
- Evidence: only `start` is declared; executed `npm test` failed with `Missing script: "test"`.
- Impact: route/status/response behavior is not reproducible by one repository command before or after refactoring.
- Recommendation: add a target-scoped validator with isolated database, configurable port, boot/readiness, representative success/failure probes, cleanup, and non-zero mismatch handling.
- Validation: run the validator twice and require deterministic success for the baseline and failure for a forced mismatch.

### [MEDIUM] TEST-002 — No finding-specific failure validation

- File: `package.json:6-8`; no validation/test files found
- Evidence: no executable check covers unauthorized report access, orphan prevention/rollback, repeated durable boot, malformed-input leakage, or process cleanup.
- Impact: happy-path smoke checks could pass while the audited security and consistency defects remain.
- Recommendation: add negative/failure probes with database-state assertions and restart checks for every finding.
- Validation: require probes to fail against the vulnerable behavior and pass only after the corresponding correction.

### [LOW] QUAL-005 — Inconsistent response construction and error mapping

- File: `src/controllers/checkoutController.js:16-30`; `src/controllers/reportController.js:6-12`; `src/controllers/userController.js:6-12`
- Evidence: checkout maps `ApplicationError` and returns `Erro interno`, while report/user catch all errors and return `500`/`Erro DB`; no shared transport error policy exists.
- Impact: clients depend on route-specific error conventions.
- Recommendation: centralize expected application-error and unexpected-error mapping while preserving approved contract behavior.
- Validation: execute expected domain and injected repository failures across all controllers and compare stable statuses/bodies.

## Relevant rules checked with no current finding

- `SEC-001`: no request-controlled SQL, shell, eval, template execution, or dynamic module loading.
- `SEC-003`/`SEC-004`: no usable hardcoded secret; checkout passwords use scrypt and user queries exclude password data.
- `ARCH-001`–`ARCH-003`: current source has route/controller/service/repository boundaries; routes/controllers do not execute raw SQL.
- `DATA-003`: cache update follows the checkout transaction.
- `DATA-001`: repository values are parameterized and report SQL is static.
- `PERF-001`: financial reporting uses one joined query.
- `DEP-001`: no deprecated API was raised without authoritative repository/version evidence.

## Proposed Phase 3 plan

1. Protect the financial report and add unauthorized/authorized regression probes for `SEC-002`.
2. Make schema initialization idempotent and seeds development-only for `OPS-001`.
3. Implement consistent transactional/cascade user deletion with rollback proof for `DATA-002`.
4. Add central parser/unexpected-error mapping for `ERR-001` and `QUAL-005`.
5. Add deterministic and finding-specific validation for `TEST-001` and `TEST-002`.

## Contract risks

- Correcting report authorization intentionally changes unauthenticated behavior to `401`.
- Correcting deletion changes persisted side effects currently acknowledged as dirty.
- Replacing malformed-JSON stack HTML is an intentional security/transport contract change.
- Production boot and seed behavior must be validated against durable isolated storage.

## Approval gate

Proceed with Phase 3 refactoring? [y/n]

Phase 3 has not been executed. No application source, configuration, dependency manifest, or other target project was modified during this Project 3 audit.

## Final finding disposition

Not applicable before Phase 3. Complete the mandatory disposition matrix only after explicit approval, implementation, finding-specific validation, and the final closure gate.
