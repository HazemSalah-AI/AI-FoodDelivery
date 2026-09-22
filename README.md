# Abo Hammad Delivery System

Website-only local marketplace for Abu Hammad, Egypt. Cash on Delivery only.

All four role workflows and container packaging are implemented and CI-validated. Read [PROJECT_STATUS.md](PROJECT_STATUS.md) before continuing.
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

## Local setup

Python 3.12 and Node 24 are required. From the repository root:

```bash
python scripts/setup_env.py
python -m venv .venv
# Windows Git Bash: source .venv/Scripts/activate
# Linux/macOS: source .venv/bin/activate
pip install -r backend/requirements-dev.txt
docker compose up -d db
cd backend
alembic upgrade head
python -m app.bootstrap
uvicorn app.main:create_app --factory --reload --port 8000
```

In another terminal: `cd frontend`, `npm ci`, `npm run dev`. Open http://localhost:5173.
API health: http://localhost:8000/api/v1/health; Swagger: http://localhost:8000/docs.
Run `pytest` and `ruff check .` from `backend/`; `npm run build` from `frontend/`.
The health route is a liveness check and intentionally does not create the schema.
Customer, merchant, driver and admin interfaces are implemented and browser-tested.

Optional sample catalog and role accounts: on a fresh **development** database run `python -m app.seed_demo`
from backend and choose a 12+ character password when prompted. Do not run this in production.
No preset passwords are provided; the seed refuses to overwrite existing demo accounts.

Browser verification: install Chromium with `cd frontend && npx playwright install chromium`, then
from the repository root with the Python virtualenv active run `python scripts/run_e2e.py`. This
creates a separate temporary database and ephemeral credentials, starts both apps, and cleans up.

## Container deployment

For the full local stack: `python scripts/setup_env.py` (first setup only), then
`docker compose --profile app up --build -d`. Create the initial admin with
`docker compose exec backend python -m app.bootstrap` and open http://localhost:8080.
Production HTTPS setup and update/backup procedures: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
No cloud resources have been provisioned or site deployed by this repository change.
