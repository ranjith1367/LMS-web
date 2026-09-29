from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from services.material_service import (
    get_lesson_materials,
    get_material,
    create_material,
    delete_material
)


def list_lesson_materials(lesson_id):
    response, status_code = get_lesson_materials(
        lesson_id
    )

    return jsonify(response), status_code


def material_details(material_id):
    response, status_code = get_material(
        material_id
    )

    return jsonify(response), status_code


def upload_material(lesson_id):
    trainer_id = int(
        get_jwt_identity()
    )

    material_name = request.form.get(
        "material_name"
    )

    file = request.files.get(
        "file"
    )

    response, status_code = create_material(
        lesson_id,
        trainer_id,
        material_name,
        file
    )

    return jsonify(response), status_code


def remove_material(material_id):
    trainer_id = int(
        get_jwt_identity()
    )

    response, status_code = delete_material(
        material_id,
        trainer_id
    )

    return jsonify(response), status_code