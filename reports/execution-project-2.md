# Execution Evidence — ecommerce-api-legacy

## Scope and gate

- Target: `ecommerce-api-legacy`
- Requested phases: Phase 1 (project analysis) and Phase 2 (architecture audit), independently against the current source.
- Required audit: `../reports/audit-project-2.md`
- This run stopped before Phase 3. No application source file was edited.
- The only in-repository operational file created during this run was `.codex/napkin.md`; `npm ci` created/updated ignored dependency artifacts only.

## Phase 1: project analysis

### Detected contract

| Item | Evidence/result |
|---|---|
| Runtime | Node.js `v20.20.2` |
| Package manager | npm `10.8.2`; `package-lock.json` uses lockfile version 3 |
| Framework | Express, manifest `^4.18.2`, lockfile resolution `4.22.1` |
| Database | sqlite3, manifest `^5.1.6`, lockfile resolution `5.1.7`; `new sqlite3.Database(':memory:')` |
| Domain | LMS/e-commerce checkout with users, courses, enrollments, payments and audit logs |
| Relevant application source | 3 files: `src/app.js`, `src/AppManager.js`, `src/utils.js` |
| Startup | `npm start` → `node src/app.js` |
| Public routes | 3: `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id` |
| Health route | None found; no `/health` endpoint is defined |
| Test script | None; `npm test -- --runInBand` failed with exit 1 |
| Current architecture | Monolithic/hybrid: `AppManager` owns bootstrap-adjacent database setup, routes, SQL, workflows and reporting; `utils.js` owns config and mutable state |

### Endpoint inventory and baseline responses

| Method/path | Baseline result | Representative shape |
|---|---|---|
| `GET /api/admin/financial-report` | exit 0; HTTP 200 | JSON array of course objects with `course`, `revenue`, and `students` |
| `POST /api/checkout` valid card/course | exit 0; HTTP 200 | `{"msg":"Sucesso","enrollment_id":2}` |
| `POST /api/checkout` denied card | exit 0; HTTP 400 | `Pagamento recusado` |
| `POST /api/checkout` missing required fields | exit 0; HTTP 400 | `Bad Request` |
| `DELETE /api/users/1` | exit 0; HTTP 200 | `Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.` |

The route source also establishes a checkout 404 (`Curso não encontrado`) and several 500 text responses for database/write failures; those branches were not claimed as runtime-smoke passes because they were not invoked in the baseline sequence. No health check was possible because no health route exists.

### Phase 1 summary

`PHASE 1: PROJECT ANALYSIS`

- Stack: Node.js 20.20.2 + Express 4.22.1 + sqlite3 5.1.7.
- Domain: in-memory LMS checkout and financial reporting.
- Architecture: monolithic/hybrid.
- Source-file count: 3 relevant application files.
- Endpoint count: 3 public routes.
- Startup: `npm start`.
- Validation availability: dependencies were installable; no project test script or dedicated target validation script exists. Syntax, boot and representative route smoke checks were available after `npm ci`.

## Phase 2: architecture audit

Audit completed independently before reading the manual analysis. The report contains 10 current-source findings, each with severity, rule, exact lines, evidence, impact and recommendation:

| Severity | Count |
|---|---:|
| CRITICAL | 2 |
| HIGH | 4 |
| MEDIUM | 3 |
| LOW | 1 |
| Total | 10 |

The report requires at least five findings and contains CRITICAL findings `SEC-002` and `SEC-003`.

### Comparison with the manual analysis

The manual analysis was read only after the independent audit was written, using `../README.md:12-40`. Its Project 2 table has 8 findings (`../README.md:33-40`). All 8 were rediscovered at the concept level:

| Manual item | Independent finding(s) | Comparison |
|---|---|---|
| Credentials/payment key hardcoded | `SEC-002` | Rediscovered; current lines also show the raw card and key in the checkout log |
| Card and gateway key in logs | `SEC-002` | Rediscovered and deduplicated with the same secret-handling root cause |
| God Class `AppManager` | `ARCH-001` | Rediscovered |
| Checkout without transaction | `ARCH-003` | Rediscovered; severity raised to HIGH because partial writes and false success are evidenced |
| N+1 financial report | `PERF-001` | Rediscovered |
| Callback pyramid/inconsistent errors | `ARCH-002`, `ERR-001` | Rediscovered; split into route-boundary and error-propagation causes |
| Cryptic variables | `LOW-002` | Rediscovered, with dead `totalRevenue` state also recorded |
| Mutable global state | `ARCH-004` | Rediscovered |

Rediscovery count: **8 of 8 manual Project 2 findings**. Independent additions not listed in that table: `SEC-003` (plaintext/weak password handling) and `DATA-001` (orphaned enrollment/payment data). The manual report's line ranges were treated as comparison metadata only; current findings use the current source lines in the audit.

### Phase 2 summary

`PHASE 2: ARCHITECTURE AUDIT COMPLETE`

- Audit path: `../reports/audit-project-2.md`.
- Finding totals: 2 CRITICAL, 4 HIGH, 3 MEDIUM, 1 LOW; 10 total.
- Manual rediscovery: 8/8 Project 2 table entries.
- Deprecated API check: no application-level deprecated API claim proven. `npm ci` emitted transitive package deprecation warnings, recorded below as a limitation/risk rather than `API-001`.
- Gate: stopped before Phase 3; no refactoring plan was applied and no application source changed.

## Exact commands and outcomes

Commands are listed with the `rtk` prefix required by the repository instructions.

| Command | Exit/result |
|---|---|
| `rtk git status --short` | 0; initially only the newly created `.codex/napkin.md` appeared as untracked |
| `rtk rg --files --hidden -g '!.git/**' \| sort` | 0; source/manifests/docs inventory collected |
| `rtk nl -ba package.json` | 0; startup and dependency manifest inspected |
| `rtk nl -ba src/app.js` | 0; bootstrap inspected |
| `rtk nl -ba src/AppManager.js` | 0; routes, SQL and workflows inspected |
| `rtk nl -ba src/utils.js` | 0; config, password transform and globals inspected |
| `rtk nl -ba api.http` | 0; request examples inspected |
| `rtk rg -n '"(express\|sqlite3)"\|node_modules/(express\|sqlite3)' package-lock.json` | 0; dependency locations identified |
| `rtk sed -n '1,34p' package-lock.json` | 0; lockfile metadata inspected |
| `rtk sed -n '636,658p' package-lock.json` | 0; Express resolution inspected |
| `rtk sed -n '2018,2045p' package-lock.json` | 0; sqlite3 resolution inspected |
| `rtk node --version` | 0; `v20.20.2` |
| `rtk npm --version` | 0; `10.8.2` |
| `rtk ls -ld node_modules` | 2 before installation; `node_modules` did not exist |
| `rtk npm test -- --runInBand` | 1; npm reported `Missing script: "test"` |
| `rtk node --check src/app.js` | 0 |
| `rtk node --check src/AppManager.js` | 0 |
| `rtk node --check src/utils.js` | 0 |
| `rtk npm ci` | 0; 191 packages installed, 13 vulnerabilities reported by npm audit (2 low, 4 moderate, 6 high, 1 critical); deprecation warnings for transitive packages were emitted |
| `rtk npm start` | Spawned successfully and remained available for smoke testing; no clean exit was expected before termination |
| `rtk curl -sS -i http://localhost:3000/api/admin/financial-report` | 0; HTTP 200 and JSON array returned |
| `rtk curl -sS -i -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' --data '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}'` | 0; HTTP 200 and checkout JSON returned |
| `rtk curl -sS -i -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' --data '{"usr":"Joao","eml":"joao@teste.com","pwd":"123","c_id":1,"card":"5111222233334444"}'` | 0; HTTP 400 `Pagamento recusado` |
| `rtk curl -sS -i -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' --data '{"usr":"Missing"}'` | 0; HTTP 400 `Bad Request` |
| `rtk curl -sS -i -X DELETE http://localhost:3000/api/users/1` | 0; HTTP 200 deletion text returned |
| Ctrl-C sent to the `rtk npm start` session | spawned process terminated; session exit 1 reflects intentional interruption |
| `rtk ss -ltnp` | 0; no listener on port 3000 remained after termination |
| `rtk rg -n 'app\\.(post\\|get\\|delete)\|new sqlite3\|CREATE TABLE\|INSERT INTO\|SELECT \|DELETE FROM\|paymentGatewayKey\|dbPass\|badCrypto\|globalCache\|totalRevenue\|forEach\|catch\|try\|res\\.status\|res\\.json\|res\\.send' src package.json` | 0; anti-pattern evidence search completed |
| `rtk rg -n 'health\|/api/' src api.http README.md` | 0; route/health search completed; no health route found |
| `rtk npm ls --depth=0` | 0; `express@4.22.1` and `sqlite3@5.1.7` confirmed |
| `rtk nl -ba README.md` | 0; target README inspected; it contains run instructions but no manual findings table |
| `rtk rg --files ../reports \| sort` | 0; existing report artifacts located |
| `rtk rg -n -i 'manual\|análise\|auditoria\|hardcoded\|secret\|god class\|fat\|transa\|global\|n\\+1\|orphan\|password\|senha\|AppManager\|badCrypto\|financial-report' ../README.md ../reports -g '!audit-project-2.md' -g '!execution-project-2.md'` | 0; manual-analysis location identified without using it to generate findings |
| `rtk nl -ba ../README.md \| sed -n '12,40p'` | 0; manual Project 2 table read after audit completion |

## Limitations and unverified assumptions

- No target-specific validation script or test suite exists; the missing test script is a baseline failure, not a pass.
- The app hardcodes port 3000 and does not consume a configurable port variable; the smoke test used that fixed port.
- The database is in memory, so the baseline did not validate persistence across process restarts.
- The smoke requests were launched concurrently; their HTTP status/body contracts were captured, but cross-request ordering should not be treated as a deterministic business-sequence test.
- `npm ci` succeeded, but npm reported 13 installed-dependency vulnerabilities and several deprecated transitive packages. No `npm audit` remediation was applied in Phases 1/2.
- Whether the production-like literals are active credentials cannot be verified from local source; they remain release blockers by the security baseline.
- No application source, manifest, lockfile, or route contract was intentionally changed. Phase 3 was not started.

## Gate

`Proceed with Phase 3 refactoring? [y/n]`
