import os
import uuid

from werkzeug.utils import secure_filename

from extensions import db
from models.course import Course
from models.module import Module
from models.lesson import Lesson
from models.material import Material


ALLOWED_FILE_TYPES = {
    "pdf": "PDF",
    "mp4": "VIDEO"
}

MAX_FILE_SIZE = 50 * 1024 * 1024

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

MATERIAL_FOLDER = os.path.join(
    BASE_DIR,
    "database",
    "material"
)


def material_to_dict(material):
    return {
        "material_id": material.material_id,
        "lesson_id": material.lesson_id,
        "material_name": material.material_name,
        "file_path": material.file_path,
        "file_type": material.file_type,
        "file_size": material.file_size,
        "created_at": material.created_at
    }


def get_lesson_course(lesson):
    module = db.session.get(
        Module,
        lesson.module_id
    )

    if not module:
        return None

    return db.session.get(
        Course,
        module.course_id
    )


def get_lesson_materials(lesson_id):
    lesson = db.session.get(
        Lesson,
        lesson_id
    )

    if not lesson:
        return {
            "success": False,
            "message": "Lesson not found",
            "error_code": "LESSON_NOT_FOUND"
        }, 404

    materials = Material.query.filter_by(
        lesson_id=lesson_id
    ).order_by(
        Material.material_id
    ).all()

    return {
        "success": True,
        "materials": [
            material_to_dict(material)
            for material in materials
        ]
    }, 200


def get_material(material_id):
    material = db.session.get(
        Material,
        material_id
    )

    if not material:
        return {
            "success": False,
            "message": "Material not found",
            "error_code": "MATERIAL_NOT_FOUND"
        }, 404

    return {
        "success": True,
        "material": material_to_dict(material)
    }, 200


def create_material(lesson_id, trainer_id, material_name, file):
    lesson = db.session.get(
        Lesson,
        lesson_id
    )

    if not lesson:
        return {
            "success": False,
            "message": "Lesson not found",
            "error_code": "LESSON_NOT_FOUND"
        }, 404

    course = get_lesson_course(lesson)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage materials in your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    if not material_name or not material_name.strip():
        return {
            "success": False,
            "message": "Material name is required",
            "error_code": "VALIDATION_ERROR"
        }, 400

    if not file or not file.filename:
        return {
            "success": False,
            "message": "Material file is required",
            "error_code": "VALIDATION_ERROR"
        }, 400

    safe_filename = secure_filename(file.filename)

    if "." not in safe_filename:
        return {
            "success": False,
            "message": "File extension is required",
            "error_code": "INVALID_FILE_TYPE"
        }, 400

    extension = safe_filename.rsplit(
        ".",
        1
    )[1].lower()

    if extension not in ALLOWED_FILE_TYPES:
        return {
            "success": False,
            "message": "Only PDF and MP4 files are allowed",
            "error_code": "INVALID_FILE_TYPE"
        }, 400

    file.stream.seek(
        0,
        os.SEEK_END
    )

    file_size = file.stream.tell()

    file.stream.seek(0)

    if file_size <= 0:
        return {
            "success": False,
            "message": "Uploaded file is empty",
            "error_code": "INVALID_FILE"
        }, 400

    if file_size > MAX_FILE_SIZE:
        return {
            "success": False,
            "message": "File size must not exceed 50 MB",
            "error_code": "FILE_TOO_LARGE"
        }, 400

    file_header = file.stream.read(12)
    file.stream.seek(0)

    if extension == "pdf":
        if not file_header.startswith(b"%PDF-"):
            return {
                "success": False,
                "message": "Invalid PDF file",
                "error_code": "INVALID_FILE_TYPE"
            }, 400

    if extension == "mp4":
        if b"ftyp" not in file_header:
            return {
                "success": False,
                "message": "Invalid MP4 file",
                "error_code": "INVALID_FILE_TYPE"
            }, 400

    os.makedirs(
        MATERIAL_FOLDER,
        exist_ok=True
    )

    stored_filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    full_file_path = os.path.join(
        MATERIAL_FOLDER,
        stored_filename
    )

    database_file_path = (
        f"/database/material/{stored_filename}"
    )

    try:
        file.save(full_file_path)

        material = Material(
            lesson_id=lesson_id,
            material_name=material_name.strip(),
            file_path=database_file_path,
            file_type=ALLOWED_FILE_TYPES[extension],
            file_size=file_size
        )

        db.session.add(material)
        db.session.commit()

        return {
            "success": True,
            "message": "Material uploaded successfully",
            "material": material_to_dict(material)
        }, 201

    except Exception:
        db.session.rollback()

        if os.path.exists(full_file_path):
            os.remove(full_file_path)

        return {
            "success": False,
            "message": "Failed to upload material",
            "error_code": "UPLOAD_FAILED"
        }, 500


def delete_material(material_id, trainer_id):
    material = db.session.get(
        Material,
        material_id
    )

    if not material:
        return {
            "success": False,
            "message": "Material not found",
            "error_code": "MATERIAL_NOT_FOUND"
        }, 404

    lesson = db.session.get(
        Lesson,
        material.lesson_id
    )

    if not lesson:
        return {
            "success": False,
            "message": "Lesson not found",
            "error_code": "LESSON_NOT_FOUND"
        }, 404

    course = get_lesson_course(lesson)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage materials in your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    full_file_path = None

    if material.file_path:
        relative_path = material.file_path.lstrip(
            "/"
        )

        full_file_path = os.path.join(
            BASE_DIR,
            *relative_path.split("/")
        )

    db.session.delete(material)
    db.session.commit()

    if (
        full_file_path
        and os.path.exists(full_file_path)
    ):
        os.remove(full_file_path)

    return {
        "success": True,
        "message": "Material deleted successfully"
    }, 200