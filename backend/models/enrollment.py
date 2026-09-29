from extensions import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    enrollment_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
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

    status = db.Column(
        db.Enum(
            "ACTIVE",
            "COMPLETED",
            "CANCELLED"
        ),
        nullable=True,
        server_default="ACTIVE"
    )

    enrolled_at = db.Column(
        db.DateTime,
        nullable=True,
        server_default=db.func.current_timestamp()
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )