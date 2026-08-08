from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def register_user(self, username: str, email: str, password: str, role: str = "user") -> User:
        if self.user_repo.get_by_username(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        if self.user_repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        hashed_password = get_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_password, role=role)
        try:
            self.user_repo.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repo.get(user_id)

    def list_users(self, limit: int = 100, offset: int = 0):
        return self.user_repo.list_active(limit=limit, offset=offset)

    def update_last_login(self, user: User) -> User:
        from datetime import datetime, timezone

        user.last_login = datetime.now(timezone.utc)
        try:
            self.user_repo.session.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise
