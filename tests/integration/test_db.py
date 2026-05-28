import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Task

@pytest.fixture(scope="module")
def postgres_container():
    """Testcontainers ile PostgreSQL container'ı başlatır."""
    postgres = PostgresContainer("postgres:16-alpine")
    with postgres as container:
        yield container

@pytest.fixture(scope="module")
def db_engine(postgres_container):
    """Container üzerinden DB bağlantısı (Engine) oluşturur."""
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def integration_db_session(db_engine):
    """Her test için yeni bir DB oturumu açar."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_and_read_task_integration(integration_db_session):
    """PostgreSQL container'ı üzerinde görev oluşturup okumayı test eder."""
    # Yeni görev ekle
    new_task = Task(title="Integration Test Task", description="Testing DB container")
    integration_db_session.add(new_task)
    integration_db_session.commit()
    
    # DB'den oku
    saved_task = integration_db_session.query(Task).filter(Task.title == "Integration Test Task").first()
    assert saved_task is not None
    assert saved_task.id is not None
    assert saved_task.description == "Testing DB container"
