from extensions import db


class Quiz(db.Model):
    __tablename__ = "quizzes"

    quiz_id = db.Column(
        db.Integer,
        primary_key=True
    )

    course_id = db.Column(
        db.Integer,
        nullable=False
    )

    module_id = db.Column(
        db.Integer,
        nullable=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    time_limit = db.Column(
        db.Integer,
        nullable=False
    )

    maximum_attempts = db.Column(
        db.Integer,
        nullable=False
    )

    passing_score = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=True
    )

    is_final_assessment = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )