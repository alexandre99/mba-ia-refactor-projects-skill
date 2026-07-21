# Anti-pattern Catalog

Use stable rule IDs in reports.

## CRITICAL

### SEC-001 — Arbitrary command or SQL execution

Signals: request-controlled input passed directly to SQL execution, shell, eval, template execution, or dynamic module loading.

Impact: data loss, data disclosure, remote code execution, or full application compromise.

### SEC-002 — Exposed destructive administration

Signals: unauthenticated routes that reset databases, delete broad datasets, change authorization, or expose unrestricted administration.

Impact: catastrophic integrity or availability failure.

### SEC-003 — Hardcoded usable credentials or secrets

Signals: committed secret keys, passwords, tokens, private keys, or production connection strings.

Use HIGH instead when the value is clearly a development-only placeholder with no privileged effect.

## HIGH

### ARCH-001 — God class or god module

Signals: one class/module owns routing, persistence, business rules, validation, configuration, and external effects; excessive size and unrelated domains strengthen the finding.

### ARCH-002 — Business logic in routes/controllers

Signals: handlers calculate prices, stock, authorization, order state, reports, or multi-step workflows rather than delegating orchestration.

### ARCH-003 — Persistence coupled to transport

Signals: route/controller executes raw SQL, opens transactions, or depends directly on database cursors.

### SEC-004 — Insecure password handling

Signals: plaintext storage/comparison, reversible password encryption, password logging, or returning password fields.

### OPS-001 — Unsafe runtime defaults

Signals: debug mode enabled by default, broad CORS without rationale, development server used as production contract, fixed sensitive configuration.

## MEDIUM

### DATA-001 — Dynamic query construction

Signals: string concatenation/interpolation for filters or SQL fragments, even when current inputs seem constrained.

### PERF-001 — N+1 or query-in-loop

Signals: repeated per-item queries where a join, batch query, or prefetch is available.

### QUAL-001 — Duplicated validation/business rules

Signals: repeated field checks, category/status lists, response mapping, or transaction rules across handlers.

### ERR-001 — Generic exception leakage

Signals: broad `except Exception`/`catch (err)` returning raw exception text to clients or treating all failures as HTTP 500.

### DEP-001 — Deprecated or obsolete API

Signals: APIs marked deprecated by the framework/library version, removed migration paths, or legacy calls with a documented replacement. Include installed version evidence and the modern equivalent. Do not flag based on memory alone when repository evidence is insufficient.

### TEST-001 — Missing behavioral safety net

Signals: no tests or smoke validation for startup and representative endpoints before structural changes.

## LOW

### QUAL-002 — Magic values and scattered constants

Signals: repeated status lists, category lists, ports, limits, or messages embedded in handlers.

### QUAL-003 — Misleading names or boundary names

Signals: modules named model/controller/service whose actual responsibility materially differs.

### QUAL-004 — Dead imports, prints, and debugging residue

Signals: unused imports, ad-hoc prints, unreachable code, and temporary diagnostics.

### QUAL-005 — Inconsistent response construction

Signals: repeated but divergent success/error envelopes and status mapping without a central policy.

## Severity adjustment

Raise severity when the code is reachable, externally controllable, destructive, or repeated across domains. Lower severity only when evidence proves the code is unreachable, test-only, or safely constrained. Explain every adjustment.
