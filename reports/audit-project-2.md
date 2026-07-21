# Architecture Audit Report — Project 2

## Phase 1 — Project Analysis

- Project: `ecommerce-api-legacy`
- Language: JavaScript
- Runtime: Node.js
- Framework: Express
- Database: in-memory SQLite
- Domain: LMS checkout, enrollment, payment and financial reporting
- Current architecture: bootstrap in `src/app.js`; database schema, routes, checkout workflow and reporting concentrated in `src/AppManager.js`; configuration and mutable global utilities in `src/utils.js`
- Source files reviewed: `src/app.js`, `src/AppManager.js`, `src/utils.js`, `package.json`, `api.http`

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 3 |
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **11** |

## Findings

### [CRITICAL] Production credentials and payment key hardcoded

- File: `src/utils.js:1-8`
- Evidence: database password and a live-looking payment gateway key are embedded in source code.
- Impact: secret exposure through source control, logs and copied environments.
- Recommendation: read secrets from environment/runtime secret management and fail closed when absent.

### [CRITICAL] Sensitive card data and gateway key written to logs

- File: `src/AppManager.js:45-50`
- Evidence: checkout logs the full submitted card value together with the payment gateway key.
- Impact: severe payment-data exposure and credential compromise.
- Recommendation: never log card data or secrets; use tokenized payment-provider inputs and redacted structured logs.

### [CRITICAL] Weak custom password hashing and insecure default password

- File: `src/utils.js:19-24`, `src/AppManager.js:68-74`
- Evidence: `badCrypto` repeatedly encodes Base64 and truncates output; missing passwords default to `123456`.
- Impact: passwords are trivial to recover and accounts may be created with a known credential.
- Recommendation: require a password and hash it with an established adaptive password library.

### [HIGH] God Class owns database, routing and business workflows

- File: `src/AppManager.js:6-143`
- Evidence: `AppManager` initializes schema, seeds data, registers routes, processes payments, enrolls users, builds reports and deletes users.
- Impact: violates SRP, couples every layer and prevents isolated testing.
- Recommendation: split bootstrap, routes/controllers, checkout service and repositories.

### [HIGH] Checkout is non-transactional

- File: `src/AppManager.js:45-65`
- Evidence: enrollment, payment and audit-log inserts are separate asynchronous operations with no transaction or compensation.
- Impact: partial failures can leave enrollment without payment or payment without audit consistency.
- Recommendation: execute the persistence workflow in a transaction and isolate external payment from database state transitions.

### [HIGH] Destructive endpoint has no authentication or authorization

- File: `src/AppManager.js:133-139`
- Evidence: any caller can delete an arbitrary user.
- Impact: unauthorized data deletion and broken authorization boundaries.
- Recommendation: introduce authentication/authorization middleware and an explicit user-deletion use case.

### [MEDIUM] N+1 query pattern in financial report

- File: `src/AppManager.js:82-130`
- Evidence: every course loads enrollments, then each enrollment separately loads its user and payment.
- Impact: query volume grows rapidly with course enrollment counts.
- Recommendation: aggregate with joins or batched queries.

### [MEDIUM] Callback pyramid and fragmented error handling

- File: `src/AppManager.js:39-79`, `src/AppManager.js:85-130`
- Evidence: deeply nested callbacks contain inconsistent error checks; some callback errors are ignored.
- Impact: control flow is difficult to reason about and failures may produce incorrect responses.
- Recommendation: repository methods returning promises, `async/await`, and centralized HTTP error mapping.

### [MEDIUM] Orphan records deliberately retained after user deletion

- File: `src/AppManager.js:133-138`
- Evidence: user deletion does not remove or constrain enrollments and payments.
- Impact: referential inconsistency and misleading financial/reporting data.
- Recommendation: define foreign keys and an intentional cascade, restrict or anonymization policy.

### [LOW] Cryptic variable names obscure checkout behavior

- File: `src/AppManager.js:30-35`
- Evidence: variables such as `u`, `e`, `p`, `cid` and `cc` hide domain meaning.
- Impact: reduces readability and increases maintenance mistakes.
- Recommendation: use domain names such as `userName`, `email`, `courseId` and `paymentToken`.

### [LOW] Mutable global cache and unused revenue state

- File: `src/utils.js:11-17`
- Evidence: process-global mutable cache is changed by utility functions, while `totalRevenue` is exported as global state.
- Impact: hidden coupling, test leakage and multi-process inconsistency.
- Recommendation: inject a cache abstraction and remove unused global state.

## Deprecated API Check

The code uses callback-style SQLite APIs, but static inspection is insufficient to classify them as deprecated. Package versions and official package documentation must be checked during execution before reporting a deprecated API finding.

## Phase Gate

Phase 2 complete. Application files must not be modified until Phase 3 is explicitly approved.
