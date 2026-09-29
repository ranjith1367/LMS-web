from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.material_controller import (
    list_lesson_materials,
    material_details,
    upload_material,
    remove_material
)

from utils.auth_utils import role_required


material_bp = Blueprint(
    "materials",
    __name__
)


@material_bp.route(
    "/lessons/<int:lesson_id>/materials",
    methods=["GET"]
)
@jwt_required()
def get_lesson_materials_route(lesson_id):
    return list_lesson_materials(lesson_id)


@material_bp.route(
    "/lessons/<int:lesson_id>/materials",
    methods=["POST"]
)
@role_required("Trainer")
def upload_material_route(lesson_id):
    return upload_material(lesson_id)


@material_bp.route(
    "/materials/<int:material_id>",
    methods=["GET"]
)
@jwt_required()
def get_material_route(material_id):
    return material_details(material_id)


@material_bp.route(
    "/materials/<int:material_id>",
    methods=["DELETE"]
)
@role_required("Trainer")
def delete_material_route(material_id):
    return remove_material(material_id)