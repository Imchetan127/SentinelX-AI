from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.schemas.attack import AttackCreate, AttackOut
from app.services.attack_service import AttackService

router = APIRouter(
    prefix="/attacks",
    tags=["Attack Events"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=AttackOut)
def create_attack(payload: AttackCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AttackService(db)
    attack = service.create_attack(
        user_id=current_user["id"],
        attack_type=payload.attack_type,
        payload=payload.payload,
        target=payload.target,
        severity=payload.severity,
        status=payload.status,
        source_ip=payload.source_ip,
    )
    return attack


@router.get("/", response_model=List[AttackOut])
def list_attacks(db: Session = Depends(get_db)):
    service = AttackService(db)
    return service.list_attacks()


@router.get("/{attack_id}", response_model=AttackOut)
def get_attack(attack_id: UUID, db: Session = Depends(get_db)):
    service = AttackService(db)
    attack = service.get_attack(attack_id)
    if not attack or attack.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attack record not found")
    return attack


@router.delete("/{attack_id}")
def delete_attack(attack_id: UUID, db: Session = Depends(get_db)):
    service = AttackService(db)
    attack = service.get_attack(attack_id)
    if not attack or attack.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attack record not found")
    service.soft_delete_attack(attack)
    return {"success": True, "message": "Attack soft deleted"}
