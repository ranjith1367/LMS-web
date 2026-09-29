from extensions import db
from models.notification import Notification


def create_notification(
    user_id,
    title,
    message,
    notification_type
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False
    )

    db.session.add(notification)
    db.session.commit()

    return notification


def get_user_notifications(user_id):
    return Notification.query.filter_by(
        user_id=user_id
    ).order_by(
        Notification.created_at.desc()
    ).all()


def get_notification(notification_id):
    return Notification.query.get(notification_id)


def mark_notification_as_read(notification):
    notification.is_read = True

    db.session.commit()

    return notification


def mark_all_notifications_as_read(user_id):
    Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).update(
        {"is_read": True},
        synchronize_session=False
    )

    db.session.commit()


def delete_notification(notification):
    db.session.delete(notification)
    db.session.commit()