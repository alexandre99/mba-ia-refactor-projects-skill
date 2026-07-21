# Validation Playbook

## Before refactoring

1. Confirm runtime versions.
2. Record dependency install command.
3. Inventory routes and representative payloads.
4. Start the app using an isolated local database where supported.
5. Exercise health, one read path, one successful write path, one validation failure, and one not-found path.
6. Record status codes and response shapes.

## After refactoring

Run the same probes and compare:

- startup success;
- endpoint method/path availability;
- status codes;
- JSON field names and nesting;
- persisted side effects;
- expected validation behavior.

## Minimum commands

### Python

- syntax/compile check: `python -m compileall .`
- tests when present: `pytest` or repository command
- boot/smoke: repository validation script

### Node.js

- install: `npm ci` when a lockfile exists, otherwise `npm install`
- tests when present: `npm test`
- boot/smoke: repository validation script

## Failure policy

A timeout, missing runtime, dependency failure, startup crash, or endpoint mismatch is a failed or blocked validation. Include the exact command and relevant error. Do not substitute static inspection for an executed result.
