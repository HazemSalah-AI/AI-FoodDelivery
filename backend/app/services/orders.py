from sqlalchemy import select

from app.core.errors import DomainError
from app.db.base import now
from app.models import Assignment, OrderItem, Product
from app.repositories.orders import visible_order
from app.services.events import notify, order_event

TRANSITIONS = {
    "Pending": {"Accepted", "Rejected", "Cancelled"},
    "Accepted": {"Preparing"},
    "Preparing": {"Ready"},
    "Ready": {"OnDelivery"},
    "OnDelivery": {"Delivered"},
}
ROLE_TARGETS = {
    "Customer": {"Cancelled"},
    "Merchant": {"Accepted", "Rejected", "Preparing", "Ready"},
    "Driver": {"OnDelivery", "Delivered"},
    "Admin": {"Accepted", "Rejected", "Cancelled", "Preparing", "Ready", "OnDelivery", "Delivered"},
}


def transition(db, user, identity, data):
    order = visible_order(db, user, identity, lock=True)
    if data.status not in ROLE_TARGETS[user.role]:
        raise DomainError(403, "forbidden", "Your role cannot perform this transition.")
    if data.status not in TRANSITIONS.get(order.status, set()):
        raise DomainError(
            409, "invalid_transition", f"Cannot change {order.status} to {data.status}."
        )
    if data.status == "Rejected" and not data.reason:
        raise DomainError(422, "reason_required", "Please provide the rejection reason.")
    assignment = db.scalar(
        select(Assignment)
        .where(Assignment.order_id == order.id, Assignment.status == "Accepted")
        .with_for_update()
    )
    if data.status in {"OnDelivery", "Delivered"}:
        if not assignment or (user.role == "Driver" and assignment.driver_id != user.id):
            raise DomainError(
                409, "assignment_required", "An accepted driver assignment is required."
            )
    if data.status in {"Rejected", "Cancelled"}:
        lines = list(db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)))
        products = list(
            db.scalars(
                select(Product)
                .where(Product.id.in_([x.product_id for x in lines]))
                .order_by(Product.id)
                .with_for_update()
            )
        )
        quantities = {x.product_id: x.quantity for x in lines}
        for product in products:
            product.stock_quantity += quantities[product.id]
    order.status = data.status
    if data.status == "Rejected":
        order.rejection_reason = data.reason
    if data.status == "Delivered":
        order.delivered_at = now()
        assignment.status = "Completed"
    order_event(db, order, user, data.reason or "")
    if assignment:
        notify(
            db,
            [assignment.driver_id],
            f"Order #{order.id}: {order.status}",
            f"Order is now {order.status}.",
            order.id,
        )
    db.flush()
    return order
