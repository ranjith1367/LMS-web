from extensions import db
from models.course import Course
from models.category import Category
from models.user import User
from models.course_status_history import CourseStatusHistory


VALID_LEVELS = [
    "BEGINNER",
    "INTERMEDIATE",
    "ADVANCED"
]


def course_to_dict(course):
    return {
        "course_id": course.course_id,
        "category_id": course.category_id,
        "trainer_id": course.trainer_id,
        "title": course.title,
        "description": course.description,
        "learning_objectives": course.learning_objectives,
        "thumbnail": course.thumbnail,
        "level": course.level,
        "duration": course.duration,
        "status": course.status,
        "created_at": course.created_at,
        "updated_at": course.updated_at
    }


def get_all_courses():
    courses = Course.query.all()

    return {
        "success": True,
        "courses": [
            course_to_dict(course)
            for course in courses
        ]
    }, 200


def get_course_by_id(course_id):
    course = db.session.get(Course, course_id)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    return {
        "success": True,
        "course": course_to_dict(course)
    }, 200


def get_trainer_courses(trainer_id):
    courses = Course.query.filter_by(
        trainer_id=trainer_id
    ).all()

    return {
        "success": True,
        "courses": [
            course_to_dict(course)
            for course in courses
        ]
    }, 200


def create_course(data, trainer_id):
    category_id = data.get("category_id")
    title = data.get("title")

    if not category_id or not title:
        return {
            "success": False,
            "message": "Category ID and title are required",
            "error_code": "VALIDATION_ERROR"
        }, 400

    category = db.session.get(Category, category_id)

    if not category:
        return {
            "success": False,
            "message": "Category not found",
            "error_code": "CATEGORY_NOT_FOUND"
        }, 404

    trainer = db.session.get(User, trainer_id)

    if not trainer:
        return {
            "success": False,
            "message": "Trainer not found",
            "error_code": "TRAINER_NOT_FOUND"
        }, 404

    level = data.get("level")

    if level and level not in VALID_LEVELS:
        return {
            "success": False,
            "message": "Invalid course level",
            "error_code": "INVALID_LEVEL"
        }, 400

    duration = data.get("duration")

    if duration is not None:
        if not isinstance(duration, int) or duration <= 0:
            return {
                "success": False,
                "message": "Duration must be a positive integer",
                "error_code": "INVALID_DURATION"
            }, 400

    course = Course(
        category_id=category_id,
        trainer_id=trainer_id,
        title=title,
        description=data.get("description"),
        learning_objectives=data.get(
            "learning_objectives"
        ),
        thumbnail=data.get("thumbnail"),
        level=level,
        duration=duration,
        status="DRAFT"
    )

    db.session.add(course)
    db.session.flush()

    history = CourseStatusHistory(
        course_id=course.course_id,
        old_status=None,
        new_status="DRAFT",
        changed_by=trainer_id,
        remarks="Course created by trainer"
    )

    db.session.add(history)
    db.session.commit()

    return {
        "success": True,
        "message": "Course created successfully",
        "course": course_to_dict(course)
    }, 201


def update_course(course_id, trainer_id, data):
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
            "message": "You can only update your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    if course.status not in [
        "DRAFT",
        "REVISION",
        "REJECTED"
    ]:
        return {
            "success": False,
            "message": "Course cannot be edited in its current status",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    if "category_id" in data:
        category = db.session.get(
            Category,
            data["category_id"]
        )

        if not category:
            return {
                "success": False,
                "message": "Category not found",
                "error_code": "CATEGORY_NOT_FOUND"
            }, 404

        course.category_id = data["category_id"]

    if "title" in data:
        if not data["title"]:
            return {
                "success": False,
                "message": "Title cannot be empty",
                "error_code": "VALIDATION_ERROR"
            }, 400

        course.title = data["title"]

    if "description" in data:
        course.description = data["description"]

    if "learning_objectives" in data:
        course.learning_objectives = data[
            "learning_objectives"
        ]

    if "thumbnail" in data:
        course.thumbnail = data["thumbnail"]

    if "level" in data:
        if (
            data["level"] is not None
            and data["level"] not in VALID_LEVELS
        ):
            return {
                "success": False,
                "message": "Invalid course level",
                "error_code": "INVALID_LEVEL"
            }, 400

        course.level = data["level"]

    if "duration" in data:
        duration = data["duration"]

        if (
            duration is not None
            and (
                not isinstance(duration, int)
                or duration <= 0
            )
        ):
            return {
                "success": False,
                "message": "Duration must be a positive integer",
                "error_code": "INVALID_DURATION"
            }, 400

        course.duration = duration

    db.session.commit()

    return {
        "success": True,
        "message": "Course updated successfully",
        "course": course_to_dict(course)
    }, 200


def delete_course(course_id, trainer_id):
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
            "message": "You can only delete your own courses",
            "error_code": "FORBIDDEN"
        }, 403

    if course.status != "DRAFT":
        return {
            "success": False,
            "message": "Only draft courses can be deleted",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    db.session.delete(course)
    db.session.commit()

    return {
        "success": True,
        "message": "Course deleted successfully"
    }, 200