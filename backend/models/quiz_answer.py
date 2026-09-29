from extensions import db


class QuizAnswer(db.Model):
    __tablename__ = "quiz_answers"

    answer_id = db.Column(
        db.Integer,
        primary_key=True
    )

    attempt_id = db.Column(
        db.Integer,
        nullable=False
    )

    question_id = db.Column(
        db.Integer,
        nullable=False
    )

    selected_option = db.Column(
        db.String(1),
        nullable=True
    )

    marks_awarded = db.Column(
        db.Numeric(10, 2),
        nullable=True,
        default=0.00
    )