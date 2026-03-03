from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func, UniqueConstraint
from src.database.database import Base


class VideoLog(Base):
    __tablename__ = "video_log"

    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    verdict = Column(String(20), nullable=False)
    source = Column(String(20), nullable=False, default="pipeline")
    notes = Column(Text)
    channel_name = Column(Text)
    channel_url = Column(Text)
    profile_used = Column(String(255))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    logged_at = Column(DateTime, default=func.now())
