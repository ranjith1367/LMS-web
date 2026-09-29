from flask import jsonify

from services.progress_service import (
    mark_lesson_complete,
    get_lesson_progress,
    get_course_progress
)


def complete_lesson_for_student(student_id, lesson_id):
    progress = mark_lesson_complete(
        student_id,
        lesson_id
    )

    return jsonify({
        "success": True,
        "message": "Lesson marked as completed",
        "data": {
            "lesson_id": progress.lesson_id,
            "completed": progress.completed,
            "completed_at": (
                progress.completed_at.isoformat()
                if progress.completed_at
                else None
            )
        }
    }), 200


def get_lesson_progress_for_student(student_id, lesson_id):
    progress = get_lesson_progress(
        student_id,
        lesson_id
    )

    if progress is None:
        return jsonify({
            "success": True,
            "data": {
                "lesson_id": lesson_id,
                "completed": False,
                "completed_at": None
            }
        }), 200

    return jsonify({
        "success": True,
        "data": {
            "lesson_id": progress.lesson_id,
            "completed": progress.completed,
            "completed_at": (
                progress.completed_at.isoformat()
                if progress.completed_at
                else None
            )
        }
    }), 200


def get_course_progress_for_student(student_id, course_id):
    progress = get_course_progress(
        student_id,
        course_id
    )

    return jsonify({
        "success": True,
        "data": progress
    }), 200