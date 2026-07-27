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
