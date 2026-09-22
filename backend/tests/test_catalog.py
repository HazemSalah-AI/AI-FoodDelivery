from conftest import PASSWORD, sign_in

PRODUCT = {"name": "أرز مصري", "price": "35.50", "stock_quantity": 20}
ADDRESS = {
    "title": "المنزل",
    "street": "شارع المحطة أبو حماد",
    "city_id": 1,
    "latitude": 30.538,
    "longitude": 31.679,
}


def test_catalog_ownership_and_search(client):
    sign_in(client, 2)
    response = client.post("/api/v1/products", json=PRODUCT)
    assert response.status_code == 201, response.text
    identity = response.json()["id"]
    sign_in(client, 5)
    assert client.patch(f"/api/v1/products/{identity}", json=PRODUCT).status_code == 404
    assert client.post("/api/v1/products", json={**PRODUCT, "merchant_id": 2}).status_code == 403
    sign_in(client, 4)
    assert client.post("/api/v1/products", json=PRODUCT).status_code == 403
    assert client.get("/api/v1/products?managed=true").status_code == 403
    assert client.get("/api/v1/products?q=أرز&sort=price&page=1&page_size=1").json()["total"] == 1
    assert client.get("/api/v1/products?sort=DROP").status_code == 422
    assert client.get("/api/v1/products?page_size=1001").status_code == 422


def test_address_ownership_defaults_and_archive(client):
    sign_in(client, 4)
    one = client.post("/api/v1/addresses", json={**ADDRESS, "is_default": True}).json()
    two = client.post("/api/v1/addresses", json={**ADDRESS, "is_default": True}).json()
    assert sum(a["is_default"] for a in client.get("/api/v1/addresses").json()) == 1
    sign_in(client, 6)
    assert client.patch(f"/api/v1/addresses/{one['id']}", json=ADDRESS).status_code == 404
    assert client.delete(f"/api/v1/addresses/{one['id']}").status_code == 404
    sign_in(client, 4)
    assert client.delete(f"/api/v1/addresses/{two['id']}").status_code == 204
    assert len(client.get("/api/v1/addresses").json()) == 1
    assert client.post("/api/v1/addresses", json={**ADDRESS, "latitude": 91}).status_code == 422


def test_admin_creation_role_separation_and_activation(client):
    for identity in (2, 3, 4):
        sign_in(client, identity)
        assert client.get("/api/v1/admin/users").status_code == 403
        assert client.get("/api/v1/admin/merchants").status_code == 403
    sign_in(client, 1)
    response = client.post(
        "/api/v1/admin/users",
        json={
            "name": "New Driver",
            "email": "newdriver@example.com",
            "phone": "01112345678",
            "password": PASSWORD,
            "role": "Driver",
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["role"] == "Driver"
    assert client.patch("/api/v1/admin/users/1", json={"is_active": False}).status_code == 409
    assert client.patch("/api/v1/admin/users/4", json={"is_active": False}).status_code == 200
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "user4@example.com", "password": PASSWORD}
        ).status_code
        == 401
    )


def test_cross_merchant_category_and_inactive_merchant(client):
    sign_in(client, 5)
    category = client.post("/api/v1/categories", json={"name": "Bakery"}).json()
    sign_in(client, 2)
    assert (
        client.post("/api/v1/products", json={**PRODUCT, "category_id": category["id"]}).status_code
        == 404
    )
    client.post("/api/v1/products", json=PRODUCT)
    sign_in(client, 1)
    client.patch("/api/v1/admin/merchants/2", json={"status": "Rejected"})
    assert client.get("/api/v1/merchants/2").status_code == 404
    assert client.get("/api/v1/products").json()["total"] == 0
