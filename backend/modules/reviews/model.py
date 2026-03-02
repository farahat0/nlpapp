from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.core.database import Base
import datetime


class ReviewRecord(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False, index=True)
    department = Column(String, nullable=False, index=True)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String)
    sentiment_confidence = Column(Float)
    skills_found = Column(String)  # comma-separated list
    performance_score = Column(String)
    score_confidence = Column(Float)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
