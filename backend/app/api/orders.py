from fastapi import APIRouter

from app.api.catalog import PageNumber, PageSize
from app.api.dependencies import DB, CurrentUser, Customer
from app.repositories.common import page
from app.repositories.orders import visible_order, visible_orders
from app.schemas.catalog import Page
from app.schemas.orders import CartOut, Checkout, OrderOut, OrderStatus, Quantity, Transition
from app.services import cart, orders
from app.services.presenters import order_out

router = APIRouter(tags=["Cart and orders"])


@router.get("/cart", response_model=CartOut)
def get_cart(user: Customer, db: DB):
    return cart.cart_out(db, user)


@router.put("/cart/items/{identity}", response_model=CartOut)
def set_item(identity: int, data: Quantity, user: Customer, db: DB):
    return cart.set_item(db, user, identity, data.quantity)


@router.delete("/cart/items/{identity}", status_code=204)
def remove_item(identity: int, user: Customer, db: DB):
    cart.remove_item(db, user, identity)


@router.post("/checkout", response_model=OrderOut, status_code=201)
def checkout(data: Checkout, user: Customer, db: DB):
    return order_out(db, cart.checkout(db, user, data))


@router.get("/orders", response_model=Page[OrderOut])
def list_orders(
    user: CurrentUser,
    db: DB,
    status: OrderStatus | None = None,
    page_number: PageNumber = 1,
    page_size: PageSize = 30,
):
    from app.models import Order

    stmt = visible_orders(user).order_by(Order.id.desc())
    if status:
        stmt = stmt.where(Order.status == status)
    result = page(db, stmt, page_number, page_size)
    result["items"] = [order_out(db, value) for value in result["items"]]
    return result


@router.get("/orders/{identity}", response_model=OrderOut)
def get_order(identity: int, user: CurrentUser, db: DB):
    return order_out(db, visible_order(db, user, identity))


@router.post("/orders/{identity}/transition", response_model=OrderOut)
def transition(identity: int, data: Transition, user: CurrentUser, db: DB):
    return order_out(db, orders.transition(db, user, identity, data))
