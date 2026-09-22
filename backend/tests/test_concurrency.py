import os
import secrets
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from conftest import sign_in
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from test_catalog import ADDRESS, PRODUCT
from test_delivery import available, ready_order
from test_orders import place_order

from app.models import Assignment, Order, Product

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL", "").startswith("postgresql"),
    reason="Requires real PostgreSQL row-lock semantics; exercised in CI",
)


def race(one, two):
    barrier = Barrier(2)

    def run(fn):
        barrier.wait(timeout=10)
        return fn()

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(run, one)
        b = pool.submit(run, two)
        return a.result(timeout=20), b.result(timeout=20)


def test_concurrent_accept_and_cancel_have_one_winner(client, app):
    order, _, _ = place_order(client)
    a = TestClient(app)
    b = TestClient(app)
    sign_in(a, 2)
    sign_in(b, 4)
    path = f"/api/v1/orders/{order['id']}/transition"
    results = race(
        lambda: a.post(path, json={"status": "Accepted"}),
        lambda: b.post(path, json={"status": "Cancelled"}),
    )
    assert sorted(r.status_code for r in results) == [200, 409]
    a.close()
    b.close()


def test_concurrent_assignments_reserve_driver_once(client, app):
    one = ready_order(client)
    two = ready_order(client)
    available(client, 3)
    a = TestClient(app)
    b = TestClient(app)
    sign_in(a, 1)
    sign_in(b, 1)
    results = race(
        lambda: a.post(f"/api/v1/orders/{one['id']}/assignments", json={"driver_id": 3}),
        lambda: b.post(f"/api/v1/orders/{two['id']}/assignments", json={"driver_id": 3}),
    )
    assert sorted(r.status_code for r in results) == [201, 409]
    with app.state.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Assignment)) == 1
    a.close()
    b.close()


def test_concurrent_checkouts_cannot_oversell(client, app):
    sign_in(client, 2)
    product = client.post("/api/v1/products", json={**PRODUCT, "stock_quantity": 1}).json()
    a = TestClient(app)
    b = TestClient(app)
    payloads = []
    for test_client, identity in ((a, 4), (b, 6)):
        sign_in(test_client, identity)
        address = test_client.post("/api/v1/addresses", json=ADDRESS).json()
        assert (
            test_client.put(f"/api/v1/cart/items/{product['id']}", json={"quantity": 1}).status_code
            == 200
        )
        payloads.append({"address_id": address["id"], "idempotency_key": secrets.token_hex(16)})
    results = race(
        lambda: a.post("/api/v1/checkout", json=payloads[0]),
        lambda: b.post("/api/v1/checkout", json=payloads[1]),
    )
    assert sorted(r.status_code for r in results) == [201, 409]
    with app.state.sessions() as db:
        assert db.get(Product, product["id"]).stock_quantity == 0
        assert db.scalar(select(func.count()).select_from(Order)) == 1
    a.close()
    b.close()
