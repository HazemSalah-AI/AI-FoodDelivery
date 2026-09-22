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

## Local setup (foundation)

Python 3.12+ and Node 22+ are required. From the repository root:

```bash
python scripts/setup_env.py
python -m venv .venv
# Windows Git Bash: source .venv/Scripts/activate
# Linux/macOS: source .venv/bin/activate
pip install -r backend/requirements-dev.txt
docker compose up -d db
cd backend
uvicorn app.main:create_app --factory --reload --port 8000
```

In another terminal: `cd frontend`, `npm ci`, `npm run dev`. Open http://localhost:5173.
API health: http://localhost:8000/api/v1/health; Swagger: http://localhost:8000/docs.
Run `pytest` and `ruff check .` from `backend/`; `npm run build` from `frontend/`.
The health route is a liveness check and intentionally does not create the schema.
Application domains and database migrations are the next checkpoint.
