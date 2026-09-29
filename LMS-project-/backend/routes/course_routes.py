from flask import Blueprint

from controllers.course_controller import (
    get_courses,
    get_course,
    get_my_courses,
    create_new_course,
    edit_course,
    remove_course
)

from utils.auth_utils import role_required


course_bp = Blueprint("courses", __name__)


@course_bp.route("", methods=["GET"])
def get_courses_route():
    return get_courses()


@course_bp.route("/my", methods=["GET"])
@role_required("Trainer")
def get_my_courses_route():
    return get_my_courses()


@course_bp.route("/<int:course_id>", methods=["GET"])
def get_course_route(course_id):
    return get_course(course_id)


@course_bp.route("", methods=["POST"])
@role_required("Trainer")
def create_course_route():
    return create_new_course()


@course_bp.route("/<int:course_id>", methods=["PUT"])
@role_required("Trainer")
def update_course_route(course_id):
    return edit_course(course_id)


@course_bp.route("/<int:course_id>", methods=["DELETE"])
@role_required("Trainer")
def delete_course_route(course_id):
    return remove_course(course_id)