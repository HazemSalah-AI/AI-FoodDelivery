from fastapi import APIRouter
from sqlalchemy import delete, select

from app.api.catalog import PageNumber, PageSize
from app.api.dependencies import DB, Admin, CurrentUser, Customer, DriverUser, MerchantUser
from app.db.base import now
from app.models import Assignment, Driver, Favorite, Merchant, Notification, Review, User
from app.repositories.common import get, owned, page
from app.schemas.catalog import MerchantOut, Page
from app.schemas.operations import (
    Assign,
    AssignmentResponse,
    Availability,
    AvailabilityOut,
    DashboardOut,
    DriverOut,
    Location,
    NotificationOut,
    ReviewOut,
    ReviewWrite,
)
from app.schemas.orders import AssignmentOut
from app.services import operations
from app.services.catalog import public_merchant

router = APIRouter(tags=["Delivery and operations"])


@router.post("/orders/{identity}/assignments", response_model=AssignmentOut, status_code=201)
def assign(identity: int, data: Assign, user: Admin, db: DB):
    return operations.assign(db, user, identity, data.driver_id)


@router.get("/assignments", response_model=Page[AssignmentOut])
def assignments(user: CurrentUser, db: DB, page_number: PageNumber = 1, page_size: PageSize = 30):
    from app.core.errors import DomainError

    if user.role not in ("Driver", "Admin"):
        raise DomainError(403, "forbidden", "Assignments are restricted.")
    stmt = select(Assignment).order_by(Assignment.id.desc())
    if user.role == "Driver":
        stmt = stmt.where(Assignment.driver_id == user.id)
    return page(db, stmt, page_number, page_size)


@router.post("/assignments/{identity}/respond", response_model=AssignmentOut)
def respond(identity: int, data: AssignmentResponse, user: DriverUser, db: DB):
    return operations.respond(db, user, identity, data)


@router.get("/driver/availability", response_model=AvailabilityOut)
def get_availability(user: DriverUser, db: DB):
    return operations.availability(db, get(db, Driver, user.id))


@router.put("/driver/availability", response_model=AvailabilityOut)
def availability(data: Availability, user: DriverUser, db: DB):
    driver = get(db, Driver, user.id, lock=True)
    driver.is_available = data.is_available
    driver.last_seen = now()
    db.flush()
    return operations.availability(db, driver)


@router.post("/driver/heartbeat", response_model=AvailabilityOut)
def heartbeat(user: DriverUser, db: DB):
    driver = get(db, Driver, user.id, lock=True)
    driver.last_seen = now()
    db.flush()
    return operations.availability(db, driver)


@router.put("/driver/location")
def location(data: Location, user: DriverUser, db: DB):
    driver = get(db, Driver, user.id, lock=True)
    driver.latitude = data.latitude
    driver.longitude = data.longitude
    driver.location_updated_at = now()
    driver.last_seen = now()
    db.flush()
    return {"updated_at": driver.location_updated_at}


@router.get("/admin/drivers", response_model=Page[DriverOut])
def drivers(user: Admin, db: DB, page_number: PageNumber = 1, page_size: PageSize = 30):
    result = page(db, select(Driver).order_by(Driver.id), page_number, page_size)
    result["items"] = [operations.driver_out(db, driver) for driver in result["items"]]
    return result


@router.get("/admin/dashboard", response_model=DashboardOut)
def admin_dashboard(user: Admin, db: DB):
    return operations.dashboard(db, user)


@router.get("/merchant/dashboard", response_model=DashboardOut)
def merchant_dashboard(user: MerchantUser, db: DB):
    return operations.dashboard(db, user)


@router.get("/driver/dashboard", response_model=DashboardOut)
def driver_dashboard(user: DriverUser, db: DB):
    return operations.dashboard(db, user)


@router.get("/notifications", response_model=Page[NotificationOut])
def notifications(
    user: CurrentUser,
    db: DB,
    unread: bool = False,
    page_number: PageNumber = 1,
    page_size: PageSize = 30,
):
    stmt = (
        select(Notification)
        .where(Notification.recipient_id == user.id)
        .order_by(Notification.id.desc())
    )
    if unread:
        stmt = stmt.where(Notification.is_read.is_(False))
    return page(db, stmt, page_number, page_size)


@router.patch("/notifications/{identity}/read", response_model=NotificationOut)
def mark_read(identity: int, user: CurrentUser, db: DB):
    value = owned(db, Notification, identity, user.id, field="recipient_id")
    value.is_read = True
    db.flush()
    return value


@router.post("/orders/{identity}/review", response_model=ReviewOut, status_code=201)
def review(identity: int, data: ReviewWrite, user: Customer, db: DB):
    return operations.review(db, user, identity, data)


@router.get("/merchants/{identity}/reviews", response_model=Page[ReviewOut])
def reviews(identity: int, db: DB, page_number: PageNumber = 1, page_size: PageSize = 30):
    public_merchant(db, identity)
    return page(
        db,
        select(Review).where(Review.merchant_id == identity).order_by(Review.id.desc()),
        page_number,
        page_size,
    )


@router.get("/favorites", response_model=Page[MerchantOut])
def favorites(user: Customer, db: DB, page_number: PageNumber = 1, page_size: PageSize = 30):
    stmt = (
        select(Merchant)
        .join(Favorite, Favorite.merchant_id == Merchant.id)
        .join(User, User.id == Merchant.id)
        .where(
            Favorite.customer_id == user.id, Merchant.status == "Approved", User.is_active.is_(True)
        )
        .order_by(Merchant.business_name)
    )
    return page(db, stmt, page_number, page_size)


@router.put("/favorites/{identity}", status_code=204)
def add_favorite(identity: int, user: Customer, db: DB):
    get(db, User, user.id, lock=True)
    public_merchant(db, identity)
    if not db.get(Favorite, (user.id, identity)):
        db.add(Favorite(customer_id=user.id, merchant_id=identity))


@router.delete("/favorites/{identity}", status_code=204)
def remove_favorite(identity: int, user: Customer, db: DB):
    get(db, User, user.id, lock=True)
    db.execute(
        delete(Favorite).where(Favorite.customer_id == user.id, Favorite.merchant_id == identity)
    )
