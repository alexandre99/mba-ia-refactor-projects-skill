from flask import Blueprint, request

from auth import require_admin
from controllers.response import execute
from controllers.user_controller import (
    create_user as create_user_controller,
)
from controllers.user_controller import (
    delete_user as delete_user_controller,
)
from controllers.user_controller import (
    get_user as get_user_controller,
)
from controllers.user_controller import (
    list_users as list_users_controller,
)
from controllers.user_controller import (
    login as login_controller,
)
from controllers.user_controller import (
    update_user as update_user_controller,
)
from controllers.user_controller import (
    user_tasks as user_tasks_controller,
)

user_bp = Blueprint("users", __name__)


@user_bp.route("/users", methods=["GET"])
def get_users():
    return execute(list_users_controller)


@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    return execute(lambda: get_user_controller(user_id))


@user_bp.route("/users", methods=["POST"])
def create_user():
    return execute(lambda: create_user_controller(request.get_json(silent=True)), 201)


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    return execute(lambda: update_user_controller(user_id, request.get_json(silent=True)))


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@require_admin
def delete_user(user_id):
    return execute(lambda: delete_user_controller(user_id))


@user_bp.route("/users/<int:user_id>/tasks", methods=["GET"])
def get_user_tasks(user_id):
    return execute(lambda: user_tasks_controller(user_id))


@user_bp.route("/login", methods=["POST"])
def login():
    return execute(lambda: login_controller(request.get_json(silent=True)))
