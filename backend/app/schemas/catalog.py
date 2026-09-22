from decimal import Decimal
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.auth import Input, Register

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class Output(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MerchantOut(Output):
    id: int
    business_name: str
    description: str
    status: str
    is_open: bool


class MerchantWrite(Input):
    business_name: str = Field(min_length=2, max_length=150)
    description: str = Field(default="", max_length=2000)
    is_open: bool = True


class Named(Input):
    name: str = Field(min_length=2, max_length=100)


class CityOut(Output):
    id: int
    name: str


class AreaWrite(Named):
    city_id: int = Field(gt=0)


class AreaOut(CityOut):
    city_id: int


class CategoryWrite(Named):
    merchant_id: int | None = Field(default=None, gt=0)


class CategoryOut(CityOut):
    merchant_id: int


class ProductWrite(Input):
    merchant_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(default="", max_length=3000)
    price: Decimal = Field(gt=0, le=9999999, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(ge=0, le=1000000)
    is_available: bool = True


class ProductOut(Output):
    id: int
    merchant_id: int
    category_id: int | None
    name: str
    description: str
    price: Decimal
    stock_quantity: int
    is_available: bool


class AddressWrite(Input):
    title: str = Field(min_length=2, max_length=100)
    street: str = Field(min_length=5, max_length=255)
    city_id: int = Field(gt=0)
    area_id: int | None = Field(default=None, gt=0)
    latitude: Decimal = Field(ge=-90, le=90, max_digits=10, decimal_places=7)
    longitude: Decimal = Field(ge=-180, le=180, max_digits=10, decimal_places=7)
    is_default: bool = False


class AddressOut(Output):
    id: int
    title: str
    street: str
    city_id: int
    area_id: int | None
    latitude: Decimal
    longitude: Decimal
    is_default: bool


class AdminCreateUser(Register):
    role: Literal["Customer", "Merchant", "Driver"]
    business_name: str | None = Field(default=None, min_length=2, max_length=150)


class ActiveWrite(Input):
    is_active: bool


class MerchantStatus(Input):
    status: Literal["Pending", "Approved", "Rejected"]
