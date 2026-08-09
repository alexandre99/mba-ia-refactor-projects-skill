# Execution Evidence — ecommerce-api-legacy

> Historical evidence: the prior Phase 1–3 execution remains preserved above. The rerun below follows the updated `refactor-arch` protocol and records only this project's current re-evaluation.

## Scope and gate

- Requested scope: only Phases 1 and 2 of `refactor-arch`.
- Before approval, application source/configuration was not edited.
- Approval response: y.
- Phase 3 then changed the application architecture and deliberately protected user deletion with an admin token.
- Approval gate response: y; Phase 3 proceeded and completed.

## Phase 1 — project analysis

The analysis was performed from the current source, package metadata, installed dependency tree, validation script, and endpoint probes. The repository's manual Project 2 analysis was not read until after the independent audit report had been completed.

- Runtime: Node.js `v20.20.2`; npm `10.8.2`.
- Framework/dependencies: Express installed `4.22.1`; SQLite3 installed `5.1.7`; declared ranges are Express `^4.18.2` and SQLite3 `^5.1.6`.
- Database: SQLite in-memory (`:memory:`).
- Domain: course LMS/e-commerce checkout, users, enrollments, payments, audit logs, and financial reporting.
- Application source files: 3 (`src/app.js`, `src/AppManager.js`, `src/utils.js`).
- Declared public endpoints: 3.
- Startup: `npm start` → `node src/app.js`; fixed port `3000`.
- Validation availability: `../scripts/validation/validate-ecommerce-legacy.sh` is now a complete deterministic safety net: it installs/verifies dependencies, starts the app, uses existing `GET /api/admin/financial-report` readiness, validates the legacy contract matrix, and cleans up the process.

### Phase 1 inspected commands

| Command | Exit | Result |
|---|---:|---|
| `rtk pwd` | 0 | Confirmed target root `/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/ecommerce-api-legacy`. |
| `rtk git status --short` | 0 | Only pre-existing modifications under `.codex/skills/.../references/` were present; no application files were modified by this run. |
| `rtk rg --files -g '!node_modules' -g '!.git' -g '!coverage' -g '!dist' -g '!build' \| sort` | 0 | Listed `package.json`, `package-lock.json`, `api.http`, and the three source files. |
| `rtk node --version` | 0 | `v20.20.2`. |
| `rtk npm --version` | 0 | `10.8.2`. |
| `rtk npm ls --depth=0` | 0 | `express@4.22.1`, `sqlite3@5.1.7`. |
| `rtk rg --files .. -g '!node_modules' -g '!.git' -g '!coverage' -g '!dist' -g '!build' \| sort` | 0 | Located the official validation script and report destination. |
| `rtk rg -n "validation\|baseline\|audit\|manual\|Projeto 2\|ecommerce-api-legacy" .. -g '!node_modules' -g '!.git' -g '!coverage' -g '!dist' -g '!build'` | 0 | Located repository contract, manual analysis, and validation references. This search was used for discovery, not for generating findings. |
| `rtk nl -ba src/app.js` | 0 | Captured exact bootstrap/startup lines `1-14`. |
| `rtk nl -ba src/AppManager.js` | 0 | Captured exact route, SQL, workflow, and class lines `1-141`. |
| `rtk nl -ba src/utils.js` | 0 | Captured exact config/cache/pseudo-crypto lines `1-25`. |
| `rtk nl -ba package.json` | 0 | Captured startup and dependency declarations at `1-13`. |
| `rtk sed -n '1,180p' ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Confirmed the corrected validator's dependency setup, existing-endpoint readiness, contract probes, and cleanup. |
| `rtk nl -ba ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Captured the corrected validator lines `1-165` for exact evidence. |
| `rtk nl -ba api.http` | 0 | Captured the three documented route requests at `3-31`. |

## Baseline execution

### Historical result before safety-net correction

| Command | Exit | Result |
|---|---:|---|
| `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` | 1 | The original validator installed 191 packages and audited 192; npm reported 13 vulnerabilities (2 low, 4 moderate, 6 high, 1 critical). npm start launched and logged Frankenstein LMS rodando na porta 3000..., but the validator probed undeclared GET / and exited with application did not become ready on port 3000. |

This historical failure is retained as the reason for the safety-net correction. It is not the final baseline status.

### Corrected safety-net baseline

The validator was updated outside ecommerce-api-legacy/src and then executed against the unchanged legacy application.

| Command or internal check | Exit | Result |
|---|---:|---|
| `rtk bash -n ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Shell syntax passed. |
| `npm ci` (inside validator) | 0 | Installed 191 packages and audited 192; npm reported 13 vulnerabilities (2 low, 4 moderate, 6 high, 1 critical), recorded without applying dependency or application changes. |
| `npm ls --depth=0` (inside validator) | 0 | Verified express@4.22.1 and sqlite3@5.1.7. |
| `node -e 'require("express"); require("sqlite3");'` (inside validator) | 0 | Runtime dependency loading passed. |
| `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` (first complete corrected run) | 0 | Booted the app, passed all contract probes, and ran cleanup. |
| `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` (final run after retry-output correction) | 0 | Booted the app, passed all contract probes, and ran cleanup. This is the authoritative baseline run. |

The first readiness curl can return transient connection exit 7 while the background server is still starting; the validator retries it. The final readiness request returned 200 and its JSON parser accepted an array. A readiness timeout, JSON mismatch, endpoint mismatch, or later curl failure exits non-zero.

#### Final endpoint contract matrix

| Probe executed by validator | Expected/observed result | Probe result |
|---|---|---|
| GET /api/admin/financial-report readiness | 200, JSON array | passed |
| POST /api/checkout with {} | 400, Bad Request | passed |
| POST /api/checkout with c_id=999 | 404, Curso não encontrado | passed |
| POST /api/checkout with card prefix 5 | 400, Pagamento recusado | passed |
| POST /api/checkout with course 2 and card prefix 4 | 200, JSON containing msg and integer enrollment_id | passed |
| GET /api/admin/financial-report after approved checkout | 200, JSON array | passed |
| DELETE /api/users/1 | 200, Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco. | passed |

### Cleanup and integrity checks

| Command | Exit | Result |
|---|---:|---|
| `rtk ss -ltnp` | 0 | No listener remained on port 3000 after validator cleanup. |
| `rtk ps -ef \| rtk rg 'ecommerce-api-legacy\|src/app.js\|npm start' \|\| true` | 0 | No validation app process remained. |
| `rtk git diff --check` | 0 | Final whitespace check passed. The first post-write check returned 2 for an extra blank line at EOF in this report; that line was removed before this final exit 0. |
| `rtk git status --short --untracked-files=all` | 0 | The requested validation script and the two Project 2 reports are modified by this task; no application source is modified. |
| `rtk git diff -- src` | 0 | Empty; no file under ecommerce-api-legacy/src changed. |

**Final baseline status: PASSED.** The complete corrected validator passed against the current legacy application, including dependency installation/verification, startup, readiness, every required endpoint contract, and process cleanup.

### Direct legacy startup and endpoint probes

To capture the actual pre-refactoring contract without editing the validator or application, `rtk npm start` was run in a temporary interactive process on its existing port. It was stopped with Ctrl-C after the probes.

| Probe command/result | Exit | Observed response |
|---|---:|---|
| `rtk curl -sS -i http://127.0.0.1:3000/` | 0 | `404 Not Found`, HTML Express error body `Cannot GET /`. |
| `rtk curl -sS -i -X POST http://127.0.0.1:3000/api/checkout -H 'Content-Type: application/json' -d '{}'` | 0 | `400 Bad Request`, text `Bad Request`. |
| `rtk curl -sS -i -X POST http://127.0.0.1:3000/api/checkout -H 'Content-Type: application/json' -d '{"usr":"Baseline Missing Course","eml":"missing-course@example.com","pwd":"pass","c_id":999,"card":"4111222233334444"}'` | 0 | `404 Not Found`, text `Curso não encontrado`. |
| `rtk curl -sS -i -X POST http://127.0.0.1:3000/api/checkout -H 'Content-Type: application/json' -d '{"usr":"Baseline Denied","eml":"denied@example.com","pwd":"pass","c_id":1,"card":"5111222233334444"}'` | 0 | `400 Bad Request`, text `Pagamento recusado`. |
| `rtk curl -sS -i -X POST http://127.0.0.1:3000/api/checkout -H 'Content-Type: application/json' -d '{"usr":"Baseline Success","eml":"success@example.com","pwd":"pass","c_id":2,"card":"4111222233334444"}'` | 0 | `200 OK`, JSON `{"msg":"Sucesso","enrollment_id":2}`. |
| `rtk curl -sS -i http://127.0.0.1:3000/api/admin/financial-report` | 0 | `200 OK`, JSON array with course, revenue, and students/paid fields. |
| `rtk curl -sS -i -X DELETE http://127.0.0.1:3000/api/users/1` | 0 | `200 OK`, text `Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.` |
| `rtk write_stdin(session=12867, chars=Ctrl-C)` | 1 | Interactive server stopped by SIGINT; exit 1 is expected for this manual termination. |

The direct probes exercised the three declared paths plus the validator's undeclared root path, with disposable in-memory data. No arbitrary SQL/DDL or destructive broad operation beyond the documented single-user delete was submitted.

## Phase 2 — architecture audit

Audit report: `../reports/audit-project-2.md`

- Findings: 10 total.
- Severity totals: CRITICAL 2, HIGH 4, MEDIUM 2, LOW 2.
- Highest risks: `SEC-002`, `SEC-003`, `SEC-004`, `ARCH-001`, `ARCH-002`, `ARCH-003`.
- Deprecated API detection: no `DEP-001` finding; local dependency versions and source inspection did not provide authoritative evidence of a deprecated API call.
- The report includes exact file/line references, impact, recommendation, and validation for every finding.

## Manual-analysis comparison (performed after independent audit)

Only after the independent report body was complete, the manual section was inspected with:

| Command | Exit | Result |
|---|---:|---|
| `rtk sed -n '1,180p' ../README.md` | 0 | Read manual Project 2 analysis at `../README.md:47-60`. |
| `rtk sed -n '1,90p' ../reports/audit-project-1.md` | 0 | Read an existing report only to preserve the repository's comparison/evidence convention; it did not supply Project 2 findings. |

Comparison result: 8 manual findings; 6/8 rediscovered semantically (5 integral, 1 partial); 2 not rediscovered (cryptic variables and mutable global state). The partial match was the manual card/gateway logging item: the independent `SEC-003` finding cites the payment key in the checkout log, while the catalog has no dedicated sensitive-financial-logging rule and no separate card-logging finding was created. Additional independent findings without a direct manual equivalent: `SEC-002`, `SEC-004`, `ARCH-003`, and `QUAL-002`. `TEST-001` was retained as a historical pre-gate finding and resolved in the validation area before Phase 3.

## Integrity, limitations, and deviations

- Phase 3 intentionally changed application files under `ecommerce-api-legacy/src`; no unrelated target project was changed. The validation script and both Project 2 reports were also updated as requested; pre-existing skill-reference modifications were preserved.
- The corrected validator runs `npm ci`, verifies the dependency tree and module loading, starts the fixed-port app with a validation admin token, exercises the contract matrix including unauthorized/authorized deletion, and cleans up. Its npm audit warnings remain recorded, not converted into a DEP-001 finding without source/API migration evidence.
- The validator still uses the application's fixed port and in-memory database, so it proves current boot/HTTP behavior but not durable production persistence. It no longer depends on undeclared `GET /`; the readiness route is existing `GET /api/admin/financial-report`.
- The direct endpoint probe intentionally did not test arbitrary SQL/DDL because no such endpoint exists in the current source and destructive experiments were out of scope.
- Before Phase 3, the app had no authentication route or middleware; after refactoring, token middleware protects deletion while the report remains intentionally public for contract compatibility.
- Transient `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` errors occurred during some sandbox read/patch attempts; they caused no application or report-content change. Successful read/write operations were retried and their exit outcomes are recorded above.

## Phase 3 — Refactoring

### Approval and transformation

- Explicit approval: y.
- Composition root/server split: src/app.js now builds the app and dependencies; src/server.js owns listen and SIGINT/SIGTERM shutdown.
- MVC boundaries: src/routes.js and controllers handle HTTP mapping; services own checkout/report workflows; repositories own SQLite queries; infrastructure owns the database adapter and seed initialization.
- Security/configuration: src/config.js reads environment-backed settings; committed credential literals and payment-key logging were removed; new passwords use scrypt hashing; DELETE /api/users/:id now requires X-Admin-Token.
- Reporting: the callback/query-in-loop implementation was replaced with one repository join and a service mapper while retaining the financial-report array shape.

### Post-refactor validation commands and exit codes

| Command or check | Exit | Result |
|---|---:|---|
| node syntax checks for all 20 src JavaScript files | 0 | All files parsed successfully. |
| rtk bash -n ../scripts/validation/validate-ecommerce-legacy.sh | 0 | Validation script syntax passed. |
| npm ci, npm ls --depth=0, and module loading inside validator | 0 | Dependencies installed and verified: express 4.22.1, sqlite3 5.1.7. |
| rtk bash ../scripts/validation/validate-ecommerce-legacy.sh | 0 | Full post-refactor boot, readiness, endpoint matrix, authorization checks, and cleanup passed. |
| rtk ss -ltnp after validation | 0 | No listener remained on port 3000. |
| process search for npm start/src/server.js after validation | 0 | No validation process remained. |
| rtk git diff --check | 0 | No whitespace errors. |
| rtk git status --short --untracked-files=all | 0 | Only the approved app, validator, and Project 2 report changes are present. |

### Post-refactor contract matrix

| Endpoint/probe | Result |
|---|---|
| POST /api/checkout with {} | 400 Bad Request |
| POST /api/checkout with nonexistent course | 404 Curso não encontrado |
| POST /api/checkout with denied card | 400 Pagamento recusado |
| POST /api/checkout approved | 200 JSON containing msg and enrollment_id |
| GET /api/admin/financial-report | 200 JSON array |
| DELETE /api/users/1 without X-Admin-Token | 401 Unauthorized |
| DELETE /api/users/1 with validation token | 200 legacy deletion text |

### Findings disposition

Resolved: SEC-002, SEC-003, SEC-004, ARCH-001, ARCH-002, ARCH-003, PERF-001, TEST-001, and QUAL-002.

Remaining: QUAL-005 remains intentionally for legacy response-shape divergence; the financial report is still unauthenticated; checkout writes are sequential without an explicit transaction; storage remains in-memory by default; and no unit-test script was added beyond the executable validator.

### Intentional contract change

User deletion now fails closed with 401 unless X-Admin-Token matches the environment-provided ADMIN_TOKEN. The authorized route preserves the former 200 status and response text. The validator proves both paths, and the audit records this as the deliberate security change.

## Final state

- PHASE 1: PROJECT ANALYSIS completed.
- PHASE 2: ARCHITECTURE AUDIT COMPLETE completed.
- Phase 3 refactoring completed after explicit approval y.
- Post-refactor validator passed with exit 0.
- No validation process or port-3000 listener remained.
- Deliberate contract change: user deletion requires X-Admin-Token; authorized behavior remains 200 with the legacy text response.
- Remaining risks and resolved findings are listed in the Phase 3 section above.

## Updated protocol rerun — 2026-07-26

### Scope and gate

- Target: only `ecommerce-api-legacy`; no other application target is in scope.
- Historical audit and execution evidence were retained in this file; current findings were generated from current source lines before corrections.
- User authorization: the current request explicitly authorizes only necessary corrections for findings newly identified or still unresolved by the updated skill.

### Phase 1 evidence

| Command | Exit | Result |
|---|---:|---|
| `rtk node --version` | 0 | Node.js `v20.20.2` |
| `rtk npm --version` | 0 | npm `10.8.2` |
| `rtk npm ls --depth=0` | 0 | Express `4.22.1`, SQLite3 `5.1.7` |
| `rtk rg --files -g '!node_modules' -g '!*.db' -g '!*.sqlite'` | 0 | Current source/configuration inventory completed; 20 `src/` JavaScript files |
| `rtk nl -ba` over current `src/` files and validator | 0 | Exact current line evidence captured for stack, endpoints, boundaries, writes, cache, and validation |
| `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Baseline boot, endpoint contract, auth behavior, and cleanup passed |
| `rtk git diff --check` | 0 | No whitespace errors before application corrections |

### Baseline endpoint results before corrections

| Probe | Result |
|---|---|
| `POST /api/checkout` with `{}` | `400`, `Bad Request` |
| `POST /api/checkout` with missing course | `404`, `Curso não encontrado` |
| `POST /api/checkout` with denied card | `400`, `Pagamento recusado` |
| Approved `POST /api/checkout` | `200`, JSON `{msg,enrollment_id}` |
| `GET /api/admin/financial-report` | `200`, JSON array |
| Unauthorized `DELETE /api/users/1` | `401`, `Unauthorized` |
| Authorized `DELETE /api/users/1` | `200`, historical deletion text |

### Current Phase 2 result before corrections

- Current findings: 5.
- Severity totals: HIGH 1, MEDIUM 2, LOW 2, CRITICAL 0.
- Findings: `DATA-002`, `OPS-001`, `TEST-002`, `QUAL-002`, `QUAL-005`.
- Historical findings independently rechecked: `SEC-002`, `SEC-003`, `SEC-004`, `ARCH-001`, `ARCH-002`, `ARCH-003`, `PERF-001`, and `TEST-001` are no longer observed in current reachable code; `QUAL-005` remains; `QUAL-002` is partially resolved.
- `DATA-003` was assessed and not raised because the current cache update follows the final current database write; the correction still places it after the new aggregate commit.

### Phase 2 inspected commands

| Command | Exit | Result |
|---|---:|---|
| `rtk rg -n "router\\.(get|post|put|patch|delete)|app\\.(get|post|put|patch|delete)|listen\\(|process\\.env|cache|run\\(|get\\(|all\\(" src package.json ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Enumerated route, startup, configuration, persistence, and effect sites |
| `rtk git rev-parse --show-toplevel` | 0 | Confirmed repository root and report locations |
| `rtk git ls-files ../reports/audit-project-2.md ../reports/execution-project-2.md ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Confirmed project-2 report and validator artifacts are tracked |

The updated audit was written to `../reports/audit-project-2.md` after this independent inspection, before application corrections. Manual-analysis comparison is recorded after consulting the repository manual section, below.

### Manual-analysis comparison after current report

| Command | Exit | Result |
|---|---:|---|
| `rtk sed -n '1,180p' ../README.md` | 0 | Read the manual Project 2 findings only after the updated independent report was complete. |

Result: 1 of 8 manual findings was rediscovered in the current source (`DATA-002`, checkout without a transaction). Seven stale pre-refactor findings are no longer observed after the prior Phase 3. The current audit's `OPS-001`, `TEST-002`, `QUAL-002`, and `QUAL-005` were independently derived and were not copied from the manual table.

## Updated protocol Phase 3 closure — 2026-07-26

### Files changed in this corrective rerun

- `ecommerce-api-legacy/src/app.js`
- `ecommerce-api-legacy/src/config.js`
- `ecommerce-api-legacy/src/constants.js`
- `ecommerce-api-legacy/src/infrastructure/database.js`
- `ecommerce-api-legacy/src/services/checkoutService.js`
- `scripts/validation/validate-ecommerce-legacy.sh`
- `reports/audit-project-2.md`
- `reports/execution-project-2.md`
- `.codex/napkin.md` (runbook directive only)

No file under `code-smells-project/` or `task-manager-api/` was changed.

### Transformation evidence

1. `DATA-002`: `SqliteDatabase.transaction` now owns rollback, `CheckoutService` passes all related writes through that callback, and cache mutation occurs after successful commit.
2. `OPS-001`: production configuration rejects missing or in-memory database paths; the documented non-production default remains disposable SQLite.
3. `TEST-002`: the required validator now runs injected failure and success assertions against database row counts/cache state and checks generic unexpected-error mapping.
4. `QUAL-002`: approved-card and cache-key policies moved to named constants; endpoint behavior is unchanged.
5. `QUAL-005`: no response envelope was changed; the legacy divergence remains visible as a LOW partial disposition.

### Post-correction commands and outcomes

| Command | Exit | Outcome |
|---|---:|---|
| Node syntax checks over all `src/*.js` and nested JavaScript files | 0 | All current application files parsed. |
| `rtk bash -n ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Validator syntax passed. |
| `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Dependency install/verification, production storage guard, default-port boot, endpoint contracts, auth behavior, rollback/commit/cache/error probes, and cleanup passed. |
| `rtk bash -lc 'PORT=3017 bash ../scripts/validation/validate-ecommerce-legacy.sh'` | 0 | Same complete validation passed on a configurable non-default port. |
| `rtk rg -n "admin_master|senha_super|pk_live|badCrypto|class AppManager|startsWith\\('4'\\)" src` | 1 | No matches; exit 1 is the expected no-match result. |
| `rtk rg -n "BEGIN TRANSACTION|COMMIT|ROLLBACK|transaction|CHECKOUT_POLICY" src` | 0 | Final transaction and policy boundaries present. |
| `rtk git diff --check` | 0 | No whitespace errors before final report append; the final post-report check is recorded in the handoff. |

### Final endpoint comparison

| Endpoint/probe | Before | After | Contract result |
|---|---|---|---|
| Missing checkout payload | `400 Bad Request` | `400 Bad Request` | preserved |
| Missing course | `404 Curso não encontrado` | `404 Curso não encontrado` | preserved |
| Denied payment | `400 Pagamento recusado` | `400 Pagamento recusado` | preserved |
| Approved checkout | `200` JSON `{msg,enrollment_id}` | `200` JSON `{msg,enrollment_id}` | preserved |
| Financial report | `200` JSON array | `200` JSON array | preserved |
| Unauthorized deletion | `401 Unauthorized` | `401 Unauthorized` | preserved from prior security correction |
| Authorized deletion | `200` legacy text | `200` legacy text | preserved |

### Final finding-disposition matrix

| Finding | Disposition | Validation result | Remaining risk |
|---|---|---|---|
| `DATA-002` | `RESOLVED` | Injected failure rolled back users/enrollments/payments/audit and left cache empty; success committed rows/cache; validator exit 0. | None observed in this use case. |
| `OPS-001` | `RESOLVED` | Production guard rejected empty and `:memory:` paths; normal/default and `PORT=3017` validator runs exited 0. | Durable path permissions are deployment-owned. |
| `TEST-002` | `RESOLVED` | Finding-specific validator probe executed rollback, post-commit cache, generic error, and magic-value assertions; exit 0. | No process-crash simulation. |
| `QUAL-002` | `RESOLVED` | Static service-literal assertions and approved/denied endpoint probes passed; exit 0. | None for audited literals. |
| `QUAL-005` | `PARTIALLY_RESOLVED` | All legacy statuses/body shapes passed; response media/body divergence intentionally remains. | Compatibility requires multiple response conventions. |

The final matrix contains every current Phase 2 finding exactly once. No CRITICAL or HIGH finding remains partial or unaddressed. No intentional contract change was introduced in this rerun; the prior `DELETE` token requirement remains documented historical behavior.

### Cleanup and remaining risks

- The validator's own spawned process and temporary directory were cleaned on both successful runs; ports 3000 and 3017 had no listener afterward.
- A pre-existing `npm start`/`node src/server.js` process was observed with start time before this rerun. It had no listener on either validation port and was left untouched because it was not spawned by this run.
- `npm ci` reports 13 dependency audit warnings (2 low, 4 moderate, 6 high, 1 critical); no `DEP-001` finding was raised because repository evidence does not identify a deprecated application API or authoritative replacement use.
- The public financial report and in-memory development default remain documented scope/compatibility risks; the production default now fails closed.

### Final state

- `PHASE 1: PROJECT ANALYSIS`: completed for current source.
- `PHASE 2: ARCHITECTURE AUDIT COMPLETE`: completed with 5 current findings and 1/8 manual rediscovery.
- `PHASE 3: REFACTORING COMPLETE`: completed for scoped corrections; validator and finding-closure gate passed.
