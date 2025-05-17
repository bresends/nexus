from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()
metadata = Base.metadata


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        return {"name": self.name, "description": self.description}
