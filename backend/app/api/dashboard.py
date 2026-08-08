from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_admin, get_current_user
from app.database.session import get_db
from app.schemas.dashboard import DashboardMetrics
from app.services.audit_service import AuditService
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Security Dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    service = DashboardService(db)
    return service.get_metrics()


@router.post("/reset")
def reset_dashboard(current_user: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    audit_service = AuditService(db)
    audit_service.clear_logs()
    return {"success": True, "message": "Dashboard activity timeline has been reset."}


@router.delete("/logs")
def delete_audit_logs(current_user: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    audit_service = AuditService(db)
    audit_service.clear_logs()
    return {"success": True, "message": "Security audit log has been cleared."}
