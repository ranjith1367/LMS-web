from extensions import db

from models.course import Course
from models.module import Module
from models.lesson import Lesson


def module_to_dict(module):
    return {
        "module_id": module.module_id,
        "course_id": module.course_id,
        "module_name": module.module_name,
        "description": module.description,
        "module_order": module.module_order,
        "created_at": module.created_at
    }


def lesson_to_dict(lesson):
    return {
        "lesson_id": lesson.lesson_id,
        "module_id": lesson.module_id,
        "lesson_name": lesson.lesson_name,
        "description": lesson.description,
        "lesson_order": lesson.lesson_order,
        "created_at": lesson.created_at
    }


def get_course_modules(course_id):
    course = db.session.get(Course, course_id)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    modules = Module.query.filter_by(
        course_id=course_id
    ).order_by(
        Module.module_order
    ).all()

    return {
        "success": True,
        "modules": [
            module_to_dict(module)
            for module in modules
        ]
    }, 200


def create_module(course_id, trainer_id, data):
    course = db.session.get(Course, course_id)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    module_name = data.get("module_name")
    module_order = data.get("module_order")

    if not module_name or module_order is None:
        return {
            "success": False,
            "message": "Module name and module order are required",
            "error_code": "VALIDATION_ERROR"
        }, 400

    if not isinstance(module_order, int) or module_order <= 0:
        return {
            "success": False,
            "message": "Module order must be a positive integer",
            "error_code": "INVALID_MODULE_ORDER"
        }, 400

    module = Module(
        course_id=course_id,
        module_name=module_name,
        description=data.get("description"),
        module_order=module_order
    )

    db.session.add(module)
    db.session.commit()

    return {
        "success": True,
        "message": "Module created successfully",
        "module": module_to_dict(module)
    }, 201


def update_module(module_id, trainer_id, data):
    module = db.session.get(Module, module_id)

    if not module:
        return {
            "success": False,
            "message": "Module not found",
            "error_code": "MODULE_NOT_FOUND"
        }, 404

    course = db.session.get(
        Course,
        module.course_id
    )

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    if "module_name" in data:
        if not data["module_name"]:
            return {
                "success": False,
                "message": "Module name cannot be empty",
                "error_code": "VALIDATION_ERROR"
            }, 400

        module.module_name = data["module_name"]

    if "description" in data:
        module.description = data["description"]

    if "module_order" in data:
        module_order = data["module_order"]

        if not isinstance(module_order, int) or module_order <= 0:
            return {
                "success": False,
                "message": "Module order must be a positive integer",
                "error_code": "INVALID_MODULE_ORDER"
            }, 400

        module.module_order = module_order

    db.session.commit()

    return {
        "success": True,
        "message": "Module updated successfully",
        "module": module_to_dict(module)
    }, 200


def delete_module(module_id, trainer_id):
    module = db.session.get(Module, module_id)

    if not module:
        return {
            "success": False,
            "message": "Module not found",
            "error_code": "MODULE_NOT_FOUND"
        }, 404

    course = db.session.get(
        Course,
        module.course_id
    )

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    db.session.delete(module)
    db.session.commit()

    return {
        "success": True,
        "message": "Module deleted successfully"
    }, 200


def get_module_lessons(module_id):
    module = db.session.get(Module, module_id)

    if not module:
        return {
            "success": False,
            "message": "Module not found",
            "error_code": "MODULE_NOT_FOUND"
        }, 404

    lessons = Lesson.query.filter_by(
        module_id=module_id
    ).order_by(
        Lesson.lesson_order
    ).all()

    return {
        "success": True,
        "lessons": [
            lesson_to_dict(lesson)
            for lesson in lessons
        ]
    }, 200


def create_lesson(module_id, trainer_id, data):
    module = db.session.get(Module, module_id)

    if not module:
        return {
            "success": False,
            "message": "Module not found",
            "error_code": "MODULE_NOT_FOUND"
        }, 404

    course = db.session.get(
        Course,
        module.course_id
    )

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    lesson_name = data.get("lesson_name")
    lesson_order = data.get("lesson_order")

    if not lesson_name or lesson_order is None:
        return {
            "success": False,
            "message": "Lesson name and lesson order are required",
            "error_code": "VALIDATION_ERROR"
        }, 400

    if not isinstance(lesson_order, int) or lesson_order <= 0:
        return {
            "success": False,
            "message": "Lesson order must be a positive integer",
            "error_code": "INVALID_LESSON_ORDER"
        }, 400

    lesson = Lesson(
        module_id=module_id,
        lesson_name=lesson_name,
        description=data.get("description"),
        lesson_order=lesson_order
    )

    db.session.add(lesson)
    db.session.commit()

    return {
        "success": True,
        "message": "Lesson created successfully",
        "lesson": lesson_to_dict(lesson)
    }, 201


def update_lesson(lesson_id, trainer_id, data):
    lesson = db.session.get(Lesson, lesson_id)

    if not lesson:
        return {
            "success": False,
            "message": "Lesson not found",
            "error_code": "LESSON_NOT_FOUND"
        }, 404

    module = db.session.get(
        Module,
        lesson.module_id
    )

    course = db.session.get(
        Course,
        module.course_id
    )

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    if "lesson_name" in data:
        if not data["lesson_name"]:
            return {
                "success": False,
                "message": "Lesson name cannot be empty",
                "error_code": "VALIDATION_ERROR"
            }, 400

        lesson.lesson_name = data["lesson_name"]

    if "description" in data:
        lesson.description = data["description"]

    if "lesson_order" in data:
        lesson_order = data["lesson_order"]

        if not isinstance(lesson_order, int) or lesson_order <= 0:
            return {
                "success": False,
                "message": "Lesson order must be a positive integer",
                "error_code": "INVALID_LESSON_ORDER"
            }, 400

        lesson.lesson_order = lesson_order

    db.session.commit()

    return {
        "success": True,
        "message": "Lesson updated successfully",
        "lesson": lesson_to_dict(lesson)
    }, 200


def delete_lesson(lesson_id, trainer_id):
    lesson = db.session.get(Lesson, lesson_id)

    if not lesson:
        return {
            "success": False,
            "message": "Lesson not found",
            "error_code": "LESSON_NOT_FOUND"
        }, 404

    module = db.session.get(
        Module,
        lesson.module_id
    )

    course = db.session.get(
        Course,
        module.course_id
    )

    if course.trainer_id != trainer_id:
        return {
            "success": False,
            "message": "You can only manage your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    db.session.delete(lesson)
    db.session.commit()

    return {
        "success": True,
        "message": "Lesson deleted successfully"
    }, 200