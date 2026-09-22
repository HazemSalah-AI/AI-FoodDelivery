# API design v1

Base `/api/v1`. JSON requests and responses, UTF-8. OpenAPI `/openapi.json` and Swagger `/docs`
are generated from the same Pydantic contracts used at runtime. The table is the implementation contract.

## Conventions

- Successful reads/updates: 200; new resources: 201; removals/logout: 204.
- Errors: `{ "error": { "code": "...", "message": "...", "fields": [] } }`; fields only for validation.
- 401 missing/expired/revoked session; 403 role/CSRF/origin failure; 404 absent or not owned;
  409 duplicate/stock/cart/transition/assignment conflict; 422 malformed input; 429 auth rate limit.
- Lists return `{items: [...], total, page, page_size}`. page≥1, page_size 1–100 (default 30).
- Search `q` max 100 chars; ordering is an explicit allowlist. No SQL fragments are accepted.
- Money: decimal EGP serialized as strings. Coordinates are numeric/decimal validated to global bounds.
- Session: signed JWT in HttpOnly `delivery_session` cookie. Login sets readable anti-CSRF cookie
  `delivery_csrf`; all authenticated mutations send its value in `X-CSRF-Token`.
- Auth mutations reject unexpected Origin when present. No role input in customer registration.
- Public DTOs exclude hashes, sessions, private user data and driver location.

## Identity and account management

| Method/path | Access | Input/query | Success body | Special validation |
|---|---|---|---|---|
| POST /auth/register | Public | name, email, phone, password | User (201) | Customer only; email/phone unique; password 12–128 chars |
| POST /auth/login | Public | email, password | user + csrf_token | Generic invalid-credentials error; rate limited |
| GET /auth/me | Signed in | — | User | Active account + unrevoked session |
| POST /auth/logout | Signed in | — | 204 | Revoke session and clear cookies |
| PATCH /auth/profile | Signed in | name, phone | User | Cannot change role or activation |
| GET /admin/users | Admin | role, q, pagination | Page[User] | Allowlisted role |
| POST /admin/users | Admin | registration fields + role; business_name for Merchant | User (201) | Driver/Merchant/Customer; no public admin creation |
| PATCH /admin/users/{id} | Admin | is_active | User | Cannot suspend self; audit entry |
| GET /admin/merchants | Admin | pagination | Page[Merchant] | Includes unapproved businesses for management |
| PATCH /admin/merchants/{id} | Admin | status | Merchant | Pending/Approved/Rejected |

## Catalog and addresses

| Method/path | Access | Input/query | Success body | Special validation |
|---|---|---|---|---|
| GET /merchants | Public | q, page, page_size | Page[Merchant] | Only approved active businesses |
| GET /merchants/{id} | Public | — | Merchant | Approved and active |
| GET /merchant/profile | Merchant | — | Merchant | Own profile |
| PATCH /merchant/profile | Merchant | business_name, description, is_open | Merchant | Own profile only |
| GET /products | Public / owner / Admin | merchant_id, category_id, q, sort, pagination, managed | Page[Product] | managed requires owner/Admin; sort name/price/-price |
| POST /products | Merchant/Admin | merchant_id (Admin), category_id?, name, description, price, stock_quantity, is_available | Product (201) | Merchant ownership; price>0, stock≥0 |
| PATCH /products/{id} | Owner/Admin | product editable fields | Product | Merchant immutable; category same merchant |
| GET /categories | Public | merchant_id?, pagination | Page[Category] | — |
| POST /categories | Merchant/Admin | merchant_id (Admin), name | Category (201) | Unique name per merchant |
| PATCH /categories/{id} | Owner/Admin | name | Category | Ownership |
| GET /cities | Public | pagination | Page[City] | — |
| POST /cities | Admin | name | City (201) | Unique name |
| GET /areas | Public | city_id?, pagination | Page[Area] | — |
| POST /areas | Admin | city_id, name | Area (201) | City exists |
| GET /addresses | Customer | — | Address[] | Own active addresses |
| POST /addresses | Customer | title, street, city_id, area_id?, latitude, longitude, is_default | Address (201) | Existing area/city pair; coordinates required |
| PATCH /addresses/{id} | Customer | same editable fields | Address | Ownership; historic orders retain snapshot |
| DELETE /addresses/{id} | Customer | — | 204 | Archive; never destroy historical order data |

## Ordering and delivery

| Method/path | Access | Input/query | Success body | Special validation |
|---|---|---|---|---|
| GET /cart | Customer | — | cart items + server subtotal | Own cart |
| PUT /cart/items/{product_id} | Customer | quantity | Cart | 1–99; one merchant; available stock |
| DELETE /cart/items/{product_id} | Customer | — | 204 | Own cart |
| POST /checkout | Customer | address_id, idempotency_key | Order (201) | Atomic; own address; lock/reprice/reserve stock; Cash only |
| GET /orders | Signed in | status?, pagination | Page[Order] | Customer own, Merchant own, Driver Pending/Accepted/Completed assignments, Admin all |
| GET /orders/{id} | Signed in | — | Order + items/history/assignment | Same ownership; no driver coordinates |
| POST /orders/{id}/transition | Role/owner | status, reason? | Order | Only documented transition edges; rejection reason required |
| POST /orders/{id}/assignments | Admin | driver_id | Assignment (201) | Ready; active/available/fresh driver; no active conflict |
| GET /assignments | Driver/Admin | pagination | Page[Assignment] | Driver sees only own history |
| POST /assignments/{id}/respond | Assigned Driver | accept: boolean, reason? | Assignment | Pending only; rejection releases order for reassignment |
| GET /driver/availability | Driver | — | availability info | Own availability only |
| PUT /driver/availability | Driver | is_available | availability info | Availability requires heartbeat within 30 min |
| POST /driver/heartbeat | Driver | — | availability info | Updates last_seen only |
| PUT /driver/location | Driver | latitude, longitude | updated_at | Store paired coordinates; no readback to other roles |
| GET /admin/drivers | Admin | pagination | Page[DriverLocation] | Exclusive retrieval of driver coordinates |
| GET /admin/dashboard | Admin | — | counts + delivered COD totals | No implied earnings/commission |
| GET /merchant/dashboard | Merchant | — | own counts + delivered sales | Owned orders only |
| GET /driver/dashboard | Driver | — | assignments + delivered COD totals | Collected cash is not earnings |

Canonical states: Pending → Accepted → Preparing → Ready → OnDelivery → Delivered.
Customer Pending→Cancelled; merchant Pending→Rejected (reason required). Admin may perform valid
operational transitions but cannot bypass pickup requiring an accepted assignment. No arbitrary jumps.

## Notifications, reviews and favorites

| Method/path | Access | Input/query | Success body | Special validation |
|---|---|---|---|---|
| GET /notifications | Signed in | unread?, pagination | Page[Notification] | Recipient only |
| PATCH /notifications/{id}/read | Signed in | — | Notification | Recipient only |
| POST /orders/{id}/review | Customer | rating, comment | Review (201) | Own Delivered order; once/order; 1–5; merchant only |
| GET /merchants/{id}/reviews | Public | pagination | Page[Review] | No customer email/address |
| GET /favorites | Customer | pagination | Page[Merchant] | Own favorites |
| PUT /favorites/{merchant_id} | Customer | — | 204 | Existing public merchant; idempotent |
| DELETE /favorites/{merchant_id} | Customer | — | 204 | Own favorite; idempotent |

Health checks: `GET /health` reports process liveness; `GET /ready` checks database access and a
nonempty Alembic revision, returning 503 without database details when unavailable. All `/api/`
responses set `Cache-Control: no-store`. Deployment still runs `alembic upgrade head` explicitly.
