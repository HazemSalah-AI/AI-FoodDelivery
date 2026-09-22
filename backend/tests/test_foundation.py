import secrets

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import create_app


def test_app_boots_without_implicitly_creating_schema(tmp_path):
    settings = Settings(
        jwt_secret=secrets.token_hex(32), database_url=f"sqlite:///{tmp_path}/app.db"
    )
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        assert client.get("/openapi.json").status_code == 200
    assert not (tmp_path / "app.db").exists()


def test_production_rejects_insecure_config():
    with pytest.raises(ValidationError, match="secure cookies"):
        Settings(environment="production", jwt_secret=secrets.token_hex(32))
