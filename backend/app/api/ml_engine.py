from fastapi import APIRouter, Depends
from app.ml_engine.trainer import ml_engine
from app.explainable_ai.explainer import explainable_ai_engine
from app.core.security import get_current_user, get_current_admin

router = APIRouter(
    prefix="/ml-engine",
    tags=["ML Engine & Explainable AI"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/benchmarks")
def get_benchmarks():
    return ml_engine.get_benchmark_metrics()

@router.post("/train/{model_name}")
def train_model(model_name: str, current_user: dict = Depends(get_current_admin)):
    return ml_engine.train_and_evaluate(model_name)

@router.get("/explain")
def get_explainability(artifact_type: str = "SQL Injection Payload", threat_category: str = "SQL Injection Attack", threat_score: float = 0.94):
    return explainable_ai_engine.explain_prediction(artifact_type, threat_category, threat_score)
