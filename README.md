# Refatoração Arquitetural Automatizada com OpenAI Codex

Projeto acadêmico para criação e validação da Custom Skill `refactor-arch`. A entrega só será considerada concluída quando a mesma skill executar as três fases nos três projetos, produzir os relatórios, modificar o código após aprovação humana e registrar validação real de boot, endpoints e fechamento dos findings.

## Ferramenta escolhida

- OpenAI Codex
- Skill path: `.codex/skills/refactor-arch/`
- Referências: Markdown
- Projetos-alvo: Python/Flask, Node.js/Express e Python/Flask parcialmente organizado

## Análise Manual

Esta seção foi produzida antes da execução da skill, como exige o enunciado. Ela funciona como referência de avaliação: a skill deve encontrar independentemente pelo menos cinco problemas em cada projeto e redescobrir parte relevante destes achados.

### Projeto 1 — `code-smells-project`

| Severidade | Problema | Evidência | Relevância |
|---|---|---|---|
| CRITICAL | Endpoint de execução arbitrária de SQL | `app.py:61-80` | Permite leitura, alteração ou destruição do banco por uma requisição não autenticada. |
| CRITICAL | SQL Injection por concatenação | `models.py:45-63`, `107-131`, `287-301` | Valores do cliente são concatenados diretamente em queries. |
| HIGH | God module com múltiplos domínios | `models.py:1-316` | Produtos, usuários, autenticação, pedidos, estoque e relatórios estão acoplados. |
| MEDIUM | Queries N+1 em pedidos | `models.py:173-235` | Cada pedido busca itens e cada item busca novamente o produto. |
| MEDIUM | Validação duplicada | `controllers.py:26-98` | Regras de produto se repetem em criação e atualização. |
| MEDIUM | Tratamento amplo de exceções | `controllers.py:7-294` | Erros internos são expostos e não existe política centralizada. |
| LOW | Magic values | `controllers.py:54-56`, `models.py:258-264` | Categorias e faixas de desconto estão espalhadas. |
| LOW | Logging com `print` | `controllers.py:10-13`, `210-212` | Não há logging estruturado. |

### Projeto 2 — `ecommerce-api-legacy`

| Severidade | Problema | Evidência | Relevância |
|---|---|---|---|
| CRITICAL | Credenciais e chave de pagamento hardcoded | `src/utils.js:1-8` | Segredos ficam expostos no código-fonte. |
| CRITICAL | Cartão e chave do gateway em logs | `src/AppManager.js:45-50` | Expõe dados financeiros sensíveis. |
| HIGH | God Class `AppManager` | `src/AppManager.js:6-143` | A mesma classe cria banco, registra rotas, faz checkout e gera relatórios. |
| MEDIUM | Checkout sem transação | `src/AppManager.js:45-65` | Falhas parciais podem deixar dados inconsistentes. |
| MEDIUM | N+1 no relatório financeiro | `src/AppManager.js:82-130` | Cursos, matrículas, usuários e pagamentos são carregados em cascata. |
| MEDIUM | Callback pyramid e erros inconsistentes | `src/AppManager.js:39-79`, `85-130` | O fluxo é difícil de testar e alguns erros são ignorados. |
| LOW | Variáveis crípticas | `src/AppManager.js:30-35` | Nomes como `u`, `e`, `p`, `cid` e `cc` escondem o domínio. |
| LOW | Estado global mutável | `src/utils.js:11-17` | Cria acoplamento oculto e vazamento entre testes. |

### Projeto 3 — `task-manager-api`

| Severidade | Problema | Evidência | Relevância |
|---|---|---|---|
| CRITICAL | Token previsível | `routes/user_routes.py:187-213` | `fake-jwt-token-<id>` pode ser forjado. |
| HIGH | Secret hardcoded e debug habilitado | `app.py:13-16`, `35-36` | Configuração insegura pode chegar a ambientes não locais. |
| HIGH | Fat controllers | `routes/task_routes.py:13-301`, `routes/user_routes.py:12-213` | Rotas ainda concentram negócio, persistência e serialização. |
| MEDIUM | N+1 na listagem de tarefas | `routes/task_routes.py:13-61` | Cada tarefa pode consultar usuário e categoria separadamente. |
| MEDIUM | API legada do SQLAlchemy | `routes/task_routes.py:44`, `53`, `69`; `routes/user_routes.py:31`, `96` | `Model.query.get()` deve ser avaliado contra a versão instalada e migrado quando aplicável. |
| MEDIUM | Serialização e atraso duplicados | `routes/task_routes.py:18-61`, `67-83`; `routes/user_routes.py:155-185` | A mesma regra aparece em rotas diferentes. |
| LOW | Imports não utilizados | `app.py:9`, `routes/task_routes.py:8-9` | Aumentam ruído e escondem dependências reais. |
| LOW | Magic literals | `routes/task_routes.py:112-116`, `178-185`; `routes/user_routes.py:73-74` | Status, prioridade e roles podem divergir. |

## Construção da Skill

A skill usa um `SKILL.md` como orquestrador e sete referências especializadas:

```text
.codex/skills/refactor-arch/
├── SKILL.md
└── references/
    ├── project-analysis.md
    ├── anti-pattern-catalog.md
    ├── audit-report-template.md
    ├── mvc-guidelines.md
    ├── refactoring-playbook.md
    ├── validation-playbook.md
    └── finding-resolution.md
```

### Decisões de design

1. Três fases sequenciais: análise, auditoria e refatoração.
2. Nenhum arquivo da aplicação pode ser alterado nas Fases 1 e 2.
3. A Fase 2 exige confirmação humana explícita na mesma sessão.
4. A skill não pode copiar os findings desta análise manual; a comparação ocorre somente depois do relatório independente.
5. Todo finding exige severidade, regra, arquivo, linhas, evidência, impacto, recomendação e validação capaz de detectar a causa raiz.
6. O alvo é MVC pragmático: routes/views tratam HTTP, controllers orquestram, services executam workflows, models representam dados e repositories isolam persistência.
7. Projetos parcialmente organizados devem preservar fronteiras úteis, evitando reescrita artificial.
8. Boot e endpoints precisam ser realmente executados; ausência de runtime é bloqueio, não sucesso.
9. Cada execução produz um relatório de auditoria e um arquivo de evidências com comandos, resultados e desvios contratuais.
10. Mover código para uma camada melhor não resolve automaticamente um finding; a causa raiz precisa ser removida e validada.
11. Fluxos com múltiplas escritas relacionadas exigem análise explícita de transação, rollback e efeitos externos após commit.
12. A Fase 3 só pode ser concluída após uma matriz de disposition para todos os findings.

O catálogo contém anti-patterns com severidades distribuídas, incluindo execução arbitrária, segredos hardcoded, password handling inseguro, God Class, fat controllers, transação ausente, efeitos externos antes do commit, N+1, duplicação, exceções genéricas, falta de safety net e APIs deprecated. O playbook contém transformações com exemplos antes/depois e critérios de prova.

## Protocolo de Execução e Validação

Cada projeto deve ser executado em uma branch limpa contendo código legado e a skill, mas sem relatórios ou refatorações previamente produzidos.

Para cada projeto:

1. iniciar uma nova sessão do Codex na raiz do projeto;
2. pedir explicitamente o uso da skill `refactor-arch`;
3. executar somente Fases 1 e 2;
4. confirmar que nenhum arquivo da aplicação mudou;
5. revisar o relatório gerado e registrar quantos achados manuais foram redescobertos;
6. responder `y` ao gate na mesma sessão;
7. deixar a skill executar a Fase 3;
8. exigir boot, validação de endpoints, testes negativos/failure-path e comparação antes/depois;
9. revisar a matriz de disposition e impedir conclusão falsa de findings;
10. revisar `reports/audit-project-N.md` e `reports/execution-project-N.md`;
11. commitar o resultado daquele projeto separadamente.

### Comando de entrada

```bash
cd code-smells-project
codex "Use obrigatoriamente a skill refactor-arch. Execute as Fases 1 e 2, gere o relatório e as evidências, e pare no gate antes da Fase 3."
```

Repetir em `ecommerce-api-legacy` e `task-manager-api`. Após revisar o relatório, responder `y` na própria sessão.

### Critérios de aprovação por projeto

- stack e domínio detectados corretamente;
- pelo menos cinco findings;
- pelo menos um CRITICAL ou HIGH;
- arquivos e linhas exatos;
- detecção de API deprecated quando sustentada pela versão instalada;
- pausa real antes da Fase 3;
- estrutura MVC adequada ao contexto;
- configuração extraída;
- error handling centralizado;
- transações e efeitos externos avaliados quando houver múltiplas escritas;
- application boot aprovado;
- endpoints originais exercitados;
- validações negativas específicas executadas para segurança, rollback e erros;
- mudanças contratuais de segurança documentadas;
- matriz final contendo todos os findings e disposições válidas;
- nenhum CRITICAL/HIGH parcialmente resolvido ou não tratado sem aprovação explícita;
- relatório e evidências gerados pela execução da skill.

## Evolução orientada por evidências

A execução real do Projeto 2 revelou uma lacuna de protocolo: a separação MVC e o smoke test poderiam passar enquanto um risco de consistência transacional permanecia. A skill foi fortalecida para exigir regra própria de atomicidade, testes de falha/rollback e fechamento formal de findings. Essa evolução é uma decisão de Staff/Skill Designer baseada em evidência da execução, não um finding copiado da análise manual durante a auditoria.

Após esta atualização, as três cópias da skill devem permanecer idênticas. O Projeto 2 deve ser reavaliado pela versão consolidada antes do Projeto 3. Projetos já executados podem ser revalidados pela matriz de disposition sem apagar a evidência histórica da versão anterior.

## Estado Atual

- [x] análise manual dos três projetos;
- [x] skill e referências iniciais;
- [x] skill copiada para os três projetos;
- [x] protocolo de integridade e evidência incorporado ao `SKILL.md`;
- [x] protocolo de fechamento de findings, transações e validação negativa incorporado;
- [x] refatorações manuais removidas;
- [x] relatórios não executados removidos;
- [ ] referências das três cópias verificadas como idênticas após a revisão;
- [ ] Projeto 2 reavaliado e corrigido com a versão consolidada;
- [ ] Fases 1 e 2 executadas pelo Codex nos três projetos;
- [ ] Fase 3 executada pela skill nos três projetos;
- [ ] boot, endpoints e finding-specific validations aprovados nos três projetos;
- [ ] relatórios, logs e comparação antes/depois incorporados ao README.

## Resultados

Os resultados finais devem refletir apenas execuções reais. Relatórios históricos podem registrar a evolução da skill, mas a entrega final precisa usar a versão consolidada e indicar os findings resolvidos, parcialmente resolvidos, aceitos ou não tratados.

Os arquivos esperados ao final são:

```text
reports/
├── audit-project-1.md
├── execution-project-1.md
├── audit-project-2.md
├── execution-project-2.md
├── audit-project-3.md
└── execution-project-3.md
```