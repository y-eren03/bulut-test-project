import pytest
from src.models import Task
from tests.factories import TaskFactory


def test_health_check(client):
    """Health check endpoint'inin 200 dönüp dönmediğini test eder."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "To-Do List Manager API Çalışıyor!"}


def test_create_task(client, db_session):
    """Yeni bir görev (task) oluşturmayı test eder."""
    response = client.post("/tasks?title=Test Task&description=Test Desc")
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Test Desc"
    assert data["is_completed"] is False

    # Veritabanında (DB) görevin doğru kaydedilip kaydedilmediğini doğrula
    task_in_db = db_session.query(Task).filter(Task.id == data["id"]).first()
    assert task_in_db is not None
    assert task_in_db.title == "Test Task"


def test_create_task_with_tags(client):
    """Görev oluştururken virgülle ayrılmış etiketlerin döndüğünü test eder."""
    response = client.post(
        "/tasks?title=Tagged Task&description=Tagged Desc&tags=ci,k8s,s3"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Tagged Task"
    assert data["tags"] == ["ci", "k8s", "s3"]


def test_list_tasks(client, db_session):
    """Görevleri listeleme endpoint'ini test eder."""
    # Factory Boy kullanarak veritabanına sahte (mock) 3 adet görev (task) ekle
    TaskFactory.create_batch(3)

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_delete_task(client, db_session):
    """Bir görevin silinebildiğini test eder."""
    task = TaskFactory()

    response = client.delete(f"/tasks/{task.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted"}

    assert db_session.query(Task).filter(Task.id == task.id).first() is None


def test_delete_task_not_found(client):
    """Olmayan görev silinirken 404 dönmesini test eder."""
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_complete_task(client, db_session):
    """Bir görevi tamamlama (is_completed=True) test eder."""
    task = TaskFactory(is_completed=False)

    response = client.put(f"/tasks/{task.id}/complete")
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Task completed"
    assert data["task"]["is_completed"] is True

    # Gerçekten veritabanında güncellendiğinden (is_completed=True) emin ol
    task_in_db = db_session.query(Task).filter(Task.id == task.id).first()
    assert task_in_db.is_completed is True


import pytest
from src.models import Task
from tests.factories import TaskFactory


def test_health_check(client):
    """Health check endpoint'inin 200 dönüp dönmediğini test eder."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "To-Do List Manager API Çalışıyor!"}


def test_create_task(client, db_session):
    """Yeni bir görev (task) oluşturmayı test eder."""
    response = client.post("/tasks?title=Test Task&description=Test Desc")
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Test Desc"
    assert data["is_completed"] is False

    # Veritabanında (DB) görevin doğru kaydedilip kaydedilmediğini doğrula
    task_in_db = db_session.query(Task).filter(Task.id == data["id"]).first()
    assert task_in_db is not None
    assert task_in_db.title == "Test Task"


def test_create_task_with_tags(client):
    """Görev oluştururken virgülle ayrılmış etiketlerin döndüğünü test eder."""
    response = client.post(
        "/tasks?title=Tagged Task&description=Tagged Desc&tags=ci,k8s,s3"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Tagged Task"
    assert data["tags"] == ["ci", "k8s", "s3"]


def test_list_tasks(client, db_session):
    """Görevleri listeleme endpoint'ini test eder."""
    # Factory Boy kullanarak veritabanına sahte (mock) 3 adet görev (task) ekle
    TaskFactory.create_batch(3)

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_delete_task(client, db_session):
    """Bir görevin silinebildiğini test eder."""
    task = TaskFactory()

    response = client.delete(f"/tasks/{task.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted"}

    assert db_session.query(Task).filter(Task.id == task.id).first() is None


def test_delete_task_not_found(client):
    """Olmayan görev silinirken 404 dönmesini test eder."""
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_complete_task(client, db_session):
    """Bir görevi tamamlama (is_completed=True) test eder."""
    task = TaskFactory(is_completed=False)

    response = client.put(f"/tasks/{task.id}/complete")
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Task completed"
    assert data["task"]["is_completed"] is True

    # Gerçekten veritabanında güncellendiğinden (is_completed=True) emin ol
    task_in_db = db_session.query(Task).filter(Task.id == task.id).first()
    assert task_in_db.is_completed is True


def test_complete_task_not_found(client):
    """Olmayan bir görevi tamamlamaya çalışırken 404 dönmesini test eder."""
    response = client.put("/tasks/999/complete")
    assert response.status_code == 404


def test_read_root(client):
    """Ana sayfanın (HTML) yüklendiğini test eder."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_create_task_empty_title(client):
    """Boş başlıkla görev eklenemeyeceğini test eder."""
    response = client.post("/tasks?title=")
    assert response.status_code == 422


def test_task_stats(client, db_session):
    """Görev istatistiklerinin doğru döndüğünü test eder."""
    TaskFactory(is_completed=True)
    TaskFactory(is_completed=False)

    response = client.get("/tasks/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["completed"] == 1
    assert data["open"] == 1
    assert data["completion_rate"] == 50.0
