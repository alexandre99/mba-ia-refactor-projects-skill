# Validation Playbook

## Before refactoring

1. Record startup/install commands and runtime versions.
2. Inventory routes, methods, expected status codes and representative response shapes.
3. Run available tests and boot/smoke checks.
4. Record failures as baseline facts.

## After refactoring

1. Run syntax/static checks.
2. Run unit/integration tests.
3. Start the application with a timeout and wait for readiness.
4. Exercise health plus representative read/write/error endpoints.
5. Compare routes, status codes and response shapes to baseline.
6. Verify intentional security contract changes separately.
7. Stop the spawned process and preserve logs.

Never mark validation complete when commands were not executed. A missing runtime, dependency or unavailable service is a blocker, not a pass.