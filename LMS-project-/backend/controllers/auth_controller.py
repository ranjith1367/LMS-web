from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from services.auth_service import (
    register_user,
    login_user,
    get_user_profile,
    update_user_profile
)


def register():
    data = request.get_json() or {}

    response, status_code = register_user(data)

    return jsonify(response), status_code


def login():
    data = request.get_json() or {}

    response, status_code = login_user(data)

    return jsonify(response), status_code


def profile():
    user_id = get_jwt_identity()

    response, status_code = get_user_profile(user_id)

    return jsonify(response), status_code


def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    response, status_code = update_user_profile(user_id, data)

    return jsonify(response), status_code