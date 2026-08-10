from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.attack import Attack
from app.models.enums import Severity, AttackStatus
from app.repositories.attack_repository import AttackRepository


class AttackService:
    def __init__(self, db: Session):
        self.db = db
        self.attack_repo = AttackRepository(db)

    def create_attack(
        self,
        user_id: UUID,
        attack_type: str,
        payload: str,
        target: str | None = None,
        severity: str = "medium",
        status: str = "open",
        source_ip: str | None = None,
    ) -> Attack:
        # Map string severity to Enum
        try:
            sev_enum = Severity[severity.upper()]
        except KeyError:
            sev_enum = Severity.MEDIUM

        # Map string status to Enum
        try:
            stat_enum = AttackStatus[status.upper()]
        except KeyError:
            if status.lower() == "open":
                stat_enum = AttackStatus.PENDING
            else:
                stat_enum = AttackStatus.PENDING

        valid_user_id = None
        if user_id:
            try:
                from app.models.user import User
                existing_user = self.db.get(User, user_id)
                if existing_user:
                    valid_user_id = user_id
            except Exception:
                valid_user_id = None

        attack = Attack(
            created_by=valid_user_id,
            type=attack_type,
            payload=payload,
            target=target,
            severity=sev_enum,
            status=stat_enum,
            source_ip=source_ip,
            timestamp=datetime.now(timezone.utc),
        )
        try:
            self.attack_repo.add(attack)
            self.db.commit()
            self.db.refresh(attack)
            return attack
        except Exception:
            self.db.rollback()
            raise

    def list_attacks(self, limit: int = 100, offset: int = 0) -> List[Attack]:
        return self.attack_repo.list(limit=limit, offset=offset)

    def get_attack(self, attack_id: UUID) -> Attack:
        return self.attack_repo.get(attack_id)

    def get_recent_attacks(self, limit: int = 5) -> List[Attack]:
        return self.attack_repo.get_recent(limit=limit)

    def soft_delete_attack(self, attack: Attack) -> Attack:
        try:
            res = self.attack_repo.soft_delete(attack)
            self.db.commit()
            return res
        except Exception:
            self.db.rollback()
            raise
