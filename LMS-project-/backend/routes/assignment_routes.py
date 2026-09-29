from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from controllers.assignment_controller import (
    list_assignments,
    get_assignment,
    create_new_assignment,
    update_existing_assignment,
    delete_existing_assignment
)


assignment_bp = Blueprint("assignments", __name__)


@assignment_bp.route(
    "/api/courses/<int:course_id>/assignments",
    methods=["GET"]
)
@jwt_required()
def get_course_assignments(course_id):
    return list_assignments(course_id)


@assignment_bp.route(
    "/api/assignments/<int:assignment_id>",
    methods=["GET"]
)
@jwt_required()
def get_single_assignment(assignment_id):
    return get_assignment(assignment_id)


@assignment_bp.route(
    "/api/courses/<int:course_id>/assignments",
    methods=["POST"]
)
@jwt_required()
def create_course_assignment(course_id):
    data = request.get_json()

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return create_new_assignment(
        course_id,
        data
    )


@assignment_bp.route(
    "/api/assignments/<int:assignment_id>",
    methods=["PUT"]
)
@jwt_required()
def update_assignment(assignment_id):
    data = request.get_json()

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return update_existing_assignment(
        assignment_id,
        data
    )


@assignment_bp.route(
    "/api/assignments/<int:assignment_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_assignment(assignment_id):
    return delete_existing_assignment(
        assignment_id
    )