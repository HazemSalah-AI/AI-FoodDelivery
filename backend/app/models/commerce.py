from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Timestamps, now

ORDER_STATES = (
    "Pending",
    "Accepted",
    "Preparing",
    "Ready",
    "OnDelivery",
    "Delivered",
    "Rejected",
    "Cancelled",
)
STATE_CHECK = "status IN ('Pending','Accepted','Preparing','Ready','OnDelivery','Delivered','Rejected','Cancelled')"


class Cart(Timestamps, Base):
    __tablename__ = "carts"
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    merchant_id: Mapped[int | None] = mapped_column(ForeignKey("merchants.id"), nullable=True)


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (CheckConstraint("quantity BETWEEN 1 AND 99", name="valid_quantity"),)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.customer_id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    quantity: Mapped[int]


class Order(Timestamps, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(STATE_CHECK, name="valid_status"),
        CheckConstraint("payment_method = 'Cash'", name="cash_only"),
        CheckConstraint("total_price >= 0 AND delivery_fee >= 0", name="nonnegative_total"),
        UniqueConstraint("customer_id", "idempotency_key"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), index=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    address_snapshot: Mapped[dict] = mapped_column(JSON)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    payment_method: Mapped[str] = mapped_column(String(10), default="Cash")
    status: Mapped[str] = mapped_column(String(20), default="Pending", index=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(64))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (CheckConstraint("quantity > 0 AND unit_price > 0", name="positive_purchase"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product_name: Mapped[str] = mapped_column(String(150))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class OrderHistory(Base):
    __tablename__ = "order_history"
    __table_args__ = (CheckConstraint(STATE_CHECK, name="valid_status"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Review(Timestamps, Base):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="rating_range"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), index=True)
    rating: Mapped[int]
    comment: Mapped[str] = mapped_column(Text, default="")


class Favorite(Base):
    __tablename__ = "favorites"
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), primary_key=True)
