# MVC Target Guidelines

## Conceptual boundaries

### Routes / Views

Declare HTTP paths and methods, parse transport-level inputs, invoke a controller, and serialize the response. No SQL and no business workflow.

### Controllers

Coordinate one use case and translate expected application outcomes into transport outcomes. Controllers should be thin and independently testable.

### Models

Represent domain/data concepts and enforce local invariants. Do not let a single model module become the home of unrelated use cases and all queries.

### Services

Own business workflows that span multiple models, repositories, transactions, or external effects.

### Repositories

Own database queries and persistence mapping. Parameterize values and make transaction ownership explicit.

### Composition root

Build the application, load configuration, initialize extensions, and connect routes. Importing modules should not unexpectedly start servers or mutate persistent data.

## Flask target

Prefer an application factory, blueprints, extensions module, domain-oriented controllers/services/repositories, and configuration from environment. Keep compatibility with existing routes.

## Express target

Prefer a small `app` construction module, routers, controllers, services, repositories, middleware, and a separate server entrypoint. Inject or explicitly construct dependencies in one composition root.

## Incremental rule

Do not reorganize a partially layered project merely to match a folder diagram. Preserve useful boundaries and fix responsibility leaks. The quality of dependencies matters more than folder count.
