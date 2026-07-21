# Project Analysis Heuristics

## Detection order

1. Inspect dependency manifests and lockfiles.
2. Inspect entry points and startup scripts.
3. Identify framework imports and route registration.
4. Identify database drivers, ORM models, migrations and schema creation.
5. Inventory source files and endpoints.
6. Infer domain from routes, entities and documentation.
7. Map responsibilities to bootstrap, routes/views, controllers, models, services, repositories, middleware and configuration.

## Evidence rules

- Prefer repository evidence over assumptions.
- Report exact versions only when pinned or resolved.
- Count only relevant source files; exclude dependencies, generated output, caches and databases.
- Mark uncertain conclusions as inferences.

## Architecture classification

Classify the current design as monolithic, partially layered, layered/MVC, or hybrid, and explain the classification using file-level evidence.