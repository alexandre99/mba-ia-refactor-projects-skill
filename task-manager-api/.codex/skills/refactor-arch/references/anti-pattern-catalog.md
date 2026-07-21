# Anti-pattern Catalog

Each finding must include severity, rule id, exact file/lines, evidence, impact and recommendation.

| ID | Severity | Anti-pattern | Detection signals |
|---|---|---|---|
| SEC-001 | CRITICAL | Arbitrary SQL/command execution | Request data passed to SQL, shell, eval or dynamic execution. |
| SEC-002 | CRITICAL | Hardcoded secrets | Credentials, tokens, signing keys or live payment keys in source. |
| SEC-003 | CRITICAL | Plaintext/weak password handling | Direct comparison, reversible encoding, weak custom hashing or default passwords. |
| ARCH-001 | CRITICAL/HIGH | God Class/Module | One unit owns routing, persistence, business rules and infrastructure. |
| ARCH-002 | HIGH | Fat Controller | Route/controller performs business workflows, persistence and side effects. |
| ARCH-003 | HIGH | Missing transaction | Multi-step state mutation can partially commit. |
| ARCH-004 | HIGH | Mutable global state | Process-global caches/counters changed across requests. |
| PERF-001 | MEDIUM | N+1 queries | Query inside loops or per-child relationship lookup. |
| QUAL-001 | MEDIUM | Duplicated validation/serialization | Same rule or mapping repeated across handlers. |
| ERR-001 | MEDIUM | Broad/inconsistent error handling | Bare catch/except, ignored callback errors or internal details returned. |
| API-001 | MEDIUM | Deprecated API | Installed dependency version marks API legacy/deprecated and provides replacement. |
| DATA-001 | MEDIUM | Referential inconsistency | Deletes or writes leave orphan records. |
| LOW-001 | LOW | Magic values | Repeated domain strings, thresholds or status lists inline. |
| LOW-002 | LOW | Poor naming/dead imports | Cryptic variables, unused imports or dead state. |

Severity may be raised when exploitability, data loss or architectural blast radius is demonstrated.