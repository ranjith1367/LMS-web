from flask import Blueprint

from controllers.module_lesson_controller import (
    get_modules,
    create_new_module,
    edit_module,
    remove_module,
    get_lessons,
    create_new_lesson,
    edit_lesson,
    remove_lesson
)

from utils.auth_utils import role_required


module_lesson_bp = Blueprint(
    "module_lesson",
    __name__
)


@module_lesson_bp.route(
    "/courses/<int:course_id>/modules",
    methods=["GET"]
)
def get_modules_route(course_id):
    return get_modules(course_id)


@module_lesson_bp.route(
    "/courses/<int:course_id>/modules",
    methods=["POST"]
)
@role_required("Trainer")
def create_module_route(course_id):
    return create_new_module(course_id)


@module_lesson_bp.route(
    "/modules/<int:module_id>",
    methods=["PUT"]
)
@role_required("Trainer")
def update_module_route(module_id):
    return edit_module(module_id)


@module_lesson_bp.route(
    "/modules/<int:module_id>",
    methods=["DELETE"]
)
@role_required("Trainer")
def delete_module_route(module_id):
    return remove_module(module_id)


@module_lesson_bp.route(
    "/modules/<int:module_id>/lessons",
    methods=["GET"]
)
def get_lessons_route(module_id):
    return get_lessons(module_id)


@module_lesson_bp.route(
    "/modules/<int:module_id>/lessons",
    methods=["POST"]
)
@role_required("Trainer")
def create_lesson_route(module_id):
    return create_new_lesson(module_id)


@module_lesson_bp.route(
    "/lessons/<int:lesson_id>",
    methods=["PUT"]
)
@role_required("Trainer")
def update_lesson_route(lesson_id):
    return edit_lesson(lesson_id)


@module_lesson_bp.route(
    "/lessons/<int:lesson_id>",
    methods=["DELETE"]
)
@role_required("Trainer")
def delete_lesson_route(lesson_id):
    return remove_lesson(lesson_id)