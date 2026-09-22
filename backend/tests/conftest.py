import os
import secrets

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url

from app.core.config import Settings
from app.main import create_app
from app.models import Base, City, Driver, Merchant, User
from app.security.passwords import hash_password

PASSWORD = secrets.token_urlsafe(24)
HASHED = hash_password(PASSWORD)


@pytest.fixture
def app(tmp_path):
    url = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{tmp_path}/app.db")
    if not url.startswith("sqlite") and not (make_url(url).database or "").endswith("_test"):
        raise RuntimeError("TEST_DATABASE_URL must point to an isolated database ending in _test")
    settings = Settings(
        database_url=url, jwt_secret=secrets.token_hex(48), environment="test", secure_cookies=False
    )
    app = create_app(settings)
    engine = app.state.engine
    if url.startswith("sqlite"):
        Base.metadata.create_all(engine)
    else:
        assert set(Base.metadata.tables) <= set(inspect(engine).get_table_names()), (
            "Run migrations first"
        )
        with engine.begin() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
    with app.state.sessions.begin() as db:
        for i, role in [
            (1, "Admin"),
            (2, "Merchant"),
            (3, "Driver"),
            (4, "Customer"),
            (5, "Merchant"),
            (6, "Customer"),
            (7, "Driver"),
        ]:
            db.add(
                User(
                    id=i,
                    name=f"Test {role} {i}",
                    email=f"user{i}@example.com",
                    phone=f"0100000000{i}",
                    password_hash=HASHED,
                    role=role,
                )
            )
        db.flush()
        db.add_all(
            [
                Merchant(id=2, business_name="سوق أبو حماد"),
                Merchant(id=5, business_name="مخبز البلد"),
                Driver(id=3),
                Driver(id=7),
                City(id=1, name="أبو حماد"),
            ]
        )
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(
                text("SELECT setval(pg_get_serial_sequence('users', 'id'), 7, true)")
            )
            connection.execute(
                text("SELECT setval(pg_get_serial_sequence('cities', 'id'), 1, true)")
            )
    yield app
    engine.dispose()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


def sign_in(client, user_id):
    response = client.post(
        "/api/v1/auth/login", json={"email": f"user{user_id}@example.com", "password": PASSWORD}
    )
    assert response.status_code == 200, response.text
    client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    return response
