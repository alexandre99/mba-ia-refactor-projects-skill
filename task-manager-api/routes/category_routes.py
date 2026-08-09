from flask import Blueprint, request

from auth import require_admin
from controllers.category_controller import (
    create_category as create_category_controller,
)
from controllers.category_controller import (
    delete_category as delete_category_controller,
)
from controllers.category_controller import (
    list_categories as list_categories_controller,
)
from controllers.category_controller import (
    update_category as update_category_controller,
)
from controllers.response import execute

category_bp = Blueprint("categories", __name__)


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    return execute(list_categories_controller)


@category_bp.route("/categories", methods=["POST"])
def create_category():
    return execute(lambda: create_category_controller(request.get_json(silent=True)), 201)


@category_bp.route("/categories/<int:cat_id>", methods=["PUT"])
def update_category(cat_id):
    return execute(lambda: update_category_controller(cat_id, request.get_json(silent=True)))


@category_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
@require_admin
def delete_category(cat_id):
    return execute(lambda: delete_category_controller(cat_id))
