# Finding Resolution Protocol

Use this protocol after Phase 3 implementation and before declaring the project complete.

## Finding lifecycle

`OBSERVED → PLANNED → IMPLEMENTED → VALIDATED → RESOLVED`

A code change is not the same as a resolved finding. A finding reaches `RESOLVED` only when all required closure evidence exists.

## Allowed dispositions

- `RESOLVED`: root cause removed and finding-specific validation passed in this run.
- `PARTIALLY_RESOLVED`: meaningful improvement exists, but root cause, coverage, or proof remains incomplete.
- `ACCEPTED_RISK`: risk intentionally remains with explicit human approval, rationale, scope, and compensating controls.
- `NOT_ADDRESSED`: no effective correction was implemented.
- `NOT_APPLICABLE`: later evidence proves the original finding does not apply; explain why.

## Closure criteria

A finding may be marked `RESOLVED` only when all are true:

1. Root cause removal: the audited behavior no longer exists in the reachable final implementation.
2. Final code evidence: exact final file and line references show the correction.
3. Finding-specific validation: a test or executable probe capable of detecting the original failure passed in this run.
4. No risk relocation: the same defect was not merely moved to another controller, service, repository, middleware, or helper.
5. Remaining-risk review: limitations and intentional contract changes are documented.

Static inspection alone cannot close findings whose failure mode is behavioral, including authorization, transactions, rollback, persistence side effects, exception mapping, retries, concurrency, or external effects.

## Validation expectations by finding type

- Authorization/security: prove unauthorized failure and authorized success where applicable.
- Atomicity/transactions: force a failure after an earlier write and prove every related write was rolled back.
- External effects/cache: prove the effect is absent after rollback and occurs only after commit.
- Error handling: trigger expected and unexpected failures; prove stable status/body behavior and no sensitive leakage.
- N+1/performance: prove query-count reduction or inspect an executed query plan/query log when feasible, while preserving response behavior.
- Structural findings: cite final boundaries and run behavior checks proving the extraction did not break the contract.
- Deprecated APIs: execute the supported replacement and relevant tests under the installed dependency version.

## Mandatory disposition matrix

Add this table to the final audit or execution report:

| Finding | Disposition | Final implementation evidence | Validation evidence | Remaining risk |
|---|---|---|---|---|
| `<RULE-ID and title>` | `<allowed disposition>` | `<path:lines and explanation>` | `<command/test/probe and result>` | `<none or explicit limitation>` |

Every Phase 2 finding must appear exactly once.

## Completion policy

- Any CRITICAL or HIGH finding marked `PARTIALLY_RESOLVED` or `NOT_ADDRESSED` blocks project completion.
- `ACCEPTED_RISK` for CRITICAL or HIGH requires explicit human approval after the final matrix is presented.
- MEDIUM or LOW remaining findings do not automatically block completion, but must be visible in the final output.
- Failed or unavailable finding-specific validation prevents `RESOLVED` status.
- Passing the general endpoint smoke test does not override a failed finding-specific validation.