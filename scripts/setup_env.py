"""Create a local ignored .env once, without printing credentials."""
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    raise SystemExit(".env already exists; preserving it.")
password, jwt_secret = secrets.token_hex(24), secrets.token_hex(48)
path.write_text(
    "ENVIRONMENT=development\nPOSTGRES_USER=delivery\nPOSTGRES_DB=delivery\n"
    f"POSTGRES_PASSWORD={password}\n"
    f"DATABASE_URL=postgresql+psycopg://delivery:{password}@localhost:5433/delivery\n"
    f"JWT_SECRET={jwt_secret}\nSECURE_COOKIES=false\n"
    'ALLOWED_ORIGINS=["http://localhost:5173"]\n'
)
path.chmod(0o600)
print("Created .env. Keep it private and out of Git.")
