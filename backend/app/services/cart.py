from decimal import Decimal

from sqlalchemy import delete, select

from app.core.errors import DomainError
from app.models import Address, Cart, CartItem, Order, OrderItem, Product, User
from app.repositories.common import get, owned
from app.services.catalog import public_merchant
from app.services.events import order_event


def locked_cart(db, user):
    get(db, User, user.id, lock=True)
    cart = db.get(Cart, user.id)
    if not cart:
        cart = Cart(customer_id=user.id)
        db.add(cart)
        db.flush()
    return cart


def cart_out(db, user):
    cart = db.get(Cart, user.id)
    rows = db.execute(
        select(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .where(CartItem.cart_id == user.id)
        .order_by(Product.id)
    ).all()
    items = [
        {
            "product_id": p.id,
            "name": p.name,
            "price": p.price,
            "quantity": line.quantity,
            "stock_quantity": p.stock_quantity,
            "is_available": p.is_available,
        }
        for line, p in rows
    ]
    return {
        "merchant_id": cart.merchant_id if cart else None,
        "items": items,
        "subtotal": sum((p.price * line.quantity for line, p in rows), Decimal("0.00")),
    }


def set_item(db, user, identity, quantity):
    cart = locked_cart(db, user)
    product = get(db, Product, identity)
    merchant = public_merchant(db, product.merchant_id)
    if not merchant.is_open or not product.is_available or product.stock_quantity < quantity:
        raise DomainError(409, "unavailable", "Product or requested quantity is unavailable.")
    if cart.merchant_id not in (None, product.merchant_id):
        raise DomainError(
            409, "single_merchant", "Finish or empty your cart before choosing another merchant."
        )
    cart.merchant_id = product.merchant_id
    item = db.get(CartItem, (user.id, identity))
    if not item:
        item = CartItem(cart_id=user.id, product_id=identity)
    item.quantity = quantity
    db.add(item)
    db.flush()
    return cart_out(db, user)


def remove_item(db, user, identity):
    cart = locked_cart(db, user)
    db.execute(delete(CartItem).where(CartItem.cart_id == user.id, CartItem.product_id == identity))
    if not db.scalar(select(CartItem.product_id).where(CartItem.cart_id == user.id).limit(1)):
        cart.merchant_id = None


def checkout(db, user, data):
    cart = locked_cart(db, user)
    previous = db.scalar(
        select(Order).where(
            Order.customer_id == user.id, Order.idempotency_key == data.idempotency_key
        )
    )
    if previous:
        if previous.address_id != data.address_id:
            raise DomainError(
                409, "idempotency_conflict", "This checkout key belongs to a different address."
            )
        return previous
    address = owned(db, Address, data.address_id, user.id, field="customer_id")
    if not address.is_active:
        raise DomainError(409, "address_archived", "Choose an active address.")
    lines = list(
        db.scalars(
            select(CartItem).where(CartItem.cart_id == user.id).order_by(CartItem.product_id)
        )
    )
    if not lines:
        raise DomainError(409, "empty_cart", "Your cart is empty.")
    merchant = public_merchant(db, cart.merchant_id)
    if not merchant.is_open:
        raise DomainError(409, "merchant_closed", "The merchant is currently closed.")
    products = list(
        db.scalars(
            select(Product)
            .where(Product.id.in_([line.product_id for line in lines]))
            .order_by(Product.id)
            .with_for_update()
        )
    )
    by_id = {p.id: p for p in products}
    total = Decimal("0.00")
    for line in lines:
        product = by_id.get(line.product_id)
        if (
            not product
            or product.merchant_id != cart.merchant_id
            or not product.is_available
            or product.stock_quantity < line.quantity
        ):
            raise DomainError(
                409, "stock_conflict", "Availability changed. Please review your cart."
            )
        total += product.price * line.quantity
    order = Order(
        customer_id=user.id,
        merchant_id=cart.merchant_id,
        address_id=address.id,
        address_snapshot={
            "title": address.title,
            "street": address.street,
            "latitude": str(address.latitude),
            "longitude": str(address.longitude),
            "city_id": address.city_id,
        },
        total_price=total,
        status="Pending",
        payment_method="Cash",
        idempotency_key=data.idempotency_key,
    )
    db.add(order)
    db.flush()
    for line in lines:
        product = by_id[line.product_id]
        product.stock_quantity -= line.quantity
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=line.quantity,
                unit_price=product.price,
            )
        )
    db.execute(delete(CartItem).where(CartItem.cart_id == user.id))
    cart.merchant_id = None
    order_event(db, order, user)
    db.flush()
    return order
