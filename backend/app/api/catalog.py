from typing import Annotated, Literal

from fastapi import APIRouter, Query, Request
from sqlalchemy import select

from app.api.dependencies import DB, Admin, Customer, Manager, MerchantUser
from app.core.errors import DomainError
from app.models import Address, Area, AuditLog, Category, City, Merchant, Product, User
from app.repositories.common import get, owned, page
from app.schemas.auth import UserOut
from app.schemas.catalog import (
    ActiveWrite,
    AddressOut,
    AddressWrite,
    AdminCreateUser,
    AreaOut,
    AreaWrite,
    CategoryOut,
    CategoryWrite,
    CityOut,
    MerchantOut,
    MerchantStatus,
    MerchantWrite,
    Named,
    Page,
    ProductOut,
    ProductWrite,
)
from app.security.sessions import read_identity
from app.services import catalog

router = APIRouter(tags=["Catalog and accounts"])
PageNumber = Annotated[int, Query(ge=1, alias="page")]
PageSize = Annotated[int, Query(ge=1, le=100)]
Search = Annotated[str, Query(max_length=100)]


@router.get("/merchants", response_model=Page[MerchantOut])
def merchants(db: DB, q: Search = "", page_number: PageNumber = 1, page_size: PageSize = 30):
    stmt = (
        select(Merchant)
        .join(User, User.id == Merchant.id)
        .where(
            User.is_active.is_(True),
            Merchant.status == "Approved",
            Merchant.business_name.ilike(f"%{q}%"),
        )
        .order_by(Merchant.business_name)
    )
    return page(db, stmt, page_number, page_size)


@router.get("/merchants/{identity}", response_model=MerchantOut)
def merchant(identity: int, db: DB):
    return catalog.public_merchant(db, identity)


@router.get("/merchant/profile", response_model=MerchantOut)
def merchant_profile(user: MerchantUser, db: DB):
    return get(db, Merchant, user.id)


@router.patch("/merchant/profile", response_model=MerchantOut)
def update_merchant(data: MerchantWrite, user: MerchantUser, db: DB):
    profile = get(db, Merchant, user.id, lock=True)
    for key, value in data.model_dump().items():
        setattr(profile, key, value)
    db.flush()
    return profile


@router.get("/products", response_model=Page[ProductOut])
def products(
    request: Request,
    db: DB,
    merchant_id: int | None = None,
    category_id: int | None = None,
    q: Search = "",
    sort: Literal["name", "price", "-price"] = "name",
    managed: bool = False,
    page_number: PageNumber = 1,
    page_size: PageSize = 30,
):
    stmt = (
        select(Product)
        .join(Merchant, Merchant.id == Product.merchant_id)
        .join(User, User.id == Merchant.id)
    )
    if managed:
        user = read_identity(request, db)
        if user.role not in ("Merchant", "Admin"):
            raise DomainError(403, "forbidden", "Catalog management is restricted.")
        if user.role == "Merchant":
            stmt = stmt.where(Product.merchant_id == user.id)
    else:
        stmt = stmt.where(
            User.is_active.is_(True), Merchant.status == "Approved", Product.is_available.is_(True)
        )
    if merchant_id:
        stmt = stmt.where(Product.merchant_id == merchant_id)
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    stmt = stmt.where(Product.name.ilike(f"%{q}%")).order_by(
        {"name": Product.name, "price": Product.price, "-price": Product.price.desc()}[sort],
        Product.id,
    )
    return page(db, stmt, page_number, page_size)


@router.post("/products", response_model=ProductOut, status_code=201)
def new_product(data: ProductWrite, user: Manager, db: DB):
    return catalog.save_product(db, user, data)


@router.patch("/products/{identity}", response_model=ProductOut)
def edit_product(identity: int, data: ProductWrite, user: Manager, db: DB):
    return catalog.save_product(db, user, data, identity)


@router.get("/categories", response_model=Page[CategoryOut])
def categories(
    db: DB, merchant_id: int | None = None, page_number: PageNumber = 1, page_size: PageSize = 30
):
    stmt = select(Category).order_by(Category.name)
    if merchant_id:
        stmt = stmt.where(Category.merchant_id == merchant_id)
    return page(db, stmt, page_number, page_size)


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryWrite, user: Manager, db: DB):
    identity = catalog.owner_id(user, data.merchant_id)
    get(db, Merchant, identity)
    value = Category(name=data.name, merchant_id=identity)
    db.add(value)
    db.flush()
    return value


@router.patch("/categories/{identity}", response_model=CategoryOut)
def edit_category(identity: int, data: Named, user: Manager, db: DB):
    value = (
        get(db, Category, identity)
        if user.role == "Admin"
        else owned(db, Category, identity, user.id)
    )
    value.name = data.name
    db.flush()
    return value


@router.get("/cities", response_model=Page[CityOut])
def cities(db: DB, page_number: PageNumber = 1, page_size: PageSize = 30):
    return page(db, select(City).order_by(City.name), page_number, page_size)


@router.post("/cities", response_model=CityOut, status_code=201)
def create_city(data: Named, user: Admin, db: DB):
    value = City(name=data.name)
    db.add(value)
    db.flush()
    return value


@router.get("/areas", response_model=Page[AreaOut])
def areas(
    db: DB, city_id: int | None = None, page_number: PageNumber = 1, page_size: PageSize = 30
):
    stmt = select(Area).order_by(Area.name)
    if city_id:
        stmt = stmt.where(Area.city_id == city_id)
    return page(db, stmt, page_number, page_size)


@router.post("/areas", response_model=AreaOut, status_code=201)
def create_area(data: AreaWrite, user: Admin, db: DB):
    get(db, City, data.city_id)
    value = Area(**data.model_dump())
    db.add(value)
    db.flush()
    return value


@router.get("/addresses", response_model=list[AddressOut])
def addresses(user: Customer, db: DB):
    return list(
        db.scalars(
            select(Address)
            .where(Address.customer_id == user.id, Address.is_active.is_(True))
            .order_by(Address.is_default.desc(), Address.id)
        )
    )


@router.post("/addresses", response_model=AddressOut, status_code=201)
def new_address(data: AddressWrite, user: Customer, db: DB):
    return catalog.save_address(db, user, data)


@router.patch("/addresses/{identity}", response_model=AddressOut)
def edit_address(identity: int, data: AddressWrite, user: Customer, db: DB):
    return catalog.save_address(db, user, data, identity)


@router.delete("/addresses/{identity}", status_code=204)
def archive_address(identity: int, user: Customer, db: DB):
    value = owned(db, Address, identity, user.id, field="customer_id", lock=True)
    value.is_active = False
    value.is_default = False


@router.get("/admin/users", response_model=Page[UserOut])
def users(
    user: Admin,
    db: DB,
    role: Literal["Admin", "Merchant", "Driver", "Customer"] | None = None,
    q: Search = "",
    page_number: PageNumber = 1,
    page_size: PageSize = 30,
):
    stmt = select(User).where(User.name.ilike(f"%{q}%")).order_by(User.id)
    if role:
        stmt = stmt.where(User.role == role)
    return page(db, stmt, page_number, page_size)


@router.post("/admin/users", response_model=UserOut, status_code=201)
def create_user(data: AdminCreateUser, user: Admin, db: DB):
    return catalog.create_user(db, user, data)


@router.patch("/admin/users/{identity}", response_model=UserOut)
def active_user(identity: int, data: ActiveWrite, user: Admin, db: DB):
    return catalog.set_active(db, user, identity, data.is_active)


@router.patch("/admin/merchants/{identity}", response_model=MerchantOut)
def merchant_status(identity: int, data: MerchantStatus, user: Admin, db: DB):
    value = get(db, Merchant, identity, lock=True)
    value.status = data.status
    db.add(
        AuditLog(
            actor_id=user.id,
            action="merchant_status",
            resource_id=identity,
            details={"status": data.status},
        )
    )
    db.flush()
    return value


@router.get("/admin/merchants", response_model=Page[MerchantOut])
def managed_merchants(user: Admin, db: DB, page_number: PageNumber = 1, page_size: PageSize = 30):
    return page(db, select(Merchant).order_by(Merchant.business_name), page_number, page_size)
