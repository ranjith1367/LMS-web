from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from services.quiz_attempt_service import (
    start_attempt,
    get_attempt,
    submit_attempt,
    get_quiz_results
)


def get_current_student_id():
    student_id = get_jwt_identity()

    if isinstance(student_id, dict):
        student_id = student_id.get("user_id")

    return int(student_id)


def start_quiz_attempt(quiz_id):
    student_id = get_current_student_id()

    attempt, error = start_attempt(
        quiz_id=quiz_id,
        student_id=student_id
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    return jsonify({
        "success": True,
        "message": "Quiz attempt started",
        "data": {
            "attempt_id": attempt.attempt_id,
            "quiz_id": attempt.quiz_id,
            "attempt_number": attempt.attempt_number,
            "started_at": (
                attempt.started_at.isoformat()
                if attempt.started_at
                else None
            ),
            "status": attempt.status
        }
    }), 201


def get_single_attempt(attempt_id):
    student_id = get_current_student_id()

    attempt, error = get_attempt(
        attempt_id=attempt_id,
        student_id=student_id
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "attempt_id": attempt.attempt_id,
            "quiz_id": attempt.quiz_id,
            "attempt_number": attempt.attempt_number,
            "started_at": (
                attempt.started_at.isoformat()
                if attempt.started_at
                else None
            ),
            "submitted_at": (
                attempt.submitted_at.isoformat()
                if attempt.submitted_at
                else None
            ),
            "score": (
                float(attempt.score)
                if attempt.score is not None
                else None
            ),
            "status": attempt.status,
            "passed": attempt.status == "PASSED"
        }
    }), 200


def submit_quiz_attempt(attempt_id):
    student_id = get_current_student_id()

    data = request.get_json() or {}

    answers = data.get("answers", [])

    if not isinstance(answers, list):
        return jsonify({
            "success": False,
            "message": "answers must be a list"
        }), 400

    attempt, error = submit_attempt(
        attempt_id=attempt_id,
        student_id=student_id,
        answers=answers
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    return jsonify({
        "success": True,
        "message": "Quiz submitted successfully",
        "data": {
            "attempt_id": attempt.attempt_id,
            "score": float(attempt.score),
            "passed": attempt.status == "PASSED",
            "status": attempt.status,
            "submitted_at": (
                attempt.submitted_at.isoformat()
                if attempt.submitted_at
                else None
            )
        }
    }), 200


def get_quiz_results_controller(quiz_id):
    student_id = get_current_student_id()

    results, error = get_quiz_results(
        quiz_id=quiz_id,
        student_id=student_id
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "data": results
    }), 200