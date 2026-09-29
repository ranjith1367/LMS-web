from extensions import db


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    attempt_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    quiz_id = db.Column(
        db.Integer,
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        nullable=False
    )

    attempt_number = db.Column(
        db.Integer,
        nullable=False
    )

    started_at = db.Column(
        db.DateTime,
        nullable=False
    )

    submitted_at = db.Column(
        db.DateTime,
        nullable=True
    )

    score = db.Column(
        db.Numeric(5, 2),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="IN_PROGRESS"
    )