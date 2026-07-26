# Refactoring Playbook

Apply in small steps and validate after each structural milestone.

## T-001 — Extract application factory / app builder

Before: module configures dependencies, registers routes, creates schema, and starts the server during import.

After: `create_app()` or `buildApp()` constructs the application; a small server entrypoint starts listening.

## T-002 — Replace god module with domain slices

Before: one module handles products, users, orders, reports, database, and notifications.

After: domain-oriented route/controller/service/repository modules with one composition root.

## T-003 — Extract route registration

Before: dozens of route declarations mixed with configuration and administration logic.

After: blueprints/routers per domain registered by the application factory.

## T-004 — Move business workflow to service

Before: controller validates stock, calculates totals, updates several tables, and emits notifications.

After: controller parses input; service owns the workflow and explicit transaction boundary; repository owns queries.

Moving a workflow into a service does not resolve missing atomicity. When related writes form one business operation, the service or a dedicated unit-of-work boundary must own commit and rollback.

## T-005 — Extract reusable validation

Before: repeated presence, range, enum, and length checks across create/update handlers.

After: request schema or dedicated validator returns typed/structured validation errors.

## T-006 — Parameterize persistence

Before: request values are interpolated or passed as executable SQL.

After: repository exposes explicit parameterized operations. Remove arbitrary-query endpoints from normal runtime.

## T-007 — Externalize configuration and secrets

Before: committed secret, fixed debug mode, and environment-specific database path.

After: environment-backed config with safe development defaults and fail-closed production expectations.

## T-008 — Centralize error mapping

Before: every handler catches generic exceptions and returns internal text.

After: expected domain/application errors map centrally; unexpected exceptions are logged and return a generic response.

## T-009 — Isolate external effects

Before: handlers print simulated email/SMS/push actions or update cache before durable state is confirmed.

After: notifier/cache/publication boundary is invoked only after successful commit, or through an outbox/idempotent mechanism with explicit validation.

## T-010 — Introduce behavioral smoke tests

Before: architecture is changed without an executable contract.

After: deterministic boot and endpoint checks run before and after changes, with intentional differences documented.

## T-011 — Introduce transactional unit of work

Before: one use case performs multiple related writes sequentially; partial failure leaves committed intermediate state.

After: the use case executes related writes inside an explicit transaction or unit of work. Commit happens only after all writes succeed; any failure triggers rollback.

Required proof: inject or trigger an intermediate failure and verify no partial database state or post-commit external effect remains.

## T-012 — Add finding-specific regression validation

Before: only the successful HTTP path is tested, so the original audited defect can remain undetected.

After: each security, consistency, transaction, error-handling, or performance finding has an executable check capable of detecting its original root cause.

## Transformation safeguards

- First move behavior without changing it; then correct security defects explicitly.
- Avoid changing response envelopes during extraction.
- Preserve transaction boundaries or strengthen them intentionally.
- Keep external effects after commit unless an explicit consistency mechanism replaces that order.
- Do not mark a finding resolved merely because code moved into a more appropriate folder.
- Re-run finding-specific validation before assigning the final disposition.
- Keep each commit focused on one target project or one shared skill concern.