import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app, get_db
from src.models import Base
from tests.factories import TaskFactory, TagFactory

# Test için in-memory SQLite veritabanı (hızlı unit testler için)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Her test fonksiyonu için yeni bir DB oluşturur ve siler."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Factory Boy session set
    TaskFactory._meta.sqlalchemy_session = session
    TagFactory._meta.sqlalchemy_session = session

    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI test istemcisini dependency override ile döndürür."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
