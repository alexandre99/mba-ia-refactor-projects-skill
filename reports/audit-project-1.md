# Architecture Audit Report — code-smells-project

## Project profile

- Stack: Python 3.12.3 via `.venv/bin/python`, pip 26.1.2, Flask 3.1.1 e flask-cors 5.0.1 disponíveis no ambiente virtual preparado
- Database: SQLite, arquivo relativo `loja.db`
- Domain: API de e-commerce, cobrindo produtos, usuários/login, pedidos e relatório de vendas
- Source files analyzed: 4 (`app.py`, `controllers.py`, `database.py`, `models.py`)
- Public endpoints: 19
- Baseline status: PASSED
- Syntax: 4 arquivos Python aprovados
- Boot: aprovado
- Readiness: aprovada
- Endpoints: 19/19 paths originais exercitados
- Database: SQLite descartável e isolado
- `/admin/query`: somente um `SELECT` seguro foi executado; mutações e DDL arbitrários não foram exercitados por segurança
- Official isolated validation: aprovada
- Baseline evidence: os comandos completos e os resultados por endpoint estão documentados em `reports/execution-project-1.md`

## Executive summary

CRITICAL: 3 | HIGH: 5 | MEDIUM: 5 | LOW: 3

Há três bloqueadores críticos diretamente alcançáveis: execução de SQL fornecido pelo cliente, reset destrutivo sem autenticação e segredo utilizável hardcoded e exposto pelo health check. Os riscos altos concentram credenciais em texto puro, debug habilitado por padrão e fronteiras arquiteturais ausentes ou vazadas. A ordem recomendada é conter os endpoints administrativos e os segredos/senhas, depois separar persistência e workflows, e por fim reforçar validação, consultas e a rede de testes.

O catálogo completo foi cruzado. `DEP-001` não foi registrado: as únicas versões locais são `flask==3.1.1` e `flask-cors==5.0.1`, e não há documentação local de migração ou depreciação que sustente esse finding. `QUAL-003` também não foi duplicado: o nome `models.py` encobre responsabilidades extras, mas isso é a mesma causa raiz já registrada em `ARCH-001`.

## Comparação com a análise manual

A seção independente foi lida somente após a auditoria, em `README.md:26-79`, sem alterar os findings já produzidos.

- Findings manuais: 8
- Findings manuais reencontrados semanticamente: 8
- Findings manuais não reencontrados: nenhum

Findings manuais reencontrados:

1. Endpoint de execução arbitrária de SQL → `SEC-001`.
2. SQL injection por concatenação → `DATA-001`; a interpolação no login também foi observada em `SEC-004`, cujo escopo principal é o tratamento inseguro de senhas.
3. God module com múltiplos domínios → `ARCH-001`.
4. Queries N+1 em pedidos → `PERF-001`.
5. Validação duplicada → `QUAL-001`.
6. Tratamento amplo de exceções → `ERR-001`.
7. Magic values → `QUAL-002` (categorias e estados; as faixas de desconto da análise manual não foram repetidas como evidência do finding independente).
8. Logging com `print` → `QUAL-004`.

Findings adicionais descobertos pela skill, sem equivalente manual listado: `SEC-002`, `SEC-003`, `SEC-004`, `OPS-001`, `ARCH-002`, `ARCH-003`, `TEST-001` e `QUAL-005`.

## Findings

### [CRITICAL] SEC-001 — Execução arbitrária de SQL controlada por requisição

- File: `code-smells-project/app.py:59-78`
- Evidence: o handler `executar_query` lê `dados["sql"]` da requisição e o passa diretamente a `cursor.execute(query)`; para `SELECT` retorna as linhas e para qualquer outro comando faz `commit()`.
- Impact: qualquer cliente que alcance `POST /admin/query` pode ler, alterar ou apagar dados e tentar operações de schema, comprometendo confidencialidade e integridade do banco.
- Recommendation: remover o endpoint do runtime normal ou substituí-lo por operações administrativas explicitamente allowlisted; manter queries em um repositório com parâmetros e proteger a operação com autenticação/autorização forte.
- Validation: em banco temporário, confirmar que SQL arbitrário é rejeitado e que somente operações allowlisted autenticadas funcionam; executar probes de leitura, escrita e erro sem expor exceções.

### [CRITICAL] SEC-002 — Reset destrutivo de banco sem autenticação

- File: `code-smells-project/app.py:47-57`
- Evidence: `POST /admin/reset-db` não passa por middleware de autenticação e executa quatro `DELETE FROM` abrangentes antes de confirmar a transação.
- Impact: uma requisição não autenticada apaga usuários, produtos, pedidos e itens, causando perda irreversível de dados e indisponibilidade funcional.
- Recommendation: retirar a rota do contrato público e mover a manutenção para comando operacional protegido; se a compatibilidade exigir a rota, exigir autorização administrativa explícita, auditoria e confirmação segura.
- Validation: sem credenciais, a rota deve responder 401/403 e não alterar contagens; em teste autorizado e isolado, verificar que a operação exige o papel correto e registra o evento.

### [CRITICAL] SEC-003 — Segredo hardcoded e revelado pelo health check

- File: `code-smells-project/app.py:6-9`
- File: `code-smells-project/controllers.py:276-290`
- Evidence: `SECRET_KEY` recebe o literal `"minha-chave-super-secreta-123"`, e o mesmo valor é devolvido no campo `secret_key` de `GET /health` junto de `debug: True`.
- Impact: o segredo de assinatura/configuração fica versionado e publicamente enumerável, permitindo falsificação de dados assinados caso algum mecanismo de sessão/tokens o utilize e expondo configuração sensível.
- Recommendation: carregar o segredo de variável de ambiente/secret manager, rotacionar o valor comprometido e remover segredos e detalhes de configuração do payload de health.
- Validation: iniciar com segredo fornecido externamente, verificar que o literal não existe no código nem na resposta de `/health`, e executar a checagem de rotação sem quebrar os campos públicos permitidos.

### [HIGH] SEC-004 — Senhas armazenadas e comparadas em texto puro

- File: `code-smells-project/database.py:75-83`
- File: `code-smells-project/models.py:72-120`
- Evidence: a carga inicial insere `admin123`, `123456` e `senha123` diretamente na coluna `senha`; `login_usuario` compara `email` e `senha` por interpolação direta, enquanto listagens e busca de usuário retornam o campo `senha`.
- Impact: comprometimento do SQLite revela credenciais reutilizáveis, e as APIs `GET /usuarios` e `GET /usuarios/<id>` expõem senhas a qualquer cliente que as alcance.
- Recommendation: introduzir hash adaptativo com salt (por exemplo, API de hashing do Flask/Werkzeug), migrar registros existentes, comparar hashes e excluir `senha` de qualquer resposta ou consulta de leitura pública.
- Validation: criar usuário e confirmar que apenas o hash é persistido, validar login correto/incorreto, confirmar ausência de `senha` nas respostas e executar a migração em banco temporário.

### [HIGH] OPS-001 — Debug habilitado por padrão e servidor exposto

- File: `code-smells-project/app.py:6-9`
- File: `code-smells-project/app.py:80-88`
- Evidence: `app.config["DEBUG"] = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` são o comportamento padrão do entrypoint executável.
- Impact: a execução normal ativa recursos de debug e escuta em todas as interfaces, aumentando exposição de stack traces, console/debugger e configuração em ambientes não isolados.
- Recommendation: separar composição da aplicação e servidor, usar configuração por ambiente com debug desabilitado por padrão e delegar produção a um servidor WSGI com bind/configuração explícitos.
- Validation: iniciar sem configuração de desenvolvimento e verificar debug falso, resposta de erro genérica e bind esperado; validar que um ambiente de desenvolvimento explícito continua funcionando.

### [HIGH] ARCH-001 — Módulo `models.py` concentra domínios e camadas

- File: `code-smells-project/models.py:1-314`
- Evidence: o mesmo módulo contém mapeamento de produtos e usuários, autenticação, criação de pedido com cálculo/baixa de estoque, consultas de pedidos com itens, relatório de vendas com descontos e atualização de status, além de SQL e `commit()`.
- Impact: mudanças em produtos, identidade, checkout ou relatórios compartilham um módulo e uma conexão global, dificultando testes isolados, revisão de transações e evolução sem regressões entre domínios.
- Recommendation: dividir por domínio e responsabilidade: repositórios para SQL, serviços para workflows de pedido/autenticação/relatório, e modelos/objetos de domínio para invariantes; preservar os contratos dos controllers durante a extração.
- Validation: executar testes unitários dos serviços/repositórios e a matriz de endpoints antes/depois, verificando que cada fluxo mantém status, campos e efeitos persistidos.

### [HIGH] ARCH-002 — Regras de negócio e efeitos externos em controllers

- File: `code-smells-project/controllers.py:24-58`
- File: `code-smells-project/controllers.py:188-216`
- Evidence: `criar_produto` faz parsing, valida obrigatoriedade, faixas, tamanho e categorias e chama persistência; `criar_pedido` valida itens, interpreta erros do modelo e imprime simulações de e-mail, SMS e push no próprio handler.
- Impact: handlers HTTP ficam gordos e acoplados a listas/regras e efeitos, reduzindo reuso e tornando difícil testar o workflow sem Flask e sem banco real.
- Recommendation: extrair schemas/validadores para entrada, services para criação de produto e checkout e uma interface de notificação acionada após transação bem-sucedida; controller deve apenas orquestrar e mapear respostas.
- Validation: testar as regras fora do contexto HTTP, usar notifier falso no checkout e repetir `POST /produtos` e `POST /pedidos` com sucesso, validação e produto inexistente.

### [HIGH] ARCH-003 — Handler de health acessa persistência diretamente

- File: `code-smells-project/controllers.py:264-290`
- Evidence: `health_check` chama `get_db()`, cria cursor e executa quatro queries SQLite diretamente no handler, além de montar o payload de resposta.
- Impact: a camada HTTP conhece conexão, cursor, tabelas e estratégia de probes; mudanças no banco contaminam transporte e tornam o health check difícil de substituir ou testar.
- Recommendation: mover o probe de banco para um serviço/repositório de health e deixar o controller mapear somente o resultado para HTTP, com campos públicos mínimos.
- Validation: testar o probe com dependência fake e executar `GET /health` com banco conectado e indisponível, verificando status e formato sem detalhes sensíveis.

### [MEDIUM] DATA-001 — Construção dinâmica de query com filtros interpolados

- File: `code-smells-project/models.py:285-299`
- Evidence: `buscar_produtos` concatena `termo`, `categoria`, `preco_min` e `preco_max` em uma string SQL e a executa após receber esses valores de query string através de `controllers.buscar_produtos`.
- Impact: entradas com aspas ou padrões inesperados podem alterar predicados, causar erros e permitir extração/filtragem indevida; a query também fica difícil de revisar e otimizar.
- Recommendation: construir somente fragmentos fixos com parâmetros posicionais/nomeados para valores, incluindo escape/semântica explícita de `LIKE`, em um repositório de busca.
- Validation: testar aspas, curingas, categoria inválida e limites numéricos; confirmar que os valores permanecem parâmetros e que o resultado não muda a estrutura da query.

### [MEDIUM] QUAL-001 — Validação duplicada e divergente de produtos

- File: `code-smells-project/controllers.py:24-54`
- File: `code-smells-project/controllers.py:64-90`
- Evidence: criação e atualização repetem presença de `nome`, `preco` e `estoque`, limites não negativos e defaults; a criação também valida tamanho/categoria, enquanto a atualização não repete essas regras.
- Impact: as duas operações aceitam estados diferentes para a mesma entidade, permitindo regressões e mensagens inconsistentes quando as regras evoluírem.
- Recommendation: extrair um validador/schema compartilhado com regras explícitas para create/update e deixar diferenças deliberadas configuradas, não copiadas.
- Validation: aplicar a mesma matriz de payloads a POST e PUT e confirmar que regras comuns, mensagens e status permanecem estáveis salvo mudança documentada.

### [MEDIUM] PERF-001 — N+1 nas consultas de pedidos

- File: `code-smells-project/models.py:171-201`
- File: `code-smells-project/models.py:203-233`
- Evidence: para cada pedido o código consulta `itens_pedido`; para cada item abre outro cursor e consulta o produto por ID. O mesmo padrão aparece em `get_pedidos_usuario` e `get_todos_pedidos`.
- Impact: o custo de `GET /pedidos` e `GET /pedidos/usuario/<id>` cresce com pedidos e itens, aumentando latência e pressão no SQLite.
- Recommendation: usar uma consulta parametrizada com joins ou pré-carregamento em lote e mapear o resultado em uma única fronteira de repositório.
- Validation: medir quantidade de queries e tempo com dataset de vários pedidos, comparando resposta e ordenação antes/depois.

### [MEDIUM] ERR-001 — Exceções genéricas vazam detalhes para clientes

- File: `code-smells-project/controllers.py:5-12`
- File: `code-smells-project/app.py:68-78`
- Evidence: handlers capturam `Exception` e devolvem `str(e)` no JSON; o mesmo padrão se repete no módulo de controllers e no endpoint administrativo de query, sem mapeamento de erros esperados.
- Impact: mensagens podem revelar SQL, caminhos, nomes de tabelas ou detalhes internos e todos os defeitos acabam tratados como 500 sem política consistente.
- Recommendation: mapear erros de domínio/validação centralmente, registrar detalhes somente no log protegido e responder mensagem genérica com correlação para falhas inesperadas.
- Validation: provocar erro de SQL e falhas de validação em ambiente temporário, verificar resposta sem detalhes internos e confirmar log estruturado sem senha/segredo.

### [MEDIUM] TEST-001 — Safety net comportamental insuficiente

- File: `scripts/validation/validate-code-smells.sh:13-35`
- Evidence: o script compila, inicia em porta fixa 5000 e verifica somente `/health`, `/` e `GET /produtos`; não há arquivos de teste no alvo e não são exercitados writes, login, not-found, busca, pedidos, relatório ou endpoints administrativos.
- Impact: uma extração arquitetural pode quebrar a maior parte do contrato HTTP sem ser detectada, e o banco compartilhado não é isolado pelo script.
- Recommendation: tornar a validação configurável e isolada, usar banco temporário e cobrir health, leitura, escrita, falha de validação, not-found, login, pedido e relatório; adicionar testes determinísticos.
- Validation: executar o script em ambiente com dependências, confirmar cleanup do processo/banco e exigir falha em status, path ou shape divergente.

### [LOW] QUAL-002 — Constantes de domínio espalhadas em handlers

- File: `code-smells-project/controllers.py:52-54`
- File: `code-smells-project/controllers.py:242-250`
- Evidence: categorias válidas e estados de pedido são listas literais dentro dos handlers, e transições específicas são comparadas por strings no mesmo controller.
- Impact: alteração de categorias/status exige editar múltiplos pontos e pode criar divergência entre validação, persistência e relatório.
- Recommendation: centralizar enums/constantes no domínio e fazer services/repositories reutilizarem a mesma fonte.
- Validation: testar todos os valores válidos e inválidos nos endpoints de produto/status e verificar que o relatório continua coerente.

### [LOW] QUAL-004 — Imports não utilizados e diagnósticos ad hoc

- File: `code-smells-project/database.py:1-2`
- File: `code-smells-project/models.py:1-2`
- Evidence: `os` e `sqlite3` são importados nesses módulos sem uso observado; `controllers.py` ainda usa vários `print` para log operacional, inclusive e-mail/SMS/push simulado.
- Impact: ruído dificulta análise estática e os prints podem vazar dados ou misturar diagnóstico com efeito de negócio, sem níveis ou correlação.
- Recommendation: remover imports mortos e substituir diagnósticos por logging estruturado; encapsular efeitos de notificação em serviço.
- Validation: executar linter/análise estática sem imports mortos e verificar logs sem dados sensíveis durante smoke tests.

### [LOW] QUAL-005 — Construção de respostas de erro inconsistente

- File: `code-smells-project/controllers.py:14-22`
- File: `code-smells-project/controllers.py:136-144`
- Evidence: o not-found de produto inclui `"sucesso": False`, enquanto o not-found de usuário retorna somente `{"erro": ...}`; outros handlers também variam a presença desse envelope.
- Impact: clientes precisam tratar shapes divergentes para o mesmo tipo de resultado HTTP e a evolução do contrato fica mais arriscada.
- Recommendation: definir uma política de envelope/status no adaptador HTTP, mantendo compatibilidade explícita para consumidores existentes.
- Validation: comparar todas as respostas de sucesso, validação, not-found e erro interno por endpoint e documentar qualquer alteração intencional.

## Proposed Phase 3 plan

1. Conter `SEC-001`, `SEC-002`, `SEC-003`, `SEC-004` e `OPS-001`: proteger/remover administração destrutiva e SQL livre, externalizar/rotacionar segredo, migrar senhas para hash e desabilitar debug por padrão; documentar as mudanças de segurança no contrato.
2. Aplicar `T-002`, `T-004`, `T-006` e `T-008` do playbook: separar repositories/services/controllers, parametrizar todas as queries e centralizar erros, preservando shapes e status não afetados.
3. Aplicar `T-005`, `T-009` e `T-010`: extrair validação/notificações, remover diagnósticos ad hoc e ampliar a validação comportamental com banco temporário e todos os fluxos representativos.
4. Tratar `PERF-001`, `QUAL-002` e `QUAL-005` com consultas em lote, constantes de domínio e política de respostas; reexecutar o catálogo completo e a matriz HTTP antes/depois.

## Contract risks

- `/admin/reset-db` e `/admin/query` são públicos no código atual; removê-los ou exigir autorização é uma mudança deliberada motivada por segurança e precisa ser comunicada.
- Devem ser preservados métodos, paths, status de sucesso e campos dos endpoints públicos restantes, especialmente os envelopes `dados`/`sucesso`.
- Remover `senha` das respostas de usuários é uma correção de segurança intencional; login deve continuar retornando somente os campos não sensíveis já observados.
- A validação baseline pré-refatoração foi concluída com sucesso; os comandos completos e os resultados por endpoint estão documentados em `reports/execution-project-1.md`.

## Approval gate

Proceed with Phase 3 refactoring? [y/n]

## Final finding disposition — post-Phase 3 consolidation

The original audit above is preserved as the independent pre-refactoring record. The matrix below closes every one of its 16 findings against the final implementation and the validation evidence recorded in `reports/execution-project-1.md`. The partial dispositions are limited to MEDIUM/LOW findings for which the historical execution record does not contain the protocol-specific proof required for `RESOLVED`.

| Finding | Disposition | Final implementation evidence | Validation evidence | Remaining risk |
|---|---|---|---|---|
| `SEC-001` — arbitrary SQL execution | `RESOLVED` | `services/admin_service.py:7-24` allowlists one fixed SELECT; `repositories/admin_repository.py:13-15` owns the read. | `../scripts/validation/validate-code-smells-endpoints.py:91-98` accepted the allowlist and rejected DELETE/DDL; execution report records exit 0. | The administrative endpoint remains a compatibility route, but no request-controlled mutation/DDL is allowed. |
| `SEC-002` — unauthenticated database reset | `RESOLVED` | `services/admin_service.py:10-15` requires a configured token before `repositories/admin_repository.py:4-10` performs deletes. | `../scripts/validation/validate-code-smells-endpoints.py:99-103` proved anonymous 403/no reset and authorized reset; execution report records exit 0. | Authorization is token-based; stronger operator identity/audit policy is outside this experiment. |
| `SEC-003` — hardcoded secret exposed by health | `RESOLVED` | `config.py:12-34` loads/generates configuration outside source literals; `services/health_service.py:4-11` returns no secret/debug/path fields. | `../scripts/validation/validate-code-smells-endpoints.py:33-35` asserted the health response excludes sensitive fields; execution report records exit 0. | Previously exposed credentials still require operational rotation. |
| `SEC-004` — plaintext passwords | `RESOLVED` | `services/user_service.py:28-40` hashes/checks passwords; `repositories/user_repository.py:4-28` serializes public users without `senha`. | `../scripts/validation/validate-code-smells-endpoints.py:68-83` checked response non-disclosure, stored hash verification and login; execution report records exit 0. | Existing legacy records require the migration path in `database.py:122-134`; no plaintext is generated for new records. |
| `OPS-001` — debug/exposed runtime defaults | `RESOLVED` | `config.py:24-34` defaults to debug false and loopback; `app.py:89-94` uses those settings. | `../scripts/validation/validate-code-smells.sh:34-62` booted with `FLASK_DEBUG=0` on configurable port 5002; execution report records exit 0. | `python app.py` remains a local Flask development-server compatibility path; production must supply WSGI. |
| `ARCH-001` — cross-domain god module | `RESOLVED` | `app.py:27-74` composes `services/` and `repositories/`; domain workflows are split across those modules. | Full 19-path endpoint matrix and isolated boot passed; execution report records both validation commands with exit 0. | `models.py` remains a compatibility facade for legacy imports. |
| `ARCH-002` — business logic/effects in controllers | `RESOLVED` | `controllers.py:7-12` maps transport/application errors; `services/order_service.py:6-46` owns checkout validation/workflow. | Full endpoint matrix covered product/order success and failure behavior; execution report records exit 0. | Notification behavior is now represented by service boundaries but remains intentionally minimal. |
| `ARCH-003` — persistence coupled to health handler | `RESOLVED` | `controllers.py:154-155` delegates health; `services/health_service.py:4-11` calls `repositories/health_repository.py`. | Isolated health/boot validation passed; execution report records exit 0. | The global SQLite connection remains a deliberate compatibility implementation detail. |
| `DATA-001` — dynamic query construction | `RESOLVED` | `repositories/product_repository.py:70-88` builds only fixed SQL fragments and binds values as parameters. | Search and malformed/admin SQL probes passed in `validate-code-smells-endpoints.py`; execution report records exit 0. | LIKE wildcard semantics remain the legacy search contract. |
| `QUAL-001` — duplicated product validation | `RESOLVED` | `domain.py:19-62` centralizes payload rules; `services/product_service.py:13-23` reuses them for create/update. | Create/update matrix passed in the endpoint validation; execution report records exit 0. | Create/update strictness is intentionally shared rather than preserving every old divergence. |
| `PERF-001` — N+1 order reads | `PARTIALLY_RESOLVED` | `repositories/order_repository.py:26-80` uses one joined order query instead of per-item product lookups. | Endpoint behavior passed, but the historical record contains no query-count/query-plan proof. | Query-count regression is not formally closed and should be measured before further growth. |
| `ERR-001` — generic exception leakage | `PARTIALLY_RESOLVED` | `app.py:76-81` maps unexpected exceptions to a generic response; `controllers.py:7-12` maps expected application errors. | Normal success/validation/admin error probes passed; no recorded injected infrastructure failure proves every unexpected path. | Error mapping needs a dedicated unexpected-failure probe and protected structured logging review. |
| `TEST-001` — insufficient behavioral safety net | `RESOLVED` | `../scripts/validation/validate-code-smells-endpoints.py:22-105` covers the original route matrix, security probes and cleanup; `validate-code-smells.sh:12-62` isolates DB/port/process. | Endpoint helper and official smoke validation both exited 0 in the execution report. | The safety net is script-based and not a standalone unit-test suite. |
| `QUAL-002` — scattered domain constants | `RESOLVED` | `domain.py:1-16` centralizes categories/statuses and `domain.py:19-54` reuses category rules. | Product/status endpoint matrix passed; execution report records exit 0. | Discount thresholds remain workflow policy and should be named if they become configurable. |
| `QUAL-004` — dead imports/ad-hoc diagnostics | `PARTIALLY_RESOLVED` | `controllers.py` no longer contains the legacy notification prints; repositories/services own operational behavior. | The endpoint matrix passed, but no recorded linter/static-print validation specifically closes all residual diagnostics/imports. | Run a dedicated linter and runtime log scan before treating this quality finding as fully closed. |
| `QUAL-005` — divergent error envelopes | `PARTIALLY_RESOLVED` | `controllers.py:18-29` preserves the product not-found envelope while other handlers preserve legacy shapes. | The baseline and post-refactor endpoint status/shape checks passed. | Compatibility requires multiple error shapes; a future contract change must be explicit. |

No CRITICAL or HIGH finding is `PARTIALLY_RESOLVED` or `NOT_ADDRESSED`. The four remaining partial findings are MEDIUM/LOW and their residual risks are explicitly recorded above.
