# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + `Do instead` action.

## Execution & Validation (Highest Priority)
1. **[2026-07-27] The experiment is in final consolidation, not a new project run.**
   Do instead: inspect and reconcile README/reports only; never rerun refactor-arch phases in this consolidation.
2. **[2026-07-27] Final finding closure must be evidence-backed.**
   Do instead: require one final disposition per finding, preserve contract changes, and record residual risks.

## Shell & Command Reliability
1. **[2026-07-27] Repository shell commands use RTK.**
   Do instead: prefix read-only inspection and final validation commands with `rtk` and record exit codes.
2. **[2026-07-27] Application scope is immutable during consolidation.**
   Do instead: restrict edits to README, reports, runbooks, and other documentation/evidence files.

## Domain Behavior Guardrails
1. **[2026-07-27] Preserve historical execution evidence.**
   Do instead: distinguish baseline, re-evaluation, and final closure sections instead of overwriting prior results.
2. **[2026-07-27] Treat Project 2 as a two-stage experiment.**
   Do instead: explain the post-Project-2 skill evolution and the later transactional re-evaluation separately.

## User Directives
1. **[2026-07-27] Do not modify `code-smells-project`, `ecommerce-api-legacy`, or `task-manager-api`.**
   Do instead: record code inconsistencies without changing application files.
