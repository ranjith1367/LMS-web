from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.notification_controller import (
    list_notifications,
    get_single_notification,
    read_notification,
    read_all_notifications,
    remove_notification
)


notification_bp = Blueprint(
    "notification",
    __name__,
    url_prefix="/api/notifications"
)


@notification_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications_route():
    return list_notifications()


@notification_bp.route(
    "/<int:notification_id>",
    methods=["GET"]
)
@jwt_required()
def get_notification_route(notification_id):
    return get_single_notification(notification_id)


@notification_bp.route(
    "/<int:notification_id>/read",
    methods=["PATCH"]
)
@jwt_required()
def read_notification_route(notification_id):
    return read_notification(notification_id)


@notification_bp.route(
    "/read-all",
    methods=["PATCH"]
)
@jwt_required()
def read_all_notifications_route():
    return read_all_notifications()


@notification_bp.route(
    "/<int:notification_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_notification_route(notification_id):
    return remove_notification(notification_id)