from extensions import db


class Submission(db.Model):
    __tablename__ = "submissions"

    submission_id = db.Column(
        db.Integer,
        primary_key=True
    )

    assignment_id = db.Column(
        db.Integer,
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=True
    )

    comments = db.Column(
        db.Text,
        nullable=True
    )

    marks = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    feedback = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="PENDING"
    )

    submitted_at = db.Column(
        db.DateTime,
        nullable=True
    )

    evaluated_at = db.Column(
        db.DateTime,
        nullable=True
    )