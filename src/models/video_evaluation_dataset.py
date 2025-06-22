from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, func
from src.database.database import Base

metadata = Base.metadata


class VideoEvaluationDataset(Base):
    __tablename__ = "video_evaluation_dataset"

    id = Column(Integer, primary_key=True)
    
    # User context
    user_background = Column(Text, nullable=False)
    
    # First video
    first_video_summary = Column(Text, nullable=False)
    first_video_url = Column(String(1000), nullable=True)
    first_video_author = Column(String(255), nullable=True)
    
    # Second video
    second_video_summary = Column(Text, nullable=False)
    second_video_url = Column(String(1000), nullable=True)
    second_video_author = Column(String(255), nullable=True)
    
    # Expected output (keep as JSON to preserve flexibility)
    expected_output = Column(JSON, nullable=False)
    selected_video = Column(String(50), nullable=False)  # "first_video", "second_video", "both"
    
    # Metadata
    model_used = Column(String(100), nullable=True)  # Model used to generate expected output
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())