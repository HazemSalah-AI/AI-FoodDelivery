import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.core.errors import DomainError
from app.db.session import make_engine, make_sessions

logger = logging.getLogger("delivery")


def create_app(settings: Settings | None = None):
    settings = settings or Settings()
    engine = make_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.dispose()

    app = FastAPI(title="Abo Hammad Delivery", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.sessions = make_sessions(engine)
    app.state.engine = engine
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}}
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError):
        logger.warning("Database integrity conflict on %s", request.url.path)
        return JSONResponse(
            status_code=409,
            content={
                "error": {"code": "conflict", "message": "Record conflicts with existing data."}
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Never echo raw input (which may include a password) into logs/responses.
        fields = [
            {"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Check the supplied fields.",
                    "fields": fields,
                }
            },
        )

    @app.get("/api/v1/health", tags=["Health"])
    def health():
        return {"status": "ok"}

    from app.api.auth import router as auth_router
    from app.security.limiter import AuthLimiter

    app.state.auth_limiter = AuthLimiter()
    app.include_router(auth_router, prefix="/api/v1")
    from app.api.catalog import router as catalog_router

    app.include_router(catalog_router, prefix="/api/v1")
    from app.api.orders import router as orders_router

    app.include_router(orders_router, prefix="/api/v1")
    from app.api.operations import router as operations_router

    app.include_router(operations_router, prefix="/api/v1")
    return app
