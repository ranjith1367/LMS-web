from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text

from extensions import db

from models.enrollment import Enrollment

from services.assignment_service import (
    get_assignments_by_course,
    get_assignment_by_id,
    create_assignment,
    update_assignment,
    delete_assignment
)

from services.notification_service import create_notification


def get_current_user_id():
    user_id = get_jwt_identity()

    if isinstance(user_id, dict):
        user_id = user_id.get("user_id")

    return int(user_id)


def get_current_user_role(user_id):
    result = db.session.execute(
        text("""
            SELECT role_id
            FROM users
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).fetchone()

    if result is None:
        return None

    return result[0]


def is_trainer(user_id):
    return get_current_user_role(user_id) == 2


def is_enrolled(student_id, course_id):
    result = db.session.execute(
        text("""
            SELECT enrollment_id
            FROM enrollments
            WHERE student_id = :student_id
              AND course_id = :course_id
              AND status = 'ACTIVE'
        """),
        {
            "student_id": student_id,
            "course_id": course_id
        }
    ).fetchone()

    return result is not None


def trainer_owns_course(trainer_id, course_id):
    result = db.session.execute(
        text("""
            SELECT course_id
            FROM courses
            WHERE course_id = :course_id
              AND trainer_id = :trainer_id
        """),
        {
            "course_id": course_id,
            "trainer_id": trainer_id
        }
    ).fetchone()

    return result is not None


def assignment_to_dict(assignment):
    return {
        "assignment_id": assignment.assignment_id,
        "course_id": assignment.course_id,
        "module_id": assignment.module_id,
        "title": assignment.title,
        "description": assignment.description,
        "maximum_marks": float(assignment.maximum_marks),
        "deadline": assignment.deadline.isoformat(),
        "allowed_file_types": assignment.allowed_file_types
    }


def list_assignments(course_id):
    user_id = get_current_user_id()
    role_id = get_current_user_role(user_id)

    if role_id is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    if role_id == 3:
        if not is_enrolled(user_id, course_id):
            return jsonify({
                "success": False,
                "message": "You are not enrolled in this course"
            }), 403

    elif role_id == 2:
        if not trainer_owns_course(user_id, course_id):
            return jsonify({
                "success": False,
                "message": "You do not own this course"
            }), 403

    else:
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    assignments = get_assignments_by_course(course_id)

    return jsonify({
        "success": True,
        "data": [
            assignment_to_dict(assignment)
            for assignment in assignments
        ]
    }), 200


def get_assignment(assignment_id):
    user_id = get_current_user_id()
    role_id = get_current_user_role(user_id)

    assignment = get_assignment_by_id(assignment_id)

    if assignment is None:
        return jsonify({
            "success": False,
            "message": "Assignment not found"
        }), 404

    if role_id is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    if role_id == 3:
        if not is_enrolled(
            user_id,
            assignment.course_id
        ):
            return jsonify({
                "success": False,
                "message": "You are not enrolled in this course"
            }), 403

    elif role_id == 2:
        if not trainer_owns_course(
            user_id,
            assignment.course_id
        ):
            return jsonify({
                "success": False,
                "message": "You do not own this course"
            }), 403

    else:
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    return jsonify({
        "success": True,
        "data": assignment_to_dict(assignment)
    }), 200


def create_new_assignment(course_id, data):
    user_id = get_current_user_id()

    if not is_trainer(user_id):
        return jsonify({
            "success": False,
            "message": "Only trainers can create assignments"
        }), 403

    if not trainer_owns_course(
        user_id,
        course_id
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    required_fields = [
        "module_id",
        "title",
        "maximum_marks",
        "deadline"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    assignment = create_assignment(
        course_id=course_id,
        module_id=data["module_id"],
        title=data["title"],
        description=data.get("description"),
        maximum_marks=data["maximum_marks"],
        deadline=data["deadline"],
        allowed_file_types=data.get("allowed_file_types")
    )

    # Create a notification for every active student
    # enrolled in this course.
    active_enrollments = Enrollment.query.filter_by(
        course_id=course_id,
        status="ACTIVE"
    ).all()

    for enrollment in active_enrollments:
        create_notification(
            user_id=enrollment.student_id,
            title="New Assignment",
            message=f"A new assignment '{assignment.title}' has been added to your course.",
            notification_type="NEW_ASSIGNMENT"
        )

    return jsonify({
        "success": True,
        "message": "Assignment created successfully",
        "data": assignment_to_dict(assignment)
    }), 201


def update_existing_assignment(assignment_id, data):
    user_id = get_current_user_id()

    assignment = get_assignment_by_id(assignment_id)

    if assignment is None:
        return jsonify({
            "success": False,
            "message": "Assignment not found"
        }), 404

    if not is_trainer(user_id):
        return jsonify({
            "success": False,
            "message": "Only trainers can update assignments"
        }), 403

    if not trainer_owns_course(
        user_id,
        assignment.course_id
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    assignment = update_assignment(
        assignment=assignment,
        module_id=data.get(
            "module_id",
            assignment.module_id
        ),
        title=data.get(
            "title",
            assignment.title
        ),
        description=data.get(
            "description",
            assignment.description
        ),
        maximum_marks=data.get(
            "maximum_marks",
            assignment.maximum_marks
        ),
        deadline=data.get(
            "deadline",
            assignment.deadline
        ),
        allowed_file_types=data.get(
            "allowed_file_types",
            assignment.allowed_file_types
        )
    )

    return jsonify({
        "success": True,
        "message": "Assignment updated successfully",
        "data": assignment_to_dict(assignment)
    }), 200


def delete_existing_assignment(assignment_id):
    user_id = get_current_user_id()

    assignment = get_assignment_by_id(assignment_id)

    if assignment is None:
        return jsonify({
            "success": False,
            "message": "Assignment not found"
        }), 404

    if not is_trainer(user_id):
        return jsonify({
            "success": False,
            "message": "Only trainers can delete assignments"
        }), 403

    if not trainer_owns_course(
        user_id,
        assignment.course_id
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    delete_assignment(assignment)

    return jsonify({
        "success": True,
        "message": "Assignment deleted successfully"
    }), 200