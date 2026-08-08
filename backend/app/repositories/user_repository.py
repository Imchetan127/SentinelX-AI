from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username, User.is_deleted == False)
        return self.session.scalars(statement).first()

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email, User.is_deleted == False)
        return self.session.scalars(statement).first()

    def list_active(self, limit: int = 100, offset: int = 0):
        statement = select(User).where(User.is_deleted == False).limit(limit).offset(offset)
        return self.session.scalars(statement).all()
