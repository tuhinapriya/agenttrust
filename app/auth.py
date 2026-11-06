from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

security = HTTPBearer(auto_error=False)


def _get_verification_key(token: str) -> str:
    settings = get_settings()
    if settings.jwt_public_key:
        return settings.jwt_public_key
    if settings.jwt_jwks_url:
        jwk_client = jwt.PyJWKClient(settings.jwt_jwks_url)
        return jwk_client.get_signing_key_from_jwt(token).key
    raise ValueError("JWT verification key is not configured")


def validate_jwt_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    verification_key = _get_verification_key(token)

    try:
        payload = jwt.decode(
            token,
            verification_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing subject claim",
        )

    return payload


def require_agent_identity(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, Any]:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    return validate_jwt_token(credentials.credentials)
