from flask import Blueprint

from controllers.course_workflow_controller import (
    submit,
    review,
    approve,
    reject,
    revision,
    publish
)

from utils.auth_utils import role_required


course_workflow_bp = Blueprint(
    "course_workflow",
    __name__
)


@course_workflow_bp.route(
    "/<int:course_id>/submit",
    methods=["POST"]
)
@role_required("Trainer")
def submit_course_route(course_id):
    return submit(course_id)


@course_workflow_bp.route(
    "/<int:course_id>/review",
    methods=["POST"]
)
@role_required("Administrator")
def review_course_route(course_id):
    return review(course_id)


@course_workflow_bp.route(
    "/<int:course_id>/approve",
    methods=["POST"]
)
@role_required("Administrator")
def approve_course_route(course_id):
    return approve(course_id)


@course_workflow_bp.route(
    "/<int:course_id>/reject",
    methods=["POST"]
)
@role_required("Administrator")
def reject_course_route(course_id):
    return reject(course_id)


@course_workflow_bp.route(
    "/<int:course_id>/revision",
    methods=["POST"]
)
@role_required("Trainer")
def revision_course_route(course_id):
    return revision(course_id)


@course_workflow_bp.route(
    "/<int:course_id>/publish",
    methods=["POST"]
)
@role_required("Administrator")
def publish_course_route(course_id):
    return publish(course_id)