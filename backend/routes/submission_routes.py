from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.submission_controller import (
    submit_assignment,
    get_single_submission,
    update_existing_submission,
    list_assignment_submissions,
    evaluate_existing_submission
)


submission_bp = Blueprint(
    "submission",
    __name__,
    url_prefix="/api"
)


@submission_bp.route(
    "/assignments/<int:assignment_id>/submit",
    methods=["POST"]
)
@jwt_required()
def submit(assignment_id):
    return submit_assignment(assignment_id)


@submission_bp.route(
    "/submissions/<int:submission_id>",
    methods=["GET"]
)
@jwt_required()
def get_submission_route(submission_id):
    return get_single_submission(submission_id)


@submission_bp.route(
    "/submissions/<int:submission_id>",
    methods=["PUT"]
)
@jwt_required()
def update_submission_route(submission_id):
    return update_existing_submission(submission_id)


@submission_bp.route(
    "/assignments/<int:assignment_id>/submissions",
    methods=["GET"]
)
@jwt_required()
def assignment_submissions(assignment_id):
    return list_assignment_submissions(assignment_id)


@submission_bp.route(
    "/submissions/<int:submission_id>/evaluate",
    methods=["POST"]
)
@jwt_required()
def evaluate_submission_route(submission_id):
    return evaluate_existing_submission(submission_id)