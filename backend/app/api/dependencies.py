from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.models import User
from app.security.sessions import read_identity


def get_db(request: Request):
    # Function scope commits (or rolls back) before the HTTP response is sent.
    with request.app.state.sessions.begin() as db:
        yield db


DB = Annotated[Session, Depends(get_db, scope="function")]


def current_user(request: Request, db: DB):
    return read_identity(request, db)


CurrentUser = Annotated[User, Depends(current_user)]


def require(*roles):
    def allowed(user: CurrentUser):
        if user.role not in roles:
            raise DomainError(403, "forbidden", "This action is not allowed for your account.")
        return user

    return allowed


Customer = Annotated[User, Depends(require("Customer"))]
MerchantUser = Annotated[User, Depends(require("Merchant"))]
DriverUser = Annotated[User, Depends(require("Driver"))]
Admin = Annotated[User, Depends(require("Admin"))]
Manager = Annotated[User, Depends(require("Admin", "Merchant"))]
