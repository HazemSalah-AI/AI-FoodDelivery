import secrets

import pytest
from conftest import sign_in
from sqlalchemy import func, select
from test_catalog import ADDRESS, PRODUCT

from app.models import Notification, Order, Product


def place_order(client, quantity=2):
    sign_in(client, 2)
    product = client.post("/api/v1/products", json=PRODUCT).json()
    sign_in(client, 4)
    address = client.post("/api/v1/addresses", json=ADDRESS).json()
    assert (
        client.put(f"/api/v1/cart/items/{product['id']}", json={"quantity": quantity}).status_code
        == 200
    )
    payload = {"address_id": address["id"], "idempotency_key": secrets.token_hex(16)}
    response = client.post("/api/v1/checkout", json=payload)
    assert response.status_code == 201, response.text
    return response.json(), product, payload


def test_checkout_reprices_snapshots_and_is_idempotent(client, app):
    sign_in(client, 2)
    product = client.post("/api/v1/products", json=PRODUCT).json()
    sign_in(client, 4)
    address = client.post("/api/v1/addresses", json=ADDRESS).json()
    client.put(f"/api/v1/cart/items/{product['id']}", json={"quantity": 2})
    with app.state.sessions.begin() as db:
        db.get(Product, product["id"]).price = 40
    payload = {"address_id": address["id"], "idempotency_key": secrets.token_hex(16)}
    response = client.post("/api/v1/checkout", json=payload)
    assert response.status_code == 201, response.text
    result = response.json()
    assert result["total_price"] == "80.00"
    assert result["payment_method"] == "Cash"
    assert client.post("/api/v1/checkout", json=payload).json()["id"] == result["id"]
    client.patch(f"/api/v1/addresses/{address['id']}", json={**ADDRESS, "street": "Changed Street"})
    assert (
        client.get(f"/api/v1/orders/{result['id']}").json()["address_snapshot"]["street"]
        == ADDRESS["street"]
    )
    with app.state.sessions() as db:
        assert db.get(Product, product["id"]).stock_quantity == 18
        assert db.scalar(select(func.count()).select_from(Order)) == 1
        assert db.scalar(select(func.count()).select_from(Notification)) == 3
    assert client.get("/api/v1/cart").json()["items"] == []


@pytest.mark.parametrize("target,actor", [("Cancelled", 4), ("Rejected", 2)])
def test_terminal_pending_paths_restore_stock_once(client, app, target, actor):
    order, product, _ = place_order(client)
    sign_in(client, actor)
    url = f"/api/v1/orders/{order['id']}/transition"
    if target == "Rejected":
        assert client.post(url, json={"status": target}).status_code == 422
    response = client.post(url, json={"status": target, "reason": "Out of stock"})
    assert response.status_code == 200, response.text
    assert response.json()["history"][-1]["note"] == "Out of stock"
    assert client.post(url, json={"status": target, "reason": "Again"}).status_code == 409
    with app.state.sessions() as db:
        assert db.get(Product, product["id"]).stock_quantity == 20


def test_cancel_after_acceptance_blocked_and_merchant_transitions(client):
    order, _, _ = place_order(client)
    url = f"/api/v1/orders/{order['id']}/transition"
    sign_in(client, 2)
    assert client.post(url, json={"status": "Ready"}).status_code == 409
    assert client.post(url, json={"status": "Accepted"}).status_code == 200
    sign_in(client, 4)
    assert client.post(url, json={"status": "Cancelled"}).status_code == 409
    sign_in(client, 5)
    assert client.post(url, json={"status": "Preparing"}).status_code == 404
    sign_in(client, 2)
    assert client.post(url, json={"status": "Preparing"}).status_code == 200
    assert client.post(url, json={"status": "Ready"}).status_code == 200
    assert client.post(url, json={"status": "OnDelivery"}).status_code == 403


def test_ownership_and_checkout_rollback(client, app):
    order, product, payload = place_order(client)
    sign_in(client, 6)
    assert client.get(f"/api/v1/orders/{order['id']}").status_code == 404
    assert client.post("/api/v1/checkout", json=payload).status_code == 404
    sign_in(client, 4)
    client.put(f"/api/v1/cart/items/{product['id']}", json={"quantity": 3})
    with app.state.sessions.begin() as db:
        db.get(Product, product["id"]).stock_quantity = 1
    response = client.post(
        "/api/v1/checkout", json={**payload, "idempotency_key": secrets.token_hex(16)}
    )
    assert response.status_code == 409
    assert client.get("/api/v1/cart").json()["items"][0]["quantity"] == 3
    assert (
        client.post("/api/v1/checkout", json={**payload, "total_price": "0.01"}).status_code == 422
    )
    with app.state.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Order)) == 1
        assert db.get(Product, product["id"]).stock_quantity == 1


def test_cart_single_merchant_and_invalid_quantities(client):
    _, product, _ = place_order(client)
    sign_in(client, 5)
    other = client.post("/api/v1/products", json=PRODUCT).json()
    sign_in(client, 4)
    client.put(f"/api/v1/cart/items/{product['id']}", json={"quantity": 1})
    assert client.put(f"/api/v1/cart/items/{other['id']}", json={"quantity": 1}).status_code == 409
    assert (
        client.put(f"/api/v1/cart/items/{product['id']}", json={"quantity": 0}).status_code == 422
    )
    client.delete(f"/api/v1/cart/items/{product['id']}")
    assert client.put(f"/api/v1/cart/items/{other['id']}", json={"quantity": 1}).status_code == 200
