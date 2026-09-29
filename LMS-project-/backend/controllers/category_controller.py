from flask import request, jsonify

from services.category_service import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)


def get_categories():
    response, status_code = get_all_categories()

    return jsonify(response), status_code


def get_category(category_id):
    response, status_code = get_category_by_id(category_id)

    return jsonify(response), status_code


def create_new_category():
    data = request.get_json() or {}

    response, status_code = create_category(data)

    return jsonify(response), status_code


def edit_category(category_id):
    data = request.get_json() or {}

    response, status_code = update_category(category_id, data)

    return jsonify(response), status_code


def remove_category(category_id):
    response, status_code = delete_category(category_id)

    return jsonify(response), status_code