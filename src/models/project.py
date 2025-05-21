from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    purpose = Column(Text)
    description = Column(Text)
    desired_outcome = Column(Text)
    created_at = Column(DateTime, default=func.now())
    deadline = Column(DateTime)
    status = Column(String(50), default="active")
    priority = Column(String(50), default="normal")
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        # Return all column fields dynamically
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
