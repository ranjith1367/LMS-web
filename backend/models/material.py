from extensions import db


class Material(db.Model):
    __tablename__ = "materials"

    material_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "lessons.lesson_id"
        ),
        nullable=False
    )

    material_name = db.Column(
        db.String(200),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=True
    )

    file_type = db.Column(
        db.String(50),
        nullable=True
    )

    file_size = db.Column(
        db.BigInteger,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )