from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")
    environment: str = "development"
    database_url: str = "postgresql+psycopg://delivery@localhost:5433/delivery"
    jwt_secret: str = Field(min_length=32)
    session_hours: int = Field(default=12, ge=1, le=24)
    secure_cookies: bool = False
    allowed_origins: list[str] = ["http://localhost:5173"]

    @model_validator(mode="after")
    def validate_security(self):
        if "replace" in self.jwt_secret.lower() or "change-me" in self.jwt_secret.lower():
            raise ValueError("Generate JWT_SECRET with scripts/setup_env.py")
        if self.environment == "production":
            if not self.secure_cookies:
                raise ValueError("Production requires secure cookies")
            if not self.database_url.startswith("postgresql"):
                raise ValueError("Production requires PostgreSQL")
            if any(not value.startswith("https://") for value in self.allowed_origins):
                raise ValueError("Production requires explicit HTTPS origins")
        return self
