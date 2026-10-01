# API import/export and manual acceptance

The checked-in artifacts in [api/](api/) cover all 55 implemented method/path operations:

| File | Purpose |
|---|---|
| [openapi.json](api/openapi.json) | Unmodified OpenAPI 3.1 snapshot from `create_app().openapi()` |
| [delivery.postman_collection.json](api/delivery.postman_collection.json) | Postman v2.1 request library, grouped by runtime tags, with validated body examples and login/CSRF scripts |
| [local.postman_environment.json](api/local.postman_environment.json) | Blank credentials, tokens and resource IDs; localhost backend URL only |

## Import and login

1. Start a migrated development backend using the [README](../README.md), or the full local stack
   in [DEPLOYMENT.md](DEPLOYMENT.md). Bootstrap accounts explicitly. Optional demo accounts use the
   password you chose during `python -m app.seed_demo`; this repository supplies no default password.
2. Use Postman's **Import** to select the collection and environment JSON files. Select the imported
   environment. Set `base_url` to `http://localhost:8000/api/v1` for the host backend,
   `http://localhost:8080/api/v1` for the container proxy, or your approved HTTPS URL plus `/api/v1`.
   Do not add a trailing slash. Keep the cookie jar enabled and use the same hostname throughout.
3. Set `login_email` and `login_password` locally for an existing account. Send **POST /auth/login**,
   then **GET /auth/me**. The client stores the session cookie; the login script captures `csrf_token`,
   `current_role`, `current_user_id`, and the role's `merchant_id` or `driver_id` when applicable.
4. Every authenticated mutation includes `X-CSRF-Token: {{csrf_token}}`, including requests without
   a JSON body. Logout revokes the server session, clears cookies and clears the captured identity.
   Registration creates a Customer; it does not sign the customer in. Never use bearer-token auth.

Use a private local environment for credentials. The checked-in template is blank; do not commit or
share populated environment exports, cookie jars, response histories or real customer/location data.
Client masking is not a guarantee that an exported file has been redacted. For a handoff, share the
generated collection and blank template from this repository.

Postman documentation: [import](https://learning.postman.com/docs/getting-started/importing-and-exporting/importing-data/),
[variables](https://learning.postman.com/docs/use/send-requests/variables/define-variables/),
[cookies](https://learning.postman.com/docs/use/send-requests/response-data/cookies/).

## Useful request sequence

This is a library to send selected requests manually, not a collection to **Run all** against a live
database. IDs are deliberately blank; use the resource IDs returned by your own development database.
Numeric ID placeholders in raw bodies are unquoted so that substitution sends JSON numbers.
Pre-request scripts JSON-escape environment string values, including passwords containing quotes
or backslashes; enter the original value in the environment without manually escaping it.

| Step | Account | Requests and variables |
|---|---|---|
| Browse | Public/Customer | GET /merchants, /products, /cities. Select an approved open merchant, in-stock product and city; set `merchant_id`, `product_id`, `city_id`. Optional query filters are disabled until selected. |
| Address/cart | Customer | Login; POST /addresses captures `address_id`; PUT /cart/items/{identity} uses `product_id`; GET /cart shows server totals. Use a real development address and coordinates. |
| Checkout/retry | Customer | POST /checkout captures `order_id`. Its script generates `idempotency_key` only when blank. Resend the same body/key to confirm the same order ID and 201; clear the key only when starting a new order. |
| Prepare | Owning Merchant | Change login credentials and send login again. POST /orders/{identity}/transition with `status` Accepted, then Preparing, then Ready. Edit the saved body between sends. |
| Driver ready | Driver | Login again; PUT /driver/availability with `is_available: true` updates the heartbeat and captures the driver's ID at login. POST /driver/heartbeat refreshes activity; freshness expires after 30 minutes. |
| Assign | Admin | Login again; POST /orders/{identity}/assignments uses `order_id`/`driver_id` and captures `assignment_id`. The order must be Ready and the driver active, fresh, available and unreserved. |
| Accept/pickup/deliver | Assigned Driver | Login again; POST /assignments/{identity}/respond with `accept: true`; transition OnDelivery, then Delivered. Acceptance alone does not mark pickup. Delivery confirms COD collection. |
| Verify | Customer/Admin | Login as each role before reading. GET /orders/{identity}, recipient notifications and role dashboards. Customer may review their Delivered order once. Only Admin can GET /admin/drivers. |

Changing environments does not switch the cookie jar's identity. **Always log in again when switching
roles**, even if another environment already contains a CSRF token. Prefer one environment for the
sequence so captured order and assignment IDs remain available.

Additional checks on separate orders: Customer Pending→Cancelled; Merchant Pending→Rejected with a
reason; Driver rejects a Pending assignment, then Admin reassigns to another available driver.
Forbidden transitions return 403/409, unrelated owners get 404, repeat assignment responses get 409.
For cancellation/rejection, verify reserved stock is restored once. Authenticated private responses
use `Cache-Control: no-store`. The existing integration/browser tests cover these flows.

Create-account requests need your own unique `new_user_email`, `new_user_phone` and 12–128 character
`new_user_password`. The admin example creates a Driver; change `role` deliberately and provide
`business_name` for a Merchant. Creating a privileged Admin remains a bootstrap CLI operation.
Create-resource responses capture their IDs. GET lists do not silently choose the first result.
PATCH bodies contain all required fields and defaulted fields: edit the entire body to avoid resetting
omitted values. Product/category writes include `merchant_id`; a Merchant may use only their own ID.

## Regenerate and detect drift

From the repository root with the backend Python environment active:

```bash
python scripts/export_api.py
python scripts/export_api.py --check
```

The exporter overrides all settings, disables `.env` loading, uses an ephemeral signing key and an
in-memory engine, and never connects to or migrates a database. It preserves the runtime schema;
there are no secrets, account records or generated timestamps in the artifacts. It checks route
coverage against `API_DESIGN.md` and validates substituted examples with the actual input models.
`--check` writes nothing and exits nonzero for stale artifacts, missing examples or route/doc drift.
CI runs this check. Add reviewed examples/access guidance when new routes or input models are added.

An alternate export is the running backend's `GET http://localhost:8000/openapi.json`. The web proxy
routes `/api/` only; `/openapi.json` and `/docs` are backend-only URLs. Use the checked-in snapshot
for clients of the proxy. Other OpenAPI importers can use the snapshot but will need manual cookie
and CSRF setup. Runtime schema limitations are listed in [API_DESIGN.md](API_DESIGN.md); neither
OpenAPI import nor the collection's success-code assertions replace business/authorization tests.
