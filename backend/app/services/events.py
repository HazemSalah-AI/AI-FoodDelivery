from sqlalchemy import select

from app.models import Notification, OrderHistory, User


def admins(db):
    return list(db.scalars(select(User.id).where(User.role == "Admin", User.is_active.is_(True))))


def notify(db, recipients, title, message, order_id=None):
    for identity in set(recipients):
        db.add(Notification(recipient_id=identity, order_id=order_id, title=title, message=message))


def order_event(db, order, actor, note=""):
    db.add(OrderHistory(order_id=order.id, actor_id=actor.id, status=order.status, note=note))
    notify(
        db,
        [order.customer_id, order.merchant_id, *admins(db)],
        f"Order #{order.id}: {order.status}",
        note or f"Your order is now {order.status}.",
        order.id,
    )
