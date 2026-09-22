import secrets

from sqlalchemy import select

from app.core.errors import DomainError
from app.models import User
from app.security.passwords import hash_password, hasher, verify_password
from app.security.sessions import create_session

# Equal-cost check for unknown accounts; never a usable account credential.
DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


def register(db, data):
    user = User(
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        password_hash=hash_password(data.password),
        role="Customer",
    )
    db.add(user)
    db.flush()
    return user


def login(db, data, settings):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    valid = verify_password(user.password_hash if user else DUMMY_HASH, data.password)
    if not valid or not user or not user.is_active:
        raise DomainError(401, "invalid_credentials", "Invalid email or password.")
    if hasher.check_needs_rehash(user.password_hash):
        user.password_hash = hash_password(data.password)
    token, csrf = create_session(db, user, settings)
    db.flush()
    return user, token, csrf
