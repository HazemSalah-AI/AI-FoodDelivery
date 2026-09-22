import hashlib
import secrets
from datetime import timedelta, timezone

import jwt
from fastapi import Request

from app.core.errors import DomainError
from app.db.base import now
from app.models import AuthSession, User

COOKIE = "delivery_session"
CSRF_COOKIE = "delivery_csrf"


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def csrf_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def create_session(db, user, settings):
    sid, csrf = secrets.token_hex(32), secrets.token_urlsafe(32)
    issued = now()
    expires = issued + timedelta(hours=settings.session_hours)
    db.add(AuthSession(id=sid, user_id=user.id, csrf_hash=csrf_hash(csrf), expires_at=expires))
    token = jwt.encode(
        {
            "sub": str(user.id),
            "jti": sid,
            "iat": issued,
            "exp": expires,
            "iss": "abo-hammad-delivery",
            "aud": "delivery-web",
        },
        settings.jwt_secret,
        algorithm="HS256",
    )
    return token, csrf


def read_identity(request: Request, db, optional=False):
    token = request.cookies.get(COOKIE)
    if not token and optional:
        return None
    try:
        payload = jwt.decode(
            token,
            request.app.state.settings.jwt_secret,
            algorithms=["HS256"],
            issuer="abo-hammad-delivery",
            audience="delivery-web",
            options={"require": ["sub", "jti", "exp", "iat"]},
        )
        session = db.get(AuthSession, payload["jti"])
        if not session or session.revoked or aware(session.expires_at) <= now():
            raise ValueError("Invalid session")
        user = db.get(User, int(payload["sub"]))
        if not user or not user.is_active or user.id != session.user_id:
            raise ValueError("Inactive user")
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise DomainError(401, "unauthenticated", "Please sign in again.") from None
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        csrf = request.headers.get("X-CSRF-Token", "")
        if not csrf or not secrets.compare_digest(session.csrf_hash, csrf_hash(csrf)):
            raise DomainError(403, "csrf_failed", "Refresh the page and try again.")
    request.state.auth_session = session
    return user


def check_origin(request):
    origin = request.headers.get("origin")
    if origin and origin not in request.app.state.settings.allowed_origins:
        raise DomainError(403, "origin_forbidden", "This origin is not allowed.")
