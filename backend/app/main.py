from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    analysis,
    auth,
    attacks,
    blue_team,
    dashboard,
    explainability,
    incidents,
    ml_engine,
    red_team,
    reports,
    trained_models,
    users,
    validation,
)

app = FastAPI(
    title="AI-Driven Cyber Threat Simulation & Detection Engine",
    description="Red Team vs Blue Team Enterprise AI Cybersecurity Framework",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        payload = exc.detail
    else:
        payload = {"success": False, "message": str(exc.detail), "code": exc.status_code}

    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "code": 422, "errors": exc.errors()},
    )


from app.api import governance

app.include_router(auth, prefix="/api/v1")
app.include_router(users, prefix="/api/v1")
app.include_router(attacks, prefix="/api/v1")
app.include_router(analysis, prefix="/api/v1")
app.include_router(incidents, prefix="/api/v1")
app.include_router(trained_models, prefix="/api/v1")
app.include_router(reports, prefix="/api/v1")
app.include_router(red_team, prefix="/api/v1")
app.include_router(blue_team, prefix="/api/v1")
app.include_router(ml_engine, prefix="/api/v1")
app.include_router(dashboard, prefix="/api/v1")
app.include_router(governance.router, prefix="/api/v1")
app.include_router(validation, prefix="/api/v1")
app.include_router(explainability, prefix="/api/v1")


@app.on_event("startup")
def run_governance_startup_checks():
    from app.database.base import Base
    from app.database.session import SessionLocal, engine
    from app.services.model_governance_service import ModelGovernanceService

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Table creation warning: {str(e)}")

    db = SessionLocal()
    try:
        gov_service = ModelGovernanceService(db)
        gov_service.startup_validation()
    except Exception as e:
        print(f"Startup governance diagnostics warning: {str(e)}")
    finally:
        db.close()



@app.get("/")
def root():
    return {"status": "ONLINE", "system": "Red Team vs Blue Team AI Cyber Platform", "docs_url": "/docs"}


@app.get("/health")
@app.get("/healthz")
def health_check():
    return {"status": "healthy", "success": True, "service": "backend"}

