import pytest

from app.config import Settings, get_settings


def test_settings_loads_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = Settings()

    assert settings.app_name == "agenttrust"
    assert settings.database_url == "sqlite:///./agenttrust.db"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"


def test_get_settings_returns_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "agenttrust-test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = get_settings()

    assert settings.app_name == "agenttrust-test"
    assert settings.database_url == "sqlite:///./test.db"
    assert settings.app_env == "test"
    assert settings.log_level == "DEBUG"
