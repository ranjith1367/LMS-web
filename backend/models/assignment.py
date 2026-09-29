from extensions import db


class Assignment(db.Model):
    __tablename__ = "assignments"

    assignment_id = db.Column(
        db.Integer,
        primary_key=True
    )

    course_id = db.Column(
        db.Integer,
        nullable=False
    )

    module_id = db.Column(
        db.Integer,
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    maximum_marks = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    deadline = db.Column(
        db.DateTime,
        nullable=False
    )

    allowed_file_types = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=True
    )