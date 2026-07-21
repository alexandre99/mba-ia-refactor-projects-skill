# MVC Target Guidelines

MVC is the assignment vocabulary, but boundaries must remain testable.

- **Routes/Views:** declare endpoints, parse transport input, call controllers and map HTTP responses.
- **Controllers:** orchestrate one use case; no raw SQL, schema bootstrap or external provider implementation.
- **Models:** represent domain/data structures and local invariants; avoid framework request/response objects.
- **Services:** own workflows spanning multiple models, repositories or side effects.
- **Repositories/Data access:** own SQL, ORM queries and persistence mapping.
- **Configuration/composition root:** load environment, create dependencies, register routes and start the app.
- **Error middleware:** map known application errors to stable HTTP contracts.

Rules:

1. Preserve good existing boundaries.
2. Prefer dependency injection over hidden globals.
3. Keep public route contracts stable unless a documented security fix requires a deliberate change.
4. Do not replace a god class with a fat controller or active-record god model.
5. Refactor incrementally and validate after each boundary change.