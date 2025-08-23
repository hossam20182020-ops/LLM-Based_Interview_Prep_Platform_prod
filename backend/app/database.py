from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    # No-op in production. Use Alembic migrations instead.
    pass

def init_db_for_tests():
    # For tests only (e.g., in-memory sqlite)
    from app import models  # ensure models imported
    Base.metadata.create_all(bind=engine)
