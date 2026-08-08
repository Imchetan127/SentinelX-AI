from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin, get_current_user
from app.database.session import get_db
from app.schemas.auth import UserOut
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    service = UserService(db)
    return service.list_users()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    if not user or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(user_id: str, current_user=Depends(get_current_admin), db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    if not user or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    service.user_repo.soft_delete(user)
    return {"success": True, "message": "User soft deleted"}
