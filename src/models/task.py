from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

metadata = Base.metadata


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="todo")  # e.g., todo, in progress, done
    priority = Column(String(50), default="medium")  # e.g., low, medium, high
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )
    due_date = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="tasks")

    def to_dict(self):
        # Return all column fields dynamically
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
