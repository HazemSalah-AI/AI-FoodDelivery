import secrets

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.core.config import Settings
from app.main import create_app


def test_migrations_upgrade_check_downgrade(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path}/migration.db"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    engine = create_engine(url)
    tables = inspect(engine).get_table_names()
    assert {"users", "orders", "assignments", "auth_sessions", "notifications"} <= set(tables)
    with TestClient(
        create_app(Settings(database_url=url, jwt_secret=secrets.token_hex(48)))
    ) as client:
        assert client.get("/api/v1/ready").json() == {"status": "ready"}
    command.check(cfg)
    command.downgrade(cfg, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]
    with TestClient(
        create_app(Settings(database_url=url, jwt_secret=secrets.token_hex(48)))
    ) as client:
        assert client.get("/api/v1/ready").status_code == 503
    command.upgrade(cfg, "head")
    engine.dispose()


def test_postgres_migration_sql_compiles(monkeypatch):
    import io

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://delivery@localhost/delivery")
    output = io.StringIO()
    cfg = Config("alembic.ini", output_buffer=output)
    command.upgrade(cfg, "head", sql=True)
    sql = output.getvalue()
    assert "CREATE UNIQUE INDEX uq_assignment_active_driver" in sql
    assert "WHERE status IN ('Pending','Accepted')" in sql
