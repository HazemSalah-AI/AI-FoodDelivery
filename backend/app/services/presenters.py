from sqlalchemy import select

from app.models import Assignment, Merchant, OrderHistory, OrderItem, User


def order_out(db, order):
    customer = db.get(User, order.customer_id)
    merchant = db.get(Merchant, order.merchant_id)
    # Explicit allowlist: no driver object, location, credentials or auth session is serialized.
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "merchant_id": order.merchant_id,
        "customer_name": customer.name,
        "customer_phone": customer.phone,
        "merchant_name": merchant.business_name,
        "status": order.status,
        "payment_method": order.payment_method,
        "total_price": order.total_price,
        "delivery_fee": order.delivery_fee,
        "address_snapshot": order.address_snapshot,
        "rejection_reason": order.rejection_reason,
        "created_at": order.created_at,
        "items": list(
            db.scalars(
                select(OrderItem).where(OrderItem.order_id == order.id).order_by(OrderItem.id)
            )
        ),
        "history": list(
            db.scalars(
                select(OrderHistory)
                .where(OrderHistory.order_id == order.id)
                .order_by(OrderHistory.id)
            )
        ),
        "assignment": db.scalar(
            select(Assignment)
            .where(Assignment.order_id == order.id)
            .order_by(Assignment.id.desc())
            .limit(1)
        ),
    }
