# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + `Do instead:` action.

## Execution & Validation (Highest Priority)
1. **[2026-07-21] Refactor audits require independent current-source evidence**
   Do instead: inspect exact current lines, execute commands, and record exit codes before comparing prior analyses.

## Shell & Command Reliability
1. **[2026-07-21] Repository instructions require RTK command prefixes**
   Do instead: prefix shell commands with `rtk` and preserve the exact command and exit code in evidence.

## Domain Behavior Guardrails
1. **[2026-07-21] Phase 1/2 must not alter application behavior**
   Do instead: write only audit/evidence artifacts and stop at the Phase 3 approval gate.

## User Directives
1. **[2026-07-21] Run only Fases 1 e 2 independently for ecommerce-api-legacy**
   Do instead: generate the two project-2 reports, run baseline when possible, and request explicit Phase 3 approval.
