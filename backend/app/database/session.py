from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def create_engine_instance() -> create_engine:
    return create_engine(settings.DATABASE_URL, echo=settings.DB_ECHO, future=True)


def get_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


engine = create_engine_instance()
SessionLocal = get_session_factory(engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
