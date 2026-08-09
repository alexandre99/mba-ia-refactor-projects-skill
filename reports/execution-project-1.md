# Execution Evidence — code-smells-project

## Context

- Date: 2026-07-21
- Timezone: America/Sao_Paulo (-03)
- New baseline timestamp: 2026-07-21T13:52:29-03:00
- Scope: complete execution of Phases 1, 2 and 3, including the pre-refactoring baseline and the post-refactoring execution and validation.
- Gate: explicit approval response `y`; the baseline was completed before application changes, and Phase 3 refactoring was performed after that approval.
- Post-refactoring status: completed and validated; application and validation files were modified in Phase 3 as listed below.
- Direct-check working directory: /home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project
- Required skill: .codex/skills/refactor-arch/SKILL.md; its six required references were read in full.
- At the baseline checkpoint, .codex/napkin.md was absent and was not created, per the explicit task constraint.
- Before the gate, no application source, dependency, configuration, skill, test, audit report or napkin file had been changed. Phase 3 subsequently changed the application and validation files listed below; the audit report was preserved without changing its findings.

## Baseline status: PASSED — legacy behavior and defects separately recorded

The prepared virtual environment is usable. All four relevant Python files passed read-only syntax compilation. The legacy startup command booted successfully, reached readiness within the deterministic limit, and all 19 unique original endpoint paths were exercised against a disposable SQLite database. The official smoke validation also passed in an isolated copy.

This is a successful behavioral baseline, not a security or architecture approval. Known legacy defects and safety-limited operations are classified below.

## Runtime and dependency checks

All commands below were run from the direct-check directory and used the virtual environment explicitly:

| Exact command | Exit | Result |
| --- | ---: | --- |
| .venv/bin/python --version | 0 | Python 3.12.3 |
| .venv/bin/python -m pip --version | 0 | pip 26.1.2 from .venv/lib/python3.12/site-packages for Python 3.12 |
| .venv/bin/python -c "import flask; print(flask.__version__)" | 0 | Flask 3.1.1; Flask emitted its deprecation warning for __version__, but the check passed |

requirements.txt:1-2 declares flask==3.1.1 and flask-cors==5.0.1. No dependency was installed or changed.

## Startup command and inventory evidence

At the pre-refactoring baseline, the correct legacy command is documented in the current README's `Como Executar` section (`README.md:224-231`) as `python app.py`. app.py:80-88 initializes the database and calls app.run(host="0.0.0.0", port=5000, debug=True). Routes are declared in app.py:11-30, app.py:32-45, app.py:47-78; handlers are in controllers.py:5-292.

At the pre-refactoring baseline, the validation script at ../scripts/validation/validate-code-smells.sh:1-35 used bare python, fixed port 5000, relative loja.db, and probed only /health, / and /produtos. To preserve the original tree, it was run from a temporary copy of the same source/script with project .venv/bin first in PATH; no activation or installation was used. The script was made configurable and isolated during Phase 3, as recorded below.

### Exact commands and outcomes

| Exact command or action | Exit | Result |
| --- | ---: | --- |
| rg --files -g '*.py' -g '!.venv/**' \| sort | 0 | app.py, controllers.py, database.py, models.py |
| .venv/bin/python -c "from pathlib import Path; files=sorted(Path('.').glob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('compiled', len(files), 'files')" | 0 | compiled 4 files; no bytecode written |
| ss -ltnp \| rg ':5000\b' \| true (before boot) | 0 | No listener |
| mktemp -d /tmp/code-smells-baseline.XXXXXX | 0 | /tmp/code-smells-baseline.slHbmA |
| env PYTHONUNBUFFERED=1 PYTHONPATH=/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project /home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project/.venv/bin/python /home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project/app.py | 0 on controlled Ctrl-C | Booted actual entrypoint in temporary cwd; debug/reloader active; listened on 0.0.0.0:5000 |
| for i in $(seq 1 30); do if curl -fsS http://127.0.0.1:5000/health >/dev/null; then echo "ready attempt $i"; exit 0; fi; sleep 0.2; done; echo "readiness timeout after 6s" >&2; exit 1 | 0 | ready attempt 1; maximum 6 seconds |
| BASE_URL=http://127.0.0.1:5000 /home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project/.venv/bin/python - <<'PY' ... PY | 0 | Inline urllib.request probes; expected statuses matched |
| Interactive stop: Ctrl-C | 0 | Server terminated |
| ss -ltnp \| rg ':5000\b' \| true (after boot) | 0 | No listener |
| rm -rf /tmp/code-smells-baseline.slHbmA | 0 | Temporary direct-run directory/database removed |

The inline probe used JSON requests, a 3-second per-request timeout, and recorded method, path, payload, status, expected status, response shape, classification and side effects.

The official validation was run on an identical temporary copy with these commands:

    mktemp -d /tmp/code-smells-script-baseline.XXXXXX
    mkdir -p /tmp/code-smells-script-baseline.2gqYQq/scripts/validation /tmp/code-smells-script-baseline.2gqYQq/code-smells-project && cp app.py controllers.py database.py models.py requirements.txt /tmp/code-smells-script-baseline.2gqYQq/code-smells-project/ && cp ../scripts/validation/validate-code-smells.sh /tmp/code-smells-script-baseline.2gqYQq/scripts/validation/
    env PATH="/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project/.venv/bin:$PATH" bash /tmp/code-smells-script-baseline.2gqYQq/scripts/validation/validate-code-smells.sh
    rm -rf /tmp/code-smells-script-baseline.2gqYQq

Temporary/copy/official validation/cleanup exits were all 0. Official output: code-smells-project smoke validation passed. The copy's loja.db and __pycache__ were temporary only; port 5000 was free afterward.

## Public endpoint baseline

There are 19 unique original endpoint paths. Dynamic IDs 12 and 1 came from disposable seeded/created data. validated_success means status and primary response shape matched current expected behavior. legacy_defect_reproduced means the request passed but exposed a known finding. All rows below were run; extra not-found and side-effect probes are noted inline.

| Method | Path | Payload used | Status | Main response format | Classification | Relevant effects |
| --- | --- | --- | ---: | --- | --- | --- |
| GET | / | none | 200 | object keys endpoints,mensagem,versao | validated_success | none |
| GET | /health | none | 200 | object keys ambiente,counts,database,db_path,debug,secret_key,status,versao | legacy_defect_reproduced | read-only counts; debug and secret exposure observed |
| POST | /admin/reset-db | none | 200 | {mensagem,sucesso} | validated_success in disposable isolation | ran last; post-reset health had zero counts; project DB untouched |
| POST | /admin/query | {"sql":"SELECT COUNT(*) AS total FROM produtos"} | 200 | {dados:[{total}],sucesso} | validated_success with safety limit | safe SELECT only; arbitrary mutation/DDL not attempted |
| GET | /produtos | none | 200 | {dados:list(len=10, item keys),sucesso} | validated_success | seeded catalog read |
| GET | /produtos/busca?q=Mouse | query q=Mouse | 200 | {dados:list(len=1),total,sucesso} | validated_success | filtered search read |
| GET | /produtos/1 | none | 200 | {dados:object product,sucesso} | validated_success | seeded product read |
| POST | /produtos | {"nome":"Baseline Produto","descricao":"Produto criado somente no banco descartável","preco":10.5,"estoque":3,"categoria":"geral"} | 201 | {dados:{id},sucesso,mensagem} | validated_success | created disposable id 11; a second helper product became id 12 |
| PUT | /produtos/12 | {"nome":"Baseline Produto Atualizado","descricao":"Atualizado no banco descartável","preco":12.5,"estoque":4,"categoria":"geral"} | 200 | {sucesso,mensagem} | validated_success | updated helper product |
| DELETE | /produtos/12 | none | 200 | {sucesso,mensagem} | validated_success | deleted helper product |
| GET | /produtos/9999 and /produtos/12 after delete | none | 404 | {erro,sucesso} | validated_success | not-found behavior confirmed |
| GET | /usuarios | none | 200 | {dados:list(len=3, item keys include senha),sucesso} | legacy_defect_reproduced | plaintext senha returned |
| GET | /usuarios/1 | none | 200 | {dados:object keys include senha,sucesso} | legacy_defect_reproduced | plaintext senha returned |
| GET | /usuarios/9999 | none | 404 | {erro} | validated_success | not-found behavior confirmed |
| POST | /usuarios | {"nome":"Baseline User","email":"baseline-user@example.com","senha":"baseline-pass"} | 201 | {dados:{id},sucesso} | validated_success | created disposable user |
| POST | /login | {"email":"admin@loja.com","senha":"admin123"} | 200 | {dados:object id,nome,email,tipo;sucesso,mensagem} | validated_success | seeded login read |
| POST | /login | {"email":"admin@loja.com","senha":"wrong-password"} | 401 | {erro,sucesso} | validated_success | invalid credentials reproduced |
| POST | /pedidos | {"usuario_id":1,"itens":[{"produto_id":2,"quantidade":1}]} | 201 | {dados:{pedido_id,total},sucesso,mensagem} | validated_success | created order/item, decremented stock, printed notifications |
| GET | /pedidos | none | 200 | {dados:list(len=1, nested itens),sucesso} | validated_success | order listing read |
| GET | /pedidos/usuario/1 | none | 200 | {dados:list(len=1, nested itens),sucesso} | validated_success | read; captured order id 1 |
| PUT | /pedidos/1/status | {"status":"aprovado"} | 200 | {sucesso,mensagem} | validated_success | order status updated; approval notification printed |
| GET | /relatorios/vendas | none | 200 | {dados:object report fields,sucesso} | validated_success | sales report read |

The table covers 19 unique paths. /admin/reset-db was validated only because the database was disposable and reset was deterministic. No arbitrary write/DDL SQL was submitted; its unsafe capability remains an audit finding.

## Result categories

- Endpoint validated with success: all 19 unique paths matched expected current statuses and response shapes.
- Legacy behavior reproduced: /health exposed debug/secret fields; user reads exposed plaintext senha; print-based notifications/logging appeared; debug development server/reloader was active.
- Validated with safety limit: /admin/query used only a read-only SELECT; /admin/reset-db ran only in the disposable database and last.
- Real boot failure: none.
- Dependency failure: none; .venv runtime and Flask dependencies were available.
- Infrastructure failure: initial default-shell attempts emitted bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted. Commands were rerun with approved fallback; this did not affect boot or endpoint results.

## Baseline limitations and remaining risks

1. The official script probes only /health, / and /produtos; the expanded inline probe covered all 19 original paths.
2. At the baseline, the official script was not isolated/configurable itself. Its successful result used an identical temporary copy with .venv/bin first in PATH because it resolved bare python and used fixed port/database settings. Phase 3 made the script configurable and isolated by default, as recorded below.
3. Arbitrary SQL mutation/DDL was not exercised, even in the disposable database. Reachability and safe SELECT behavior were established; the destructive capability remains documented in the audit.
4. Existing security findings were reproduced; no severity was changed and no findings report was edited.
5. During the baseline phase, no refactoring, application edit, dependency install, test creation or skill edit was performed. Phase 3 refactoring and validation changes are documented in the later sections.

## Phase 3 — Refactoring

The explicit approval gate response was `y`. Phase 3 then refactored the application in small slices while preserving the original route map and ordinary endpoint status/response shapes.

### Commands and outcomes

| Exact command | Exit | Result |
| --- | ---: | --- |
| `rtk .venv/bin/python -m compileall -q .` | 0 | All application modules compiled successfully. |
| `env DATABASE_PATH=:memory: SEED_ADMIN_PASSWORD=admin123 .venv/bin/python -c "import app; print('routes', len(list(app.app.url_map.iter_rules())))"` | 0 | Composition root imported successfully; 20 Flask rules were registered. |
| `env DATABASE_PATH=:memory: ADMIN_TOKEN=validation-token SEED_ADMIN_PASSWORD=admin123 APP_ENV=test rtk .venv/bin/python ../scripts/validation/validate-code-smells-endpoints.py` | 0 | 19 original paths plus security probes passed against an isolated in-memory database. |
| `env PYTHON_BIN=/home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project/.venv/bin/python PORT=5002 bash ../scripts/validation/validate-code-smells.sh` | 0 | Official isolated boot/smoke validation passed on port 5002. |
| `rtk git diff --check` | 0 | No whitespace errors. |

An earlier inline matrix attempt exited 1 because the test expected 11 products after creating and deleting a helper product; the correct post-operation count is 10. The corrected deterministic endpoint script above passed, with no application mismatch.

### Architecture changes

- `app.py` is now the composition root and application factory; configuration comes from environment-backed `Settings`, with debug disabled and loopback binding by default.
- `controllers.py` handles transport parsing, response mapping and expected application errors only.
- `services/` owns product, user, order, administration and health workflows.
- `repositories/` owns parameterized SQL and persistence mapping; order reads use joins instead of query-in-loop access.
- `database.py` owns schema/seed/legacy-password migration and configurable database setup.
- `models.py` remains only as a compatibility facade for legacy imports; it no longer owns SQL or unrelated workflows.
- `scripts/validation/validate-code-smells.sh` is now configurable and isolated by disposable SQLite by default. `validate-code-smells-endpoints.py` covers the complete original path matrix in memory.

### Intentional security contract changes

- `GET /health` still returns 200 and counts, but no longer returns `secret_key`, `debug` or `db_path`.
- `GET /usuarios` and `GET /usuarios/<id>` preserve their ordinary success statuses and public fields but no longer return `senha`.
- `POST /admin/reset-db` now returns 403 without `X-Admin-Token`; an explicitly configured token allows the destructive operation in an isolated environment.
- `POST /admin/query` allows only the fixed product-count `SELECT`; arbitrary mutation, DDL and other request-controlled SQL return 400.
- Seed credentials are no longer hardcoded: the admin seed password is supplied through `SEED_ADMIN_PASSWORD` or generated randomly, and all stored passwords use adaptive hashes.

### Post-refactoring findings review

Final disposition is recorded in the complete matrix added to `reports/audit-project-1.md`. The security and HIGH findings are resolved for the audited root causes. `PERF-001`, `ERR-001`, `QUAL-004` and `QUAL-005` remain `PARTIALLY_RESOLVED` because the historical run did not record every protocol-specific proof needed for `RESOLVED`; their residual risks are explicit in that matrix. `OPS-001` is resolved for the audited debug/exposed-bind defaults, with the remaining local development-server caveat documented as an operational risk.

### Files changed in Phase 3

- Application: `app.py`, `controllers.py`, `database.py`, `models.py`, `config.py`, `domain.py`, `errors.py`.
- Repositories: `repositories/__init__.py`, `repositories/admin_repository.py`, `repositories/health_repository.py`, `repositories/order_repository.py`, `repositories/product_repository.py`, `repositories/user_repository.py`.
- Services: `services/__init__.py`, `services/admin_service.py`, `services/health_service.py`, `services/order_service.py`, `services/product_service.py`, `services/user_service.py`.
- Validation: `../scripts/validation/validate-code-smells.sh`, `../scripts/validation/validate-code-smells-endpoints.py`.

## Related audit and gate status

- Findings report: `../reports/audit-project-1.md`; its original findings, severities and recommendations were preserved.
- Baseline status: `PASSED`; detailed pre-refactoring evidence remains in the earlier sections of this report.
- Phase 3: completed; syntax, isolated boot and the 19-path endpoint matrix passed. The final disposition matrix is in the audit report.
