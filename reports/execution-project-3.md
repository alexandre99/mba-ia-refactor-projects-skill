# Execution Evidence — task-manager-api

## Scope and controls

- Execution root: `/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/task-manager-api`
- Target: `task-manager-api` only
- Explicit exclusion: `ecommerce-api-legacy` was not analyzed or modified
- Skill: `refactor-arch`, Phases 1 and 2 only
- Phase 3: not executed; the approval gate is preserved at the end of this file
- Application code policy: no application Python module was edited. The only non-report files created were the required per-repository napkin runbook and a deterministic validation helper under `scripts/validation/`; both are non-application support artifacts.

## Preconditions

| Command | Exit | Evidence |
|---|---:|---|
| `pwd` | 0 | `/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/task-manager-api` |
| `rtk sed -n '1,160p' requirements.txt` | 0 | Flask and Flask-SQLAlchemy dependencies detected |
| `rtk sed -n '1,120p' app.py` | 0 | `from flask import Flask`, `Flask()`, blueprints, and `app.route` detected |
| `rtk rg --files` | 0 | Inventory contained only the current target source/configuration files |
| `rtk rg -n "@.*route|methods=" app.py routes` | 0 | 22 endpoint declarations inventoried |

The three required guards were true before analysis: the directory ended in `/task-manager-api`; the stack evidence was Python + Flask; and the target was not `ecommerce-api-legacy`.

## Phase 1 — Project analysis

### `PHASE 1: PROJECT ANALYSIS`

- Runtime: Python 3.12.3 (`rtk bash -lc 'python3 --version'`, exit 0)
- Framework/dependencies: Flask 3.0.0, Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0; SQLAlchemy 2.0.51 in the isolated environment
- Database: SQLite via `sqlite:///tasks.db`
- Domain: users, roles, tasks, categories, login, and reports/productivity metrics
- Application source-file count: 15 Python files
- Public endpoint count: 22
- Startup command from project evidence: `python app.py`
- Test availability: no test modules or pytest configuration found
- Existing validator: `../scripts/validation/validate-task-manager.sh`; it checks only health/root and requires `python`
- Immediate blocker found initially: system `python` command, Flask imports, and pytest were unavailable

### Inspection commands and exit codes

| Command | Exit | Result |
|---|---:|---|
| `rtk bash -lc 'python --version'` | 127 | `python: command not found` |
| `rtk bash -lc 'python -m pip --version'` | 127 | `python: command not found` |
| `rtk bash -lc 'python3 -m pip --version'` | 0 | pip 24.0 available |
| `rtk bash -lc 'python3 -c "import flask, flask_sqlalchemy, flask_cors"'` | 1 | `ModuleNotFoundError: No module named 'flask'` |
| `rtk bash -lc 'python3 -m pytest --version'` | 1 | pytest unavailable |
| `rtk bash -lc 'python3 -m compileall -q .'` | 0 | syntax compilation passed |
| `rtk rg -n "SECRET_KEY|debug=True|CORS\(|sqlite:///|db\.session|\.query\.get|\.query\.all|hashlib\.md5|password|smtplib|@.*route|except:" app.py database.py models routes services utils seed.py` | 0 | security, layering, query, credential, and exception evidence collected |
| `rtk rg -n "^(import|from) " app.py models routes services utils seed.py` | 0 | import/dead-code evidence collected |
| `rtk rg -n "NotificationService|notify_task|send_email" . -g '*.py' -g '!scripts/**'` | 0 | notification service has no application call site |

### Baseline discovery and execution

The pre-existing validator was executed exactly as discovered:

```text
Command: rtk bash ../scripts/validation/validate-task-manager.sh
Exit: 1
Output: python runtime not found
```

An isolated temporary virtual environment was then created outside the repository:

| Command | Exit |
|---|---:|
| `rtk mktemp -d /tmp/task-manager-api-validation.XXXXXX` | 0 |
| `rtk bash -lc 'python3 -m venv /tmp/task-manager-api-validation.rrohN6/venv'` | 0 |
| `rtk bash -lc '/tmp/task-manager-api-validation.rrohN6/venv/bin/python -m pip install -r requirements.txt'` | 0 |
| `rtk bash -lc '/tmp/task-manager-api-validation.rrohN6/venv/bin/python -m compileall -q .'` | 0 |
| `rtk bash -lc 'mkdir -p /tmp/task-manager-api-validation.rrohN6/work; cp -a app.py database.py seed.py models routes services utils /tmp/task-manager-api-validation.rrohN6/work/'` | 0 |
| `rtk bash -lc 'cd /tmp/task-manager-api-validation.rrohN6/work; /tmp/task-manager-api-validation.rrohN6/venv/bin/python seed.py'` | 0 |

The seed command created 3 users, 4 categories, and 10 tasks in the temporary copy. It emitted Python 3.12 `datetime.utcnow()` deprecation warnings but exited successfully.

Because the existing validator did not provide the required isolated database and representative endpoint coverage, `scripts/validation/validate-task-manager-api.sh` was created in the target as a deterministic support artifact. It copies only the application source into a temporary directory, seeds an isolated SQLite database, boots the documented `python app.py` command, exercises all 22 route patterns plus negative/success probes, terminates the process group, and removes temporary state.

The first invocation without an explicit interpreter failed as expected:

```text
Command: rtk bash scripts/validation/validate-task-manager-api.sh
Exit: 1
Output: ModuleNotFoundError: No module named 'flask'
```

The actual baseline invocation passed:

```text
Command: rtk bash -lc 'PYTHON_BIN=/tmp/task-manager-api-validation.rrohN6/venv/bin/python bash scripts/validation/validate-task-manager-api.sh'
Exit: 0
```

### Boot, endpoints, and cleanup evidence

The validator booted the documented command as `/tmp/.../venv/bin/python app.py` on `127.0.0.1:5000`. Two initial readiness polls reported connection refused while the development server started; readiness then passed. All endpoint requests were unauthenticated, which also exposed the current DELETE behavior.

| Probe | Status | Observed response shape |
|---|---:|---|
| `GET /health` | 200 | object: `status`, `timestamp` |
| `GET /` | 200 | object: `message`, `version` |
| `GET /users` | 200 | array; user summary and `task_count` |
| `GET /users/999` | 404 | object: `error` |
| `POST /users` | 201 | object including `password` |
| `GET /users/4` | 200 | object including `password`, `tasks` |
| `PUT /users/4` | 200 | object including `password` |
| `GET /users/4/tasks` | 200 | array |
| `POST /login` valid | 200 | object: `message`, `token`, `user` |
| `POST /login` invalid | 401 | object: `error` |
| `POST /categories` | 201 | object: category fields |
| `GET /categories` | 200 | array; category fields and `task_count` |
| `PUT /categories/5` | 200 | object: category fields |
| `GET /tasks` | 200 | array; task fields, `overdue`, user/category names |
| `GET /tasks/999` | 404 | object: `error` |
| `POST /tasks` | 201 | object: task fields |
| `GET /tasks/11` | 200 | object: task fields and `overdue` |
| `PUT /tasks/11` | 200 | object: task fields |
| `GET /tasks/search?q=Validation` | 200 | array: task fields |
| `GET /tasks/stats` | 200 | object: totals, status counts, `overdue`, `completion_rate` |
| `GET /reports/summary` | 200 | object: overview, status/priority, overdue, activity, productivity |
| `GET /reports/user/1` | 200 | object: `user`, `statistics` |
| `GET /reports/user/999` | 404 | object: `error` |
| `DELETE /tasks/11` | 200 | object: `message` |
| `DELETE /categories/5` | 200 | object: `message` |
| `DELETE /users/4` | 200 | object: `message` |

The validator printed `ENDPOINTS: all baseline probes passed` and `CLEANUP: temporary project, database, log, and process removed`. The outer temporary virtual environment was removed with `rtk bash -lc 'rm -rf /tmp/task-manager-api-validation.rrohN6'`, exit 0. A post-run existence check returned exit 0 for “does not exist”. The final listener check showed no listener on port 5000; the process search found only its own `pgrep` command, not `app.py`.

### Phase 1 evidence conclusion

The baseline is PASSED for the observed contract when run with the isolated Python 3.12 virtual environment. The original repository validator remains inadequate as a standalone command in this environment because it assumes a `python` executable and covers only two endpoints; that failure is retained as evidence and is not reported as a passing validation.

## Phase 2 — Architecture audit

### `PHASE 2: ARCHITECTURE AUDIT COMPLETE`

The audit was generated from direct inspection of the current source after the baseline. The stale Project 3 reports were not used as evidence. Findings were deduplicated by root cause while keeping independently actionable security, transport-coupling, performance, consistency, transaction, and quality risks separate.

| Severity | Count | Rule IDs |
|---|---:|---|
| CRITICAL | 1 | SEC-002 |
| HIGH | 6 | SEC-004, SEC-003, OPS-001, ARCH-001, ARCH-002, ARCH-003 |
| MEDIUM | 3 | PERF-001, QUAL-001, DATA-002 |
| LOW | 1 | QUAL-004 |
| Total | 11 | — |

The report contains exact file/line evidence, impact, recommendation, and executable finding-specific validation for every finding:

1. `SEC-002`: unauthenticated destructive DELETE operations.
2. `SEC-004`: MD5 password verification and password-field serialization.
3. `SEC-003`: committed Flask/SMTP secrets.
4. `OPS-001`: debug, broad CORS, fixed storage/bind/port, and import-time schema mutation.
5. `ARCH-001`: cross-domain god route modules.
6. `ARCH-002`: business validation/workflows in route handlers.
7. `ARCH-003`: direct ORM/session persistence in routes.
8. `PERF-001`: query-in-loop/N+1 behavior.
9. `QUAL-001`: duplicated validation and constants.
10. `DATA-002`: separate seed commits without one atomic boundary.
11. `QUAL-004`: unused imports and ad-hoc exception/operation prints.

After the findings and report were complete, the README comparison was performed with `rtk sed -n '1,260p' README.md` (exit 0). It enumerates no concrete manual findings, so manual findings enumerated and independently rediscovered are both 0. No README finding was copied.

### Report generation and integrity checks

| Command/check | Exit | Result |
|---|---:|---|
| Replace `../reports/audit-project-3.md` | — | stale report removed and replaced with independent audit |
| Replace `../reports/execution-project-3.md` | — | stale report removed and replaced with this evidence |
| `rtk rg -n "Architecture Audit Report|CRITICAL: 1 \| HIGH: 6 \| MEDIUM: 3 \| LOW: 1|Proceed with Phase 3 refactoring" ../reports/audit-project-3.md` | 0 | audit title, totals, and gate present |
| `rtk git diff --check` | 0 | no whitespace errors |
| `rtk bash -lc 'test ! -e /tmp/task-manager-api-validation.rrohN6'` | 0 | outer temporary environment removed |
| `rtk ss -ltnp` | 0 | no target listener remained on port 5000 |

## Files generated/replaced

- `../reports/audit-project-3.md` — replaced incorrect prior Project 3 report
- `../reports/execution-project-3.md` — replaced incorrect prior Project 3 execution report
- `scripts/validation/validate-task-manager-api.sh` — deterministic non-application validation helper created for this target
- `.codex/napkin.md` — per-repository runbook created by the active napkin skill

Application files such as `app.py`, `database.py`, `seed.py`, `models/*.py`, `routes/*.py`, `services/*.py`, and `utils/*.py` were not modified. No other project was modified.

## Phase 3 gate

Phase 3 was not started. No refactoring, final disposition matrix, or finding closure was claimed. The next action requires explicit approval in this same session.

Proceed with Phase 3 refactoring? [y/n]

## Phase 3 — Refactoring execution

Approval received in the same session: `y`. The application was changed only after that approval.

### Implementation milestones

1. Added environment-backed configuration and an application factory (`config.py`, `app.py:13-38`), removed import-time schema creation, added explicit `wsgi.py`, and made production fail closed for missing secrets or accidental `python app.py` startup.
2. Added signed bearer tokens and admin authorization (`auth.py:9-42`), changed destructive endpoints to require admin access, replaced MD5 with Werkzeug password hashing, and removed password material from user serializers.
3. Split category/report route concerns and extracted `controllers/`, `services/`, `repositories/`, `utils/validation.py`, and `repositories/unit_of_work.py`. Routes now parse transport input and delegate; ORM/session operations are outside `routes/` and `controllers/`.
4. Reworked task/report aggregation to use eager/select-in loading, consolidated validation, moved commits/rollback into service transaction helpers, and made `seed.py:13-57` one transactional workflow.
5. Updated the deterministic validator for the new support modules, configurable port, password non-disclosure, anonymous 401, and authorized admin deletion. Added `scripts/validation/validate-findings.py` for security, rollback, seed, and query-count proof.

### Commands and exit codes

| Command | Exit | Result |
|---|---:|---|
| `rtk bash -lc 'python3 -m compileall -q .'` | 0 | compile check passed during implementation |
| `rtk rg -n "\.query|db\.session|db\.or_" routes controllers` | 1/no matches | route/controller persistence coupling removed |
| `rtk rg -n "hashlib\.md5|super-secret-key-123|senha123|taskmanager@gmail.com" . -g '*.py' -g '!scripts/**'` | 1/no matches | old password/secret literals removed |
| isolated app import with `create_app({'TESTING': True})` | 0 | factory imported and registered 22 application routes |
| `APP_ENV=production SECRET_KEY= /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python -c 'from app import app'` | 1 | expected missing-secret fail-closed guard |
| factory import from an empty temporary directory | 0 | no `instance/` database directory created during import |
| initial parallel install attempt | 127 | recorded race: install started before venv creation |
| sequential `/tmp/task-manager-api-phase3.oZMGVh/venv/bin/python -m pip install -r requirements.txt` | 0 | isolated dependencies installed |
| `/tmp/task-manager-api-phase3.oZMGVh/venv/bin/ruff check --select I,F401,F841 ... --fix` | 0 | mechanical import/dead-code cleanup; 18 fixes |
| `/tmp/task-manager-api-phase3.oZMGVh/venv/bin/ruff check app.py auth.py config.py controllers models repositories routes services utils seed.py wsgi.py` | 0 | full Ruff check passed |
| `python3 -m compileall -q .` | 0 | final syntax check passed |
| `APP_ENV=production SECRET_KEY=validation-secret /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python -c 'from wsgi import app; assert app.debug is False'` | 0 | production WSGI import passed |
| `APP_ENV=production SECRET_KEY=validation-secret /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python app.py` | 1 | expected guard prevents development server in production |

An earlier production guard attempt used system `python3` and exited 1 at dependency import (`ModuleNotFoundError: flask`); the authoritative retry used the isolated interpreter above and reached the intended guard.

### Post-change boot and endpoint validation

| Command | Exit | Result |
|---|---:|---|
| `rtk bash -lc 'PYTHON_BIN=/tmp/task-manager-api-phase3.oZMGVh/venv/bin/python bash scripts/validation/validate-task-manager-api.sh'` | 0 | booted `python app.py` on port 5000; all 22 route patterns plus negative/auth probes passed |
| `rtk bash -lc 'PYTHON_BIN=/tmp/task-manager-api-phase3.oZMGVh/venv/bin/python PORT=5053 bash scripts/validation/validate-task-manager-api.sh'` | 0 | configurable-port boot passed with the same endpoint contract |
| `rtk bash -lc 'PYTHONPATH=/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/task-manager-api /tmp/task-manager-api-phase3.oZMGVh/venv/bin/python scripts/validation/validate-findings.py'` | 0 | security/password/rollback/seed/query checks passed: task 1, report 5, category 2 queries |

The post-change validator observed these deliberate security differences from the captured baseline: anonymous DELETE task/category/user returned 401; the signed admin token returned 200; user create/get/login response shapes omitted `password`. All non-security endpoint paths and success statuses remained operational. Both validator runs reported `ENDPOINTS: all baseline probes passed` and `CLEANUP: temporary project, database, log, and process removed`.

### Finding disposition matrix

| Finding | Disposition | Validation evidence | Remaining risk |
|---|---|---|---|
| `SEC-002` | `RESOLVED` | anonymous DELETE 401, row counts unchanged; admin DELETE 200 in `validate-findings.py` | admin-only authorization, no per-resource ownership policy |
| `SEC-004` | `RESOLVED` | response password assertions, generated hash/check, full smoke | legacy MD5 rows need password reset/migration; no legacy verifier remains |
| `SEC-003` | `RESOLVED` | old-literal scan empty; missing production secret exits 1 | rotate credentials exposed by the old revision |
| `OPS-001` | `RESOLVED` | production WSGI import, production app guard, factory no-side-effect probe, ports 5000/5053 | external WSGI process must be supplied in deployment |
| `ARCH-001` | `RESOLVED` | split route modules, controller/service/repository boundaries, full smoke | shared Flask-SQLAlchemy extension remains a deliberate composition choice |
| `ARCH-002` | `RESOLVED` | routes contain transport/delegation only; service and endpoint checks passed | no separate external test suite was introduced |
| `ARCH-003` | `RESOLVED` | ORM/session grep returned no route/controller matches; repository tests/probes passed | repositories still wrap the global extension |
| `PERF-001` | `RESOLVED` | query event counts: task 1, report 5, category 2 | new report dimensions require query-count review |
| `QUAL-001` | `RESOLVED` | centralized validation plus finding-specific checks and Ruff | compatibility helper preserves old helper name |
| `DATA-002` | `RESOLVED` | injected after-flush seed failure preserved pre-seed counts; one commit in seed | schema creation is separate setup before the transaction |
| `QUAL-004` | `RESOLVED` | full Ruff, compileall, import cleanup, no runtime prints in audited modules | logging can be expanded for production observability |

### Cleanup and final closure

The temporary venv, temporary cloned projects, logs, databases, pycache, and empty factory-probe directory were removed with an explicit temporary-path cleanup command. Final checks showed no target process and no listener on ports 5000 or 5053. `rtk git diff --check` exited 0.

## `PHASE 3: REFACTORING COMPLETE`

The application booted, the assignment endpoint validation passed, all finding-specific validations passed, and the final finding-closure gate passed. No intentional security contract change remains undocumented.
