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

    # DB'de kayıtlı mı kontrolü
    task_in_db = db_session.query(Task).filter(Task.id == data["id"]).first()
    assert task_in_db is not None
    assert task_in_db.title == "Test Task"


def test_list_tasks(client, db_session):
    """Görevleri listeleme endpoint'ini test eder."""
    # Factory ile DB'ye 3 tane task ekle
    TaskFactory.create_batch(3)

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_complete_task(client, db_session):
    """Bir görevi tamamlama (is_completed=True) test eder."""
    task = TaskFactory(is_completed=False)

    response = client.put(f"/tasks/{task.id}/complete")
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Task completed"
    assert data["task"]["is_completed"] is True

    # DB kontrolü
    task_in_db = db_session.query(Task).filter(Task.id == task.id).first()
    assert task_in_db.is_completed is True


def test_complete_task_not_found(client):
    """Olmayan bir görevi tamamlamaya çalışırken 404 dönmesini test eder."""
    response = client.put("/tasks/999/complete")
    assert response.status_code == 404
