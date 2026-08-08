from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.audit import log_auth_event
from app.core.config import settings

security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, username: str, role: str = "user", expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "iat": now,
        "nbf": now,
        "sub": str(user_id),
        "user_id": str(user_id),
        "username": username,
        "role": role,
        "token_type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _raise_auth_error(status_code: int, message: str, event_type: str, username: Optional[str], request: Optional[Request]) -> None:
    ip_address = request.client.host if request and request.client else "unknown"
    log_auth_event(username, ip_address, event_type, "failed", message)
    raise HTTPException(
        status_code=status_code,
        detail={"success": False, "message": message, "code": status_code},
    )


def verify_access_token(token: str, request: Optional[Request] = None) -> Dict[str, Any]:
    if not token:
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "Missing access token", "unauthorized_access", None, request)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "Token expired", "expired_token_attempt", None, request)
    except JWTError:
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "Invalid token", "invalid_token", None, request)

    user_id = payload.get("user_id")
    username = payload.get("username")
    role = payload.get("role")

    if not user_id or not username or not role:
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "Malformed token payload", "invalid_token", None, request)

    return {"id": str(user_id), "username": str(username), "role": str(role)}


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    if not credentials or credentials.scheme.lower() != "bearer":
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized", "unauthorized_access", None, request)
    return verify_access_token(credentials.credentials, request=request)


def get_current_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Admin privileges required", "code": status.HTTP_403_FORBIDDEN},
        )
    return current_user
