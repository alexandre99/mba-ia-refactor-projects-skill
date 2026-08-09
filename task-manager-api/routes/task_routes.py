from flask import Blueprint, request

from auth import require_admin
from controllers.response import execute
from controllers.task_controller import (
    create_task as create_task_controller,
)
from controllers.task_controller import (
    delete_task as delete_task_controller,
)
from controllers.task_controller import (
    get_task as get_task_controller,
)
from controllers.task_controller import (
    list_tasks as list_tasks_controller,
)
from controllers.task_controller import (
    search_tasks as search_tasks_controller,
)
from controllers.task_controller import (
    stats as stats_controller,
)
from controllers.task_controller import (
    update_task as update_task_controller,
)

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/tasks", methods=["GET"])
def get_tasks():
    return execute(list_tasks_controller)


@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    return execute(lambda: get_task_controller(task_id))


@task_bp.route("/tasks", methods=["POST"])
def create_task():
    return execute(lambda: create_task_controller(request.get_json(silent=True)), 201)


@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    return execute(lambda: update_task_controller(task_id, request.get_json(silent=True)))


@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@require_admin
def delete_task(task_id):
    return execute(lambda: delete_task_controller(task_id))


@task_bp.route("/tasks/search", methods=["GET"])
def search_tasks():
    return execute(
        lambda: search_tasks_controller(
            request.args.get("q", ""),
            request.args.get("status", ""),
            request.args.get("priority", ""),
            request.args.get("user_id", ""),
        )
    )


@task_bp.route("/tasks/stats", methods=["GET"])
def task_stats():
    return execute(stats_controller)
