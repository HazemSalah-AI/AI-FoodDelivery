from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.auth import Input
from app.schemas.catalog import Output


class Assign(Input):
    driver_id: int = Field(gt=0)


class AssignmentResponse(Input):
    accept: bool
    reason: str | None = Field(default=None, max_length=255)


class Availability(Input):
    is_available: bool


class Location(Input):
    latitude: Decimal = Field(ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal = Field(ge=-180, le=180, max_digits=10, decimal_places=7)


class AvailabilityOut(Output):
    is_available: bool
    last_seen: datetime | None
    busy: bool


class DriverOut(AvailabilityOut):
    id: int
    name: str
    phone: str
    is_active: bool
    latitude: Decimal | None
    longitude: Decimal | None
    location_updated_at: datetime | None


class NotificationOut(Output):
    id: int
    order_id: int | None
    title: str
    message: str
    is_read: bool
    created_at: datetime


class ReviewWrite(Input):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=2000)


class ReviewOut(Output):
    id: int
    merchant_id: int
    rating: int
    comment: str
    created_at: datetime


class DashboardOut(Output):
    orders_total: int
    pending: int
    ready: int
    on_delivery: int
    delivered: int
    cod_total: Decimal
