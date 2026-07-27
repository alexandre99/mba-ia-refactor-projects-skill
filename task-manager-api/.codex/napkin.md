# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead" action.

## Execution & Validation (Highest Priority)
1. **[2026-07-27] Run refactor-arch from the exact target root and stop before Phase 3 without approval.**
   Do instead: confirm `pwd`, stack, and project identity before producing reports.

## Shell & Command Reliability
1. **[2026-07-27] Use `rtk` for shell commands.**
   Do instead: prefix repository inspection and validation commands with `rtk`.

## Domain Behavior Guardrails
1. **[2026-07-27] Preserve the task-manager API contract during analysis.**
   Do instead: record actual routes, statuses, and response shapes before any mutation.

## User Directives
1. **[2026-07-27] Audit only `task-manager-api` and do not modify application code.**
   Do instead: write only the requested reports and stop at the Phase 3 approval gate.
