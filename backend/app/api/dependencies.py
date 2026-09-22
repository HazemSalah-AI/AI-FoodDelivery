from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session


def get_db(request: Request):
    # Function scope commits (or rolls back) before the HTTP response is sent.
    with request.app.state.sessions.begin() as db:
        yield db


DB = Annotated[Session, Depends(get_db, scope="function")]
