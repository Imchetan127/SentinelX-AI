from app.api.auth import router as auth
from app.api.blue_team import router as blue_team
from app.api.dashboard import router as dashboard
from app.api.ml_engine import router as ml_engine
from app.api.red_team import router as red_team
from app.api.users import router as users
from app.api.attacks import router as attacks
from app.api.analysis import router as analysis
from app.api.incidents import router as incidents
from app.api.models import router as trained_models
from app.api.reports import router as reports
from app.api.validation import router as validation
from app.api.explainability import router as explainability

__all__ = [
    "auth",
    "blue_team",
    "dashboard",
    "ml_engine",
    "red_team",
    "users",
    "attacks",
    "analysis",
    "incidents",
    "trained_models",
    "reports",
    "validation",
    "explainability",
]
