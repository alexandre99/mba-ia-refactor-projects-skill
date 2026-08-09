# Refactoring Playbook

Apply in small steps and validate after each structural milestone.

## T-001 — Extract application factory / app builder

Before: module configures dependencies, registers routes, creates schema, and starts the server during import.

After: `create_app()` or `buildApp()` constructs the application; a small server entrypoint starts listening.

```python
# Before
app = App()
db = connect(os.getenv("DB_URL"))
app.register_routes()
db.create_schema()
app.listen(8000)

# After
def create_app(config):
    app = App(config)
    app.register_routes()
    return app

if __name__ == "__main__":
    create_app(load_config()).listen()
```

## T-002 — Replace god module with domain slices

Before: one module handles products, users, orders, reports, database, and notifications.

After: domain-oriented route/controller/service/repository modules with one composition root.

```python
# Before
def handle_order(request):
    user = db.find_user(request.user_id)
    order = db.insert_order(user, request.items)
    send_email(user.email, order)
    return format_order(order)

# After
# routes/orders.py -> controllers/orders.py -> services/orders.py
def create_order(request, order_service):
    return order_service.create(request.user_id, request.items)
```

## T-003 — Extract route registration

Before: dozens of route declarations mixed with configuration and administration logic.

After: blueprints/routers per domain registered by the application factory.

```javascript
// Before
app.get("/users", listUsers);
app.post("/users", createUser);
app.get("/orders", listOrders);
loadAdminConfig();

// After
const userRouter = Router();
userRouter.get("/", listUsers);
userRouter.post("/", createUser);
app.use("/users", userRouter);
```

## T-004 — Move business workflow to service

Before: controller validates stock, calculates totals, updates several tables, and emits notifications.

After: controller parses input; service owns the workflow and explicit transaction boundary; repository owns queries.

```python
# Before
def checkout(request):
    validate_stock(request.items)
    total = calculate_total(request.items)
    repo.save_order(request.user, request.items, total)
    notifier.send(request.user)
    return {"total": total}

# After
def checkout(request, service):
    return service.checkout(request.user, request.items)

class CheckoutService:
    def checkout(self, user, items):
        with self.unit_of_work:
            total = self.policy.total(items)
            order = self.orders.save(user, items, total)
        self.notifier.send(user, order)
        return order
```

Moving a workflow into a service does not resolve missing atomicity. When related writes form one business operation, the service or a dedicated unit-of-work boundary must own commit and rollback.

## T-005 — Extract reusable validation

Before: repeated presence, range, enum, and length checks across create/update handlers.

After: request schema or dedicated validator returns typed/structured validation errors.

```python
# Before
def create(data):
    if not data.get("title") or len(data["title"]) > 120:
        raise ValueError("invalid title")

def update(data):
    if not data.get("title") or len(data["title"]) > 120:
        raise ValueError("invalid title")

# After
def validate_item(data):
    title = data.get("title", "").strip()
    if not title or len(title) > 120:
        return {"title": "must contain 1..120 characters"}
    return {"title": title}
```

## T-006 — Parameterize persistence

Before: request values are interpolated or passed as executable SQL.

After: repository exposes explicit parameterized operations. Remove arbitrary-query endpoints from normal runtime.

```python
# Before
sql = f"SELECT * FROM users WHERE email = '{email}'"
rows = connection.execute(sql)

# After
def find_user_by_email(connection, email):
    return connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()
```

## T-007 — Externalize configuration and secrets

Before: committed secret, fixed debug mode, and environment-specific database path.

After: environment-backed config with safe development defaults and fail-closed production expectations.

```javascript
// Before
const config = { secret: "committed-secret", debug: true, db: ":memory:" };

// After
const config = {
  secret: process.env.APP_SECRET,
  debug: process.env.APP_ENV !== "production",
  db: process.env.DATABASE_PATH || ":memory:"
};
if (process.env.APP_ENV === "production" && (!config.secret || config.db === ":memory:")) {
  throw new Error("unsafe production configuration");
}
```

## T-008 — Centralize error mapping

Before: every handler catches generic exceptions and returns internal text.

After: expected domain/application errors map centrally; unexpected exceptions are logged and return a generic response.

```python
# Before
def route():
    try:
        return do_work()
    except Exception as error:
        return {"error": str(error)}, 500

# After
def route():
    return do_work()  # framework boundary invokes the central mapper

def map_error(error):
    if isinstance(error, DomainError):
        return {"error": error.public_message}, error.status
    logger.exception("unexpected application error")
    return {"error": "internal error"}, 500
```

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
