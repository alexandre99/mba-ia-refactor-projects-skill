---
name: refactor-arch
description: Analyze, audit, refactor, and validate a legacy backend toward an MVC-based architecture while producing reproducible evidence of each phase.
---

# Refactor Architecture

Run this skill from the root of exactly one target application. Execute the phases in order. Never skip the human approval gate or the final finding-closure gate.

## Required references

Read before starting:

1. `references/project-analysis.md`
2. `references/anti-pattern-catalog.md`
3. `references/audit-report-template.md`
4. `references/mvc-guidelines.md`
5. `references/refactoring-playbook.md`
6. `references/validation-playbook.md`
7. `references/finding-resolution.md`

## Integrity rules

- Analyze the application independently. Do not copy findings from the repository README or existing audit reports.
- Treat an existing project audit as stale input: overwrite it only after independently inspecting current source lines.
- Analyze only source, configuration, dependency, migration, and test files relevant to the current application.
- Exclude generated dependencies, virtual environments, build output, databases, caches, and VCS internals.
- Every finding must include severity, rule id, file, exact line range, evidence, impact, recommendation, and finding-specific validation.
- Distinguish observed facts from inferences.
- Never claim a command passed unless it was executed successfully in this run.
- Do not modify application files in Phases 1 or 2.
- Do not use refactoring changes prepared by another agent or prior run as evidence that this skill works.
- Moving code to another folder or layer does not by itself resolve a finding. Resolution requires root-cause removal and finding-specific proof.

## Resolve the project contract

Determine the report and evidence paths from the current directory:

- `code-smells-project` → `../reports/audit-project-1.md` and `../reports/execution-project-1.md`
- `ecommerce-api-legacy` → `../reports/audit-project-2.md` and `../reports/execution-project-2.md`
- `task-manager-api` → `../reports/audit-project-3.md` and `../reports/execution-project-3.md`

If the project does not match one of these names, ask for the report destination before writing files.

## Phase 1 — Project analysis

1. Detect language, runtime, framework, package manager, database, test framework, and startup command from repository evidence.
2. Inventory source files and all public endpoints: method, path, handler, success status, and response shape.
3. Infer the business domain from routes, entities, schemas, and documentation.
4. Map actual responsibilities: bootstrap, routes/views, controllers, models, services, repositories, database, middleware, configuration, transaction ownership, and external effects.
5. Identify multi-step write workflows and record where atomicity, rollback, cache updates, or external effects are owned.
6. Discover the baseline validation command. If none exists, create a deterministic validation plan before application edits; do not modify application files in this phase.
7. Print `PHASE 1: PROJECT ANALYSIS` with the detected stack, domain, architecture, source-file count, endpoint count, startup command, and validation availability.
8. Append the Phase 1 summary and inspected commands to the project execution-evidence file.

Do not modify application files.

## Phase 2 — Architecture audit

1. Apply every relevant rule in `anti-pattern-catalog.md` to the current source.
2. Include deprecated API detection only when repository dependency versions or authoritative local migration evidence support it.
3. Deduplicate findings that share the same root cause, but keep independently actionable consistency, security, or transactional risks separate.
4. Sort findings by severity: CRITICAL, HIGH, MEDIUM, LOW.
5. Generate the project audit using `audit-report-template.md` and save it to the resolved report path.
6. Require at least five findings, including at least one CRITICAL or HIGH. Do not invent LOW or MEDIUM findings merely to satisfy the minimum.
7. For every finding, define validation that can actually detect whether the root cause remains. Happy-path endpoint checks alone are insufficient for security, authorization, atomicity, rollback, error handling, or external-effect findings.
8. Compare the independently generated findings with the README manual analysis only after the report is complete. Record how many manual findings were rediscovered.
9. Append finding totals, report path, rediscovery count, and the exact inspected file/line commands to the execution-evidence file.
10. Print `PHASE 2: ARCHITECTURE AUDIT COMPLETE`.
11. Stop and request explicit confirmation: `Proceed with Phase 3 refactoring? [y/n]`.

Do not modify application source before an affirmative answer in the same Codex session.

## Phase 3 — Refactoring

After explicit approval:

1. Capture the pre-change baseline by running syntax/static checks, booting the application, and exercising every original endpoint when safely possible.
2. Record endpoint paths, methods, status codes, representative response shapes, persisted side effects, and relevant negative/failure behavior before edits.
3. Produce a change plan mapping every selected finding to a transformation from `refactoring-playbook.md`, implementation evidence to create, and finding-specific validation to run.
4. Add or correct the deterministic safety net before application mutations when the current baseline cannot prove behavior.
5. Apply the smallest safe sequence. Preserve useful existing boundaries; do not rewrite a partially organized project merely to make folder names uniform.
6. Keep framework bootstrap in a composition root.
7. Keep HTTP details in routes/views/controllers and persistence details in repositories/data access.
8. Move multi-step business workflows out of route handlers and god classes, with explicit transaction ownership when related writes must be atomic.
9. Externalize secrets and unsafe environment-specific defaults.
10. Keep cache updates, notifications, and other external effects after successful commit unless an outbox or equivalent consistency mechanism is intentionally implemented.
11. Run syntax/static checks, application boot, baseline endpoint validation, and finding-specific negative/failure validations after each relevant structural milestone.
12. Compare post-change behavior against the captured baseline. Document every intentional security-related contract change.
13. Re-run the anti-pattern rules against the final code.
14. Build the mandatory finding-disposition matrix defined in `finding-resolution.md`.
15. A finding may be `RESOLVED` only when the root cause is removed, implementation evidence is cited, and validation capable of detecting regression passed in this run.
16. Use only these dispositions: `RESOLVED`, `PARTIALLY_RESOLVED`, `ACCEPTED_RISK`, `NOT_ADDRESSED`, `NOT_APPLICABLE`.
17. Do not mark the project complete while any CRITICAL or HIGH finding is `PARTIALLY_RESOLVED` or `NOT_ADDRESSED`. `ACCEPTED_RISK` requires explicit human approval and documented rationale.
18. Append files changed, commands, exit codes, endpoint results, finding-specific validation, disposition matrix, intentional deviations, and unresolved risks to the execution-evidence file.
19. Print `PHASE 3: REFACTORING COMPLETE` only when the application boots, the assignment endpoint validation passes, and the finding-closure gate passes.

If validation fails, stop, preserve the failure evidence, report the exact command and error, and do not describe the project as complete.

## Final finding-closure gate

Before declaring completion:

1. Revisit every Phase 2 finding against the final implementation.
2. Verify that the risk was removed rather than merely moved to another file or layer.
3. Run the finding-specific validation recorded in the audit.
4. Produce the disposition matrix with final code evidence and validation evidence.
5. List remaining risks separately from resolved findings.
6. If a required validation cannot be executed, mark the finding `PARTIALLY_RESOLVED` or `NOT_ADDRESSED`; never infer success from code inspection alone.

## Final output

Report:

- detected stack and domain;
- audit report and execution-evidence paths;
- severity totals and manual-finding rediscovery count;
- files changed;
- before/after architecture boundaries;
- validation commands and outcomes;
- intentional contract changes;
- complete finding-disposition matrix;
- remaining risks, blockers, or unverified assumptions.