from flask import request, jsonify

from services.user_service import (
    create_user,
    get_all_users,
    get_user_by_id,
    update_user
)


def create_new_user():
    data = request.get_json() or {}

    response, status_code = create_user(data)

    return jsonify(response), status_code


def get_users():
    response, status_code = get_all_users()

    return jsonify(response), status_code


def get_user(user_id):
    response, status_code = get_user_by_id(user_id)

    return jsonify(response), status_code


def edit_user(user_id):
    data = request.get_json() or {}

    response, status_code = update_user(user_id, data)

    return jsonify(response), status_code