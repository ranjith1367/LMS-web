from flask import Blueprint

from flask_jwt_extended import jwt_required

from controllers.dashboard_controller import (
    admin_dashboard,
    trainer_dashboard,
    student_dashboard,
    trainer_students,
    reports
)


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard_bp.route(
    "/admin",
    methods=["GET"]
)
@jwt_required()
def admin_dashboard_route():
    return admin_dashboard()


@dashboard_bp.route(
    "/trainer",
    methods=["GET"]
)
@jwt_required()
def trainer_dashboard_route():
    return trainer_dashboard()

@dashboard_bp.route(
    "/trainer/students",
    methods=["GET"]
)
@jwt_required()
def trainer_students_route():
    return trainer_students()

@dashboard_bp.route(
    "/student",
    methods=["GET"]
)
@jwt_required()
def student_dashboard_route():
    return student_dashboard()


@dashboard_bp.route(
    "/reports",
    methods=["GET"]
)
@jwt_required()
def reports_route():
    return reports()