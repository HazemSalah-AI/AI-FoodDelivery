from conftest import PASSWORD, sign_in
from sqlalchemy import select

from app.models import User


def test_registration_login_logout_revocation(client, app):
    data = {
        "name": "New Customer",
        "email": "NEW@example.com",
        "phone": "01112345678",
        "password": PASSWORD,
    }
    result = client.post("/api/v1/auth/register", json=data)
    assert result.status_code == 201
    assert result.json()["role"] == "Customer"
    assert "password_hash" not in result.text
    with app.state.sessions() as db:
        assert db.scalar(
            select(User).where(User.email == "new@example.com")
        ).password_hash.startswith("$argon2id$")
    sign_in(client, 4)
    token = client.cookies.get("delivery_session")
    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 204
    client.cookies.set("delivery_session", token, path="/api/v1")
    assert client.get("/api/v1/auth/me").status_code == 401


def test_customer_cannot_register_privileged_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Wrong Role",
            "email": "x@example.com",
            "phone": "01112345678",
            "password": PASSWORD,
            "role": "Admin",
        },
    )
    assert response.status_code == 422
    assert PASSWORD not in response.text


def test_csrf_and_origin(client):
    sign_in(client, 4)
    del client.headers["X-CSRF-Token"]
    assert (
        client.patch(
            "/api/v1/auth/profile", json={"name": "Changed", "phone": "01112345678"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            headers={"Origin": "https://untrusted.example"},
            json={"email": "user4@example.com", "password": PASSWORD},
        ).status_code
        == 403
    )


def test_duplicate_phone_and_invalid_password(client):
    result = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Duplicate",
            "email": "unique@example.com",
            "phone": "01000000004",
            "password": PASSWORD,
        },
    )
    assert result.status_code == 409
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "user4@example.com", "password": "wrong"}
        ).status_code
        == 401
    )
    assert client.get("/api/v1/auth/me").status_code == 401


def test_suspended_user_session_denied(client, app):
    sign_in(client, 4)
    with app.state.sessions.begin() as db:
        db.get(User, 4).is_active = False
    assert client.get("/api/v1/auth/me").status_code == 401


def test_auth_rate_limit(client):
    for _ in range(20):
        response = client.post(
            "/api/v1/auth/login", json={"email": "missing@example.com", "password": "wrong"}
        )
        assert response.status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "missing@example.com", "password": "wrong"}
        ).status_code
        == 429
    )
