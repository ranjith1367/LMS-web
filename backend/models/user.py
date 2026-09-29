from extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.role_id"),
        nullable=False
    )

    status = db.Column(
        db.Enum("ACTIVE", "SUSPENDED", "DEACTIVATED"),
        default="ACTIVE"
    )

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    role = db.relationship("Role", back_populates="users")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(
            self.password_hash,
            password
        )