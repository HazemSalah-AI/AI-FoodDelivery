# Database

Alembic is the only application schema source. Use a **new database**, not the historical `DataBase/` exercises.
Run `cd backend && alembic upgrade head`; verify with `alembic check`. Never downgrade a production
schema without backup and a reviewed recovery plan. The initial downgrade drops application tables.

Models: `identity.py` (users, revocable sessions), `catalog.py` (merchant profiles, city/area,
addresses, categories, products), `commerce.py` (server carts, purchases, history, reviews,
favorites), `operations.py` (driver profile/location, assignment history, notifications, audit).

The original ERD is preserved in `ERD.png`. Changes are in DECISIONS.md. A user has one role;
merchant/driver profile primary keys reference user IDs. Addresses are archived, never deleted out
of historical orders. Order item names/prices and full address are immutable checkout snapshots.

All money uses Numeric(10,2), EGP. Quantities, stock, status, COD-only payment and coordinates have
check constraints. Composite category/merchant and area/city foreign keys prevent cross-owner
associations. Active assignments have partial unique indexes on both driver and order.

PostgreSQL production operations use row locks on users/carts, products, orders and drivers to
serialize conflicting writes. Stock is reserved at checkout and returned only once on a valid
Pending→Cancelled/Rejected transition. SQLite supports quick sequential tests with FKs enabled,
but does not prove concurrent PostgreSQL behavior. CI runs the integration suite on PostgreSQL 17.
