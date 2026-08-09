# Audit Report Template

```markdown
# Architecture Audit Report — <project>

## Project profile

- Stack: <language, runtime, framework>
- Database: <database>
- Domain: <domain>
- Source files analyzed: <count>
- Public endpoints: <count>
- Baseline status: <passed, failed, unavailable>

## Executive summary

CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

<short risk summary and recommended refactoring order>

## Findings

### [<SEVERITY>] <RULE-ID> — <title>

- File: `<path>:<start>-<end>`
- Evidence: <specific observed code behavior>
- Impact: <technical/business effect>
- Recommendation: <concrete target boundary or correction>
- Validation: <executable proof capable of detecting whether the root cause remains>

## Proposed Phase 3 plan

1. <safe transformation, findings addressed, implementation evidence, and validation>
2. <safe transformation, findings addressed, implementation evidence, and validation>

## Contract risks

- <route/status/response behavior that needs preservation or explicit change>

## Approval gate

Proceed with Phase 3 refactoring? [y/n]

## Final finding disposition

| Finding | Disposition | Final implementation evidence | Validation evidence | Remaining risk |
|---|---|---|---|---|
| `<RULE-ID and title>` | `<RESOLVED, PARTIALLY_RESOLVED, ACCEPTED_RISK, NOT_ADDRESSED, NOT_APPLICABLE>` | `<path:lines and explanation>` | `<command/test/probe and result>` | `<none or limitation>` |
```

Rules:

- Never use vague file references.
- Do not count the same root cause repeatedly unless impacts and locations are independently actionable.
- Keep missing atomicity separate from controller/service placement when each is independently actionable.
- Put security and destructive behavior before style concerns.
- Mention unavailable validation as a risk, not a success.
- The final disposition section is completed only after Phase 3 and must contain every Phase 2 finding exactly once.
- Do not use `RESOLVED` without final code evidence and finding-specific validation evidence.