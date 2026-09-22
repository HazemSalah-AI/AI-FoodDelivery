from datetime import timedelta

from conftest import sign_in
from test_orders import place_order

from app.db.base import now
from app.models import Driver


def ready_order(client):
    order, _, _ = place_order(client)
    sign_in(client, 2)
    for status in ("Accepted", "Preparing", "Ready"):
        assert (
            client.post(
                f"/api/v1/orders/{order['id']}/transition", json={"status": status}
            ).status_code
            == 200
        )
    return order


def available(client, identity):
    sign_in(client, identity)
    assert client.put("/api/v1/driver/availability", json={"is_available": True}).status_code == 200


def test_full_delivery_rejection_reassignment_and_location_privacy(client, app):
    order = ready_order(client)
    identity = order["id"]
    available(client, 3)
    response = client.put(
        "/api/v1/driver/location", json={"latitude": "30.5431234", "longitude": "31.6874321"}
    )
    assert response.status_code == 200 and "latitude" not in response.text
    sign_in(client, 1)
    first = client.post(f"/api/v1/orders/{identity}/assignments", json={"driver_id": 3})
    assert first.status_code == 201, first.text
    assignment = first.json()["id"]
    assert (
        client.post(f"/api/v1/orders/{identity}/assignments", json={"driver_id": 3}).status_code
        == 409
    )
    assert "30.5431234" in client.get("/api/v1/admin/drivers").text
    available(client, 7)
    assert (
        client.post(f"/api/v1/assignments/{assignment}/respond", json={"accept": True}).status_code
        == 404
    )
    sign_in(client, 3)
    assert (
        client.post(
            f"/api/v1/orders/{identity}/transition", json={"status": "OnDelivery"}
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/v1/assignments/{assignment}/respond",
            json={"accept": False, "reason": "Vehicle unavailable"},
        ).status_code
        == 200
    )
    assert client.get(f"/api/v1/orders/{identity}").status_code == 404
    sign_in(client, 1)
    second = client.post(f"/api/v1/orders/{identity}/assignments", json={"driver_id": 7})
    assert second.status_code == 201, second.text
    sign_in(client, 7)
    assert (
        client.post(
            f"/api/v1/assignments/{second.json()['id']}/respond", json={"accept": True}
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/assignments/{second.json()['id']}/respond", json={"accept": True}
        ).status_code
        == 409
    )
    for status in ("OnDelivery", "Delivered"):
        response = client.post(f"/api/v1/orders/{identity}/transition", json={"status": status})
        assert response.status_code == 200, response.text
    assert response.json()["assignment"]["status"] == "Completed"
    assert client.get("/api/v1/driver/dashboard").json()["cod_total"] == "71.00"
    for user_id in (2, 3, 4, 7):
        sign_in(client, user_id)
        assert client.get("/api/v1/admin/drivers").status_code == 403
        assert client.get("/api/v1/driver/location").status_code == 405
        response = client.get(f"/api/v1/orders/{identity}")
        assert "30.5431234" not in response.text and "31.6874321" not in response.text
        assert "location_updated_at" not in response.text
    sign_in(client, 4)
    assert client.get(f"/api/v1/orders/{identity}").json()["status"] == "Delivered"
    notices = client.get("/api/v1/notifications").json()["items"]
    assert any("Delivered" in n["title"] for n in notices)
    assert client.patch(f"/api/v1/notifications/{notices[0]['id']}/read").status_code == 200
    sign_in(client, 6)
    assert client.patch(f"/api/v1/notifications/{notices[0]['id']}/read").status_code == 404


def test_assignment_roles_readiness_and_stale_driver(client, app):
    order, _, _ = place_order(client)
    for identity in (2, 3, 4):
        sign_in(client, identity)
        assert (
            client.post(
                f"/api/v1/orders/{order['id']}/assignments", json={"driver_id": 3}
            ).status_code
            == 403
        )
    available(client, 3)
    sign_in(client, 1)
    assert (
        client.post(f"/api/v1/orders/{order['id']}/assignments", json={"driver_id": 3}).status_code
        == 409
    )
    order = ready_order(client)
    with app.state.sessions.begin() as db:
        db.get(Driver, 3).last_seen = now() - timedelta(minutes=31)
    sign_in(client, 1)
    assert (
        client.post(f"/api/v1/orders/{order['id']}/assignments", json={"driver_id": 3}).status_code
        == 409
    )


def test_reviews_and_favorites(client):
    order = ready_order(client)
    sign_in(client, 4)
    assert (
        client.post(f"/api/v1/orders/{order['id']}/review", json={"rating": 5}).status_code == 409
    )
    for _ in range(2):
        assert client.put("/api/v1/favorites/2").status_code == 204
    assert client.get("/api/v1/favorites").json()["total"] == 1
    assert client.delete("/api/v1/favorites/2").status_code == 204
    assert client.get("/api/v1/favorites").json()["total"] == 0
    available(client, 3)
    sign_in(client, 1)
    assignment = client.post(
        f"/api/v1/orders/{order['id']}/assignments", json={"driver_id": 3}
    ).json()
    sign_in(client, 3)
    client.post(f"/api/v1/assignments/{assignment['id']}/respond", json={"accept": True})
    for status in ("OnDelivery", "Delivered"):
        client.post(f"/api/v1/orders/{order['id']}/transition", json={"status": status})
    sign_in(client, 4)
    response = client.post(
        f"/api/v1/orders/{order['id']}/review", json={"rating": 5, "comment": "Excellent"}
    )
    assert response.status_code == 201, response.text
    assert (
        client.post(f"/api/v1/orders/{order['id']}/review", json={"rating": 4}).status_code == 409
    )
    assert "customer_id" not in client.get("/api/v1/merchants/2/reviews").text
