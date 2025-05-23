from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from database.database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # e.g., "video", "article", "paper"
    notes = Column(Text)
    added_at = Column(DateTime, default=func.now())
    is_consumed = Column(Boolean, default=False)

    task = relationship("Task", back_populates="resources")