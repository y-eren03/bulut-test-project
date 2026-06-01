import time

import docker
import psycopg2
import pytest
from docker.errors import DockerException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Task


@pytest.fixture(scope="module")
def postgres_url():
    """Docker ile PostgreSQL başlatır ve yerel ağ (localhost) bağlantı URL'sini döndürür."""
    try:
        client = docker.from_env()
        client.ping()
    except DockerException as exc:
        pytest.skip(f"Entegrasyon testleri için Docker servisine ulaşılamıyor: {exc}")

    image = "postgres:16-alpine"
    client.images.pull(image)
    container = client.containers.run(
        image,
        detach=True,
        environment={
            "POSTGRES_USER": "test",
            "POSTGRES_PASSWORD": "test",
            "POSTGRES_DB": "test",
        },
        ports={"5432/tcp": None},
    )

    try:
        container.reload()
        host_port = container.attrs["NetworkSettings"]["Ports"]["5432/tcp"][0][
            "HostPort"
        ]
        connection_url = f"postgresql://test:test@localhost:{host_port}/test"

        # Veritabanının bağlantı kabul edene kadar hazır olmasını bekle
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=host_port,
                    dbname="test",
                    user="test",
                    password="test",
                )
                conn.close()
                break
            except psycopg2.OperationalError:
                time.sleep(0.5)
        else:
            pytest.fail("PostgreSQL container'ı belirtilen sürede hazır olamadı")

        yield connection_url
    finally:
        # Testler bittikten sonra container'ı durdur ve temizle
        container.stop(timeout=5)
        container.remove(force=True)


@pytest.fixture(scope="module")
def db_engine(postgres_url):
    """PostgreSQL container'ı için SQLAlchemy bağlantı motoru (engine) oluşturur."""
    engine = create_engine(postgres_url)
    # Veritabanı tablolarını oluştur
    Base.metadata.create_all(engine)
    yield engine
    # Test bitiminde tabloları sil
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def integration_db_session(db_engine):
    """Her entegrasyon testi için yepyeni bir veritabanı oturumu açar."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()


def test_create_and_read_task_integration(integration_db_session):
    """PostgreSQL container'ı üzerinde görev oluşturup okumayı test eder."""
    new_task = Task(title="Integration Test Task", description="Testing DB container")
    integration_db_session.add(new_task)
    integration_db_session.commit()

    saved_task = (
        integration_db_session.query(Task)
        .filter(Task.title == "Integration Test Task")
        .first()
    )
    assert saved_task is not None
    assert saved_task.id is not None
    assert saved_task.description == "Testing DB container"


def test_update_task_status_integration(integration_db_session):
    """PostgreSQL container'ı üzerinde görev durumunu güncellemeyi test eder."""
    new_task = Task(title="Status Update Task")
    integration_db_session.add(new_task)
    integration_db_session.commit()

    task_id = new_task.id
    task_to_update = (
        integration_db_session.query(Task).filter(Task.id == task_id).first()
    )
    task_to_update.is_completed = True
    integration_db_session.commit()

    updated_task = integration_db_session.query(Task).filter(Task.id == task_id).first()
    assert updated_task.is_completed is True


def test_delete_task_integration(integration_db_session):
    """PostgreSQL container'ı üzerinde görev silmeyi test eder."""
    new_task = Task(title="Delete Me Task")
    integration_db_session.add(new_task)
    integration_db_session.commit()

    task_id = new_task.id
    task_to_delete = (
        integration_db_session.query(Task).filter(Task.id == task_id).first()
    )
    integration_db_session.delete(task_to_delete)
    integration_db_session.commit()

    deleted_task = integration_db_session.query(Task).filter(Task.id == task_id).first()
    assert deleted_task is None
