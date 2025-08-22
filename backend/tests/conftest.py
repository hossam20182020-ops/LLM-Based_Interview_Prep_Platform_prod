import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Import after setting envs
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["CORS_ORIGINS"] = "http://testserver"

from app.database import Base, SessionLocal
from app.main import app, get_db
from app import models

@pytest.fixture(scope="session")
def engine():
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="session", autouse=True)
def create_tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the app's DB dependency to use our sqlite session
app.dependency_overrides[get_db] = lambda: iter([pytest.lazy_fixture("db_session")])

@pytest.fixture
def client():
    return TestClient(app)
