from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile
from prometheus_fastapi_instrumentator import Instrumentator
from . import models
from .observability import setup_observability
from src.services.s3 import upload_file

# Demo Mesajı
# DB bağlantı URL'si (Çevresel değişkenden veya varsayılan SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todos.db")

# Veritabanı motoru ve oturumu
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tabloları oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do List Manager", description="Bulut Mimarilerinde Test Müh. Projesi"
)

# Prometheus Metriklerini Ekle
Instrumentator().instrument(app).expose(app)
setup_observability(app)

templates = Jinja2Templates(directory="src/templates")


# Her HTTP isteği (request) için veritabanı oturumu oluşturur ve sonunda kapatır
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Ana sayfayı (HTML arayüzü) döndürür."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Basit bir sağlık kontrolü endpoint'i."""
    return {"message": "To-Do List Manager API Çalışıyor!"}


@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    """Tüm görevleri en yeniden eskiye doğru sıralayarak listeler."""
    tasks = db.query(models.Task).order_by(models.Task.id.desc()).all()
    return [serialize_task(task) for task in tasks]


@app.post("/tasks")
def create_task(
    title: str,
    description: str | None = None,
    tags: str | None = None,
    db: Session = Depends(get_db),
):
    """Verilen başlık ve açıklama ile veritabanına yeni bir görev ekler."""
    clean_title = title.strip()
    if not clean_title:
        raise HTTPException(status_code=422, detail="Task title cannot be empty")

    new_task = models.Task(title=clean_title, description=description)
    if tags:
        for tag_name in [t.strip() for t in tags.split(",") if t.strip()]:
            new_task.tags.append(models.Tag(name=tag_name))

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return serialize_task(new_task)


@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Belirtilen ID'ye sahip görevi tamamlandı (completed) olarak işaretler."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_completed = True
    db.commit()
    db.refresh(task)
    return {"message": "Task completed", "task": serialize_task(task)}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Belirtilen görevi siler."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


@app.get("/tasks/stats/overview")
def task_stats(db: Session = Depends(get_db)):
    """Görevlerin toplam, tamamlanma ve etiket istatistiklerini hesaplayıp döndürür."""
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


@app.post("/tasks/{task_id}/attachment")
def add_attachment(
    task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Görefe bir dosya (attachment) ekler ve LocalStack S3'e yükler."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Dosyayı geçici olarak diske kaydet
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    # S3'e yükle
    s3_url = upload_file(tmp_path, file.filename)
    os.remove(tmp_path)

    if not s3_url:
        raise HTTPException(status_code=500, detail="Failed to upload file to S3")

    task.attachment_url = s3_url
    db.commit()
    db.refresh(task)

    return {"message": "Attachment uploaded successfully", "task": serialize_task(task)}


def parse_tags(tags: str = None):
    if not tags:
        return []
    return [tag.strip() for tag in tags.split(",") if tag.strip()]


def serialize_task(task: models.Task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "attachment_url": task.attachment_url,
        "tags": [tag.name for tag in task.tags],
    }
