from extensions import db
from models.course import Course
from models.course_status_history import CourseStatusHistory
from services.notification_service import create_notification

def add_status_history(
    course_id,
    old_status,
    new_status,
    changed_by,
    remarks=None
):
    history = CourseStatusHistory(
        course_id=course_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        remarks=remarks
    )

    db.session.add(history)


def submit_course(course_id, trainer_id, remarks=None):
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
            "message": "You can only submit your own course",
            "error_code": "FORBIDDEN"
        }, 403

    if course.status not in ["DRAFT", "REVISION"]:
        return {
            "success": False,
            "message": "Course cannot be submitted in its current status",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    old_status = course.status

    if old_status == "DRAFT":
        new_status = "SUBMITTED"
    else:
        new_status = "RESUBMITTED"

    course.status = new_status

    add_status_history(
        course.course_id,
        old_status,
        new_status,
        trainer_id,
        remarks or "Course submitted for administrator approval"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Course submitted successfully",
        "course_id": course.course_id,
        "old_status": old_status,
        "new_status": new_status
    }, 200


def start_review(course_id, admin_id, remarks=None):
    course = db.session.get(Course, course_id)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.status not in ["SUBMITTED", "RESUBMITTED"]:
        return {
            "success": False,
            "message": "Course is not ready for review",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    old_status = course.status
    course.status = "UNDER_REVIEW"

    add_status_history(
        course.course_id,
        old_status,
        "UNDER_REVIEW",
        admin_id,
        remarks or "Course review started by administrator"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Course is now under review",
        "course_id": course.course_id,
        "old_status": old_status,
        "new_status": "UNDER_REVIEW"
    }, 200


def approve_course(course_id, admin_id, remarks=None):
    course = db.session.get(Course, course_id)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.status != "UNDER_REVIEW":
        return {
            "success": False,
            "message": "Only courses under review can be approved",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    old_status = course.status
    course.status = "APPROVED"

    add_status_history(
        course.course_id,
        old_status,
        "APPROVED",
        admin_id,
        remarks or "Course approved by administrator"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Course approved successfully",
        "course_id": course.course_id,
        "old_status": old_status,
        "new_status": "APPROVED"
    }, 200

    create_notification(
        user_id=course.trainer_id,
        title="Course Approved",
        message=f"Your Course '{course.title}' has been approved and published.",
        notification_type="COURSE_APPROVED"
    )

def reject_course(course_id, admin_id, remarks=None):
    course = db.session.get(Course, course_id)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.status != "UNDER_REVIEW":
        return {
            "success": False,
            "message": "Only courses under review can be rejected",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    old_status = course.status
    course.status = "REJECTED"

    add_status_history(
        course.course_id,
        old_status,
        "REJECTED",
        admin_id,
        remarks or "Course rejected by administrator"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Course rejected successfully",
        "course_id": course.course_id,
        "old_status": old_status,
        "new_status": "REJECTED"
    }, 200

    create_notification(
    user_id=course.trainer_id,
    title="Course Rejected",
    message=f"Your course '{course.title}' was rejected. Remarks: {remarks}",
    notification_type="COURSE_REJECTED"
    )

def move_to_revision(course_id, trainer_id, remarks=None):
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
            "message": "You can only revise your own course",
            "error_code": "FORBIDDEN"
        }, 403

    if course.status != "REJECTED":
        return {
            "success": False,
            "message": "Only rejected courses can be moved to revision",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    old_status = course.status
    course.status = "REVISION"

    add_status_history(
        course.course_id,
        old_status,
        "REVISION",
        trainer_id,
        remarks or "Trainer started course revision"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Course moved to revision",
        "course_id": course.course_id,
        "old_status": old_status,
        "new_status": "REVISION"
    }, 200


def publish_course(course_id, admin_id, remarks=None):
    course = db.session.get(Course, course_id)

    if not course:
        return {
            "success": False,
            "message": "Course not found",
            "error_code": "COURSE_NOT_FOUND"
        }, 404

    if course.status != "APPROVED":
        return {
            "success": False,
            "message": "Only approved courses can be published",
            "error_code": "INVALID_COURSE_STATUS"
        }, 409

    old_status = course.status
    course.status = "PUBLISHED"

    add_status_history(
        course.course_id,
        old_status,
        "PUBLISHED",
        admin_id,
        remarks or "Course published by administrator"
    )

    db.session.commit()

    return {
        "success": True,
        "message": "Course published successfully",
        "course_id": course.course_id,
        "old_status": old_status,
        "new_status": "PUBLISHED"
    }, 200