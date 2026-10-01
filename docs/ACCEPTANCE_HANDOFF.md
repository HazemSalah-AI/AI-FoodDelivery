# Acceptance and handoff — 2026-10-01

The API import/export checkpoint passes the developer-handoff checks below. Backend/frontend
application code and migrations are unchanged. This focused contract/workflow review does not
constitute a complete security audit or production launch signoff.

| Acceptance check | Result and evidence |
|---|---|
| API coverage and import format | PASS: all 55 runtime operations match the API docs, OpenAPI snapshot and Postman library. OpenAPI 3.1 and the official Postman v2.1 schema validate; snapshot equals live `/openapi.json`. |
| Usable client workflow | PASS: Newman 6.2.2 sends 69 requests covering all operations with cookies, CSRF, captured IDs, checkout retry, role switches and delivery. Rerun also verifies template credentials containing quotes/backslashes and the optional role filter. |
| Export maintenance | PASS: exporter `--check`, Ruff lint/format and intentional stale-output/invalid-example rejection. CI checks artifact/doc drift. Export requires neither `.env` nor database connectivity. |
| Backend acceptance | PASS: all 26 tests on PostgreSQL 17, including three concurrency races. Tests cover session revocation, CSRF/origin, ownership/roles, driver-location privacy, repricing, snapshots, retries, stock restoration and assignment/reassignment. |
| Database | PASS: `alembic upgrade head` and `alembic check`; revision `342305e2a522`, no drift. Existing SQLite migration lifecycle and PostgreSQL offline-SQL tests pass. |
| Role UI | PASS: fresh TypeScript/Vite build and four Chromium tests covering customer, merchant, admin and delivery after rejection/reassignment. |
| Remote/container evidence | PASS: [run 36923110410](https://github.com/HazemSalah-AI/AI-FoodDelivery/actions/runs/36923110410) on final source checkpoint `f6bb511` passed validate and containers, including exporter drift checks, PostgreSQL tests, browser/build and proxy readiness/config checks. |

The request library and blank environment are in [api/](api/); follow [API_CLIENT.md](API_CLIENT.md)
for import and the role sequence. It is a manual request library, not a run-all production test.
Always re-login when changing roles. Keep a checkout key across retries; clear it for a new order.

The API docs now use runtime `{identity}` parameters and explain full-model PATCH/default resets,
decimal coordinates and availability heartbeat refresh. The raw schema still omits cookie/CSRF
security declarations, most domain errors and readiness 503; its automatic 422 schema differs from
the custom error envelope. Health/readiness/location-update responses are untyped. Companion docs
and scripts supply the workflow; a future contract-only checkpoint can improve runtime metadata.
`/openapi.json` and `/docs` are backend-only URLs; use the snapshot for web-proxy clients.

Remaining operator checks:

1. Separately authorize hosting/domain work; provision fresh secrets, HTTPS/secure cookies and an
   admin; run [DEPLOYMENT.md](DEPLOYMENT.md)'s device/role smoke flow. No live hosting, DNS or paid
   resources were created.
2. Configure monitoring/encrypted backups and prove restoration. No high-availability or capacity
   evidence exists. `/ready` checks connectivity and a nonempty revision, not schema/head equality;
   explicit migration/drift checks remain necessary.
3. Verify physical-device GPS, background behavior, live HTTPS permissions and other browsers.
   Chromium used simulated location. The admin map sends selected coordinates to OpenStreetMap;
   notifications use in-site polling, with no external delivery.
4. Postman desktop import was not separately exercised; format validation and Newman execution
   verify the artifacts/scripts. Other importers need manual cookie/CSRF setup. Share only blank
   templates, never credentials, cookie jars or real response data.

COD-only payment, zero delivery fee, one-merchant carts and COD totals distinct from earnings remain
the documented scope. Legacy SQL remains reference only. Non-failing dependency warnings and the
resolved Windows pytest temporary-directory issue are recorded in [PROJECT_STATUS.md](../PROJECT_STATUS.md).
Resume there and select only the next separately authorized checkpoint.
