from sqlalchemy import select, update

from app.core.errors import DomainError
from app.models import (
    Address,
    Area,
    Assignment,
    AuditLog,
    Category,
    City,
    Driver,
    Merchant,
    Product,
    User,
)
from app.repositories.common import get, owned
from app.security.passwords import hash_password


def public_merchant(db, identity):
    merchant = db.scalar(
        select(Merchant)
        .join(User, User.id == Merchant.id)
        .where(Merchant.id == identity, Merchant.status == "Approved", User.is_active.is_(True))
    )
    if not merchant:
        raise DomainError(404, "not_found", "Merchant not found.")
    return merchant


def owner_id(user, submitted):
    if user.role == "Merchant":
        if submitted is not None and submitted != user.id:
            raise DomainError(403, "forbidden", "You can manage only your business.")
        return user.id
    if submitted is None:
        raise DomainError(422, "merchant_required", "Choose a merchant.")
    return submitted


def save_product(db, user, data, identity=None):
    if identity:
        product = get(db, Product, identity, lock=True)
        if user.role != "Admin" and product.merchant_id != user.id:
            raise DomainError(404, "not_found", "Product not found.")
        merchant_id = product.merchant_id
        if data.merchant_id not in (None, merchant_id):
            raise DomainError(409, "immutable_merchant", "A product cannot change merchant.")
    else:
        merchant_id = owner_id(user, data.merchant_id)
        get(db, Merchant, merchant_id)
        product = Product(merchant_id=merchant_id)
    if data.category_id:
        owned(db, Category, data.category_id, merchant_id)
    for key, value in data.model_dump(exclude={"merchant_id"}).items():
        setattr(product, key, value)
    db.add(product)
    db.flush()
    return product


def save_address(db, user, data, identity=None):
    get(db, User, user.id, lock=True)
    get(db, City, data.city_id)
    if data.area_id:
        owned(db, Area, data.area_id, data.city_id, field="city_id")
    address = (
        owned(db, Address, identity, user.id, field="customer_id", lock=True)
        if identity
        else Address(customer_id=user.id)
    )
    if identity and not address.is_active:
        raise DomainError(404, "not_found", "Address not found.")
    if data.is_default:
        db.execute(update(Address).where(Address.customer_id == user.id).values(is_default=False))
    for key, value in data.model_dump().items():
        setattr(address, key, value)
    db.add(address)
    db.flush()
    return address


def create_user(db, admin, data):
    if data.role == "Merchant" and not data.business_name:
        raise DomainError(422, "business_name_required", "Merchant needs a business name.")
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        role=data.role,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.flush()
    if user.role == "Merchant":
        db.add(Merchant(id=user.id, business_name=data.business_name))
    if user.role == "Driver":
        db.add(Driver(id=user.id))
    db.add(
        AuditLog(
            actor_id=admin.id,
            action="create_user",
            resource_id=user.id,
            details={"role": user.role},
        )
    )
    db.flush()
    return user


def set_active(db, admin, identity, active):
    user = get(db, User, identity, lock=True)
    if user.id == admin.id and not active:
        raise DomainError(409, "self_suspend", "You cannot suspend your own account.")
    if (
        not active
        and user.role == "Driver"
        and db.scalar(
            select(Assignment.id).where(
                Assignment.driver_id == identity, Assignment.status.in_(["Pending", "Accepted"])
            )
        )
    ):
        raise DomainError(409, "active_delivery", "Resolve the active delivery before suspension.")
    user.is_active = active
    db.add(
        AuditLog(
            actor_id=admin.id,
            action="activate_user" if active else "suspend_user",
            resource_id=identity,
        )
    )
    db.flush()
    return user
