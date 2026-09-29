from flask import Blueprint

from controllers.category_controller import (
    get_categories,
    get_category,
    create_new_category,
    edit_category,
    remove_category
)

from utils.auth_utils import role_required


category_bp = Blueprint("categories", __name__)


@category_bp.route("", methods=["GET"])
def get_categories_route():
    return get_categories()


@category_bp.route("/<int:category_id>", methods=["GET"])
def get_category_route(category_id):
    return get_category(category_id)


@category_bp.route("", methods=["POST"])
@role_required("Administrator")
def create_category_route():
    return create_new_category()


@category_bp.route("/<int:category_id>", methods=["PUT"])
@role_required("Administrator")
def update_category_route(category_id):
    return edit_category(category_id)


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@role_required("Administrator")
def delete_category_route(category_id):
    return remove_category(category_id)