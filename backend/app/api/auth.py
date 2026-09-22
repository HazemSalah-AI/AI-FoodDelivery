from fastapi import APIRouter, Request, Response

from app.api.dependencies import DB, CurrentUser
from app.schemas.auth import Login, LoginOut, ProfileUpdate, Register, UserOut
from app.security.sessions import COOKIE, CSRF_COOKIE, check_origin
from app.services import auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


def guard(request):
    check_origin(request)
    request.app.state.auth_limiter.check(request.client.host if request.client else "unknown")


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: Register, request: Request, db: DB):
    guard(request)
    return auth.register(db, data)


@router.post("/login", response_model=LoginOut)
def login(data: Login, request: Request, response: Response, db: DB):
    guard(request)
    settings = request.app.state.settings
    user, token, csrf = auth.login(db, data, settings)
    response.set_cookie(
        COOKIE,
        token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/api/v1",
        max_age=settings.session_hours * 3600,
    )
    response.set_cookie(
        CSRF_COOKIE,
        csrf,
        httponly=False,
        secure=settings.secure_cookies,
        samesite="strict",
        path="/",
        max_age=settings.session_hours * 3600,
    )
    response.headers["Cache-Control"] = "no-store"
    return {"user": user, "csrf_token": csrf}


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return user


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, user: CurrentUser):
    request.state.auth_session.revoked = True
    response.delete_cookie(COOKIE, path="/api/v1")
    response.delete_cookie(CSRF_COOKIE, path="/")


@router.patch("/profile", response_model=UserOut)
def profile(data: ProfileUpdate, db: DB, user: CurrentUser):
    user.name, user.phone = data.name, data.phone
    db.flush()
    return user
