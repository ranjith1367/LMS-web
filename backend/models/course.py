from extensions import db


class Course(db.Model):
    __tablename__ = "courses"

    course_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id"),
        nullable=False
    )

    trainer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
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

    learning_objectives = db.Column(
        db.Text,
        nullable=True
    )

    thumbnail = db.Column(
        db.String(500),
        nullable=True
    )

    level = db.Column(
        db.Enum(
            "BEGINNER",
            "INTERMEDIATE",
            "ADVANCED"
        ),
        nullable=True
    )

    duration = db.Column(
        db.Integer,
        nullable=True
    )

    status = db.Column(
        db.Enum(
            "DRAFT",
            "SUBMITTED",
            "UNDER_REVIEW",
            "APPROVED",
            "PUBLISHED",
            "REJECTED",
            "ARCHIVED",
            "REVISION",
            "RESUBMITTED"
        ),
        nullable=False,
        server_default="DRAFT"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        server_onupdate=db.func.current_timestamp()
    )