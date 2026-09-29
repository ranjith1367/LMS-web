from flask import Blueprint

from controllers.user_controller import (
    create_new_user,
    get_users,
    get_user,
    edit_user
)

from utils.auth_utils import role_required


user_bp = Blueprint("users", __name__)


@user_bp.route("", methods=["POST"])
@role_required("Administrator")
def create_user_route():
    return create_new_user()


@user_bp.route("", methods=["GET"])
@role_required("Administrator")
def get_users_route():
    return get_users()


@user_bp.route("/<int:user_id>", methods=["GET"])
@role_required("Administrator")
def get_user_route(user_id):
    return get_user(user_id)


@user_bp.route("/<int:user_id>", methods=["PUT"])
@role_required("Administrator")
def edit_user_route(user_id):
    return edit_user(user_id)