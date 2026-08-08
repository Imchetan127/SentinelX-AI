from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.red_team.generator import red_team_generator
from app.core.security import get_current_user
from app.database.session import get_db
from app.services.attack_service import AttackService
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/red-team",
    tags=["Red Team Simulations"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/vectors")
def list_attack_vectors():
    return {"vectors": red_team_generator.get_all_vectors()}

@router.post("/simulate/{vector_id}")
def run_simulation(vector_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 1. Generate simulation payload
    sim_result = red_team_generator.simulate_attack(vector_id)
    vector = sim_result["vector_details"]

    # 2. Persist attack to DB
    user_id = UUID(current_user["id"]) if current_user.get("id") else None
    attack_service = AttackService(db)
    payload_str = str(vector["payload"])
    attack = attack_service.create_attack(
        user_id=user_id,
        attack_type=vector["name"],
        payload=payload_str,
        target="system",
        severity=vector["risk_level"].lower(),
        status="completed",
        source_ip="127.0.0.1",
    )

    # 3. Log Launch Attack action
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=user_id,
        action="LAUNCH_ATTACK",
        resource="Attack",
        resource_id=attack.id,
        ip_address="127.0.0.1",
        status="success",
        details=f"Red Team Simulation executed: {vector['name']} ({vector['category']}) [Severity: {attack.severity.value}]",
    )

    return sim_result

