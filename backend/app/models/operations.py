from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Timestamps, now


class Driver(Timestamps, Base):
    __tablename__ = "drivers"
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="longitude"),
        CheckConstraint("(latitude IS NULL) = (longitude IS NULL)", name="coordinate_pair"),
    )
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), default="Motorcycle")
    is_available: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    location_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Assignment(Timestamps, Base):
    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('Pending','Accepted','Rejected','Completed')", name="valid_status"
        ),
        Index(
            "uq_assignment_active_order",
            "order_id",
            unique=True,
            postgresql_where=text("status IN ('Pending','Accepted')"),
            sqlite_where=text("status IN ('Pending','Accepted')"),
        ),
        Index(
            "uq_assignment_active_driver",
            "driver_id",
            unique=True,
            postgresql_where=text("status IN ('Pending','Accepted')"),
            sqlite_where=text("status IN ('Pending','Accepted')"),
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(150))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(100))
    resource_id: Mapped[int | None] = mapped_column(nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
