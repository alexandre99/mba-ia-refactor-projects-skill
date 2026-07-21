# Execution Evidence — code-smells-project

## Context

- Date: 2026-07-21
- Timezone: America/Sao_Paulo (-03)
- New baseline timestamp: 2026-07-21T13:52:29-03:00
- Scope: pre-refactoring baseline only; Phase 3 was not started.
- Direct-check working directory: /home/alexandredev/fullcycle-mba/mba-ia-refactor-projects-skill/code-smells-project
- Required skill: .codex/skills/refactor-arch/SKILL.md; its six required references were read in full.
- .codex/napkin.md was absent and was not created, per the explicit task constraint.
- No application source, dependency, configuration, skill, test, audit report or napkin file was changed. Only this execution report was replaced.

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

The correct legacy command is documented in README.md:7-10 as python app.py. app.py:80-88 initializes the database and calls app.run(host="0.0.0.0", port=5000, debug=True). Routes are declared in app.py:11-30, app.py:32-45, app.py:47-78; handlers are in controllers.py:5-292.

The validation script at ../scripts/validation/validate-code-smells.sh:1-35 uses bare python, fixed port 5000, relative loja.db, and probes only /health, / and /produtos. To preserve the original tree, it was run from a temporary copy of the same source/script with project .venv/bin first in PATH; no activation or installation was used.

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

## Limitations and remaining blockers

1. The official script probes only /health, / and /produtos; the expanded inline probe covered all 19 original paths.
2. The official script is not isolated/configurable itself. Its successful result used an identical temporary copy with .venv/bin first in PATH because it resolves bare python and uses fixed port/database settings.
3. Arbitrary SQL mutation/DDL was not exercised, even in the disposable database. Reachability and safe SELECT behavior were established; the destructive capability remains documented in the audit.
4. Existing security findings were reproduced; no severity was changed and no findings report was edited.
5. No refactoring, application edit, dependency install, test creation or skill edit was performed.

## Related audit and gate status

- Findings report: ../reports/audit-project-1.md (not modified in this attempt).
- Previous BLOCKED state: replaced by this real baseline result.
- Phase 3: not started.

Proceed with Phase 3 refactoring? [y/n]

