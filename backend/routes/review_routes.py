from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.review_controller import (
    create_course_review,
    list_course_reviews,
    update_student_review,
    delete_student_review
)


review_bp = Blueprint(
    "review",
    __name__,
    url_prefix="/api"
)


@review_bp.route(
    "/courses/<int:course_id>/reviews",
    methods=["POST"]
)
@jwt_required()
def create_review_route(course_id):
    return create_course_review(course_id)


@review_bp.route(
    "/courses/<int:course_id>/reviews",
    methods=["GET"]
)
def get_reviews_route(course_id):
    return list_course_reviews(course_id)


@review_bp.route(
    "/reviews/<int:review_id>",
    methods=["PUT"]
)
@jwt_required()
def update_review_route(review_id):
    return update_student_review(review_id)


@review_bp.route(
    "/reviews/<int:review_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_review_route(review_id):
    return delete_student_review(review_id)