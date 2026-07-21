# Refatoração Arquitetural Automatizada com OpenAI Codex

Projeto acadêmico para criação e validação da Custom Skill `refactor-arch`. A skill analisa uma codebase, audita anti-patterns, pausa para revisão humana, refatora para uma arquitetura MVC adequada ao contexto e valida que a aplicação continua funcionando.

## Ferramenta escolhida

- OpenAI Codex
- Skill path: `.codex/skills/refactor-arch/`
- Referências da skill: Markdown
- Projetos-alvo: Python/Flask, Node.js/Express e Python/Flask com organização parcial

## Análise Manual

A análise foi realizada antes da refatoração. Os relatórios completos, com evidências e recomendações, estão em `reports/`.

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

A skill foi estruturada como um orquestrador pequeno em `SKILL.md` e referências especializadas:

```text
.codex/skills/refactor-arch/
├── SKILL.md
└── references/
    ├── project-analysis.md
    ├── anti-pattern-catalog.md
    ├── audit-report-template.md
    ├── mvc-guidelines.md
    ├── refactoring-playbook.md
    └── validation-playbook.md
```

### Decisões de design

1. **Três fases sequenciais:** análise, auditoria e refatoração.
2. **Gate humano obrigatório:** a Fase 2 termina pedindo confirmação e nenhum arquivo da aplicação pode ser alterado antes da aprovação.
3. **Evidência verificável:** todo finding deve possuir arquivo e linhas exatas.
4. **Agnosticismo de tecnologia:** os sinais de detecção descrevem responsabilidades e dependências, não nomes específicos de frameworks.
5. **MVC pragmático:** routes/views cuidam do transporte HTTP, controllers orquestram, services concentram workflows, models representam dados/invariantes e repositories isolam persistência.
6. **Refatoração incremental:** projetos parcialmente organizados devem preservar boas fronteiras em vez de sofrer uma reescrita forçada.
7. **Validação honesta:** boot e endpoints precisam ser realmente executados; ausência de runtime ou dependências deve ser registrada como bloqueio.

### Catálogo de anti-patterns

O catálogo possui severidades distribuídas e cobre, entre outros:

- arbitrary SQL/command execution;
- hardcoded secrets;
- plaintext ou weak password handling;
- God Class/God Module;
- fat controllers;
- ausência de transação;
- estado global mutável;
- N+1 queries;
- duplicação de validação;
- broad exception handling;
- APIs deprecated;
- magic values e nomenclatura ruim.

### Playbook de refatoração

O playbook contém transformações concretas antes/depois para parametrização de SQL, extração de configuração, password hashing, separação de controllers/services/repositories, transações, remoção de estado global, eliminação de N+1, validação centralizada, error handling e migração de APIs deprecated.

## Resultados

### Auditorias da Fase 2

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|---:|
| `code-smells-project` | 5 | 2 | 3 | 2 | 12 |
| `ecommerce-api-legacy` | 3 | 3 | 3 | 2 | 11 |
| `task-manager-api` | 1 | 2 | 4 | 2 | 9 |

### Estado atual da execução

- [x] Análise manual dos três projetos
- [x] Skill inicial com três fases
- [x] Catálogo com mais de 8 anti-patterns e severidades distribuídas
- [x] Detecção de APIs deprecated incluída
- [x] Playbook com mais de 8 transformações
- [x] Relatórios da Fase 2 salvos em `reports/`
- [x] Gate de confirmação antes da Fase 3
- [ ] Skill copiada para os três projetos
- [ ] Fase 3 executada no projeto 1
- [ ] Fase 3 executada no projeto 2
- [ ] Fase 3 executada no projeto 3
- [ ] Boot e endpoints validados nos três projetos
- [ ] Logs/screenshots de execução registrados

Os itens pendentes não são apresentados como concluídos até que a execução real seja feita.

## Como Executar

### Pré-requisitos

- OpenAI Codex instalado e autenticado;
- Python compatível com os projetos Flask;
- Node.js e npm compatíveis com o projeto Express;
- `curl` para smoke tests.

### Invocar a skill

Dentro de cada projeto, solicite ao Codex a execução explícita da skill `refactor-arch`:

```bash
cd code-smells-project
codex "Use a skill refactor-arch neste projeto. Execute as Fases 1 e 2, salve o relatório e pare para minha aprovação antes da Fase 3."

cd ../ecommerce-api-legacy
codex "Use a skill refactor-arch neste projeto. Execute as Fases 1 e 2, salve o relatório e pare para minha aprovação antes da Fase 3."

cd ../task-manager-api
codex "Use a skill refactor-arch neste projeto. Execute as Fases 1 e 2, salve o relatório e pare para minha aprovação antes da Fase 3."
```

Após revisar o relatório, autorize explicitamente a Fase 3.

### Validar

```bash
bash scripts/validation/run-all.sh
```

Cada script deve iniciar a aplicação, aguardar readiness, consultar endpoints representativos, encerrar o processo e retornar código diferente de zero em caso de falha.

## Estrutura dos relatórios

- `reports/audit-project-1.md`
- `reports/audit-project-2.md`
- `reports/audit-project-3.md`

## Observação acadêmica

O trabalho usa OpenAI Codex, uma das ferramentas permitidas pelo enunciado. A documentação distingue claramente análise estática, execução da skill e validação real para evitar evidências artificiais de conclusão.
