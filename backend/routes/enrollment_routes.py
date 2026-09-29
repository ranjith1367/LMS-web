from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.enrollment_controller import (
    create_enrollment,
    list_enrollments,
    enrollment_details,
    cancel_enrollment,
    get_my_enrollments
)
from models.enrollment import Enrollment
from models.course import Course
from models.user import User
from utils.auth_utils import role_required


enrollment_bp = Blueprint(
    "enrollments",
    __name__
)


@enrollment_bp.route(
    "/courses/<int:course_id>/enroll",
    methods=["POST"]
)
@role_required("Student")
def enroll_course_route(course_id):
    return create_enrollment(course_id)


@enrollment_bp.route(
    "/enrollments",
    methods=["GET"]
)
@role_required("Student")
def get_enrollments_route():
    return list_enrollments()

@enrollment_bp.route(
    "/enrollments/my",
    methods=["GET"]
)
@jwt_required()
def get_my_enrollments_route():
    return get_my_enrollments()

@enrollment_bp.route(
    "/enrollments/<int:enrollment_id>",
    methods=["GET"]
)
@role_required("Student")
def get_enrollment_route(enrollment_id):
    return enrollment_details(enrollment_id)


@enrollment_bp.route(
    "/enrollments/<int:enrollment_id>/cancel",
    methods=["PATCH"]
)
@role_required("Student")
def cancel_enrollment_route(enrollment_id):
    return cancel_enrollment(enrollment_id)

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.enrollment import Enrollment
from models.course import Course


@jwt_required()
def get_my_enrollments():
    student_id = int(get_jwt_identity())

    enrollments = (
        Enrollment.query
        .join(Course, Enrollment.course_id == Course.course_id)
        .filter(Enrollment.student_id == student_id)
        .all()
    )

    return jsonify({
        "success": True,
        "courses": [
            {
                "enrollment_id": enrollment.enrollment_id,
                "course_id": enrollment.course_id,
                "course_title": course.title,
                "status": enrollment.status,
                "enrolled_at": enrollment.enrolled_at.isoformat()
                    if enrollment.enrolled_at else None
            }
            for enrollment, course in [
                (enrollment, Course.query.get(enrollment.course_id))
                for enrollment in enrollments
            ]
        ]
    }), 200

@enrollment_bp.route("/courses/<int:course_id>/students", methods=["GET"])
@role_required("Trainer")
def get_course_students(course_id):
    enrollments = (
        Enrollment.query
        .filter_by(course_id=course_id, status="ACTIVE")
        .all()
    )
    return jsonify({
        "success": True,
        "students": [
            {
                "student_id": e.student_id,
                "student_name": User.query.get(e.student_id).full_name,
                "status": e.status,
                "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None
            }
            for e in enrollments
        ]
    }), 200