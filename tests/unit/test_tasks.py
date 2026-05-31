from src.models import Task
from tests.factories import TaskFactory


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "To-Do List Manager API is running"}


def test_create_task(client, db_session):
    response = client.post("/tasks?title=Test Task&description=Test Desc")
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Test Desc"
    assert data["is_completed"] is False
    assert data["tags"] == []

    task_in_db = db_session.query(Task).filter(Task.id == data["id"]).first()
    assert task_in_db is not None
    assert task_in_db.title == "Test Task"


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks?title=%20%20")
    assert response.status_code == 422


def test_list_tasks(client):
    TaskFactory.create_batch(3)

    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_task(client):
    task = TaskFactory(title="Investigate alert")

    response = client.get(f"/tasks/{task.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Investigate alert"


def test_complete_task(client, db_session):
    task = TaskFactory(is_completed=False)

    response = client.put(f"/tasks/{task.id}/complete")
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Task completed"
    assert data["task"]["is_completed"] is True

    task_in_db = db_session.query(Task).filter(Task.id == task.id).first()
    assert task_in_db.is_completed is True


def test_complete_task_not_found(client):
    response = client.put("/tasks/999/complete")
    assert response.status_code == 404


def test_add_task_tag(client):
    task = TaskFactory(title="Secure pipeline")

    response = client.post(f"/tasks/{task.id}/tags?name=CI")
    assert response.status_code == 200
    assert response.json()["task"]["tags"] == ["ci"]


def test_task_stats(client):
    TaskFactory.create_batch(2, is_completed=False)
    TaskFactory(is_completed=True)

    response = client.get("/tasks/stats/overview")
    assert response.status_code == 200
    assert response.json() == {
        "total": 3,
        "open": 2,
        "completed": 1,
        "completion_rate": 33.33,
        "tags": [],
    }


def test_delete_task(client, db_session):
    task = TaskFactory()

    response = client.delete(f"/tasks/{task.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted", "task_id": task.id}
    assert db_session.query(Task).filter(Task.id == task.id).first() is None
