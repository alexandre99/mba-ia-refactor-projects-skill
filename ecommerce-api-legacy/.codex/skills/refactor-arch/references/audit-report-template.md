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
- Validation: <how the correction will be proven>

## Proposed Phase 3 plan

1. <safe transformation and findings addressed>
2. <safe transformation and findings addressed>

## Contract risks

- <route/status/response behavior that needs preservation or explicit change>

## Approval gate

Proceed with Phase 3 refactoring? [y/n]
```

Rules:

- Never use vague file references.
- Do not count the same root cause repeatedly unless impacts and locations are independently actionable.
- Put security and destructive behavior before style concerns.
- Mention unavailable validation as a risk, not a success.
