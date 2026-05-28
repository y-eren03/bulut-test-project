from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from . import models

# DB bağlantı URL'si (Çevresel değişkenden veya varsayılan SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todos.db")

# Veritabanı motoru ve oturumu
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tabloları oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="To-Do List Manager", description="Bulut Mimarilerinde Test Müh. Projesi")

templates = Jinja2Templates(directory="src/templates")

# Dependency: Her istek için DB session oluştur ve kapat
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
    """Tüm görevleri listeler."""
    tasks = db.query(models.Task).all()
    return tasks

@app.post("/tasks")
def create_task(title: str, description: str = None, db: Session = Depends(get_db)):
    """Yeni bir görev oluşturur."""
    new_task = models.Task(title=title, description=description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Belirtilen görevi tamamlanmış olarak işaretler."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_completed = True
    db.commit()
    db.refresh(task)
    return {"message": "Task completed", "task": task}
