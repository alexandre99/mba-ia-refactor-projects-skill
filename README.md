# Consolidação Final — experimento `refactor-arch`

Este repositório registra a criação, evolução e execução da skill `refactor-arch` em três APIs legadas. O experimento está concluído: os três projetos passaram por análise, auditoria, aprovação para mudança, refatoração MVC incremental e validação comportamental. Este documento é a consolidação final; não representa uma nova execução das Fases 1, 2 ou 3.

## Objetivo

Avaliar se uma skill do Codex consegue conduzir uma refatoração arquitetural reproduzível e baseada em evidências, preservando o contrato HTTP observável. O trabalho mede, em cada aplicação, a capacidade de:

- inventariar runtime, framework, banco, arquivos, startup e endpoints;
- produzir auditoria independente com evidência de arquivo e linha;
- pausar antes de modificar a aplicação e exigir aprovação humana;
- conduzir uma migração incremental para fronteiras MVC pragmáticas;
- provar boot, endpoints, caminhos negativos, rollback e fechamento dos findings.

## Escopo e metodologia

Foram avaliadas três aplicações: `code-smells-project` (Python/Flask, e-commerce), `ecommerce-api-legacy` (Node.js/Express, LMS/checkout) e `task-manager-api` (Python/Flask, tarefas e relatórios). A metodologia teve quatro momentos:

1. análise manual inicial, preservada explicitamente nesta seção e usada somente para comparação posterior;
2. execução da versão corrente da `refactor-arch` nas Fases 1 e 2, com inventário e auditoria independente;
3. gate explícito de aprovação humana e Fase 3 incremental, com preservação de rotas, status e shapes salvo correção de segurança documentada;
4. validação final por aplicação e matriz de disposition, incluindo provas específicas para segurança, transação, rollback, erros, efeitos externos e N+1 quando aplicável.

A skill usa um `SKILL.md` e sete referências especializadas: `project-analysis.md`, `anti-pattern-catalog.md`, `audit-report-template.md`, `mvc-guidelines.md`, `refactoring-playbook.md`, `validation-playbook.md` e `finding-resolution.md`. As cópias completas ficam em `.codex/skills/refactor-arch/` dentro de cada projeto.

## Análise Manual

Esta análise foi realizada antes da refatoração e é o baseline humano original do desafio. Ela permanece separada dos findings produzidos posteriormente pela skill; as evidências abaixo não foram reescritas para coincidir com as auditorias automatizadas. Os paths e números de linha são evidência histórica do código pré-refatoração.

### Projeto 1 — `code-smells-project`

Stack: Python, Flask e SQLite. Domínio: e-commerce com produtos, usuários, pedidos e relatórios.

| Severidade | Problema | Evidência | Por que é relevante |
|---|---|---|---|
| CRITICAL | Endpoint de execução arbitrária de SQL | `app.py:61-80` | Permite leitura, alteração ou destruição completa do banco por uma requisição não autenticada. |
| CRITICAL | SQL Injection por concatenação | `models.py:45-63`, `107-131`, `287-301` | Valores controlados pelo cliente são concatenados diretamente em queries. |
| HIGH | God module com múltiplos domínios | `models.py:1-316` | Produtos, usuários, autenticação, pedidos, estoque, relatórios e SQL estão acoplados no mesmo módulo. |
| MEDIUM | Queries N+1 ao carregar pedidos | `models.py:173-235` | Cada pedido busca itens e cada item busca novamente o produto. |
| MEDIUM | Validação duplicada | `controllers.py:26-98` | Regras de produto se repetem entre criação e atualização e podem divergir. |
| MEDIUM | Tratamento amplo de exceções | `controllers.py:7-294` | Erros internos são expostos ao cliente e não existe contrato centralizado. |
| LOW | Magic values em regras de negócio | `controllers.py:54-56`, `models.py:258-264` | Categorias e faixas de desconto ficam difíceis de descobrir e alterar. |
| LOW | Logging com `print` | `controllers.py:10-13`, `210-212` | Não há nível, contexto ou estrutura adequada para observabilidade. |

Relatório: `reports/audit-project-1.md`.

### Projeto 2 — `ecommerce-api-legacy`

Stack: Node.js, Express e SQLite. Domínio: LMS com checkout, matrícula, pagamento e relatório financeiro.

| Severidade | Problema | Evidência | Por que é relevante |
|---|---|---|---|
| CRITICAL | Credenciais e chave de pagamento hardcoded | `src/utils.js:1-8` | Segredos ficam expostos no código-fonte e em qualquer cópia do repositório. |
| CRITICAL | Dados de cartão e chave do gateway em logs | `src/AppManager.js:45-50` | Expõe dados financeiros sensíveis e credenciais operacionais. |
| HIGH | God Class `AppManager` | `src/AppManager.js:6-143` | A mesma classe cria banco, registra rotas, executa checkout, gera relatórios e deleta usuários. |
| MEDIUM | Checkout sem transação | `src/AppManager.js:45-65` | Falhas intermediárias podem deixar matrícula, pagamento e auditoria inconsistentes. |
| MEDIUM | N+1 no relatório financeiro | `src/AppManager.js:82-130` | Cada curso busca matrículas e cada matrícula busca usuário e pagamento. |
| MEDIUM | Callback pyramid e erros inconsistentes | `src/AppManager.js:39-79`, `85-130` | O fluxo assíncrono é difícil de testar e alguns erros são ignorados. |
| LOW | Variáveis crípticas | `src/AppManager.js:30-35` | Nomes como `u`, `e`, `p`, `cid` e `cc` escondem significado de domínio. |
| LOW | Estado global mutável | `src/utils.js:11-17` | Cache global cria acoplamento oculto e vazamento entre testes/processos. |

Relatório: `reports/audit-project-2.md`.

### Projeto 3 — `task-manager-api`

Stack: Python, Flask, Flask-SQLAlchemy e SQLite. Domínio: usuários, tarefas, categorias e relatórios.

| Severidade | Problema | Evidência | Por que é relevante |
|---|---|---|---|
| CRITICAL | Token de autenticação previsível | `routes/user_routes.py:187-213` | O token `fake-jwt-token-<id>` pode ser forjado sem assinatura, expiração ou verificação. |
| HIGH | Secret hardcoded e debug habilitado | `app.py:13-16`, `35-36` | Configuração insegura pode chegar a ambientes não locais. |
| HIGH | Rotas continuam concentrando negócio e persistência | `routes/task_routes.py:13-301`, `routes/user_routes.py:12-213` | A separação existente é apenas parcial; os blueprints ainda são fat controllers. |
| MEDIUM | N+1 na listagem de tarefas | `routes/task_routes.py:13-61` | Cada tarefa pode disparar consultas separadas de usuário e categoria. |
| MEDIUM | API legada/deprecated do SQLAlchemy | `routes/task_routes.py:44`, `53`, `69`; `routes/user_routes.py:31`, `96` | `Model.query.get()` deve migrar para `Session.get()` no SQLAlchemy 2.x. |
| MEDIUM | Serialização e cálculo de atraso duplicados | `routes/task_routes.py:18-61`, `67-83`; `routes/user_routes.py:155-185` | A mesma regra é reimplementada em rotas diferentes. |
| LOW | Imports não utilizados | `app.py:9`, `routes/task_routes.py:8-9` | Aumentam ruído e escondem dependências reais. |
| LOW | Políticas como magic literals | `routes/task_routes.py:112-116`, `178-185`; `routes/user_routes.py:73-74` | Status, prioridade e roles podem divergir entre fluxos. |

Relatório: `reports/audit-project-3.md`.

## Construção da Skill

A skill foi construída em `.codex/skills/refactor-arch/`. O arquivo [`SKILL.md`](code-smells-project/.codex/skills/refactor-arch/SKILL.md) funciona como um protocolo executável: define a ordem das fases, as regras de integridade, o formato mínimo das evidências e os gates que impedem declarar sucesso sem prova. As cópias nos três projetos foram mantidas sincronizadas; os relatórios de auditoria e execução continuam sendo a fonte dos achados, mudanças e resultados históricos.

### Decisões de design

O `SKILL.md` foi dividido em três fases sequenciais, com responsabilidades e saídas distintas:

1. **Fase 1 — Análise:** detecta runtime, linguagem, framework, gerenciador de pacotes, banco, testes e comando de inicialização; inventaria endpoints e contratos observáveis; infere o domínio e mapeia responsabilidades reais, incluindo bootstrap, transporte, negócio, persistência, configuração, transações e efeitos externos.
2. **Fase 2 — Auditoria:** aplica as regras relevantes do catálogo ao código atual, deduplica causas-raiz sem esconder riscos independentes, ordena os findings por severidade e gera o relatório padronizado com arquivo, linhas, evidência, impacto, recomendação e validação específica. A comparação com a análise manual só ocorre depois da auditoria independente.
3. **Fase 3 — Refatoração e prova:** somente após aprovação, captura o baseline, executa transformações incrementais do playbook, preserva o contrato observado salvo mudanças de segurança documentadas, roda boot/endpoints e provas negativas específicas, reavalia o catálogo e fecha cada finding na matriz de disposition.

As referências complementam o protocolo sem duplicar sua orquestração:

| Referência | Papel na skill |
|---|---|
| `project-analysis.md` | Heurísticas de stack, banco, domínio, responsabilidades e inventário de endpoints. |
| `anti-pattern-catalog.md` | Regras estáveis, sinais de detecção, severidade e critérios de ajuste. |
| `audit-report-template.md` | Estrutura do relatório da Fase 2, riscos contratuais, gate e matriz final. |
| `mvc-guidelines.md` | Responsabilidades de Routes/Views, Controllers, Models, Services, Repositories e composition root, com orientações incrementais para Flask e Express. |
| `refactoring-playbook.md` | Transformações T-001 a T-012, incluindo exemplos antes/depois e salvaguardas para contrato, transação e efeitos externos. |
| `validation-playbook.md` | Baseline, boot, endpoints, cleanup e validações negativas para segurança, erros, transações, efeitos e N+1. |
| `finding-resolution.md` | Ciclo de fechamento, dispositions permitidas, evidência exigida e política para não confundir mudança estrutural com resolução. |

O gate humano é explícito: a Fase 2 termina com `Proceed with Phase 3 refactoring? [y/n]`, não altera código da aplicação antes de uma resposta afirmativa na mesma sessão e só então libera a Fase 3. Depois da implementação há ainda um gate de fechamento: um finding só pode ser `RESOLVED` com causa-raiz removida, evidência final e validação capaz de detectar a falha original; validação indisponível ou insuficiente permanece visível como risco/disposition parcial.

### Catálogo de anti-patterns

O catálogo atual contém 21 regras, organizadas por risco e severidade para cobrir o que o desafio pede e o que os três projetos efetivamente exercitam:

- **Segurança crítica:** execução arbitrária de SQL/comandos, administração destrutiva exposta e credenciais/segredos utilizáveis no código.
- **Arquitetura, segurança operacional e consistência em nível alto:** god class/module, negócio em rotas/controllers, persistência acoplada ao transporte, tratamento inseguro de senhas, defaults de runtime inseguros, ausência de fronteira transacional atômica e efeitos externos antes do commit.
- **Dados, performance, erros, dependências e prova comportamental em nível médio:** queries dinâmicas, N+1/query-in-loop, regras duplicadas, vazamento de exceções, ausência de safety net e ausência de validação específica para falhas.
- **Qualidade em nível baixo:** magic values/constantes dispersas, nomes de fronteira enganosos, imports ou diagnósticos mortos e respostas construídas de modo inconsistente.

Essas categorias foram escolhidas para combinar segurança e integridade de dados, separação MVC/SOLID, comportamento de persistência e performance, qualidade de manutenção e confiabilidade da própria validação. O catálogo não força findings: exige evidência de código alcançável, usa IDs estáveis, separa causas-raiz independentes e permite ajustar a severidade somente com justificativa.

Há detecção explícita de **APIs deprecated** em `DEP-001`. Ela só é aplicada quando a versão da dependência ou evidência autoritativa de migração no repositório sustenta o diagnóstico, devendo registrar o equivalente moderno; memória isolada não basta. Isso aparece no Projeto 3 com `Model.query.get()` e a migração recomendada para `Session.get()`. No Projeto 2, a auditoria registrou que não havia evidência autoritativa para criar um finding desse tipo.

### Agnosticidade de tecnologia

A agnosticidade está no método, não em fingir que as stacks são iguais. As heurísticas usam sinais do repositório — arquivos de dependência, imports/construtores, routers, configuração, banco e comandos — e o mapeamento considera a responsabilidade efetiva de cada arquivo, não o nome de uma pasta. Assim, Flask e Express aparecem como sinais e exemplos de integração, não como pré-condição das regras de arquitetura.

O catálogo descreve problemas transferíveis entre linguagens (segredo hardcoded, god module, SQL dinâmico, N+1, transação ausente, erro exposto, API deprecated, magic values). As guidelines definem fronteiras conceituais; o playbook traz exemplos em Python e JavaScript; e os playbooks de validação e resolução exigem provas observáveis, independentemente do framework. Isso permite preservar boas camadas existentes e adaptar a transformação ao projeto, em vez de impor uma árvore de diretórios.

O experimento comprovou essa adaptação nos três alvos: `code-smells-project` e `task-manager-api` são Python/Flask, mas um começa monolítico e o outro já possui organização parcial; `ecommerce-api-legacy` é Node.js/Express e contém o fluxo de checkout. A mesma skill detectou e auditou essas diferenças, conduziu fronteiras MVC incrementais e produziu validações específicas para cada contrato, conforme os relatórios vinculados nas seções de execução e evidências.

### Desafios encontrados e soluções

O aprendizado central veio do Projeto 2. A primeira refatoração estrutural separou rotas, controllers, services e repositories e passou pelo smoke test, mas isso não provava atomicidade do checkout: uma falha intermediária ainda poderia deixar matrícula, pagamento ou auditoria parcialmente persistidos. O episódio está detalhado em [Evolução da skill após o Projeto 2](#evolução-da-skill-após-o-projeto-2); em resumo, a skill evoluiu para:

- manter `DATA-002` separado de um finding genérico de arquitetura;
- exigir uma transaction boundary/unit of work explícita para as escritas relacionadas;
- injetar uma falha intermediária e verificar rollback de todas as linhas relacionadas, ausência de cache/efeito externo antes do commit e commit/efeito no caminho de sucesso;
- exigir validações específicas de rollback, commit, cache, erro e políticas, além da matriz final de disposition.

Na reavaliação consolidada, `DATA-002` e `TEST-002` foram fechados como `RESOLVED`; a matriz atual do Projeto 2 ficou com quatro findings `RESOLVED` e `QUAL-005` `PARTIALLY_RESOLVED` por compatibilidade dos formatos legados. O resultado confirmou que mover código de arquivo não basta para resolver um risco comportamental.

Outros limites comprovados reforçaram a mesma decisão: no Projeto 1, a ausência histórica de provas específicas de contagem de queries, falha inesperada e lint/log manteve quatro findings MEDIUM/LOW parciais; no Projeto 3, a limitação do validator original foi registrada antes de uma validação isolada e específica permitir a cobertura completa. Em ambos os casos, a skill passou a tratar prova ausente como limitação explícita, não como sucesso inferido.

## Evolução da skill após o Projeto 2

A primeira execução do Projeto 2 mostrou que separar rotas, controllers, services e repositories e passar no smoke test não prova atomicidade. O checkout ainda podia deixar escritas parciais sem que a validação detectasse o defeito.

Com base nessa evidência, a skill foi fortalecida para:

- tratar `DATA-002` como regra independente de fronteiras arquiteturais;
- exigir uma unidade transacional explícita para escritas relacionadas;
- exigir falha injetada, rollback verificável e efeitos externos somente após commit;
- exigir validação específica para findings de segurança, consistência, erro e performance;
- exigir matriz final completa antes de declarar conclusão.

As três cópias da skill e de suas referências foram então mantidas sincronizadas. O Projeto 2 foi reavaliado pela versão consolidada antes da execução final do Projeto 3.

## Comparação estrutural Antes/Depois

As tabelas mostram somente as fronteiras principais observadas; não são árvores completas de arquivos.

### Projeto 1 — `code-smells-project`

| Antes | Depois |
|---|---|
| `app.py` misturava bootstrap, rotas e configuração; `controllers.py` concentrava transporte, negócio e efeitos; `models.py` reunia domínios, SQL e relatórios. | `app.py` é composition root/factory; controllers fazem parsing e response mapping; `services/` orquestra workflows; `repositories/` concentra SQL/persistência; `models.py` permanece apenas como facade de compatibilidade. |

### Projeto 2 — `ecommerce-api-legacy`

| Antes | Depois |
|---|---|
| `src/AppManager.js` criava banco, registrava rotas, executava checkout, gerava relatório e excluía usuários; `src/utils.js` mantinha configuração/cache globais. | `src/app.js` compõe dependências e `src/server.js` inicia o servidor; `routes.js`/controllers mapeiam HTTP; services possuem workflows; repositories possuem SQL; infrastructure possui adapter/seed; config, middleware e segurança são fronteiras explícitas. |

### Projeto 3 — `task-manager-api`

| Antes | Depois |
|---|---|
| `app.py` fazia bootstrap/configuração e rotas; blueprints misturavam parsing, validação, ORM, cálculos, commits e serialização. | `create_app()`/configuração/WSGI compõem a aplicação; routes são wrappers de transporte; controllers/services possuem orquestração e regras; repositories possuem ORM e unit of work; response mapping é centralizado. |

## Execução dos três projetos

| Projeto | Execução final registrada | Findings da matriz final | Resultado documentado |
|---|---|---:|---|
| 1 — `code-smells-project` | [audit](reports/audit-project-1.md) e [execution](reports/execution-project-1.md) | 16 | 12 `RESOLVED`; 4 `PARTIALLY_RESOLVED` MEDIUM/LOW (`PERF-001`, `ERR-001`, `QUAL-004`, `QUAL-005`) |
| 2 — `ecommerce-api-legacy` | reavaliação consolidada em [audit](reports/audit-project-2.md) e [execution](reports/execution-project-2.md) | 5 atuais | 4 `RESOLVED`; 1 `PARTIALLY_RESOLVED` de baixa severidade (`QUAL-005`) |
| 3 — `task-manager-api` | [audit](reports/audit-project-3.md) e [execution](reports/execution-project-3.md) | 11 | 11 `RESOLVED` |

Os números do Projeto 2 são da reavaliação final. O mesmo relatório preserva, antes dela, a auditoria e a execução históricas do primeiro ciclo; findings históricos não são contados novamente na linha final.

### Resumo dos relatórios por severidade

Os totais abaixo reproduzem os sumários dos relatórios de auditoria; são um índice documental e não alteram findings, dispositions ou evidências históricas.

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Contexto |
|---|---:|---:|---:|---:|---|
| 1 — `code-smells-project` | 3 | 5 | 5 | 3 | Auditoria que originou a matriz final de 16 findings. |
| 2 — `ecommerce-api-legacy` | 2 | 4 | 2 | 2 | Auditoria histórica; a reavaliação final registra 0 CRITICAL, 1 HIGH, 2 MEDIUM e 2 LOW. |
| 3 — `task-manager-api` | 1 | 6 | 3 | 1 | Auditoria final de 11 findings. |

### Projeto 1 — e-commerce Python/Flask

O baseline executou os 19 paths originais em SQLite descartável. A Fase 3 criou composição configurável, services e repositories, parametrizou as consultas, limitou as operações administrativas, removeu segredos do health check, aplicou hashing de senha, centralizou erros e ampliou a validação. A validação final registrada cobriu os 19 paths e probes de segurança; boot, endpoints e cleanup passaram com exit code 0.

As mudanças contratuais intencionais foram: `/health` não expõe segredo/debug/path; respostas de usuário não expõem `senha`; reset administrativo exige token; e `/admin/query` aceita somente a consulta allowlisted. O risco residual documentado é a divergência histórica de envelopes de erro (`QUAL-005`), além da necessidade operacional de usar WSGI em produção.

### Projeto 2 — LMS/checkout Node.js/Express

O primeiro ciclo removeu segredos, hashing inseguro, god module, acoplamento HTTP/SQLite e N+1 no relatório, preservando os contratos observados. A reavaliação pela skill consolidada encontrou cinco itens atuais: transação ausente, default de storage inseguro em produção, safety net sem prova de rollback, magic values e respostas legadas divergentes.

A correção final adicionou unidade transacional no checkout, rollback após falha intermediária, cache somente depois do commit, guard de storage durável em produção, probes específicos e constantes de checkout. O validator padrão e o validator em porta configurável passaram com exit code 0. `QUAL-005` permanece parcialmente resolvido por compatibilidade: falhas textuais, sucesso JSON e relatório em array continuam distintos. O relatório também registra os avisos de auditoria de dependências do npm e o risco de relatório financeiro público como limitações fora do escopo corretivo final.

### Projeto 3 — task manager Python/Flask

O baseline primeiro registrou a limitação do validator original (`python` indisponível e cobertura insuficiente); depois uma virtualenv isolada permitiu a validação completa dos 22 padrões de rota. Após aprovação, a Fase 3 adicionou configuração por ambiente, application factory, WSGI, tokens assinados, autorização administrativa, hashing de senha, controllers/services/repositories, validação centralizada, carregamento sem N+1 e seed transacional.

As validações finais passaram em portas 5000 e 5053, incluindo boot, todos os endpoints, 401 anônimo, 200 autorizado, rollback, seed, contagem de queries, Ruff, compileall e guards de produção. Nenhum finding permaneceu parcial ou não tratado. Mudanças de segurança documentadas: DELETE passou a exigir autorização; tokens passaram a ser assinados; respostas não expõem `password`; e produção exige segredo e WSGI.

## Evidências de execução pós-refatoração

Os trechos abaixo são transcrições curtas dos resultados já registrados nos execution reports; esta consolidação não executou novamente aplicações ou validators.

### Projeto 1

```text
validate-code-smells-endpoints.py | exit 0 | 19 original paths plus security probes passed against an isolated in-memory database.
validate-code-smells.sh | exit 0 | Official isolated boot/smoke validation passed on port 5002.
```

### Projeto 2

```text
validate-ecommerce-legacy.sh | exit 0 | Dependency installation/verification, production storage guard, boot, endpoint contracts, rollback/commit/cache/error probes, and cleanup passed.
PORT=3017 ... validate-ecommerce-legacy.sh | exit 0 | Same complete validation passed on a configurable non-default port.
```

### Projeto 3

```text
validate-task-manager-api.sh | exit 0 | All endpoint probes, anonymous 401 checks, authorized 200 checks, and cleanup passed.
ENDPOINTS: all baseline probes passed
CLEANUP: temporary project, database, log, and process removed
```

## Resultados consolidados

Nas matrizes finais atuais há 32 findings distintos entre os três escopos: 27 `RESOLVED` e 5 `PARTIALLY_RESOLVED`, todos MEDIUM/LOW. Não há `CRITICAL` ou `HIGH` com disposition `PARTIALLY_RESOLVED` ou `NOT_ADDRESSED`. Não há `ACCEPTED_RISK` sem aprovação explícita registrada.

Os contratos não relacionados a segurança foram preservados nos três projetos: paths, métodos, status de sucesso e shapes observados nos baselines. As exceções estão listadas nos relatórios de execução e nas seções de mudanças contratuais acima.

## Como Executar

### Pré-requisitos

- OpenAI Codex instalado e configurado/autenticado;
- Python compatível e dependências Flask dos projetos Python;
- Node.js, npm e dependências do projeto Express;
- `curl` e os comandos usados pelos validators (`mktemp`, `setsid` no validator específico do Projeto 3).

### Sincronizar e verificar a skill

Na raiz do repositório, os scripts oficiais existentes são:

```bash
bash scripts/sync-refactor-skill.sh
bash scripts/verify-refactor-skill.sh
```

O primeiro copia a skill canônica de `code-smells-project/.codex/skills/refactor-arch/` para os outros dois projetos; o segundo compara recursivamente as três cópias.

### Abrir a sessão correta e executar Fases 1 e 2

Abra uma nova sessão do Codex na raiz de cada projeto, uma por vez, e use o prompt mínimo abaixo. O prompt exige inventário, auditoria, relatório e parada no gate; ele não autoriza a Fase 3.

```text
Use obrigatoriamente a skill refactor-arch neste projeto. Execute somente as Fases 1 e 2, gere o relatório de auditoria e as evidências com arquivo/linha exatos, preserve o contrato observado e pare no gate humano antes de editar qualquer arquivo da aplicação.
```

Sessões e diretórios:

```bash
cd code-smells-project
# abrir a sessão Codex neste diretório e enviar o prompt mínimo

cd ../ecommerce-api-legacy
# abrir uma nova sessão Codex neste diretório e enviar o mesmo prompt

cd ../task-manager-api
# abrir uma nova sessão Codex neste diretório e enviar o mesmo prompt
```

Depois de cada Fase 2, revise o audit report, confirme que não houve alteração prematura e responda explicitamente `y` ao gate na mesma sessão. Só então envie:

```text
Aprovo explicitamente a Fase 3 para este projeto. Execute a refatoração incremental prevista, preserve rotas/status/shapes salvo as mudanças de segurança documentadas, rode o validator aplicável e registre boot, endpoints, validações específicas, cleanup e dispositions sem inventar resultados.
```

### Startup e validators

Os comandos de startup históricos registrados são `python app.py` para os projetos Flask e `npm start` para `ecommerce-api-legacy`. Para validação determinística, use os scripts existentes:

```bash
bash scripts/validation/validate-code-smells.sh
bash scripts/validation/validate-ecommerce-legacy.sh
bash task-manager-api/scripts/validation/validate-task-manager-api.sh
```

Também existe `bash scripts/validation/run-all.sh`; ele delega aos três scripts de validação da raiz, incluindo o smoke validator original de `task-manager-api`. O relatório do Projeto 3 registra a limitação desse validator original e a execução aprovada do validator específico `task-manager-api/scripts/validation/validate-task-manager-api.sh`; portanto essa diferença deve permanecer explícita.

### Consultar os relatórios

Os resultados detalhados estão nos pares abaixo:

- [Auditoria e execução do Projeto 1](reports/audit-project-1.md) · [evidências](reports/execution-project-1.md)
- [Auditoria e execução do Projeto 2](reports/audit-project-2.md) · [evidências](reports/execution-project-2.md)
- [Auditoria e execução do Projeto 3](reports/audit-project-3.md) · [evidências](reports/execution-project-3.md)

Para inspeção textual, os relatórios também foram consultados historicamente com `rtk sed -n '1,260p' reports/<arquivo>.md`.

## Checklist final por projeto

| Requisito | Projeto 1 — `code-smells-project` | Projeto 2 — `ecommerce-api-legacy` | Projeto 3 — `task-manager-api` |
|---|---|---|---|
| Stack detectada | ✅ Python + Flask + SQLite | ✅ Node.js + Express + SQLite | ✅ Python + Flask + Flask-SQLAlchemy + SQLite |
| Mínimo de findings na Fase 2 | ✅ 16 findings na matriz final | ✅ 5 findings atuais na reavaliação; histórico preservado | ✅ 11 findings |
| CRITICAL/HIGH | ✅ findings CRITICAL/HIGH no relatório | ✅ histórico com CRITICAL/HIGH; reavaliação atual com HIGH | ✅ 1 CRITICAL e 6 HIGH |
| Comparação com análise manual | ✅ 8/8 redescobertos semanticamente | ⚠️ histórico: 6/8; reavaliação: 1/8 após o primeiro ciclo | ⚠️ a comparação histórica ocorreu quando o README ainda não enumerava findings; o baseline manual foi restaurado nesta consolidação sem alterar a auditoria |
| Gate humano | ✅ aprovação `y` antes da Fase 3 | ✅ aprovação `y` antes das mudanças | ✅ aprovação `y` antes das mudanças |
| MVC/refatoração | ✅ composition root, controllers, services e repositories | ✅ composition root, routes/controllers, services, repositories e infrastructure | ✅ factory/WSGI, routes, controllers, services e repositories |
| Boot | ✅ boot isolado e smoke em porta 5002 | ✅ boot padrão e porta 3017 | ✅ boot em portas 5000 e 5053 |
| Endpoints | ✅ 19 paths originais | ✅ contratos de checkout, relatório e exclusão | ✅ 22 padrões de rota e probes negativos |
| Validações específicas | ⚠️ matriz completa passou; `PERF-001`, `ERR-001`, `QUAL-004` e `QUAL-005` permanecem parciais por provas históricas ausentes | ✅ rollback/commit/cache/error/magic-value probes passaram | ✅ autorização, password, rollback, seed, query-count, Ruff, compileall e guards de produção passaram |
| Disposition final | ⚠️ 12 `RESOLVED`; 4 `PARTIALLY_RESOLVED` MEDIUM/LOW | ⚠️ 4 `RESOLVED`; `QUAL-005` `PARTIALLY_RESOLVED` | ⚠️ 11 `RESOLVED`; limitações operacionais de hashes legados e WSGI externo permanecem documentadas |

## Limitações conhecidas e riscos residuais

- O Projeto 1 preserva envelopes de erro historicamente divergentes e usa o servidor Flask apenas para compatibilidade local; produção deve fornecer WSGI externo.
- O Projeto 1 não possui, nos registros históricos, uma medição formal de contagem de queries para fechar `PERF-001`; também faltam probes específicos para falha inesperada (`ERR-001`) e uma verificação dedicada de lint/log (`QUAL-004`). Esses findings permanecem parciais apesar das melhorias implementadas.
- O Projeto 2 mantém respostas legadas com mídias/shapes diferentes e um relatório financeiro público por compatibilidade do escopo; a configuração de produção, porém, falha fechada sem storage durável.
- O Projeto 2 registrou 13 avisos de vulnerabilidade do `npm audit` no processo de instalação; nenhum finding de API obsoleta foi criado sem evidência autoritativa de uso.
- O Projeto 3 requer migração/reset de registros com hashes antigos e depende de um processo WSGI externo em produção; o escopo não adicionou uma suíte unitária externa.
- IDs, timestamps, seeds e valores agregados são dependentes dos dados temporários; a comparação válida é por shape, status e invariantes.
- A consolidação final verifica documentação e referências. Ela não reexecuta aplicações, validators ou qualquer fase da skill.

## Evidências e validações históricas

Os seis relatórios são a fonte de verdade dos comandos e exit codes de cada execução:

- [Auditoria e execução do Projeto 1](reports/audit-project-1.md) · [evidências](reports/execution-project-1.md)
- [Auditoria e execução do Projeto 2](reports/audit-project-2.md) · [evidências](reports/execution-project-2.md)
- [Auditoria e execução do Projeto 3](reports/audit-project-3.md) · [evidências](reports/execution-project-3.md)

Cada auditoria contém findings com severidade, regra, arquivo, linhas, evidência, impacto, recomendação e validação; cada execução contém baseline, aprovação, mudanças, contratos, validações e cleanup. O relatório do Projeto 1 agora inclui a matriz final completa; o do Projeto 2 separa histórico e reavaliação; e o do Projeto 3 separa o gate histórico da implementação efetivamente executada.

## Validações da consolidação final — 2026-08-09

Foram executadas somente verificações documentais e de consistência; nenhuma aplicação ou validator de projeto foi iniciado:

- `rtk git diff --check`: exit 0;
- `rtk bash scripts/verify-refactor-skill.sh`: exit 0; três cópias idênticas;
- verificação das referências documentais e existência dos seis relatórios: exit 0;
- verificação dos links locais do README: exit 0;
- verificação de que não há diff em caminhos funcionais das três aplicações: exit 0, conjunto vazio;
- `rtk git status --short`: somente README, relatórios e referências da skill sincronizadas modificados.

Não foram executados novamente validators, boot, endpoints, Fases 1/2/3 ou qualquer experimento nesta consolidação.

## Estado final do experimento

- [x] análise manual e metodologia documentadas;
- [x] Fases 1 e 2 executadas nos três projetos;
- [x] aprovação humana e Fase 3 executadas nos três projetos;
- [x] Projeto 2 reavaliado após a evolução da skill;
- [x] boot, endpoints e validações específicas registradas;
- [x] dispositions finais revisadas e riscos residuais registrados;
- [x] README e relatórios consolidados;
- [x] três cópias da skill verificadas como sincronizadas.
