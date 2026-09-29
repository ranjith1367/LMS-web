from extensions import db

from models.course import Course
from models.enrollment import Enrollment


def enrollment_to_dict(enrollment):
    return {
        "enrollment_id": enrollment.enrollment_id,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id,
        "status": enrollment.status,
        "enrolled_at": enrollment.enrolled_at,
        "completed_at": enrollment.completed_at
    }


def enroll_student(course_id, student_id):
    course = db.session.get(
        Course,
        course_id
    )

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.status != "PUBLISHED":
        return {
            "success": False,
            "message": "Students can only enroll in published courses",
            "error_code": "COURSE_NOT_PUBLISHED"
        }, 400

    existing_enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if existing_enrollment:
        return {
            "success": False,
            "message": "You are already enrolled in this course",
            "error_code": "ALREADY_ENROLLED"
        }, 409

    try:
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status="ACTIVE"
        )

        db.session.add(enrollment)
        db.session.commit()

        return {
            "success": True,
            "message": "Course enrollment successful",
            "enrollment": enrollment_to_dict(
                enrollment
            )
        }, 201

    except Exception:
        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to enroll in course",
            "error_code": "ENROLLMENT_FAILED"
        }, 500


def get_student_enrollments(student_id):
    enrollments = Enrollment.query.filter_by(
        student_id=student_id
    ).order_by(
        Enrollment.enrolled_at.desc()
    ).all()

    return {
        "success": True,
        "enrollments": [
            enrollment_to_dict(enrollment)
            for enrollment in enrollments
        ]
    }, 200


def get_student_enrollment(
    enrollment_id,
    student_id
):
    enrollment = db.session.get(
        Enrollment,
        enrollment_id
    )

    if not enrollment:
        return {
            "success": False,
            "message": "Enrollment not found",
            "error_code": "ENROLLMENT_NOT_FOUND"
        }, 404

    if enrollment.student_id != student_id:
        return {
            "success": False,
            "message": "You can only view your own enrollments",
            "error_code": "FORBIDDEN"
        }, 403

    return {
        "success": True,
        "enrollment": enrollment_to_dict(
            enrollment
        )
    }, 200


def cancel_student_enrollment(
    enrollment_id,
    student_id
):
    enrollment = db.session.get(
        Enrollment,
        enrollment_id
    )

    if not enrollment:
        return {
            "success": False,
            "message": "Enrollment not found",
            "error_code": "ENROLLMENT_NOT_FOUND"
        }, 404

    if enrollment.student_id != student_id:
        return {
            "success": False,
            "message": "You can only cancel your own enrollment",
            "error_code": "FORBIDDEN"
        }, 403

    if enrollment.status == "CANCELLED":
        return {
            "success": False,
            "message": "Enrollment is already cancelled",
            "error_code": "ALREADY_CANCELLED"
        }, 400

    if enrollment.status == "COMPLETED":
        return {
            "success": False,
            "message": "Completed enrollment cannot be cancelled",
            "error_code": "ENROLLMENT_COMPLETED"
        }, 400

    try:
        enrollment.status = "CANCELLED"

        db.session.commit()

        return {
            "success": True,
            "message": "Enrollment cancelled successfully",
            "enrollment": enrollment_to_dict(
                enrollment
            )
        }, 200

    except Exception:
        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to cancel enrollment",
            "error_code": "CANCELLATION_FAILED"
        }, 500
