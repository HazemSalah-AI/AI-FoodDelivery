from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Timestamps


class Merchant(Timestamps, Base):
    __tablename__ = "merchants"
    __table_args__ = (
        CheckConstraint("status IN ('Pending','Approved','Rejected')", name="valid_status"),
    )
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    business_name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="Approved")
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)


class City(Timestamps, Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Area(Timestamps, Base):
    __tablename__ = "areas"
    __table_args__ = (UniqueConstraint("city_id", "name"), UniqueConstraint("id", "city_id"))
    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))


class Address(Timestamps, Base):
    __tablename__ = "addresses"
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="longitude"),
        ForeignKeyConstraint(["area_id", "city_id"], ["areas.id", "areas.city_id"]),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(255))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    area_id: Mapped[int | None] = mapped_column(nullable=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Category(Timestamps, Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("merchant_id", "name"),
        UniqueConstraint("id", "merchant_id"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))


class Product(Timestamps, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price > 0", name="positive_price"),
        CheckConstraint("stock_quantity >= 0", name="nonnegative_stock"),
        ForeignKeyConstraint(
            ["category_id", "merchant_id"], ["categories.id", "categories.merchant_id"]
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), index=True)
    category_id: Mapped[int | None] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock_quantity: Mapped[int] = mapped_column(default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
