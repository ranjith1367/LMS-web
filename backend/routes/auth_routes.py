from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.auth_controller import (
    register,
    login,
    profile,
    update_profile
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register_route():
    return register()


@auth_bp.route("/login", methods=["POST"])
def login_route():
    return login()


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile_route():
    return profile()


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile_route():
    return update_profile()