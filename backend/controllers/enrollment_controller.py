from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.enrollment import Enrollment
from models.course import Course

from services.enrollment_service import (
    enroll_student,
    get_student_enrollments,
    get_student_enrollment,
    cancel_student_enrollment
)

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

def create_enrollment(course_id):
    student_id = int(
        get_jwt_identity()
    )

    response, status_code = enroll_student(
        course_id,
        student_id
    )

    return jsonify(response), status_code


def list_enrollments():
    student_id = int(
        get_jwt_identity()
    )

    response, status_code = get_student_enrollments(
        student_id
    )

    return jsonify(response), status_code


def enrollment_details(enrollment_id):
    student_id = int(
        get_jwt_identity()
    )

    response, status_code = get_student_enrollment(
        enrollment_id,
        student_id
    )

    return jsonify(response), status_code


def cancel_enrollment(enrollment_id):
    student_id = int(
        get_jwt_identity()
    )

    response, status_code = cancel_student_enrollment(
        enrollment_id,
        student_id
    )

    return jsonify(response), status_code
