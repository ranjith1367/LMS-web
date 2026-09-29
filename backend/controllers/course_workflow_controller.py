from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from services.course_workflow_service import (
    submit_course,
    start_review,
    approve_course,
    reject_course,
    move_to_revision,
    publish_course
)


def submit(course_id):
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = submit_course(
        course_id,
        trainer_id,
        data.get("remarks")
    )

    return jsonify(response), status_code


def review(course_id):
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = start_review(
        course_id,
        admin_id,
        data.get("remarks")
    )

    return jsonify(response), status_code


def approve(course_id):
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = approve_course(
        course_id,
        admin_id,
        data.get("remarks")
    )

    return jsonify(response), status_code


def reject(course_id):
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = reject_course(
        course_id,
        admin_id,
        data.get("remarks")
    )

    return jsonify(response), status_code


def revision(course_id):
    trainer_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = move_to_revision(
        course_id,
        trainer_id,
        data.get("remarks")
    )

    return jsonify(response), status_code


def publish(course_id):
    admin_id = int(get_jwt_identity())
    data = request.get_json() or {}

    response, status_code = publish_course(
        course_id,
        admin_id,
        data.get("remarks")
    )

    return jsonify(response), status_code