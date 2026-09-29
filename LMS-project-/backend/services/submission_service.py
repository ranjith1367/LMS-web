from datetime import datetime

from models.submission import Submission
from models.assignment import Assignment
from extensions import db

import os
import uuid
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

SUBMISSION_FOLDER = os.path.join(
    BASE_DIR,
    "database",
    "submissions"
)

MAX_FILE_SIZE = 50 * 1024 * 1024


def save_submission_file(file, allowed_file_types):
    if not file or not file.filename:
        return None, "Submission file is required"

    safe_filename = secure_filename(file.filename)

    if "." not in safe_filename:
        return None, "File extension is required"

    extension = safe_filename.rsplit(".", 1)[1].lower()

    if allowed_file_types:
        allowed = [
            t.strip().lower().lstrip(".")
            for t in allowed_file_types.split(",")
            if t.strip()
        ]

        if allowed and extension not in allowed:
            return None, f"Allowed file types: {allowed_file_types}"

    file.stream.seek(0, os.SEEK_END)
    file_size = file.stream.tell()
    file.stream.seek(0)

    if file_size <= 0:
        return None, "Uploaded file is empty"

    if file_size > MAX_FILE_SIZE:
        return None, "File size must not exceed 50 MB"

    os.makedirs(SUBMISSION_FOLDER, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}.{extension}"
    full_file_path = os.path.join(SUBMISSION_FOLDER, stored_filename)
    database_file_path = f"/database/submissions/{stored_filename}"

    file.save(full_file_path)

    return database_file_path, None

def create_submission(
    assignment_id,
    student_id,
    file=None,
    comments=None
):
    assignment = Assignment.query.get(assignment_id)

    if assignment is None:
        return None, "Assignment not found"

    existing = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=student_id
    ).first()

    if existing:
        return None, "Submission already exists"

    file_path, error = save_submission_file(
        file,
        assignment.allowed_file_types
    )

    if error:
        return None, error

    now = datetime.utcnow()

    status = "SUBMITTED"

    if assignment.deadline and now > assignment.deadline:
        status = "LATE"

    submission = Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        file_path=file_path,
        comments=comments,
        status=status,
        submitted_at=now
    )

    db.session.add(submission)
    db.session.commit()

    return submission, None

def get_submission(submission_id):
    return Submission.query.get(submission_id)


def update_submission(
    submission_id,
    file_path=None,
    comments=None
):
    submission = Submission.query.get(submission_id)

    if submission is None:
        return None, "Submission not found"

    if submission.status == "EVALUATED":
        return None, "Evaluated submissions cannot be modified"

    if file_path is not None:
        submission.file_path = file_path

    if comments is not None:
        submission.comments = comments

    db.session.commit()

    return submission, None


def get_assignment_submissions(assignment_id):
    return Submission.query.filter_by(
        assignment_id=assignment_id
    ).all()


def evaluate_submission(
    submission_id,
    marks,
    feedback
):
    submission = Submission.query.get(submission_id)

    if submission is None:
        return None, "Submission not found"

    assignment = Assignment.query.get(
        submission.assignment_id
    )

    if assignment is None:
        return None, "Assignment not found"

    if marks < 0:
        return None, "Marks cannot be negative"

    if marks > float(assignment.maximum_marks):
        return None, "Marks cannot exceed maximum marks"

    submission.marks = marks
    submission.feedback = feedback
    submission.status = "EVALUATED"
    submission.evaluated_at = datetime.utcnow()

    db.session.commit()

    return submission, None