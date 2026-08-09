# Architecture Audit Report — ecommerce-api-legacy

> Historical evidence: the original report and its prior Phase 3 disposition are preserved above. The updated-protocol re-evaluation below was generated independently from the current source on 2026-07-26.

## Project profile

- Stack: Node.js `v20.20.2`, npm `10.8.2`, Express `4.22.1`, SQLite3 `5.1.7`
- Database: SQLite in-memory (`:memory:`)
- Domain: LMS/e-commerce de cursos, checkout, matrículas, pagamentos e relatório financeiro
- Pre-refactor source files analyzed: 3 (src/app.js, src/AppManager.js, src/utils.js).
- Post-refactor source files: 20, organized under composition, routes, controllers, services, repositories, infrastructure, security, and configuration.
- Public endpoints: 3 declarados (`POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`)
- Baseline status: PASSED; the corrected safety-net script booted the process and validated the legacy endpoint contracts without depending on `GET /`

## Executive summary

CRITICAL: 2 | HIGH: 4 | MEDIUM: 2 | LOW: 2

The pre-refactor implementation exposed destructive administration without authorization, committed production-looking credentials, stored passwords through a non-cryptographic routine, and coupled all use cases in AppManager. Phase 3 extracted MVC-oriented boundaries, removed committed secrets, added password hashing and fail-closed admin authorization, and preserved the tested checkout/report contracts. The remaining risks are documented in the Phase 3 disposition.

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

### [MEDIUM] TEST-001 — Behavioral safety net was missing before Phase 3 (resolved)

- File: `package.json:6-8` and `../scripts/validation/validate-ecommerce-legacy.sh:1-165`
- Evidence: The package exposes only `start` and no test script, and the initial validator covered only undeclared `GET /`. The validator was corrected before Phase 3 to install and verify dependencies, use existing `GET /api/admin/financial-report` readiness, exercise all required legacy contracts, validate response shapes, and clean up the spawned process.
- Impact: Before this correction, architectural changes lacked a deterministic automated check for checkout outcomes, report shape, deletion behavior, or failure paths. The current safety net now supplies that gate; the application still requires the behavioral and security refactoring described below.
- Recommendation: Keep the corrected validator as a mandatory pre- and post-refactoring gate, and require explicit approval of this safety net before changing application files.
- Validation: `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` completed with exit 0 after `npm ci`, dependency verification, boot, all endpoint probes, and process cleanup.

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

1. Preserve and explicitly approve the corrected safety net (`TEST-001`, `QUAL-005`) before any application file is changed; use it to capture and compare the current route/status/response contract.
2. Externalize/rotate secrets and add explicit authorization for destructive administration (`SEC-002`, `SEC-003`), then replace the password routine and seed/default credentials (`SEC-004`).
3. Extract a composition root, routers/controllers, checkout/reporting services, and repositories in small steps (`ARCH-001`, `ARCH-002`, `ARCH-003`); preserve parameterized queries and route contracts.
4. Replace the report's query-in-loop with a repository query/aggregation (`PERF-001`) and centralize named constants (`QUAL-002`).

## Contract risks

- `GET /` is not a public application endpoint; the corrected validator deliberately uses existing `GET /api/admin/financial-report` for readiness and does not require a compatibility route.
- `POST /api/checkout` currently uses `usr`, `eml`, `pwd`, `c_id`, and `card`, returns plain-text failures for several cases, and returns `{msg, enrollment_id}` on success.
- `GET /api/admin/financial-report` is reachable without an authorization check and returns course revenue and student names; this is an observed exposure to resolve during security design even though the catalog rule used here is scoped to destructive administration.
- `DELETE /api/users/:id` returns success regardless of the database callback error and explicitly leaves related records; any correction must define whether deletion is restricted, transactional, or removed.
- The database is in-memory and seeded at startup, so endpoint observations are disposable and do not establish production persistence behavior.

## Phase 3 disposition

- Approval: explicit user response y was received before application changes.
- SEC-002 resolved: DELETE /api/users/:id now passes through middleware at src/routes.js:4-10 and src/middleware/adminAuth.js:1-8; missing or unconfigured tokens return 401, while the authorized path preserves the legacy 200 text response.
- SEC-003 resolved: committed credential/payment-key literals and checkout key logging were removed. Runtime settings now come from src/config.js:1-6.
- SEC-004 resolved: new users are stored with scrypt-derived password hashes in src/security/passwordHasher.js:3-15; the plaintext seed/fallback password was removed.
- ARCH-001, ARCH-002, and ARCH-003 resolved: src/app.js:17-40 is the composition root; HTTP wiring is in src/routes.js; controllers orchestrate transport; services own workflows; repositories own SQL.
- PERF-001 resolved: src/repositories/reportRepository.js:6-20 uses one join query, and src/services/reportService.js:8-34 maps the result to the preserved array shape.
- TEST-001 resolved: the validator passed dependency installation, boot, endpoint contracts, authorization behavior, and cleanup with exit 0.
- QUAL-002 resolved through src/constants.js and environment-backed src/config.js.
- QUAL-005 remains intentionally constrained by compatibility: plain-text error/deletion responses and JSON success/report responses are centrally mapped by controllers but retain their legacy shapes.
- Remaining risks: the financial report remains reachable without authorization; checkout writes are sequential without an explicit transaction; the database defaults to in-memory storage; and the project still has no unit-test script beyond the executable validation safety net.

## Approval gate

- Approval received: y.
- Phase 3 refactoring completed and post-refactor validation passed.

## Updated protocol re-evaluation — 2026-07-26

### Current project profile

- Stack: Node.js `v20.20.2`, npm `10.8.2`, Express `4.22.1`, SQLite3 `5.1.7`
- Database: SQLite, default `:memory:`; `DATABASE_PATH` can select a file
- Domain: LMS/e-commerce checkout, users, enrollments, payments, audit logs, and financial reporting
- Current source files analyzed: 20 JavaScript files under `src/`
- Public endpoints: 3 declared routes
- Startup command: `npm start` → `node src/server.js`
- Baseline status in this run: PASSED; `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` exited 0
- Explicit Phase 3 authority: the current user request authorizes only corrections required by this re-evaluation, and requires preservation of historical evidence

### PHASE 1: PROJECT ANALYSIS

The current application has a composition root in `src/app.js`, a server entrypoint in `src/server.js`, route registration in `src/routes.js`, HTTP controllers, domain services, repositories, a SQLite adapter, database initialization, configuration, middleware, and password hashing. The three declared endpoints are:

| Method | Path | Handler | Success/status behavior | Response shape |
|---|---|---|---|---|
| POST | `/api/checkout` | `CheckoutController.create` | `200` for an approved checkout; `400`/`404` for expected failures | `{msg, enrollment_id}` on success; legacy plain text on expected failures |
| GET | `/api/admin/financial-report` | `ReportController.financialReport` | `200` | JSON array of course/revenue/students objects |
| DELETE | `/api/users/:id` | `UserController.delete`, protected by `requireAdminToken` | `401` without the configured token; `200` with it | Plain text |

The checkout use case reads a course and user, then may create a user, enrollment, payment, audit row, and in-memory cache entry. Repository methods parameterize values, but each write currently uses SQLite autocommit and no shared transaction. The report uses one joined query and a service mapper. The admin token fails closed when absent. No endpoint exposes password verification or arbitrary SQL.

### Phase 1 inspected commands

| Command | Exit | Evidence |
|---|---:|---|
| `rtk node --version` | 0 | `v20.20.2` |
| `rtk npm --version` | 0 | `10.8.2` |
| `rtk npm ls --depth=0` | 0 | `express@4.22.1`, `sqlite3@5.1.7` |
| `rtk rg --files -g '!node_modules' -g '!*.db' -g '!*.sqlite'` | 0 | Current project files and 20 `src/` files inventoried |
| `rtk nl -ba src/app.js src/server.js src/routes.js src/config.js ...` | 0 | Current composition, startup, routes, configuration, controllers, services, repositories, infrastructure, middleware, and security lines inspected |
| `rtk rg -n "router\\.(get|post|put|patch|delete)|app\\.(get|post|put|patch|delete)|listen\\(|process\\.env|cache|run\\(|get\\(|all\\(" src package.json ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Endpoint, persistence, configuration, and effect references inventoried |
| `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Baseline boot, representative endpoints, authorization behavior, and cleanup passed |
| `rtk git diff --check` | 0 | No whitespace errors before application corrections |

### Phase 2 — current architecture audit

CRITICAL: 0 | HIGH: 1 | MEDIUM: 2 | LOW: 2

The prior Phase 3 removed the historical security and layering findings. The updated catalog identifies an unresolved transactional boundary, an unsafe production storage default, an incomplete finding-specific safety net, one remaining magic policy value, and the deliberately preserved legacy response divergence.

#### [HIGH] DATA-002 — Checkout writes lack an atomic transaction boundary

- File: `src/services/checkoutService.js:22-36`; `src/repositories/checkoutRepository.js:6-24`; `src/infrastructure/database.js:8-14`
- Evidence: A successful checkout can create a user, enrollment, payment, and audit row through separate `db.run` calls. `SqliteDatabase` exposes `run`, `get`, `all`, and `close`, but no begin/commit/rollback or transaction callback. A later failure can therefore leave earlier writes committed.
- Impact: A failed checkout can leave an orphan user or enrollment without the corresponding payment/audit state, causing inconsistent business and financial data and unsafe retries.
- Recommendation: Add an explicit database transaction/unit-of-work boundary owned by `CheckoutService`; commit all related writes together, roll back on any intermediate failure, and update the cache only after commit.
- Validation: Inject a deterministic failure after a user/enrollment write and assert that user, enrollment, payment, audit, and cache state are all unchanged; then execute the success path and assert committed rows and the post-commit cache entry.

#### [MEDIUM] OPS-001 — Production defaults to ephemeral in-memory storage

- File: `src/config.js:1-5`; `src/infrastructure/initializeDatabase.js:1-21`; `src/server.js:4-6`
- Evidence: `databasePath` defaults to `':memory:'` whenever `DATABASE_PATH` is absent, and startup always creates schema and seed data. `NODE_ENV` is not considered and production startup does not fail closed when durable storage is unconfigured.
- Impact: A deployment that omits `DATABASE_PATH` loses users, enrollments, payments, and audit history on restart and can appear healthy while discarding production state.
- Recommendation: Keep the disposable in-memory default only for non-production execution; require an explicit non-memory `DATABASE_PATH` when `NODE_ENV=production`.
- Validation: Execute production configuration loading with `DATABASE_PATH` unset and assert non-zero failure; execute the normal isolated validator with the development default and assert boot/endpoint behavior remains unchanged.

#### [MEDIUM] TEST-002 — Safety net has no finding-specific rollback/effect proof

- File: `../scripts/validation/validate-ecommerce-legacy.sh:123-176`
- Evidence: The validator checks readiness, successful checkout/report behavior, expected validation failures, and authorized/unauthorized deletion, but it does not inject an intermediate persistence failure or inspect rollback and cache state. Passing endpoint smoke tests cannot detect DATA-002.
- Impact: A future refactor can preserve all happy-path HTTP responses while reintroducing partial checkout writes or moving effects before commit.
- Recommendation: Extend the target-specific validator with a deterministic service-level failure injection and success-path transaction probe, plus stable unexpected-error response mapping where relevant.
- Validation: Run the extended validator and require non-zero failure if injected checkout failure leaves any related row or cache entry behind.

#### [LOW] QUAL-002 — Checkout policy still contains magic values

- File: `src/services/checkoutService.js:17,36`
- Evidence: The payment decision uses the literal card prefix `'4'`, and the cache key uses the literal prefix `'last_checkout_'` inside the workflow. Existing status/message constants are centralized, but these policy values remain embedded in the service.
- Impact: Policy changes require editing workflow code and can create inconsistent behavior if another checkout path introduces a different literal.
- Recommendation: Move the approved-card prefix and cache-key prefix into named checkout constants while preserving the external request and response contract.
- Validation: Assert the service no longer embeds those policy literals, then run approved/denied checkout probes and the transaction probe.

#### [LOW] QUAL-005 — Legacy response construction remains intentionally divergent

- File: `src/controllers/checkoutController.js:12-30`; `src/controllers/reportController.js:6-12`; `src/controllers/userController.js:6-12`
- Evidence: Checkout expected failures and user deletion use plain text, checkout success uses a JSON object, and the financial report returns a bare JSON array. The separate controllers preserve these legacy response shapes.
- Impact: Consumers must handle multiple media/body conventions, and a future endpoint can drift without a shared response policy.
- Recommendation: Preserve the observed contract for this compatibility-sensitive task; document the divergence and centralize response mapping only in a separately approved contract change.
- Validation: Compare status, content type, body text, JSON field names, and array/object shape for every endpoint in the target validator.

### Rules assessed but not raised

- `SEC-001`, `SEC-002`, `SEC-003`, `SEC-004`: current source uses parameterized repository queries, fail-closed deletion authorization, environment-backed admin configuration, and salted scrypt hashes; no reachable arbitrary execution, committed usable secret, plaintext password flow, or unprotected destructive route was observed.
- `ARCH-001`, `ARCH-002`, `ARCH-003`: the prior god-module and transport/persistence coupling were removed; current route/controller/service/repository boundaries are real and used.
- `DATA-003`: `cache.set` occurs after `await this.checkoutRepository.recordAudit(...)` at current `src/services/checkoutService.js:35-36`; the remaining defect is lack of an atomic aggregate commit (`DATA-002`), not an observed cache update before the final current database write. The correction will preserve the after-commit ordering.
- `DATA-001`, `PERF-001`, `ERR-001`, `DEP-001`, `QUAL-001`, and `TEST-001`: current queries are parameterized/static, the report uses a join, errors map to generic client responses, no authoritative deprecated API evidence was found, validation rules are not duplicated across handlers, and the executable safety net exists and passed.

### Proposed corrective Phase 3 plan

1. Add a transaction callback to `SqliteDatabase` and make `CheckoutService` own one unit of work for user/enrollment/payment/audit writes; retain cache update after successful commit. Addresses `DATA-002` and supplies the proof needed by `TEST-002`.
2. Make production configuration fail closed unless `DATABASE_PATH` is explicitly non-memory, while retaining `:memory:` for non-production validation. Addresses `OPS-001` without changing the documented development contract.
3. Move checkout policy literals to `src/constants.js` and extend the target validator with rollback/cache, commit, and error-mapping probes. Addresses `QUAL-002` and closes `TEST-002`; preserve `QUAL-005` as a compatibility limitation.

### Contract risks before correction

- `POST /api/checkout` payload names, statuses, text failures, success object, and enrollment ID type must remain unchanged.
- `GET /api/admin/financial-report` remains a public JSON array for compatibility; no authorization contract change is authorized by this request.
- `DELETE /api/users/:id` must continue returning `401` without a token and the historical `200` text only with the configured admin token.
- The development/default validation path must continue using disposable in-memory SQLite data.

## Approval gate for updated protocol

The user instruction in this Codex session explicitly authorizes the conditional corrective Phase 3 work described above and limits it to findings identified by this re-evaluation. No additional approval prompt is required before those scoped corrections.

### Manual-analysis comparison

Only after the current independent report was complete, `rtk sed -n '1,180p' ../README.md` was executed. The manual Project 2 table contains 8 findings; 1/8 was rediscovered against the current source: checkout without a transaction (`DATA-002`). The other 7 manual findings (committed secrets, sensitive gateway/card logging, the `AppManager` god class, report N+1, callback-pyramid error handling, cryptic legacy variables, and mutable global state) are no longer observed after the prior Phase 3 and were not copied into this current audit. Current `OPS-001`, `TEST-002`, `QUAL-002`, and `QUAL-005` were independently derived from the current implementation and protocol rules.

## Updated protocol final closure — 2026-07-26

### Phase 3 corrective implementation

- `src/infrastructure/database.js:35-53` now owns `BEGIN TRANSACTION`, `COMMIT`, and rollback on failure.
- `src/app.js:21-27` injects the database transaction function into the checkout service.
- `src/services/checkoutService.js:25-45` performs user/enrollment/payment/audit writes inside one transaction and updates the cache only after the transaction resolves.
- `src/config.js:1-14` preserves the development `:memory:` default but rejects absent or `:memory:` storage under `NODE_ENV=production`.
- `src/constants.js:14-19` owns the approved-card and cache-key policy values.
- `../scripts/validation/validate-ecommerce-legacy.sh:6,120-127,185-282` accepts a configurable port, checks production storage safety, and executes finding-specific rollback/commit/cache/error/magic-value probes.

### Final finding-disposition matrix

| Finding | Disposition | Final implementation evidence | Validation evidence | Remaining risk |
|---|---|---|---|---|
| `DATA-002 — Checkout writes lack an atomic transaction boundary` | `RESOLVED` | `src/infrastructure/database.js:35-53` supplies the unit of work; `src/services/checkoutService.js:28-44` encloses all related writes and places cache update after commit. | `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` exit 0; inline probe at `../scripts/validation/validate-ecommerce-legacy.sh:221-235` injected failure after payment and verified seed counts/cache unchanged, then `238-251` verified committed rows/cache. | None observed in this use case. |
| `OPS-001 — Production defaults to ephemeral in-memory storage` | `RESOLVED` | `src/config.js:1-14` fails closed for missing or explicit `:memory:` production storage while retaining non-production behavior. | The same validator exited 0; its production guard at `../scripts/validation/validate-ecommerce-legacy.sh:120-125` rejected both unsafe values, and the normal boot path passed. | A durable path's filesystem permissions are deployment-owned and were not tested. |
| `TEST-002 — Safety net has no finding-specific rollback/effect proof` | `RESOLVED` | `../scripts/validation/validate-ecommerce-legacy.sh:185-282` is executable and checks rollback, post-commit cache, generic error mapping, and policy-literal removal. | `PORT=3017 bash ../scripts/validation/validate-ecommerce-legacy.sh` exited 0, including `Finding-specific validation passed`. | The probe is service-level and does not simulate database process crashes. |
| `QUAL-002 — Checkout policy still contains magic values` | `RESOLVED` | `src/constants.js:14-19` defines `CHECKOUT_POLICY`; `src/services/checkoutService.js:18,44` consumes it. | The validator's `203-205` assertions found neither old service literal, and the approved/denied endpoint probes passed; command exit 0. | None for the audited literals. |
| `QUAL-005 — Legacy response construction remains intentionally divergent` | `PARTIALLY_RESOLVED` | Controllers remain contract-specific at `src/controllers/checkoutController.js:12-30`, `src/controllers/reportController.js:6-12`, and `src/controllers/userController.js:6-12`; no incompatible envelope rewrite was introduced. | The full validator exited 0 for all legacy status/body shapes, including `../scripts/validation/validate-ecommerce-legacy.sh:144-183`. | Plain-text and JSON response conventions remain intentionally different for compatibility. |

No CRITICAL or HIGH finding is `PARTIALLY_RESOLVED` or `NOT_ADDRESSED`. `DATA-003` remains not raised because the cache is after the aggregate commit in the final implementation. The unauthenticated financial report and in-memory development default remain documented compatibility/development choices, outside the scoped current findings; the prior deletion authorization change remains historical and unchanged.

### Final validation status

- Node syntax checks over all current `src` JavaScript files: exit 0.
- `rtk bash -n ../scripts/validation/validate-ecommerce-legacy.sh`: exit 0.
- `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh`: exit 0 on the default port.
- `rtk bash -lc 'PORT=3017 bash ../scripts/validation/validate-ecommerce-legacy.sh'`: exit 0 on a configurable non-default port.
- `rtk git diff --check`: exit 0 before final report append; the final post-report check is recorded in execution evidence and the handoff.
- No listener remained on ports 3000 or 3017 after validation. A pre-existing `npm start`/`node src/server.js` process from before this rerun was observed without a listener on either validation port and was not terminated because it was not spawned by this run.

### PHASE 3: REFACTORING COMPLETE

The scoped corrective refactoring boots, preserves the endpoint contract, passes the assignment validator and finding-specific closure gate, and leaves only the documented LOW response-shape compatibility risk.
