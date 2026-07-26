# Validation Playbook

## Before refactoring

1. Confirm runtime versions.
2. Record dependency install command.
3. Inventory routes and representative payloads.
4. Start the app using an isolated local database where supported.
5. Exercise health/readiness, one read path, one successful write path, one validation failure, and one not-found path.
6. Record status codes, response shapes, and persisted side effects.
7. Identify findings that require negative or failure-path proof, such as authorization, transaction rollback, exception mapping, concurrency, retries, or external effects.
8. If the existing validator cannot prove the current contract, improve the validation safety net before changing application files.

## After refactoring

Run the same baseline probes and compare:

- startup success;
- endpoint method/path availability;
- status codes;
- JSON field names and nesting;
- persisted side effects;
- expected validation behavior;
- intentional security-related contract changes.

Then run finding-specific validation. General smoke tests are necessary but not sufficient.

## Finding-specific negative validation

### Authorization and destructive actions

- prove unauthorized requests fail closed;
- prove authorized requests succeed when part of the intended contract;
- verify no protected state changed after the denied request.

### Transactions and atomic writes

For every use case with multiple related writes:

1. establish the initial database state;
2. inject or deterministically trigger a failure after at least one write would have occurred;
3. execute the use case;
4. verify every related database change was rolled back;
5. verify cache, notification, publication, or other external effects did not occur;
6. execute the success path and verify commit and post-commit effects.

A happy-path success does not prove atomicity.

### Error handling and data exposure

- trigger expected application errors and unexpected infrastructure errors;
- verify stable status/body mapping;
- verify secrets, SQL text, stack traces, and sensitive values are not returned to clients.

### Query behavior

When N+1 or query-in-loop is a finding, compare query count, query log, executed statement shape, or another repeatable signal before and after when feasible. Response equality alone does not prove the performance finding is resolved.

## Minimum commands

### Python

- syntax/compile check: `python -m compileall .`
- tests when present: `pytest` or repository command
- boot/smoke: repository validation script

### Node.js

- install: `npm ci` when a lockfile exists, otherwise `npm install`
- tests when present: `npm test`
- boot/smoke: repository validation script

## Process and cleanup checks

- use a configurable port when the application supports it;
- terminate spawned processes on success and failure;
- verify no listener or application process remains;
- clean temporary files and isolated databases;
- fail non-zero on timeout, mismatch, malformed response, missing rollback, or cleanup failure.

## Failure policy

A timeout, missing runtime, dependency failure, startup crash, endpoint mismatch, missing rollback, authorization bypass, persisted partial state, external effect before commit, or unavailable required validation is a failed or blocked validation. Include the exact command and relevant error. Do not substitute static inspection for an executed result.

A finding cannot be marked `RESOLVED` when its finding-specific validation failed, was skipped, or could not detect the original root cause.