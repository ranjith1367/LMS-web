from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from services.course_service import (
    get_all_courses,
    get_course_by_id,
    get_trainer_courses,
    create_course,
    update_course,
    delete_course
)


def get_courses():
    response, status_code = get_all_courses()
    return jsonify(response), status_code


def get_course(course_id):
    response, status_code = get_course_by_id(course_id)
    return jsonify(response), status_code


def get_my_courses():
    trainer_id = int(get_jwt_identity())

    response, status_code = get_trainer_courses(
        trainer_id
    )

    return jsonify(response), status_code


def create_new_course():
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = create_course(
        data,
        trainer_id
    )

    return jsonify(response), status_code


def edit_course(course_id):
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = update_course(
        course_id,
        trainer_id,
        data
    )

    return jsonify(response), status_code


def remove_course(course_id):
    trainer_id = int(get_jwt_identity())

    response, status_code = delete_course(
        course_id,
        trainer_id
    )

    return jsonify(response), status_code