from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="agenttrust")
    app_env: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./agenttrust.db")
    log_level: str = Field(default="INFO")
    jwt_issuer: str = Field(default="https://issuer.example.com")
    jwt_audience: str = Field(default="agenttrust-api")
    jwt_algorithm: str = Field(default="RS256")
    jwt_public_key: str | None = Field(default=None)
    jwt_jwks_url: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()
