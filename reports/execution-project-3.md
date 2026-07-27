# Execution Evidence — Project 3 (`ecommerce-api-legacy`)

## Scope and gate

- Target: `/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/ecommerce-api-legacy` only.
- Report paths: `../reports/audit-project-3.md` and `../reports/execution-project-3.md`.
- Scope: independent Phases 1 and 2 only.
- No application source, configuration, package manifest, or other project was modified.
- Phase 3 was not started; execution stops at the approval gate.

## Phase 1 — project analysis

- Runtime: Node.js `v20.20.2`; npm `10.8.2`.
- Installed dependencies: Express `4.22.1`; SQLite3 `5.1.7`.
- Database: SQLite; `:memory:` default outside production.
- Domain: LMS checkout/enrollment, users, courses, payments, audit logs, financial reporting, and admin deletion.
- Source files: 20 under `src/`.
- Public routes: 3.
- Startup: `npm start` → `node src/server.js`.
- Validation: no `scripts/validation/` directory or test files; `npm test` exited `1` with `Missing script: "test"`.

### Inspected commands

| Command | Exit | Result |
|---|---:|---|
| `rtk pwd` | 0 | Confirmed target root. |
| `rtk git status --short` | 0 | Confirmed initial report-only changes from the prior mistaken numbering run. |
| `rtk rg --files -g '!node_modules' -g '!.git' -g '!reports' \| sort` | 0 | Inventoried package metadata, API examples, and source files. |
| `rtk node --version` | 0 | `v20.20.2`. |
| `rtk npm --version` | 0 | `10.8.2`. |
| `rtk npm ls --depth=0` | 0 | Express `4.22.1`, SQLite3 `5.1.7`. |
| `rtk npm test` | 1 | No test script. |
| `rtk rg --files src \| wc -l` | 0 | `20`. |
| `rtk nl -ba package.json` | 0 | Captured startup/dependency lines `1-13`. |
| `rtk nl -ba api.http` | 0 | Captured documented routes/payloads `1-31`. |
| `rtk nl -ba` on each current `src/` file | 0 | Captured exact route, workflow, persistence, security, and bootstrap evidence. |

### Baseline probes

Started with `rtk env PORT=4317 DATABASE_PATH=:memory: ADMIN_TOKEN=baseline-admin-token npm start`.

| Probe | Result |
|---|---|
| `GET /api/admin/financial-report` without token | `200`, financial JSON array; authorization defect. |
| Same report with valid token | `200`, same JSON shape. |
| Approved checkout | `200`, `{"msg":"Sucesso","enrollment_id":2}`. |
| Denied card | `400`, `Pagamento recusado`. |
| Missing checkout fields | `400`, `Bad Request`. |
| Unknown course | `404`, `Curso não encontrado`. |
| Unauthorized deletion | `401`, `Unauthorized`. |
| Authorized deletion | `200`, legacy dirty-state text. |
| Malformed JSON | `400` HTML with parser stack/path details. |

The spawned process was stopped and no listener remained on port `4317`.

## Phase 2 — architecture audit

- Audit report: `../reports/audit-project-3.md`.
- Findings: 7 total.
- Severity totals: CRITICAL 1, HIGH 2, MEDIUM 3, LOW 1.
- Findings: `SEC-002`, `DATA-002`, `OPS-001`, `ERR-001`, `TEST-001`, `TEST-002`, `QUAL-005`.
- The repository's manual table was inspected only after the independent report was complete using `rtk sed -n '1,220p' ../README.md`; 0 of its 8 historical findings were copied or rediscovered in this current source.

### Finding-specific evidence

- Persistent deletion probe against `/tmp/tmp.ly78LEBD5o/audit.sqlite`: after authorized deletion of user `1`, SQLite counts were `users=0`, `enrollments=1`, `payments=1`, `audit_logs=0`.
- Persistent restart probe: a second boot on the same database exited `1` with `SQLITE_ERROR: table users already exists` at `src/infrastructure/initializeDatabase.js:10`.
- Malformed JSON probe exposed `SyntaxError` and absolute repository paths in the response.
- Temporary database was removed with `rtk bash -lc 'rm -f /tmp/tmp.ly78LEBD5o/audit.sqlite && rmdir /tmp/tmp.ly78LEBD5o'`.

### Evidence integrity checks

| Command | Exit | Result |
|---|---:|---|
| `rtk git diff -- src` | 0 | Empty; application source unchanged. |
| `rtk git diff --check` | 0 | No whitespace errors. |
| `rtk git status --short` | 0 | Only report artifacts are in scope for this correction. |
| `rtk ss -ltnp` | 0 | No validation listener remained on ports `4317`/`4318`. |

## Approval gate

`PHASE 1: PROJECT ANALYSIS` completed.

`PHASE 2: ARCHITECTURE AUDIT COMPLETE` completed.

Proceed with Phase 3 refactoring? [y/n]

Phase 3 was not executed. The disposition matrix remains intentionally incomplete until explicit approval and a later Phase 3 run.
