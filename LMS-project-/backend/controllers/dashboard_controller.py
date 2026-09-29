from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from services.dashboard_service import (
    get_user_role,
    get_admin_dashboard,
    get_trainer_dashboard,
    get_trainer_students,
    get_student_dashboard,
    get_reports
)


def current_user_id():
    identity = get_jwt_identity()

    if isinstance(identity, dict):
        return int(identity["user_id"])

    return int(identity)


def admin_dashboard():
    user_id = current_user_id()
    role = get_user_role(user_id)

    if role != "Administrator":
        return jsonify({
            "success": False,
            "message": "Administrator access required"
        }), 403

    return jsonify({
        "success": True,
        "data": get_admin_dashboard()
    }), 200


def trainer_dashboard():
    user_id = current_user_id()
    role = get_user_role(user_id)

    if role != "Trainer":
        return jsonify({
            "success": False,
            "message": "Trainer access required"
        }), 403

    return jsonify({
        "success": True,
        "data": get_trainer_dashboard(user_id)
    }), 200

def trainer_students():
    user_id = current_user_id()
    role = get_user_role(user_id)

    if role != "Trainer":
        return jsonify({
            "success": False,
            "message": "Trainer access required"
        }), 403

    return jsonify({
        "success": True,
        "data": get_trainer_students(user_id)
    }), 200

def student_dashboard():
    user_id = current_user_id()
    role = get_user_role(user_id)

    if role != "Student":
        return jsonify({
            "success": False,
            "message": "Student access required"
        }), 403

    return jsonify({
        "success": True,
        "data": get_student_dashboard(user_id)
    }), 200


def reports():
    user_id = current_user_id()
    role = get_user_role(user_id)

    if role != "Administrator":
        return jsonify({
            "success": False,
            "message": "Administrator access required"
        }), 403

    return jsonify({
        "success": True,
        "data": get_reports()
    }), 200