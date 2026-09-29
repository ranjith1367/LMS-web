from extensions import db
from models.user import User
from models.role import Role


def create_user(data):
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    role_name = data.get("role")

    if not full_name or not email or not password or not role_name:
        return {
            "success": False,
            "message": "Required fields should not be empty",
            "error_code": "VALIDATION_ERROR"
        }, 400

    if role_name not in ["Student", "Trainer"]:
        return {
            "success": False,
            "message": "Administrator can create only Student or Trainer accounts",
            "error_code": "INVALID_ROLE"
        }, 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {
            "success": False,
            "message": "Email already exists",
            "error_code": "EMAIL_EXISTS"
        }, 409

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
        "message": "User created successfully",
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.role_name,
            "status": user.status
        }
    }, 201


def get_all_users():
    users = User.query.all()

    user_list = []

    for user in users:
        user_list.append({
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.role_name,
            "status": user.status,
            "created_at": user.created_at
        })

    return {
        "success": True,
        "users": user_list
    }, 200


def get_user_by_id(user_id):
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


def update_user(user_id, data):
    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found",
            "error_code": "USER_NOT_FOUND"
        }, 404

    full_name = data.get("full_name")
    email = data.get("email")
    role_name = data.get("role")
    status = data.get("status")

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

    if role_name:
        role = Role.query.filter_by(role_name=role_name).first()

        if not role:
            return {
                "success": False,
                "message": "Role not found",
                "error_code": "ROLE_NOT_FOUND"
            }, 404

        user.role_id = role.role_id

    if status:
        if status not in ["ACTIVE", "SUSPENDED", "DEACTIVATED"]:
            return {
                "success": False,
                "message": "Invalid status",
                "error_code": "INVALID_STATUS"
            }, 400

        user.status = status

    db.session.commit()

    return {
        "success": True,
        "message": "User updated successfully",
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.role_name,
            "status": user.status
        }
    }, 200