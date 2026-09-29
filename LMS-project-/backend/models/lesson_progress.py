from datetime import datetime

from extensions import db


class LessonProgress(db.Model):
    __tablename__ = "lesson_progress"

    progress_id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        nullable=False
    )

    lesson_id = db.Column(
        db.Integer,
        nullable=False
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "lesson_id",
            name="unique_student_lesson"
        ),
    )