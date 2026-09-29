from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.progress_controller import (
    complete_lesson_for_student,
    get_lesson_progress_for_student,
    get_course_progress_for_student
)


progress_bp = Blueprint("progress", __name__)


@progress_bp.route(
    "/api/lessons/<int:lesson_id>/complete",
    methods=["POST"]
)
@jwt_required()
def complete_lesson(lesson_id):
    student_id = get_jwt_identity()

    return complete_lesson_for_student(
        student_id,
        lesson_id
    )


@progress_bp.route(
    "/api/lessons/<int:lesson_id>/progress",
    methods=["GET"]
)
@jwt_required()
def get_lesson_progress(lesson_id):
    student_id = get_jwt_identity()

    return get_lesson_progress_for_student(
        student_id,
        lesson_id
    )


@progress_bp.route(
    "/api/courses/<int:course_id>/progress",
    methods=["GET"]
)
@jwt_required()
def get_course_progress(course_id):
    student_id = get_jwt_identity()

    return get_course_progress_for_student(
        student_id,
        course_id
    )