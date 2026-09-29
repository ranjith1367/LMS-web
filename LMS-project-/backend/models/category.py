from extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    category_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime
    )