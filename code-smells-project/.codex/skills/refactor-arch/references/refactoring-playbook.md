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

After: controller parses input; service owns the workflow and transaction; repository owns queries.

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

Before: handlers print simulated email/SMS/push actions.

After: notifier interface/service invoked after successful business state transition; test double used in validation.

## T-010 — Introduce behavioral smoke tests

Before: architecture is changed without an executable contract.

After: deterministic boot and endpoint checks run before and after changes, with intentional differences documented.

## Transformation safeguards

- First move behavior without changing it; then correct security defects explicitly.
- Avoid changing response envelopes during extraction.
- Preserve transaction boundaries or strengthen them intentionally.
- Keep each commit focused on one target project or one shared skill concern.
