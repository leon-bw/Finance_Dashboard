"""
Helpers for creating user notifications.

Kept separate from the router so other parts of the app (e.g. the learning
engine) can raise notifications without importing router modules.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from .models import Notification


def create_notification(
    db: Session,
    user_id: UUID,
    type: str,
    title: str,
    message: str,
    icon: str | None = None,
) -> Notification:
    """
    Create and stage a notification (caller is responsible for committing).
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        icon=icon,
    )
    db.add(notification)
    return notification
