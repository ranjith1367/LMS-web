from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from services.submission_service import (
    create_submission,
    get_submission,
    update_submission,
    get_assignment_submissions,
    evaluate_submission
)

def submit_assignment(assignment_id):
    student_id = get_jwt_identity()

    if isinstance(student_id, dict):
        student_id = student_id.get("user_id")

    student_id = int(student_id)

    comments = request.form.get("comments")
    file = request.files.get("file")

    submission, error = create_submission(
        assignment_id=assignment_id,
        student_id=student_id,
        file=file,
        comments=comments
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    return jsonify({
        "success": True,
        "message": "Assignment submitted successfully",
        "data": {
            "submission_id": submission.submission_id,
            "assignment_id": submission.assignment_id,
            "student_id": submission.student_id,
            "file_path": submission.file_path,
            "comments": submission.comments,
            "status": submission.status,
            "submitted_at": (
                submission.submitted_at.isoformat()
                if submission.submitted_at
                else None
            )
        }
    }), 201

def get_single_submission(submission_id):
    submission = get_submission(submission_id)

    if submission is None:
        return jsonify({
            "success": False,
            "message": "Submission not found"
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "submission_id": submission.submission_id,
            "assignment_id": submission.assignment_id,
            "student_id": submission.student_id,
            "file_path": submission.file_path,
            "comments": submission.comments,
            "marks": (
                float(submission.marks)
                if submission.marks is not None
                else None
            ),
            "feedback": submission.feedback,
            "status": submission.status,
            "submitted_at": (
                submission.submitted_at.isoformat()
                if submission.submitted_at
                else None
            ),
            "evaluated_at": (
                submission.evaluated_at.isoformat()
                if submission.evaluated_at
                else None
            )
        }
    }), 200


def update_existing_submission(submission_id):
    data = request.get_json() or {}

    submission, error = update_submission(
        submission_id=submission_id,
        file_path=data.get("file_path"),
        comments=data.get("comments")
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    return jsonify({
        "success": True,
        "message": "Submission updated successfully"
    }), 200


def list_assignment_submissions(assignment_id):
    submissions = get_assignment_submissions(
        assignment_id
    )

    return jsonify({
        "success": True,
        "data": [
            {
                "submission_id": submission.submission_id,
                "assignment_id": submission.assignment_id,
                "student_id": submission.student_id,
                "file_path": submission.file_path,
                "comments": submission.comments,
                "marks": (
                    float(submission.marks)
                    if submission.marks is not None
                    else None
                ),
                "feedback": submission.feedback,
                "status": submission.status,
                "submitted_at": (
                    submission.submitted_at.isoformat()
                    if submission.submitted_at
                    else None
                ),
                "evaluated_at": (
                    submission.evaluated_at.isoformat()
                    if submission.evaluated_at
                    else None
                )
            }
            for submission in submissions
        ]
    }), 200


def evaluate_existing_submission(submission_id):
    data = request.get_json() or {}

    marks = data.get("marks")
    feedback = data.get("feedback")

    if marks is None:
        return jsonify({
            "success": False,
            "message": "Marks are required"
        }), 400

    try:
        marks = float(marks)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Marks must be a number"
        }), 400

    submission, error = evaluate_submission(
        submission_id=submission_id,
        marks=marks,
        feedback=feedback
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    return jsonify({
        "success": True,
        "message": "Submission evaluated successfully",
        "data": {
            "submission_id": submission.submission_id,
            "marks": float(submission.marks),
            "feedback": submission.feedback,
            "status": submission.status
        }
    }), 200