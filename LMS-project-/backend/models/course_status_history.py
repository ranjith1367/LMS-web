from extensions import db


class CourseStatusHistory(db.Model):
    __tablename__ = "course_status_history"

    history_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "courses.course_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    old_status = db.Column(
        db.Enum(
            "DRAFT",
            "SUBMITTED",
            "UNDER_REVIEW",
            "APPROVED",
            "PUBLISHED",
            "ARCHIVED",
            "REJECTED",
            "REVISION",
            "RESUBMITTED"
        ),
        nullable=True
    )

    new_status = db.Column(
        db.Enum(
            "DRAFT",
            "SUBMITTED",
            "UNDER_REVIEW",
            "APPROVED",
            "PUBLISHED",
            "ARCHIVED",
            "REJECTED",
            "REVISION",
            "RESUBMITTED"
        ),
        nullable=False
    )

    changed_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.user_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    changed_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )