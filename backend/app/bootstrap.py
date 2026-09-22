"""Explicit initial admin creation; password is prompted or supplied via ADMIN_PASSWORD."""

import getpass
import os

from sqlalchemy import select

from app.core.config import Settings
from app.db.session import make_engine, make_sessions
from app.models import City, User
from app.schemas.auth import Register
from app.security.passwords import hash_password


def main():
    settings = Settings()
    email = os.environ.get("ADMIN_EMAIL") or input("Admin email: ")
    name = os.environ.get("ADMIN_NAME") or input("Admin name: ")
    phone = os.environ.get("ADMIN_PHONE") or input("Admin phone: ")
    password = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Admin password (12+ chars): ")
    data = Register(email=email, name=name, phone=phone, password=password)
    engine = make_engine(settings.database_url)
    try:
        with make_sessions(engine).begin() as db:
            if db.scalar(select(User).where(User.role == "Admin")):
                raise SystemExit("An admin already exists. Existing accounts were not changed.")
            db.add(
                User(
                    name=data.name,
                    email=data.email,
                    phone=data.phone,
                    password_hash=hash_password(data.password),
                    role="Admin",
                )
            )
            if not db.scalar(select(City).where(City.name == "أبو حماد")):
                db.add(City(name="أبو حماد"))
        print("Initial admin and Abu Hammad city created.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
