from jose import JWTError, jwt

from app.config import settings


def validate_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("invalid_token") from exc
    if payload.get("type") != "access" or not payload.get("sub"):
        raise ValueError("invalid_token_type")
    return str(payload["sub"])
