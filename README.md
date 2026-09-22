# Abo Hammad Delivery System

Website-only local marketplace for Abu Hammad, Egypt. Cash on Delivery only.

Implementation is in progress. Read [PROJECT_STATUS.md](PROJECT_STATUS.md) before continuing.
Original diagrams live in `docs/`; original SQL exercises remain in `DataBase/` as reference only.
Do not run the legacy seed against the application database: it contains insecure illustrative passwords.

## Stack and structure

FastAPI / SQLAlchemy / Alembic / PostgreSQL backend, React / TypeScript / Vite frontend.
`backend/`, `frontend/`, `docs/`, `scripts/`, `.github/`.

## Business rules

Customer → Pending → merchant Accepted → Preparing → Ready → OnDelivery → Delivered.
Only Pending can become Cancelled (customer) or Rejected (merchant, with reason).
Admin assigns an available driver to a Ready order. Driver accepts or rejects; rejection permits reassignment.
Only admin can retrieve driver location. Prices and workflow rules are enforced on the server.
