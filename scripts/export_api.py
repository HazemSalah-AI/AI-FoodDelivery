"""Export the runtime OpenAPI and a cookie/CSRF-aware Postman collection, without a DB."""

import argparse
import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from fastapi.routing import APIRoute, iter_route_contexts  # noqa: E402

METHODS = {"get", "post", "put", "patch", "delete"}
BASE = "/api/v1"
ID_VARIABLES = {
    "merchants": "merchant_id",
    "products": "product_id",
    "categories": "category_id",
    "addresses": "address_id",
    "users": "target_user_id",
    "items": "product_id",
    "orders": "order_id",
    "assignments": "assignment_id",
    "notifications": "notification_id",
    "favorites": "merchant_id",
}
VARIABLES = {
    "base_url": "http://localhost:8000/api/v1",
    "login_email": "",
    "login_password": "",
    "new_user_email": "",
    "new_user_phone": "",
    "new_user_password": "",
    "csrf_token": "",
    "current_role": "",
    "current_user_id": "",
    "merchant_id": "",
    "product_id": "",
    "category_id": "",
    "city_id": "",
    "area_id": "",
    "address_id": "",
    "order_id": "",
    "assignment_id": "",
    "driver_id": "",
    "target_user_id": "",
    "notification_id": "",
    "idempotency_key": "",
}
EXAMPLES = {
    "Register": {
        "name": "API example customer",
        "email": "{{new_user_email}}",
        "phone": "{{new_user_phone}}",
        "password": "{{new_user_password}}",
    },
    "Login": {"email": "{{login_email}}", "password": "{{login_password}}"},
    "ProfileUpdate": {"name": "API example name", "phone": "{{new_user_phone}}"},
    "MerchantWrite": {
        "business_name": "API example merchant",
        "description": "Development example",
        "is_open": True,
    },
    "ProductWrite": {
        "merchant_id": "{{merchant_id}}",
        "category_id": None,
        "name": "API example product",
        "description": "Development example",
        "price": "35.50",
        "stock_quantity": 20,
        "is_available": True,
    },
    "CategoryWrite": {"merchant_id": "{{merchant_id}}", "name": "API example category"},
    "Named": {"name": "API example name"},
    "AreaWrite": {"city_id": "{{city_id}}", "name": "API example area"},
    "AddressWrite": {
        "title": "API example home",
        "street": "Development example address, Abu Hammad",
        "city_id": "{{city_id}}",
        "area_id": None,
        "latitude": "30.5385000",
        "longitude": "31.6798000",
        "is_default": True,
    },
    "AdminCreateUser": {
        "name": "API example driver",
        "email": "{{new_user_email}}",
        "phone": "{{new_user_phone}}",
        "password": "{{new_user_password}}",
        "role": "Driver",
        "business_name": None,
    },
    "ActiveWrite": {"is_active": True},
    "MerchantStatus": {"status": "Approved"},
    "Quantity": {"quantity": 1},
    "Checkout": {
        "address_id": "{{address_id}}",
        "idempotency_key": "{{idempotency_key}}",
    },
    "Transition": {"status": "Accepted", "reason": None},
    "Assign": {"driver_id": "{{driver_id}}"},
    "AssignmentResponse": {"accept": True, "reason": None},
    "Availability": {"is_available": True},
    "Location": {"latitude": "30.5385000", "longitude": "31.6798000"},
    "ReviewWrite": {"rating": 5, "comment": "Development example"},
}
CAPTURE = {
    ("POST", "/products"): "product_id",
    ("POST", "/categories"): "category_id",
    ("POST", "/cities"): "city_id",
    ("POST", "/areas"): "area_id",
    ("POST", "/addresses"): "address_id",
    ("POST", "/checkout"): "order_id",
    ("POST", "/orders/{identity}/assignments"): "assignment_id",
    ("POST", "/admin/users"): "target_user_id",
    ("GET", "/merchant/profile"): "merchant_id",
}


def encode(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def event(kind, source):
    return {
        "listen": kind,
        "script": {"type": "text/javascript", "exec": source.splitlines()},
    }


def access(method, path):
    if path in {"/health", "/ready", "/auth/register", "/auth/login"}:
        return "Public"
    if path.startswith("/auth/") or path.startswith("/notifications"):
        return "Signed in; own account/recipient"
    if path.startswith("/admin/") or path.endswith("/assignments") and method == "POST":
        return "Admin"
    if path.startswith("/merchant/"):
        return "Merchant; own business"
    if path.startswith("/driver/"):
        return "Driver; own profile"
    if path.startswith(("/products", "/categories")):
        if method == "GET":
            return "Public; GET /products with managed=true requires Merchant/Admin"
        return "Merchant owner/Admin"
    if path.startswith(("/cities", "/areas")):
        return "Public" if method == "GET" else "Admin"
    if path.startswith("/merchants/") or path == "/merchants":
        return "Public"
    if path.startswith(("/cart", "/addresses", "/favorites")) or path == "/checkout":
        return "Customer; own resources"
    if path.startswith("/orders"):
        return "Customer; own Delivered order" if path.endswith("/review") else "Role/owner scoped"
    if path.startswith("/assignments"):
        return "Driver/Admin" if method == "GET" else "Assigned Driver"
    raise ValueError(f"Review access guidance for new operation: {method} {path}")


def render_body(example):
    # IDs are JSON numbers after substitution; passwords and decimal amounts remain strings.
    return re.sub(r'"(\{\{\w+_id\}\})"', r"\1", encode(example)).rstrip()


def example_values():
    values = {key: "1" if key.endswith("_id") else "example" for key in VARIABLES}
    values.update(
        login_email="login@example.com",
        new_user_email="new@example.com",
        login_password="example-password-123",
        new_user_password="example-password-123",
        new_user_phone="01012345678",
        idempotency_key="example-order-123",
    )
    return values


def item(method, full_path, operation, route):
    path = full_path.removeprefix(BASE)
    parts = path.strip("/").split("/")
    url_parts = []
    for index, part in enumerate(parts):
        if part.startswith("{"):
            url_parts.append("{{" + ID_VARIABLES[parts[index - 1]] + "}}")
        else:
            url_parts.append(part)
    queries = []
    for param in operation.get("parameters", []):
        if param["in"] != "query":
            continue
        schema = param["schema"]
        value = schema.get("default")
        disabled = value is None
        if disabled:
            value = "{{" + param["name"] + "}}" if param["name"].endswith("_id") else "Pending"
        elif isinstance(value, bool):
            value = str(value).lower()
        queries.append({"key": param["name"], "value": str(value), "disabled": disabled})
    raw_url = "{{base_url}}/" + "/".join(url_parts)
    active_queries = [f"{q['key']}={q['value']}" for q in queries if not q["disabled"]]
    if active_queries:
        raw_url += "?" + "&".join(active_queries)
    url = {"raw": raw_url, "host": ["{{base_url}}"], "path": url_parts}
    if queries:
        url["query"] = queries
    description = (
        f"{method} {full_path}\nAccess: {access(method, path)}.\n"
        "Use resource IDs from your own database. See docs/API_CLIENT.md for the role workflow."
    )
    headers = [{"key": "Accept", "value": "application/json"}]
    if method != "GET" and path not in {"/auth/login", "/auth/register"}:
        headers.append({"key": "X-CSRF-Token", "value": "{{csrf_token}}"})
    request = {
        "method": method,
        "header": headers,
        "url": url,
        "description": description,
    }
    if "requestBody" in operation:
        schema = operation["requestBody"]["content"]["application/json"]["schema"]
        example = EXAMPLES[schema["$ref"].rsplit("/", 1)[1]]
        body = render_body(example)
        resolved = re.sub(r"\{\{(\w+)\}\}", lambda m: example_values()[m[1]], body)
        route.body_field.field_info.annotation.model_validate(json.loads(resolved))
        request["body"] = {
            "mode": "raw",
            "raw": body,
            "options": {"raw": {"language": "json"}},
        }
        headers.append({"key": "Content-Type", "value": "application/json"})
    success = next(int(code) for code in operation["responses"] if code.startswith("2"))
    test = (
        f'pm.test("Expected HTTP {success}", () => pm.expect(pm.response.code).to.eql({success}));'
    )
    if path == "/auth/login":
        test += """
if (pm.response.code === 200) {
    const body = pm.response.json();
    pm.environment.set("csrf_token", body.csrf_token);
    pm.environment.set("current_role", body.user.role);
    pm.environment.set("current_user_id", body.user.id);
    if (body.user.role === "Driver") pm.environment.set("driver_id", body.user.id);
    if (body.user.role === "Merchant") pm.environment.set("merchant_id", body.user.id);
}
"""
    elif path == "/auth/logout":
        test += """
if (pm.response.code === 204) {
    ["csrf_token", "current_role", "current_user_id"].forEach(k => pm.environment.unset(k));
}
"""
    elif (method, path) in CAPTURE:
        key = CAPTURE[method, path]
        test += f'\nif (pm.response.code === {success}) pm.environment.set("{key}", pm.response.json().id);'
        if path == "/admin/users":
            test += """
if (pm.response.code === 201 && pm.response.json().role === "Driver") {
    pm.environment.set("driver_id", pm.response.json().id);
}
"""
    events = [event("test", test)]
    if path == "/auth/login":
        events.insert(
            0,
            event(
                "prerequest",
                """
["csrf_token", "current_role", "current_user_id"].forEach(k => pm.environment.unset(k));
""".strip(),
            ),
        )
    elif path == "/checkout":
        events.insert(
            0,
            event(
                "prerequest",
                """
if (!pm.environment.get("idempotency_key")) {
    pm.environment.set("idempotency_key", pm.variables.replaceIn("{{$guid}}"));
}
""".strip(),
            ),
        )
    return {
        "name": f"{method} {path}",
        "request": request,
        "event": events,
        "response": [],
    }


def artifacts():
    # Override every setting and disable .env reads: no real credentials or DB access are needed.
    app = create_app(
        Settings(
            _env_file=None,
            environment="test",
            database_url="sqlite:///:memory:",
            jwt_secret=secrets.token_hex(48),
            session_hours=12,
            secure_cookies=False,
            allowed_origins=["http://localhost:5173"],
        )
    )
    try:
        schema = app.openapi()
        routes = {
            (method, context.path): context.original_route
            for context in iter_route_contexts(app.routes)
            if isinstance(context.original_route, APIRoute)
            and context.original_route.include_in_schema
            for method in context.methods
        }
        operations = {
            (method.upper(), path): operation
            for path, path_item in schema["paths"].items()
            for method, operation in path_item.items()
            if method in METHODS
        }
        if routes.keys() != operations.keys():
            raise ValueError("Runtime routes and OpenAPI operations differ")
        docs = (ROOT / "docs/API_DESIGN.md").read_text(encoding="utf-8")
        documented = {
            (method, BASE + re.sub(r"\{[^}]+\}", "{identity}", path))
            for method, path in re.findall(r"\b(GET|POST|PUT|PATCH|DELETE) (/[^\s|`]+)", docs)
        }
        if documented != operations.keys():
            raise ValueError(
                f"API_DESIGN route drift: missing={operations.keys() - documented}, "
                f"extra={documented - operations.keys()}"
            )
        folders = {}
        for key, operation in operations.items():
            folders.setdefault(operation["tags"][0], []).append(item(*key, operation, routes[key]))
        collection = {
            "info": {
                "name": "Abo Hammad Delivery API v1",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                "description": (
                    "Generated by python scripts/export_api.py from the runtime OpenAPI. "
                    "Import the blank environment template, set local credentials, and send login. "
                    "Cookies are managed by the client; mutations send X-CSRF-Token. "
                    "Re-login whenever changing roles. This is a request library, not a run-all suite. "
                    "Checkout retains its idempotency key for retries; clear it for a new order. "
                    "See docs/API_CLIENT.md and docs/ACCEPTANCE_HANDOFF.md."
                ),
            },
            "auth": {"type": "noauth"},
            "item": [{"name": name, "item": items} for name, items in folders.items()],
        }
        environment = {
            "name": "Abo Hammad Delivery - local template",
            "_postman_variable_scope": "environment",
            "values": [
                {
                    "key": key,
                    "value": value,
                    "enabled": True,
                    "type": "secret" if "password" in key or key == "csrf_token" else "default",
                }
                for key, value in VARIABLES.items()
            ],
        }
        return {
            "openapi.json": schema,
            "delivery.postman_collection.json": collection,
            "local.postman_environment.json": environment,
        }, len(operations)
    finally:
        app.state.engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail on artifact/docs drift; write nothing",
    )
    args = parser.parse_args()
    exports, count = artifacts()
    directory = ROOT / "docs/api"
    stale = []
    for name, value in exports.items():
        path = directory / name
        content = encode(value)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            directory.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if stale:
        print("Stale API artifacts: " + ", ".join(stale) + "; run python scripts/export_api.py")
        return 1
    print(f"{'Checked' if args.check else 'Exported'} {count} operations and 3 API artifacts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
