from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from services.module_lesson_service import (
    get_course_modules,
    create_module,
    update_module,
    delete_module,
    get_module_lessons,
    create_lesson,
    update_lesson,
    delete_lesson
)


def get_modules(course_id):
    response, status_code = get_course_modules(
        course_id
    )

    return jsonify(response), status_code


def create_new_module(course_id):
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = create_module(
        course_id,
        trainer_id,
        data
    )

    return jsonify(response), status_code


def edit_module(module_id):
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = update_module(
        module_id,
        trainer_id,
        data
    )

    return jsonify(response), status_code


def remove_module(module_id):
    trainer_id = int(get_jwt_identity())

    response, status_code = delete_module(
        module_id,
        trainer_id
    )

    return jsonify(response), status_code


def get_lessons(module_id):
    response, status_code = get_module_lessons(
        module_id
    )

    return jsonify(response), status_code


def create_new_lesson(module_id):
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = create_lesson(
        module_id,
        trainer_id,
        data
    )

    return jsonify(response), status_code


def edit_lesson(lesson_id):
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = update_lesson(
        lesson_id,
        trainer_id,
        data
    )

    return jsonify(response), status_code


def remove_lesson(lesson_id):
    trainer_id = int(get_jwt_identity())

    response, status_code = delete_lesson(
        lesson_id,
        trainer_id
    )

    return jsonify(response), status_code