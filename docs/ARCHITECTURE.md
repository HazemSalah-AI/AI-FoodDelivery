# Architecture

Browser React UI → versioned FastAPI routes → services → repository queries → PostgreSQL.

Routes validate typed inputs and role access. Services own order state transitions, transactions,
stock reservation, ownership, notifications, and assignment policy. Repository helpers centralize
ownership queries and locking. SQLAlchemy constraints provide final relational integrity.

Use JWT in an HttpOnly cookie with an anti-CSRF token for state-changing authenticated requests,
revocable server-side sessions and Argon2 password hashes. Explicit response schemas never include
passwords or driver coordinates in public/customer order output. Production uses same-origin reverse
proxy, secure cookies, HTTPS, and environment-provided secrets. No external message delivery.

In-site notifications and admin location refresh use lightweight polling; no paid map API is required.
Monolith plus PostgreSQL, no microservices or message broker. Alembic owns the application schema.

## Transaction and access boundaries

`get_db` uses a transaction-scoped session. FastAPI function-scoped dependencies commit before
sending a response and roll back on errors. Services lock resources in a documented order and flush
before returning typed DTOs. Repositories provide shared locking/ownership filters. There is one
state-machine implementation. Database constraints arbitrate competing assignment/stock updates.

Polling does not grant access: all reads are server-filtered to the current role/owner. JWT roles
are never trusted; current user/activation and server session are read on every authenticated request.
Admin is an operational role, not a way to invent invalid order transitions. Logs omit secrets and
validation error bodies omit raw submitted inputs. The browser stores neither JWT nor password.
