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
