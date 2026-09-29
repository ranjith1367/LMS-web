from extensions import db


class Question(db.Model):
    __tablename__ = "questions"

    question_id = db.Column(
        db.Integer,
        primary_key=True
    )

    quiz_id = db.Column(
        db.Integer,
        nullable=False
    )

    question_text = db.Column(
        db.Text,
        nullable=False
    )

    option_a = db.Column(
        db.String(500),
        nullable=False
    )

    option_b = db.Column(
        db.String(500),
        nullable=False
    )

    option_c = db.Column(
        db.String(500),
        nullable=False
    )

    option_d = db.Column(
        db.String(500),
        nullable=False
    )

    correct_option = db.Column(
        db.String(1),
        nullable=False
    )

    marks = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )