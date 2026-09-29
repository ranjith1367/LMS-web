from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from services.notification_service import (
    get_user_notifications,
    get_notification,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification
)


def get_current_user_id():
    identity = get_jwt_identity()

    if isinstance(identity, dict):
        return int(identity["user_id"])

    return int(identity)


def notification_to_dict(notification):
    return {
        "notification_id": notification.notification_id,
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "is_read": notification.is_read,
        "created_at": (
            notification.created_at.isoformat()
            if notification.created_at
            else None
        )
    }


def list_notifications():
    user_id = get_current_user_id()

    notifications = get_user_notifications(user_id)

    return jsonify({
        "success": True,
        "data": [
            notification_to_dict(notification)
            for notification in notifications
        ]
    }), 200


def get_single_notification(notification_id):
    user_id = get_current_user_id()

    notification = get_notification(notification_id)

    if notification is None:
        return jsonify({
            "success": False,
            "message": "Notification not found"
        }), 404

    if notification.user_id != user_id:
        return jsonify({
            "success": False,
            "message": "You cannot access this notification"
        }), 403

    return jsonify({
        "success": True,
        "data": notification_to_dict(notification)
    }), 200


def read_notification(notification_id):
    user_id = get_current_user_id()

    notification = get_notification(notification_id)

    if notification is None:
        return jsonify({
            "success": False,
            "message": "Notification not found"
        }), 404

    if notification.user_id != user_id:
        return jsonify({
            "success": False,
            "message": "You cannot modify this notification"
        }), 403

    notification = mark_notification_as_read(
        notification
    )

    return jsonify({
        "success": True,
        "message": "Notification marked as read",
        "data": notification_to_dict(notification)
    }), 200


def read_all_notifications():
    user_id = get_current_user_id()

    mark_all_notifications_as_read(user_id)

    return jsonify({
        "success": True,
        "message": "All notifications marked as read"
    }), 200


def remove_notification(notification_id):
    user_id = get_current_user_id()

    notification = get_notification(notification_id)

    if notification is None:
        return jsonify({
            "success": False,
            "message": "Notification not found"
        }), 404

    if notification.user_id != user_id:
        return jsonify({
            "success": False,
            "message": "You cannot delete this notification"
        }), 403

    delete_notification(notification)

    return jsonify({
        "success": True,
        "message": "Notification deleted successfully"
    }), 200