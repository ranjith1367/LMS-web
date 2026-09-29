from datetime import datetime

from extensions import db


class Certificate(db.Model):
    __tablename__ = "certificates"

    certificate_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    certificate_number = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.course_id"),
        nullable=False
    )

    issued_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )