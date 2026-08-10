from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.red_team.generator import red_team_generator
from app.core.security import get_current_user
from app.database.session import get_db
from app.services.attack_service import AttackService
from app.services.audit_service import AuditService

from app.services.event_pipeline_service import EventPipelineService

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
    source_ip = vector.get("source_ip") or vector.get("payload", {}).get("headers", {}).get("X-Originating-IP") or "198.51.100.42"
    attack = attack_service.create_attack(
        user_id=user_id,
        attack_type=vector["name"],
        payload=payload_str,
        target="system",
        severity=vector["risk_level"].lower(),
        status="completed",
        source_ip=source_ip,
    )

    # 3. Trigger End-to-End Blue Team Detection Pipeline Server-Side
    pipeline_service = EventPipelineService(db)
    pipeline_output = pipeline_service.process_attack(attack.id, user_id=user_id)

    # 4. Attach persistent correlation keys and pipeline execution details
    sim_result["attack_id"] = str(attack.id)
    sim_result["pipeline"] = pipeline_output
    sim_result["status"] = "success"

    return sim_result

