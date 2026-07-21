# Architecture Audit Report — ecommerce-api-legacy

## Phase 1 — Project Analysis

- Project: `ecommerce-api-legacy`
- Language/runtime: Node.js `v20.20.2` (CommonJS)
- Framework: Express `4.22.1` resolved by `package-lock.json` (manifest range `^4.18.2`)
- Database: SQLite `5.1.7` resolved by `package-lock.json` (manifest range `^5.1.6`), opened as an in-memory database
- Domain: LMS/e-commerce checkout: users, courses, enrollments, payments and audit logs
- Current architecture: monolithic/hybrid. `src/app.js` bootstraps Express and delegates all application setup to `AppManager`; `src/AppManager.js` combines schema/data initialization, route registration, SQL, checkout workflow, report aggregation and deletion; `src/utils.js` combines configuration, cache state and password transformation.
- Source files reviewed: 3 application source files (`src/app.js`, `src/AppManager.js`, `src/utils.js`)
- Startup command: `npm start` → `node src/app.js`
- Baseline validation: available after `npm ci` (exit 0). `node --check` passed for all three source files. `npm test -- --runInBand` was executed and failed with exit 1 because no `test` script exists. `npm start` booted and all three public routes were exercised with successful curl commands; no health endpoint is defined. The spawned process was terminated with Ctrl-C; the terminal command reported exit 1 because it was interrupted.

### Public endpoint inventory

| Method | Path | Success status | Success response shape |
|---|---|---:|---|
| POST | `/api/checkout` | 200 | JSON object `{ msg: "Sucesso", enrollment_id: number }` |
| GET | `/api/admin/financial-report` | 200 | JSON array of `{ course, revenue, students: [{ student, paid }] }` |
| DELETE | `/api/users/:id` | 200 | Text: `Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.` |

Observed error contracts include 400 text for invalid checkout input/payment denial, 404 text for an unavailable course, and 500 text for selected database/write errors. No `/health` route was found.

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 2 |
| HIGH | 4 |
| MEDIUM | 3 |
| LOW | 1 |
| Total | 10 |

## Findings

### [CRITICAL] Hardcoded credentials and payment secret in source

- Rule: `SEC-002`
- File: `src/utils.js:2-5`
- Evidence: `config` contains `dbUser`, `dbPass`, a `paymentGatewayKey` named `pk_live_...`, and an SMTP account as source literals. The checkout path interpolates the payment key into a log message at `src/AppManager.js:45`.
- Impact: credentials or payment material committed to source can be copied from the repository and the payment key is exposed to application logs during checkout. The names and values indicate production-like secrets; whether they are active cannot be established from local source alone.
- Recommendation: move required secrets to environment-backed configuration that fails closed, redact them from logs, rotate any exposed values, and inject configuration from the composition root.

### [CRITICAL] Plaintext seed password and deterministic weak password transformation

- Rule: `SEC-003`
- File: `src/AppManager.js:18-21,68-69`; `src/utils.js:17-22`
- Evidence: the seed inserts `pass` as the literal `'123'`. New users use `badCrypto(p || "123456")`; `badCrypto` repeatedly Base64-encodes the password, concatenates only the first two characters, and truncates the result to 10 characters. No adaptive password hash or verification boundary exists.
- Impact: a reachable checkout request can persist credentials using a reversible/deterministic custom scheme or a predictable default, while the seed stores a plaintext password. This is a release-blocking password-handling defect even though no login route is currently exposed.
- Recommendation: use an established adaptive password hasher with per-password salts and a verify function, reject missing/weak passwords instead of applying a default, and rotate/migrate seeded credentials.

### [HIGH] `AppManager` is a god class/module

- Rule: `ARCH-001`
- File: `src/AppManager.js:4-138`
- Evidence: one class creates the database, creates schema and seed data (`10-23`), registers all HTTP routes (`25-138`), performs checkout/payment/audit workflow (`28-78`), aggregates the financial report (`80-129`), and deletes users (`131-136`).
- Impact: transport, persistence, domain decisions and infrastructure are inseparable, making focused tests and safe boundary changes difficult. A failure or change in one concern affects the whole application manager.
- Recommendation: keep `src/app.js` as the composition root and incrementally extract repositories, a checkout service, report service, controllers/route adapters, and centralized error handling while preserving the current contracts.

### [HIGH] Checkout route is a fat controller

- Rule: `ARCH-002`
- File: `src/AppManager.js:28-78`
- Evidence: the route parses abbreviated request fields, validates input, queries course/user state, decides payment status from the card prefix, creates users, inserts enrollment/payment/audit records, writes cache state, logs a secret-bearing message, and maps every response directly inside nested callbacks.
- Impact: HTTP transport is coupled to business workflow and SQL side effects; the route cannot be tested or reused without Express and a live database handle, and partial failure paths are difficult to reason about.
- Recommendation: reduce the route to input parsing and response mapping; delegate checkout orchestration to a service and persistence to repositories, with the payment decision isolated behind a domain/provider abstraction.

### [HIGH] Multi-step checkout writes are not transactional

- Rule: `ARCH-003`
- File: `src/AppManager.js:50-61,68-74`
- Evidence: enrollment, payment and audit rows are written in separate callbacks, and user creation may precede them. There is no `BEGIN`, `COMMIT` or `ROLLBACK`; an audit callback error is ignored before returning the 200 success response.
- Impact: a failure after any earlier write can leave a user/enrollment/payment partially persisted, and the API can report success after the audit write fails. This can corrupt checkout state and financial reporting.
- Recommendation: move the workflow into a repository transaction with explicit commit/rollback and propagate every write error before mapping the response.

### [HIGH] Mutable process-global cache state

- Rule: `ARCH-004`
- File: `src/utils.js:9-15,25`; `src/AppManager.js:59`
- Evidence: `globalCache` is a module-level object exported from `utils.js` and mutated by `logAndCache`; each successful checkout writes `last_checkout_<userId>` into that shared object.
- Impact: data persists across requests and users for the process lifetime, has no eviction or ownership boundary, and couples request behavior through hidden mutable state. It is also not suitable for multiple processes or controlled test isolation.
- Recommendation: inject an explicit cache interface from the composition root, define retention/ownership semantics, or remove the cache if it is not part of the required contract.

### [MEDIUM] Financial report performs N+1-style query expansion

- Rule: `PERF-001`
- File: `src/AppManager.js:83-127`
- Evidence: the handler fetches all courses, then queries enrollments once per course (`92`), then queries a user and payment once per enrollment (`104-106`) inside nested `forEach` loops.
- Impact: query count grows with the number of courses and enrollments, increasing latency and database contention as the dataset grows.
- Recommendation: use a bounded join or batch query for course/enrollment/user/payment data and map the result in memory once.

### [MEDIUM] Database errors are inconsistently ignored and not centrally mapped

- Rule: `ERR-001`
- File: `src/AppManager.js:57-61,92-106,133-136`
- Evidence: the audit-log callback ignores `err` and sends success; the enrollment, user and payment callbacks in the report path do not check their `err` values before dereferencing results; the delete callback ignores its error and always sends a success message.
- Impact: database failures can become false-positive 200 responses, runtime exceptions, incomplete reports, or unhandled asynchronous errors. Error behavior is distributed across deeply nested callbacks rather than mapped centrally.
- Recommendation: check and propagate every callback error, use typed application errors, and add Express error middleware that preserves stable public responses while logging internal details separately.

### [MEDIUM] User deletion leaves orphaned enrollment/payment data

- Rule: `DATA-001`
- File: `src/AppManager.js:14-15,131-136`
- Evidence: the schema declares `enrollments.user_id` and `payments.enrollment_id` without foreign-key constraints or an explicit delete policy; the delete route removes only the user row and its own response explicitly states that enrollments and payments remain dirty.
- Impact: administrative reports can retain financial records pointing to a missing user, and repeated deletion can produce inconsistent domain state. The baseline report already represents a missing user as `student: "Unknown"` when no matching user is found.
- Recommendation: choose and enforce a domain policy (soft delete, restricted delete, or transactional cascade) with foreign keys and tests for the selected behavior.

### [LOW] Dead state and opaque local naming reduce maintainability

- Rule: `LOW-002`
- File: `src/AppManager.js:2,26-33`; `src/utils.js:10,25`
- Evidence: `totalRevenue` is imported but never used by `AppManager`, while `utils.js` exports a mutable `totalRevenue` that is never updated. The checkout handler uses one-letter aliases (`u`, `e`, `p`, `cc`) for domain inputs.
- Impact: unused exported state obscures the actual design and abbreviated names make review of security-sensitive checkout logic harder.
- Recommendation: remove dead state or give it a tested owner, and use explicit names such as `userName`, `email`, `password` and `cardNumber`.

## Deprecated API Check

No application-level `API-001` finding is claimed. The locked direct dependencies are Express `4.22.1` and sqlite3 `5.1.7`; `npm ci` emitted deprecation warnings for several transitive packages, but the local evidence does not prove that this application calls a deprecated Express or SQLite API with a documented replacement. Those install warnings are recorded as dependency-maintenance risk, not as an application API finding.

## Phase Gate

`Phase 2 complete. Proceed with Phase 3 refactoring? [y/n]`
