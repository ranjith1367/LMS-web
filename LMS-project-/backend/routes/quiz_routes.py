from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from controllers.quiz_controller import (
    list_course_quizzes,
    get_single_quiz,
    create_new_quiz,
    update_existing_quiz,
    delete_existing_quiz,
    create_new_question,
    update_existing_question,
    delete_existing_question
)


quiz_bp = Blueprint(
    "quiz",
    __name__,
    url_prefix="/api"
)


@quiz_bp.route(
    "/courses/<int:course_id>/quizzes",
    methods=["GET"]
)
@jwt_required()
def course_quizzes(course_id):
    return list_course_quizzes(course_id)


@quiz_bp.route(
    "/quizzes/<int:quiz_id>",
    methods=["GET"]
)
@jwt_required()
def single_quiz(quiz_id):
    return get_single_quiz(quiz_id)


@quiz_bp.route(
    "/courses/<int:course_id>/quizzes",
    methods=["POST"]
)
@jwt_required()
def create_quiz(course_id):
    data = request.get_json() or {}

    return create_new_quiz(
        course_id,
        data
    )


@quiz_bp.route(
    "/quizzes/<int:quiz_id>",
    methods=["PUT"]
)
@jwt_required()
def update_quiz(quiz_id):
    data = request.get_json() or {}

    return update_existing_quiz(
        quiz_id,
        data
    )


@quiz_bp.route(
    "/quizzes/<int:quiz_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_quiz(quiz_id):
    return delete_existing_quiz(quiz_id)


@quiz_bp.route(
    "/quizzes/<int:quiz_id>/questions",
    methods=["POST"]
)
@jwt_required()
def create_question(quiz_id):
    data = request.get_json() or {}

    return create_new_question(
        quiz_id,
        data
    )


@quiz_bp.route(
    "/questions/<int:question_id>",
    methods=["PUT"]
)
@jwt_required()
def update_question(question_id):
    data = request.get_json() or {}

    return update_existing_question(
        question_id,
        data
    )


@quiz_bp.route(
    "/questions/<int:question_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_question(question_id):
    return delete_existing_question(
        question_id
    )