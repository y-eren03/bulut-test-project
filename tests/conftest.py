import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import threading
import time
import uvicorn
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

class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

@pytest.fixture(scope="session")
def live_server():
    """FastAPI uygulamasını E2E testleri için arka planda (ayrı bir thread'de) uvicorn ile çalıştırır (eğer port 8000 zaten aktif değilse)."""
    import socket
    # Port 8000'in zaten kullanımda olup olmadığını kontrol et
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("127.0.0.1", 8000))
        s.close()
        # Bağlantı başarılı oldu, yani sunucu zaten çalışıyor! Uvicorn başlatmaya gerek yok.
        yield
        return
    except socket.error:
        s.close()

    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
    server = Server(config=config)
    
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    
    # Sunucunun başlamasını bekle
    while not server.started:
        time.sleep(0.1)
        
    yield
    
    server.should_exit = True
    thread.join(timeout=5)
