from datetime import timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.core.errors import DomainError
from app.db.base import now
from app.models import Assignment, AuditLog, Driver, Order, Review, User
from app.repositories.common import get, owned
from app.repositories.orders import visible_order, visible_orders
from app.security.sessions import aware
from app.services.events import admins, notify

ACTIVE = ("Pending", "Accepted")


def is_fresh(driver):
    return bool(
        driver.is_available
        and driver.last_seen
        and aware(driver.last_seen) > now() - timedelta(minutes=30)
    )


def availability(db, driver):
    return {
        "is_available": is_fresh(driver),
        "last_seen": driver.last_seen,
        "busy": bool(
            db.scalar(
                select(Assignment.id).where(
                    Assignment.driver_id == driver.id, Assignment.status.in_(ACTIVE)
                )
            )
        ),
    }


def assign(db, admin, identity, driver_id):
    order = get(db, Order, identity, lock=True)
    if order.status != "Ready":
        raise DomainError(409, "order_not_ready", "Driver assignment requires a Ready order.")
    driver = get(db, Driver, driver_id, lock=True)
    account = get(db, User, driver_id, lock=True)
    if not account.is_active or not is_fresh(driver):
        raise DomainError(
            409, "driver_unavailable", "Choose an active, available driver with a recent heartbeat."
        )
    if db.scalar(
        select(Assignment.id).where(
            Assignment.status.in_(ACTIVE),
            (Assignment.driver_id == driver_id) | (Assignment.order_id == identity),
        )
    ):
        raise DomainError(
            409, "assignment_conflict", "Order or driver already has an active assignment."
        )
    assignment = Assignment(order_id=identity, driver_id=driver_id, assigned_by=admin.id)
    db.add(assignment)
    db.add(
        AuditLog(
            actor_id=admin.id,
            action="assign_driver",
            resource_id=identity,
            details={"driver_id": driver_id},
        )
    )
    notify(
        db,
        [driver_id],
        f"New delivery #{identity}",
        "Please accept or reject this delivery.",
        identity,
    )
    notify(
        db,
        [order.customer_id],
        f"Order #{identity}",
        "A driver has been assigned; awaiting confirmation.",
        identity,
    )
    db.flush()
    return assignment


def respond(db, user, identity, data):
    existing = owned(db, Assignment, identity, user.id, field="driver_id")
    order = get(db, Order, existing.order_id, lock=True)
    assignment = get(db, Assignment, identity, lock=True)
    if assignment.status != "Pending" or order.status != "Ready":
        raise DomainError(409, "invalid_assignment", "This assignment can no longer be answered.")
    assignment.status = "Accepted" if data.accept else "Rejected"
    assignment.reason = None if data.accept else (data.reason or "Driver declined delivery.")
    get(db, Driver, user.id, lock=True).last_seen = now()
    db.add(
        AuditLog(
            actor_id=user.id,
            action="accept_assignment" if data.accept else "reject_assignment",
            resource_id=order.id,
        )
    )
    notify(
        db,
        [*admins(db), order.merchant_id],
        f"Delivery #{order.id}: {assignment.status}",
        assignment.reason or "Driver accepted the delivery.",
        order.id,
    )
    db.flush()
    return assignment


def driver_out(db, driver):
    user = db.get(User, driver.id)
    return {
        "id": driver.id,
        "name": user.name,
        "phone": user.phone,
        "is_active": user.is_active,
        "latitude": driver.latitude,
        "longitude": driver.longitude,
        "location_updated_at": driver.location_updated_at,
        **availability(db, driver),
    }


def dashboard(db, user):
    statement = visible_orders(user).subquery()
    rows = db.execute(select(statement.c.status, func.count()).group_by(statement.c.status)).all()
    counts = dict(rows)
    total = db.scalar(
        select(func.sum(statement.c.total_price)).where(statement.c.status == "Delivered")
    ) or Decimal("0.00")
    return {
        "orders_total": sum(counts.values()),
        "pending": counts.get("Pending", 0),
        "ready": counts.get("Ready", 0),
        "on_delivery": counts.get("OnDelivery", 0),
        "delivered": counts.get("Delivered", 0),
        "cod_total": total,
    }


def review(db, user, identity, data):
    order = visible_order(db, user, identity, lock=True)
    if order.status != "Delivered":
        raise DomainError(409, "not_delivered", "Only delivered orders can be reviewed.")
    if db.scalar(select(Review.id).where(Review.order_id == identity)):
        raise DomainError(409, "already_reviewed", "This order already has a review.")
    value = Review(
        order_id=identity, customer_id=user.id, merchant_id=order.merchant_id, **data.model_dump()
    )
    db.add(value)
    db.flush()
    return value
