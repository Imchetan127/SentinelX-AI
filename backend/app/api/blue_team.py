from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from app.blue_team.analyzer import blue_team_analyzer
from app.core.security import get_current_user
from app.database.session import get_db
from app.services.analysis_service import AnalysisService

router = APIRouter(
    prefix="/blue-team",
    tags=["Blue Team Monitoring & Detection"],
    dependencies=[Depends(get_current_user)]
)

class TextInspectionRequest(BaseModel):
    content: str
    artifact_type: str = "text"

class UrlInspectionRequest(BaseModel):
    url: str

class EmailInspectionRequest(BaseModel):
    subject: str
    sender: str
    body: str

@router.post("/inspect-text")
def inspect_text(
    payload: TextInspectionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    res = blue_team_analyzer.analyze_text(payload.content, payload.artifact_type)
    user_id = UUID(current_user["id"]) if current_user.get("id") else None
    analysis_service = AnalysisService(db)
    analysis_service.record_blue_team_inspection(
        user_id=user_id,
        artifact_type=payload.artifact_type,
        threat_detected=res["threat_detected"],
        threat_category=res["threat_category"],
        risk_level=res["risk_level"],
        confidence=res["confidence_score"],
        recommendations=res["recommended_mitigations"],
        payload=payload.content,
        source_ip="127.0.0.1"
    )
    return res

@router.post("/inspect-url")
def inspect_url(
    payload: UrlInspectionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    res = blue_team_analyzer.inspect_url(payload.url)
    user_id = UUID(current_user["id"]) if current_user.get("id") else None
    analysis_service = AnalysisService(db)
    analysis_service.record_blue_team_inspection(
        user_id=user_id,
        artifact_type="url",
        threat_detected=res["is_phishing"],
        threat_category=res["category"],
        risk_level=res["risk_level"],
        confidence=res["confidence_score"],
        recommendations=res["mitigation"],
        payload=payload.url,
        source_ip="127.0.0.1"
    )
    return res

@router.post("/inspect-email")
def inspect_email(
    payload: EmailInspectionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    res = blue_team_analyzer.inspect_email(payload.subject, payload.sender, payload.body)
    user_id = UUID(current_user["id"]) if current_user.get("id") else None
    analysis_service = AnalysisService(db)
    analysis_service.record_blue_team_inspection(
        user_id=user_id,
        artifact_type="email",
        threat_detected=res["is_spam"],
        threat_category=res["category"],
        risk_level=res["risk_level"],
        confidence=res["confidence_score"],
        recommendations=res["mitigation"],
        payload=f"Subject: {payload.subject} | Sender: {payload.sender} | Body: {payload.body}",
        source_ip="127.0.0.1"
    )
    return res

@router.post("/upload-file")
async def upload_and_inspect(
    file: UploadFile = File(...),
    artifact_type: str = Form("file"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    content_bytes = await file.read()
    text_content = content_bytes.decode("utf-8", errors="ignore")
    res = blue_team_analyzer.analyze_text(text_content, artifact_type)
    user_id = UUID(current_user["id"]) if current_user.get("id") else None
    analysis_service = AnalysisService(db)
    analysis_service.record_blue_team_inspection(
        user_id=user_id,
        artifact_type=artifact_type,
        threat_detected=res["threat_detected"],
        threat_category=res["threat_category"],
        risk_level=res["risk_level"],
        confidence=res["confidence_score"],
        recommendations=res["recommended_mitigations"],
        payload=f"File: {file.filename} | Content: {text_content[:1000]}",
        source_ip="127.0.0.1"
    )
    res["filename"] = file.filename
    res["file_size_bytes"] = len(content_bytes)
    return res
