import re
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import log_auth_event
from app.core.security import create_access_token, get_current_user
from app.database.session import get_db
from app.schemas.auth import TokenResponse, UserLogin, UserRegister
from app.services.audit_service import AuditService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _error_response(status_code: int, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"success": False, "message": message, "code": status_code},
    )


@router.post("/register", response_model=TokenResponse)
def register(user: UserRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    username = user.username.strip()

    if not username:
        log_auth_event(None, client_ip, "registration", "failed", "Username is required")
        raise _error_response(status.HTTP_400_BAD_REQUEST, "Username is required")

    if not re.fullmatch(r"^[A-Za-z0-9_.-]{3,40}$", username):
        log_auth_event(username, client_ip, "registration", "failed", "Username format is invalid")
        raise _error_response(status.HTTP_400_BAD_REQUEST, "Username format is invalid")

    user_service = UserService(db)
    audit_service = AuditService(db)

    try:
        new_user = user_service.register_user(username=username, email=str(user.email), password=user.password)
    except HTTPException as exc:
        log_auth_event(username, client_ip, "registration", "failed", exc.detail)
        raise exc

    token = create_access_token(user_id=str(new_user.id), username=new_user.username, role=new_user.role)
    audit_service.log_action(
        user_id=new_user.id,
        action="registration",
        resource="user",
        resource_id=new_user.id,
        ip_address=client_ip,
        status="success",
        details="User registered",
    )
    log_auth_event(username, client_ip, "registration", "success", "User registered")

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "username": new_user.username,
        "role": new_user.role,
        "user_id": str(new_user.id),
    }


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    username = user.username.strip()

    if not username:
        log_auth_event(None, client_ip, "login", "failed", "Username is required")
        raise _error_response(status.HTTP_400_BAD_REQUEST, "Username is required")

    user_service = UserService(db)
    audit_service = AuditService(db)
    db_user = user_service.authenticate_user(username=username, password=user.password)
    if not db_user:
        log_auth_event(username, client_ip, "login", "failed", "Invalid username or password")
        raise _error_response(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    token = create_access_token(user_id=str(db_user.id), username=db_user.username, role=db_user.role)
    audit_service.log_action(
        user_id=db_user.id,
        action="login",
        resource="user",
        resource_id=db_user.id,
        ip_address=client_ip,
        status="success",
        details="User logged in",
    )
    log_auth_event(username, client_ip, "login", "success", "User logged in")
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "username": db_user.username,
        "role": db_user.role,
        "user_id": str(db_user.id),
    }


@router.post("/logout")
def logout(request: Request, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.get("id"),
        action="logout",
        resource="user",
        resource_id=current_user.get("id"),
        ip_address=client_ip,
        status="success",
        details="User logged out",
    )
    log_auth_event(current_user.get("username"), client_ip, "logout", "success", "User logged out")
    return {"success": True, "message": "Logged out"}


@router.get("/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}
