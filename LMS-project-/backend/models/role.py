from extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship("User", back_populates="role")