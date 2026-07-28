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

1. análise manual inicial, mantida no histórico do README e usada somente para comparação posterior;
2. execução da versão corrente da `refactor-arch` nas Fases 1 e 2, com inventário e auditoria independente;
3. gate explícito de aprovação humana e Fase 3 incremental, com preservação de rotas, status e shapes salvo correção de segurança documentada;
4. validação final por aplicação e matriz de disposition, incluindo provas específicas para segurança, transação, rollback, erros, efeitos externos e N+1 quando aplicável.

A skill usa um `SKILL.md` e sete referências especializadas: `project-analysis.md`, `anti-pattern-catalog.md`, `audit-report-template.md`, `mvc-guidelines.md`, `refactoring-playbook.md`, `validation-playbook.md` e `finding-resolution.md`. As cópias completas ficam em `.codex/skills/refactor-arch/` dentro de cada projeto.

## Evolução da skill após o Projeto 2

A primeira execução do Projeto 2 mostrou que separar rotas, controllers, services e repositories e passar no smoke test não prova atomicidade. O checkout ainda podia deixar escritas parciais sem que a validação detectasse o defeito.

Com base nessa evidência, a skill foi fortalecida para:

- tratar `DATA-002` como regra independente de fronteiras arquiteturais;
- exigir uma unidade transacional explícita para escritas relacionadas;
- exigir falha injetada, rollback verificável e efeitos externos somente após commit;
- exigir validação específica para findings de segurança, consistência, erro e performance;
- exigir matriz final completa antes de declarar conclusão.

As três cópias da skill e de suas referências foram então mantidas sincronizadas. O Projeto 2 foi reavaliado pela versão consolidada antes da execução final do Projeto 3.

## Execução dos três projetos

| Projeto | Execução final registrada | Findings da matriz final | Resultado documentado |
|---|---|---:|---|
| 1 — `code-smells-project` | [audit](reports/audit-project-1.md) e [execution](reports/execution-project-1.md) | 16 | 12 `RESOLVED`; 4 `PARTIALLY_RESOLVED` MEDIUM/LOW (`PERF-001`, `ERR-001`, `QUAL-004`, `QUAL-005`) |
| 2 — `ecommerce-api-legacy` | reavaliação consolidada em [audit](reports/audit-project-2.md) e [execution](reports/execution-project-2.md) | 5 atuais | 4 `RESOLVED`; 1 `PARTIALLY_RESOLVED` de baixa severidade (`QUAL-005`) |
| 3 — `task-manager-api` | [audit](reports/audit-project-3.md) e [execution](reports/execution-project-3.md) | 11 | 11 `RESOLVED` |

Os números do Projeto 2 são da reavaliação final. O mesmo relatório preserva, antes dela, a auditoria e a execução históricas do primeiro ciclo; findings históricos não são contados novamente na linha final.

### Projeto 1 — e-commerce Python/Flask

O baseline executou os 19 paths originais em SQLite descartável. A Fase 3 criou composição configurável, services e repositories, parametrizou as consultas, limitou as operações administrativas, removeu segredos do health check, aplicou hashing de senha, centralizou erros e ampliou a validação. A validação final registrada cobriu os 19 paths e probes de segurança; boot, endpoints e cleanup passaram com exit code 0.

As mudanças contratuais intencionais foram: `/health` não expõe segredo/debug/path; respostas de usuário não expõem `senha`; reset administrativo exige token; e `/admin/query` aceita somente a consulta allowlisted. O risco residual documentado é a divergência histórica de envelopes de erro (`QUAL-005`), além da necessidade operacional de usar WSGI em produção.

### Projeto 2 — LMS/checkout Node.js/Express

O primeiro ciclo removeu segredos, hashing inseguro, god module, acoplamento HTTP/SQLite e N+1 no relatório, preservando os contratos observados. A reavaliação pela skill consolidada encontrou cinco itens atuais: transação ausente, default de storage inseguro em produção, safety net sem prova de rollback, magic values e respostas legadas divergentes.

A correção final adicionou unidade transacional no checkout, rollback após falha intermediária, cache somente depois do commit, guard de storage durável em produção, probes específicos e constantes de checkout. O validator padrão e o validator em porta configurável passaram com exit code 0. `QUAL-005` permanece parcialmente resolvido por compatibilidade: falhas textuais, sucesso JSON e relatório em array continuam distintos. O relatório também registra os avisos de auditoria de dependências do npm e o risco de relatório financeiro público como limitações fora do escopo corretivo final.

### Projeto 3 — task manager Python/Flask

O baseline primeiro registrou a limitação do validator original (`python` indisponível e cobertura insuficiente); depois uma virtualenv isolada permitiu a validação completa dos 22 padrões de rota. Após aprovação, a Fase 3 adicionou configuração por ambiente, application factory, WSGI, tokens assinados, autorização administrativa, hashing de senha, controllers/services/repositories, validação centralizada, carregamento sem N+1 e seed transacional.

As validações finais passaram em portas 5000 e 5053, incluindo boot, todos os endpoints, 401 anônimo, 200 autorizado, rollback, seed, contagem de queries, Ruff, compileall e guards de produção. Nenhum finding permaneceu parcial ou não tratado. Mudanças de segurança documentadas: DELETE passou a exigir autorização; tokens passaram a ser assinados; respostas não expõem `password`; e produção exige segredo e WSGI.

## Resultados consolidados

Nas matrizes finais atuais há 32 findings distintos entre os três escopos: 27 `RESOLVED` e 5 `PARTIALLY_RESOLVED`, todos MEDIUM/LOW. Não há `CRITICAL` ou `HIGH` com disposition `PARTIALLY_RESOLVED` ou `NOT_ADDRESSED`. Não há `ACCEPTED_RISK` sem aprovação explícita registrada.

Os contratos não relacionados a segurança foram preservados nos três projetos: paths, métodos, status de sucesso e shapes observados nos baselines. As exceções estão listadas nos relatórios de execução e nas seções de mudanças contratuais acima.

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

## Validações da consolidação final — 2026-07-27

Foram executadas somente verificações documentais e de consistência:

- `rtk git diff --check`: exit 0;
- `rtk diff -rq` entre cada par das três cópias completas da skill: exit 0;
- existência dos seis relatórios, 24 arquivos de skill/referência (oito em cada cópia) e três READMEs dos projetos: exit 0;
- links locais do README apontando para os seis relatórios: exit 0;
- matrizes finais: exit 0, com 16, 5 e 11 rows respectivamente;
- busca por whitespace final, checklist pendente e frases obsoletas do Projeto 3: exit 1 em cada busca, interpretação esperada de “nenhuma ocorrência”;
- busca específica por `CRITICAL`/`HIGH` parcial ou não tratado: exit 1, sem ocorrência;
- `git status --short`: somente README, relatórios e `.codex/napkin.md` modificados.

Nenhuma aplicação, validator de projeto, boot, endpoint ou fase da skill foi executado nesta consolidação.

## Estado final do experimento

- [x] análise manual e metodologia documentadas;
- [x] Fases 1 e 2 executadas nos três projetos;
- [x] aprovação humana e Fase 3 executadas nos três projetos;
- [x] Projeto 2 reavaliado após a evolução da skill;
- [x] boot, endpoints e validações específicas registradas;
- [x] dispositions finais revisadas e riscos residuais registrados;
- [x] README e relatórios consolidados;
- [x] três cópias da skill verificadas como sincronizadas.
