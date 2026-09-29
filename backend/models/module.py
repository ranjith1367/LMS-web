from extensions import db


class Module(db.Model):
    __tablename__ = "modules"

    module_id = db.Column(
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

    module_name = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    module_order = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )