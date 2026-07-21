# Execution Evidence — ecommerce-api-legacy

## Scope and gate

- Requested scope: only Phases 1 and 2 of `refactor-arch`.
- Application source/configuration was not edited.
- Phase 3 was not executed.
- Final gate: `Proceed with Phase 3 refactoring? [y/n]`

## Phase 1 — project analysis

The analysis was performed from the current source, package metadata, installed dependency tree, validation script, and endpoint probes. The repository's manual Project 2 analysis was not read until after the independent audit report had been completed.

- Runtime: Node.js `v20.20.2`; npm `10.8.2`.
- Framework/dependencies: Express installed `4.22.1`; SQLite3 installed `5.1.7`; declared ranges are Express `^4.18.2` and SQLite3 `^5.1.6`.
- Database: SQLite in-memory (`:memory:`).
- Domain: course LMS/e-commerce checkout, users, enrollments, payments, audit logs, and financial reporting.
- Application source files: 3 (`src/app.js`, `src/AppManager.js`, `src/utils.js`).
- Declared public endpoints: 3.
- Startup: `npm start` → `node src/app.js`; fixed port `3000`.
- Validation availability: `../scripts/validation/validate-ecommerce-legacy.sh` exists, but only probes `/` and explicitly leaves endpoint inventory pending.

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
| `rtk sed -n '1,180p' ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Confirmed the validator's fixed port, `npm ci`, root readiness probe, and pending endpoint inventory. |
| `rtk nl -ba ../scripts/validation/validate-ecommerce-legacy.sh` | 0 | Captured validator lines `1-32` for exact evidence. |
| `rtk nl -ba api.http` | 0 | Captured the three documented route requests at `3-31`. |

## Baseline execution

### Official validation command

| Command | Exit | Result |
|---|---:|---|
| `rtk bash ../scripts/validation/validate-ecommerce-legacy.sh` | 1 | `npm ci` installed 191 packages and audited 192; npm reported 13 vulnerabilities (2 low, 4 moderate, 6 high, 1 critical). `npm start` launched and logged `Frankenstein LMS rodando na porta 3000...`, but the validator's `curl -fsS http://127.0.0.1:3000/` readiness probe never succeeded because `/` is undeclared and returned 404. The script exited with `application did not become ready on port 3000`. |
| `rtk sed -n '1,120p' /tmp/ecommerce-api-legacy-validation.log` | 0 | Confirmed the application startup log; no startup crash was recorded. |
| `rtk ss -ltnp` | 0 | Confirmed no lingering listener on port 3000 after the script's EXIT cleanup. |
| `rtk git status --short` | 0 | Confirmed no application/configuration change after baseline; pre-existing skill-reference modifications remained unchanged. |

Baseline conclusion: the official baseline is **FAILED**, not passed. The application booted in the failed run, but the provided readiness contract is invalid for the current route set and no endpoint behavior was validated by that script.

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
| `rtk sed -n '1,180p' ../README.md` | 0 | Read manual Project 2 analysis at `../README.md:29-41`. |
| `rtk sed -n '1,90p' ../reports/audit-project-1.md` | 0 | Read an existing report only to preserve the repository's comparison/evidence convention; it did not supply Project 2 findings. |

Comparison result: 8 manual findings; 6/8 rediscovered semantically (5 integral, 1 partial); 2 not rediscovered (cryptic variables and mutable global state). The partial match was the manual card/gateway logging item: the independent `SEC-003` finding cites the payment key in the checkout log, while the catalog has no dedicated sensitive-financial-logging rule and no separate card-logging finding was created. Additional independent findings without a direct manual equivalent: `SEC-002`, `SEC-004`, `ARCH-003`, `TEST-001`, and `QUAL-002`.

## Integrity, limitations, and deviations

- No application files were edited. The only requested artifacts are the audit and execution reports under `../reports/`; pre-existing modifications under `.codex/skills/refactor-arch/references/` and the sibling target's skill references were preserved.
- The official validator runs `npm ci`; this regenerated ignored installed dependencies but did not change tracked application/configuration files. Its npm audit warnings are recorded, not converted into a `DEP-001` finding without source/API migration evidence.
- The validator has no configurable port/database and probes `/`, so its failed result cannot establish endpoint correctness. Direct probes used the application's fixed in-memory database and therefore do not prove durable production persistence.
- The direct endpoint probe intentionally did not test arbitrary SQL/DDL because no such endpoint exists in the current source and destructive experiments were out of scope.
- Because the current app has no authentication route/middleware, authorization behavior for future protected administration was not testable; the unauthenticated reachability of the delete route was observed.
- Transient `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` errors occurred during some sandbox read/patch attempts; they caused no application or report-content change. Successful read/write operations were retried and their exit outcomes are recorded above.

## Final state

- `PHASE 1: PROJECT ANALYSIS` completed.
- `PHASE 2: ARCHITECTURE AUDIT COMPLETE` completed.
- Phase 3 not run; awaiting explicit user response at the required gate.

Proceed with Phase 3 refactoring? [y/n]
