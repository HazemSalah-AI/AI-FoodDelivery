from sqlalchemy import func, select

from app.core.errors import DomainError


def get(db, model, identity, *, lock=False):
    stmt = select(model).where(model.id == identity)
    value = db.scalar(
        stmt.with_for_update().execution_options(populate_existing=True) if lock else stmt
    )
    if value is None:
        raise DomainError(404, "not_found", "Record not found.")
    return value


def owned(db, model, identity, owner_id, field="merchant_id", lock=False):
    value = get(db, model, identity, lock=lock)
    if getattr(value, field) != owner_id:
        raise DomainError(404, "not_found", "Record not found.")
    return value


def page(db, statement, page=1, page_size=30):
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery()))
    return {
        "items": list(db.scalars(statement.limit(page_size).offset((page - 1) * page_size))),
        "total": total,
        "page": page,
        "page_size": page_size,
    }
