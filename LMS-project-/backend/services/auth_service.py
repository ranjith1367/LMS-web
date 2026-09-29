from flask_jwt_extended import create_access_token

from extensions import db
from models.user import User
from models.role import Role


def register_user(data):
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    role_name = data.get("role", "Student")

    if not full_name or not email or not password or not confirm_password:
        return {
            "success": False,
            "message": "Required fields should not be empty",
            "error_code": "VALIDATION_ERROR"
        }, 400

    if password != confirm_password:
        return {
            "success": False,
            "message": "Password and Confirm Password should match",
            "error_code": "PASSWORD_MISMATCH"
        }, 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {
            "success": False,
            "message": "Email already exists",
            "error_code": "EMAIL_EXISTS"
        }, 409

    if role_name not in ["Student", "Trainer"]:
        return {
            "success": False,
            "message": "Invalid role for registration",
            "error_code": "INVALID_ROLE"
        }, 400

    role = Role.query.filter_by(role_name=role_name).first()

    if not role:
        return {
            "success": False,
            "message": "Role not found",
            "error_code": "ROLE_NOT_FOUND"
        }, 404

    user = User(
        full_name=full_name,
        email=email,
        role_id=role.role_id,
        status="ACTIVE"
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return {
        "success": True,
        "message": "User registered successfully",
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": role.role_name,
            "status": user.status
        }
    }, 201


def login_user(data):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {
            "success": False,
            "message": "Email and Password are required",
            "error_code": "VALIDATION_ERROR"
        }, 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return {
            "success": False,
            "message": "Invalid email or password",
            "error_code": "INVALID_CREDENTIALS"
        }, 401

    if user.status != "ACTIVE":
        return {
            "success": False,
            "message": "User account is not active",
            "error_code": "ACCOUNT_INACTIVE"
        }, 403

    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={
            "role": user.role.role_name,
            "role_id": user.role_id
        }
    )

    return {
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.role_name,
            "status": user.status
        }
    }, 200


def get_user_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found",
            "error_code": "USER_NOT_FOUND"
        }, 404

    return {
        "success": True,
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.role_name,
            "status": user.status,
            "created_at": user.created_at
        }
    }, 200


def update_user_profile(user_id, data):
    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found",
            "error_code": "USER_NOT_FOUND"
        }, 404

    full_name = data.get("full_name")
    email = data.get("email")

    if email and email != user.email:
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return {
                "success": False,
                "message": "Email already exists",
                "error_code": "EMAIL_EXISTS"
            }, 409

        user.email = email

    if full_name:
        user.full_name = full_name

    db.session.commit()

    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.role_name,
            "status": user.status
        }
    }, 200