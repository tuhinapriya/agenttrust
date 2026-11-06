import time

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.main import create_app


def _build_rsa_keypair() -> tuple[bytes, bytes]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def _issue_token(monkeypatch, *, subject: str, issuer: str, audience: str, expired: bool = False) -> str:
    private_pem, public_pem = _build_rsa_keypair()
    monkeypatch.setenv("JWT_ISSUER", issuer)
    monkeypatch.setenv("JWT_AUDIENCE", audience)
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem.decode())
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")

    payload = {
        "sub": subject,
        "iss": issuer,
        "aud": audience,
        "exp": int(time.time()) - 60 if expired else int(time.time()) + 300,
    }
    return jwt.encode(payload, private_pem, algorithm="RS256")


def test_valid_jwt_returns_agent_identity(monkeypatch) -> None:
    monkeypatch.setenv("JWT_ISSUER", "https://issuer.example.com")
    monkeypatch.setenv("JWT_AUDIENCE", "agenttrust-api")
    private_pem, public_pem = _build_rsa_keypair()
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem.decode())
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")

    token = jwt.encode(
        {
            "sub": "agent-123",
            "iss": "https://issuer.example.com",
            "aud": "agenttrust-api",
            "exp": int(time.time()) + 300,
        },
        private_pem,
        algorithm="RS256",
    )

    client = TestClient(create_app())
    response = client.get("/api/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["agent_id"] == "agent-123"


def test_missing_token_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("JWT_ISSUER", "https://issuer.example.com")
    monkeypatch.setenv("JWT_AUDIENCE", "agenttrust-api")
    _private_pem, public_pem = _build_rsa_keypair()
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem.decode())
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")

    client = TestClient(create_app())
    response = client.get("/api/whoami")

    assert response.status_code == 401


def test_wrong_issuer_is_rejected(monkeypatch) -> None:
    private_pem, public_pem = _build_rsa_keypair()
    monkeypatch.setenv("JWT_ISSUER", "https://issuer.example.com")
    monkeypatch.setenv("JWT_AUDIENCE", "agenttrust-api")
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem.decode())
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")

    token = jwt.encode(
        {
            "sub": "agent-123",
            "iss": "https://evil.example.com",
            "aud": "agenttrust-api",
            "exp": int(time.time()) + 300,
        },
        private_pem,
        algorithm="RS256",
    )

    client = TestClient(create_app())
    response = client.get("/api/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_wrong_audience_is_rejected(monkeypatch) -> None:
    private_pem, public_pem = _build_rsa_keypair()
    monkeypatch.setenv("JWT_ISSUER", "https://issuer.example.com")
    monkeypatch.setenv("JWT_AUDIENCE", "agenttrust-api")
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem.decode())
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")

    token = jwt.encode(
        {
            "sub": "agent-123",
            "iss": "https://issuer.example.com",
            "aud": "wrong-audience",
            "exp": int(time.time()) + 300,
        },
        private_pem,
        algorithm="RS256",
    )

    client = TestClient(create_app())
    response = client.get("/api/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_expired_token_is_rejected(monkeypatch) -> None:
    token = _issue_token(
        monkeypatch,
        subject="agent-123",
        issuer="https://issuer.example.com",
        audience="agenttrust-api",
        expired=True,
    )

    client = TestClient(create_app())
    response = client.get("/api/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
