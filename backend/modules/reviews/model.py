from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.core.database import Base
import datetime


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    department = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)


class ReviewRecord(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False, index=True)
    department = Column(String, nullable=False, index=True)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String)
    sentiment_confidence = Column(Float)
    skills_found = Column(String)  # comma-separated list
    skill_gaps = Column(String)  # comma-separated list
    behavioral_rating = Column(Integer)
    performance_rating = Column(Integer)
    recommendations = Column(Text)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
