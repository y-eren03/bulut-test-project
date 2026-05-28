from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Temel model sınıfımız
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    attachment_url = Column(String, nullable=True)  # S3'teki dosya linki

    # Etiketler ile ilişki
    tags = relationship("Tag", back_populates="task", cascade="all, delete-orphan")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))

    # Görev ile ilişki
    task = relationship("Task", back_populates="tags")
