import os
import tempfile

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from src import models
from src.services.s3 import upload_file

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todos.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do List Manager",
    description="Cloud testing project with a security operations themed task board.",
    version="0.2.0",
)
Instrumentator().instrument(app).expose(app)

templates = Jinja2Templates(directory="src/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_task(task: models.Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "attachment_url": task.attachment_url,
        "tags": [tag.name for tag in task.tags],
    }


def get_task_or_404(task_id: int, db: Session) -> models.Task:
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    try:
        return templates.TemplateResponse(
            request=request, name="index.html", context={}
        )
    except TypeError:
        return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    return {"message": "To-Do List Manager API is running"}


@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).order_by(models.Task.id.desc()).all()
    return [serialize_task(task) for task in tasks]


@app.post("/tasks")
def create_task(
    title: str, description: str | None = None, db: Session = Depends(get_db)
):
    clean_title = title.strip()
    if not clean_title:
        raise HTTPException(status_code=422, detail="Task title cannot be empty")

    new_task = models.Task(title=clean_title, description=description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return serialize_task(new_task)


@app.get("/tasks/stats/overview")
def task_stats(db: Session = Depends(get_db)):
    total = db.query(models.Task).count()
    completed = db.query(models.Task).filter(models.Task.is_completed.is_(True)).count()
    open_count = total - completed
    tag_rows = (
        db.query(models.Tag.name, func.count(models.Tag.id))
        .group_by(models.Tag.name)
        .order_by(func.count(models.Tag.id).desc())
        .all()
    )
    return {
        "total": total,
        "open": open_count,
        "completed": completed,
        "completion_rate": round((completed / total) * 100, 2) if total else 0,
        "tags": [{"name": name, "count": count} for name, count in tag_rows],
    }


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    return serialize_task(get_task_or_404(task_id, db))


@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, db)
    task.is_completed = True
    db.commit()
    db.refresh(task)
    return {"message": "Task completed", "task": serialize_task(task)}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, db)
    db.delete(task)
    db.commit()
    return {"message": "Task deleted", "task_id": task_id}


@app.post("/tasks/{task_id}/tags")
def add_task_tag(task_id: int, name: str, db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, db)
    clean_name = name.strip().lower()
    if not clean_name:
        raise HTTPException(status_code=422, detail="Tag name cannot be empty")

    existing = next((tag for tag in task.tags if tag.name == clean_name), None)
    if not existing:
        db.add(models.Tag(name=clean_name, task=task))
        db.commit()
        db.refresh(task)

    return {"message": "Tag attached", "task": serialize_task(task)}


@app.post("/tasks/{task_id}/attachment")
def add_attachment(
    task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    task = get_task_or_404(task_id, db)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        s3_url = upload_file(tmp_path, file.filename)
    finally:
        os.remove(tmp_path)

    if not s3_url:
        raise HTTPException(status_code=500, detail="Failed to upload file to S3")

    task.attachment_url = s3_url
    db.commit()
    db.refresh(task)

    return {"message": "Attachment uploaded successfully", "task": serialize_task(task)}
