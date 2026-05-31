from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Görev (Task) veritabanı tablosu şeması
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    attachment_url = Column(String, nullable=True)

    # Göreve ait etiketlerle (Tag) bire-çok ilişki
    tags = relationship("Tag", back_populates="task", cascade="all, delete-orphan")


# Etiket (Tag) veritabanı tablosu şeması
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # Etiketin bağlı olduğu ana görev (Task) ilişkisi
    task = relationship("Task", back_populates="tags")
