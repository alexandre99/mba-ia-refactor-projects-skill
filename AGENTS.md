# AGENTS.md

## Mission

Implement and validate the `refactor-arch` Codex skill for the three legacy applications in this repository.

The skill must analyze the project, produce an evidence-based audit, pause before mutations, refactor toward MVC, and prove that observable behavior still works.

## Repository targets

- `code-smells-project/`: Python + Flask e-commerce API.
- `ecommerce-api-legacy/`: Node.js + Express LMS/checkout API.
- `task-manager-api/`: Python + Flask task manager with partial layering.

## Non-negotiable workflow

1. Inventory the target before changing it: runtime, framework, database, source files, startup command, and HTTP endpoints.
2. Establish a baseline using the target validation script.
3. Run Phase 1 and Phase 2 of `refactor-arch`.
4. Save the audit under `reports/` with exact file and line evidence.
5. Do not edit application files before explicit approval for Phase 3.
6. Preserve routes, status codes, and response shapes unless a documented security fix requires a deliberate contract change.
7. Refactor in small, reversible steps.
8. Run boot and endpoint validation after refactoring.
9. Report failed checks honestly. Never claim validation that was not executed.

## Architecture policy

MVC is the required target vocabulary, but it must not create fat controllers or active-record god models.

- Routes/Views: HTTP transport, request parsing, response mapping.
- Controllers: orchestration of a use case; no raw SQL and no framework bootstrap.
- Models: domain/data representation and invariants.
- Services: business workflows spanning models or external effects.
- Repositories: persistence and query implementation.
- Config/Composition root: environment, dependency wiring, app startup.

Existing good boundaries should be retained. Refactoring is incremental, not a forced rewrite.

## Security baseline

Treat the following as release blockers when reachable in normal execution:

- arbitrary SQL or command execution;
- hardcoded production credentials or secrets;
- plaintext password storage or comparison;
- debug mode exposed by default;
- destructive unauthenticated administration endpoints;
- unsafe dynamic query construction;
- sensitive exception details returned to clients.

## Validation contract

Each target must have a deterministic script under `scripts/validation/` that:

- checks runtime and dependencies;
- uses an isolated temporary database when possible;
- starts the application on a configurable local port;
- waits for readiness with a timeout;
- exercises health and representative domain endpoints;
- terminates the spawned process;
- exits non-zero on failure.

If dependencies cannot be installed or the runtime is unavailable, record the exact blocker and do not mark the target as validated.

## Change discipline

- Do not combine refactoring of multiple target projects in one commit.
- Keep generated audit reports separate from application refactors when practical.
- Do not delete legacy behavior merely because it looks odd; first capture it in the baseline.
- Avoid broad formatting-only changes.
- Do not add AI attribution banners or fabricated human-authorship claims.
