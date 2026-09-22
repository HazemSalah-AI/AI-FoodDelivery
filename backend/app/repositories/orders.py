from sqlalchemy import select

from app.core.errors import DomainError
from app.models import Assignment, Order


def visible_orders(user):
    stmt = select(Order)
    if user.role == "Customer":
        stmt = stmt.where(Order.customer_id == user.id)
    elif user.role == "Merchant":
        stmt = stmt.where(Order.merchant_id == user.id)
    elif user.role == "Driver":
        stmt = stmt.where(
            Order.id.in_(
                select(Assignment.order_id).where(
                    Assignment.driver_id == user.id,
                    Assignment.status.in_(["Pending", "Accepted", "Completed"]),
                )
            )
        )
    return stmt


def visible_order(db, user, identity, lock=False):
    stmt = visible_orders(user).where(Order.id == identity)
    value = db.scalar(stmt.with_for_update() if lock else stmt)
    if not value:
        raise DomainError(404, "not_found", "Order not found.")
    return value
