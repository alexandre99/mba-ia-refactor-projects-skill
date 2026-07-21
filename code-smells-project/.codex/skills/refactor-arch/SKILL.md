---
name: refactor-arch
description: Analyze, audit, refactor, and validate a legacy backend toward an MVC-based architecture without silently changing its public behavior.
---

# Refactor Architecture

Use this skill from the root of one target application. Execute the phases in order. Never skip the approval gate.

## Required references

Read before starting:

1. `references/project-analysis.md`
2. `references/anti-pattern-catalog.md`
3. `references/audit-report-template.md`
4. `references/mvc-guidelines.md`
5. `references/refactoring-playbook.md`
6. `references/validation-playbook.md`

## Global rules

- Analyze only source, configuration, dependency, migration, and test files relevant to the application.
- Exclude generated dependencies, virtual environments, build output, databases, caches, and VCS internals.
- Every finding must include severity, rule id, file, exact line range, evidence, impact, and recommendation.
- Distinguish observed facts from inferences.
- Preserve endpoint paths, methods, status codes, and response shapes unless a security correction requires an explicit breaking change.
- Never claim a command passed unless it was executed successfully.
- Do not change application files in Phases 1 or 2.

## Phase 1 — Project analysis

1. Detect language, runtime, framework, package manager, database, test framework, and startup command.
2. Inventory source files and public endpoints.
3. Infer the business domain from route names, entities, schemas, and documentation.
4. Map current responsibilities: bootstrap, routes/views, controllers, models, services, repositories, database, middleware, configuration.
5. Identify the baseline validation command or explain why none exists.
6. Print a concise `PHASE 1: PROJECT ANALYSIS` summary.

Do not modify files.

## Phase 2 — Architecture audit

1. Apply every relevant rule in `anti-pattern-catalog.md`.
2. Include deprecated API detection based on the installed dependency versions and official migration signals available in the repository.
3. Deduplicate findings that share the same root cause.
4. Sort by severity: CRITICAL, HIGH, MEDIUM, LOW.
5. Save the report to the project-specific path requested by the repository assignment.
6. Print finding counts and the report path.
7. Stop and request explicit confirmation: `Proceed with Phase 3 refactoring? [y/n]`.

Do not modify application files before an affirmative answer.

## Phase 3 — Refactoring

After approval:

1. Capture or run the pre-change baseline.
2. Produce a short change plan mapping findings to transformations.
3. Apply the smallest safe sequence from `refactoring-playbook.md`.
4. Keep framework bootstrap in a composition root.
5. Keep HTTP details in routes/controllers and persistence details in repositories/data access.
6. Move business workflows out of route handlers and god classes.
7. Externalize secrets and unsafe environment-specific defaults.
8. Add or update tests and smoke validation where needed.
9. Run syntax/static checks, boot validation, and endpoint smoke tests.
10. Compare public behavior to the baseline and document intentional deviations.
11. Print `PHASE 3: REFACTORING COMPLETE` only when required validation passes.

If validation fails, stop, report the exact command and error, and do not describe the work as complete.

## Final output

Report:

- detected stack and domain;
- audit report path and severity totals;
- files changed;
- new architecture boundaries;
- validation commands and outcomes;
- intentional contract changes;
- unresolved risks or blockers.
