from pathlib import Path
from sqlalchemy import event

from app import create_app
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from repositories.unit_of_work import UnitOfWork
from seed import seed_data
from services.category_service import CategoryService
from services.report_service import ReportService
from services.task_service import TaskService
from services.user_service import UserService
from utils.errors import ApplicationError


app = create_app(
    {
        "TESTING": True,
        "SECRET_KEY": "validation-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "CORS_ORIGINS": [],
    }
)


def count(model):
    return db.session.query(model).count()


def check_security_contract(client, admin):
    response = client.post(
        "/users",
        json={
            "name": "Response User",
            "email": "response@example.com",
            "password": "pass1234",
        },
    )
    assert response.status_code == 201
    created = response.get_json()
    assert "password" not in created
    created_user = db.session.get(User, created["id"])
    assert len(created_user.password) > 32
    assert created_user.check_password("pass1234")

    login = client.post("/login", json={"email": admin.email, "password": "admin-pass"})
    assert login.status_code == 200
    login_body = login.get_json()
    assert "password" not in login_body["user"]
    admin_headers = {"Authorization": f"Bearer {login_body['token']}"}

    target_task = Task(title="Protected task", user_id=created_user.id)
    target_category = Category(name="Protected category")
    db.session.add_all([target_category, target_task])
    db.session.commit()
    target_task.category_id = target_category.id
    db.session.commit()

    before = (count(User), count(Task), count(Category))
    for path in (
        f"/tasks/{target_task.id}",
        f"/categories/{target_category.id}",
        f"/users/{created_user.id}",
    ):
        denied = client.delete(path)
        assert denied.status_code == 401, (path, denied.status_code)
    assert before == (count(User), count(Task), count(Category))

    for path in (
        f"/tasks/{target_task.id}",
        f"/categories/{target_category.id}",
        f"/users/{created_user.id}",
    ):
        allowed = client.delete(path, headers=admin_headers)
        assert allowed.status_code == 200, (path, allowed.status_code)


def check_transaction_rollback(admin):
    victim = User(name="Rollback User", email="rollback@example.com", role="user")
    victim.set_password("rollback-pass")
    db.session.add(victim)
    db.session.flush()
    task = Task(title="Rollback task", user_id=victim.id)
    db.session.add(task)
    db.session.commit()

    class FailingUnitOfWork(UnitOfWork):
        def commit(self):
            db.session.flush()
            raise RuntimeError("injected failure after delete flush")

    try:
        UserService(FailingUnitOfWork()).delete_user(victim.id)
    except ApplicationError as exc:
        assert exc.status_code == 500
    else:
        raise AssertionError("failure injection did not fail")
    assert db.session.get(User, victim.id) is not None
    assert db.session.query(Task).filter_by(user_id=victim.id).count() == 1


def check_query_scaling():
    counts = {"task": 0, "report": 0, "category": 0}
    active = None

    def before_execute(*_args):
        if active:
            counts[active] += 1

    event.listen(db.engine, "before_cursor_execute", before_execute)
    try:
        active = "task"
        TaskService().list_tasks()
        active = "report"
        ReportService().summary()
        active = "category"
        CategoryService().list_categories()
    finally:
        event.remove(db.engine, "before_cursor_execute", before_execute)
    assert counts["task"] <= 2, counts
    assert counts["report"] <= 8, counts
    assert counts["category"] <= 2, counts
    return counts


def check_seed_transaction():
    import seed

    seed.app = app
    before = (count(User), count(Category), count(Task))
    failure = {"enabled": True}

    def fail_after_flush(_session, _context):
        if failure["enabled"]:
            raise RuntimeError("injected seed failure after flush")

    event.listen(db.session, "after_flush", fail_after_flush)
    try:
        try:
            seed_data()
        except RuntimeError as exc:
            assert "injected seed failure" in str(exc)
        else:
            raise AssertionError("seed failure injection did not fail")
    finally:
        event.remove(db.session, "after_flush", fail_after_flush)
        failure["enabled"] = False
    assert before == (count(User), count(Category), count(Task))
    assert Path("seed.py").read_text().count("db.session.commit()") == 1


with app.app_context():
    db.create_all()
    admin = User(name="Admin", email="admin@example.com", role="admin")
    admin.set_password("admin-pass")
    member = User(name="Member", email="member@example.com", role="user")
    member.set_password("member-pass")
    category = Category(name="Initial category")
    db.session.add_all([admin, member, category])
    db.session.flush()
    db.session.add(Task(title="Initial task", user_id=member.id, category_id=category.id))
    db.session.commit()

    client = app.test_client()
    check_security_contract(client, admin)
    check_transaction_rollback(admin)
    query_counts = check_query_scaling()
    check_seed_transaction()
    print(f"FINDING-SPECIFIC: security, password, rollback, seed, and query checks passed {query_counts}")
