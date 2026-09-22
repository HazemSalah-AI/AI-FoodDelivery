from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.auth import Input
from app.schemas.catalog import Output

OrderStatus = Literal[
    "Pending", "Accepted", "Preparing", "Ready", "OnDelivery", "Delivered", "Rejected", "Cancelled"
]


class Quantity(Input):
    quantity: int = Field(ge=1, le=99)


class Checkout(Input):
    address_id: int = Field(gt=0)
    idempotency_key: str = Field(min_length=8, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")


class Transition(Input):
    status: OrderStatus
    reason: str | None = Field(default=None, max_length=255)


class CartLine(Output):
    product_id: int
    name: str
    price: Decimal
    quantity: int
    stock_quantity: int
    is_available: bool


class CartOut(Output):
    merchant_id: int | None
    items: list[CartLine]
    subtotal: Decimal
    delivery_fee: Decimal = Decimal("0.00")


class PurchaseLine(Output):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal


class HistoryOut(Output):
    status: str
    note: str
    created_at: datetime


class AssignmentOut(Output):
    id: int
    order_id: int
    driver_id: int
    status: str
    reason: str | None
    created_at: datetime


class AddressSnapshot(Output):
    title: str
    street: str
    latitude: str
    longitude: str
    city_id: int


class OrderOut(Output):
    id: int
    customer_id: int
    merchant_id: int
    customer_name: str
    customer_phone: str
    merchant_name: str
    status: OrderStatus
    payment_method: Literal["Cash"]
    total_price: Decimal
    delivery_fee: Decimal
    address_snapshot: AddressSnapshot
    rejection_reason: str | None
    created_at: datetime
    items: list[PurchaseLine]
    history: list[HistoryOut]
    assignment: AssignmentOut | None
