from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.quiz_attempt_controller import (
    start_quiz_attempt,
    get_single_attempt,
    submit_quiz_attempt,
    get_quiz_results_controller
)


quiz_attempt_bp = Blueprint(
    "quiz_attempt",
    __name__,
    url_prefix="/api"
)


@quiz_attempt_bp.route(
    "/quizzes/<int:quiz_id>/attempts",
    methods=["POST"]
)
@jwt_required()
def start_attempt_route(quiz_id):
    return start_quiz_attempt(quiz_id)


@quiz_attempt_bp.route(
    "/quiz-attempts/<int:attempt_id>",
    methods=["GET"]
)
@jwt_required()
def get_attempt_route(attempt_id):
    return get_single_attempt(attempt_id)


@quiz_attempt_bp.route(
    "/quiz-attempts/<int:attempt_id>/submit",
    methods=["POST"]
)
@jwt_required()
def submit_attempt_route(attempt_id):
    return submit_quiz_attempt(attempt_id)


@quiz_attempt_bp.route(
    "/quizzes/<int:quiz_id>/results",
    methods=["GET"]
)
@jwt_required()
def quiz_results_route(quiz_id):
    return get_quiz_results_controller(quiz_id)