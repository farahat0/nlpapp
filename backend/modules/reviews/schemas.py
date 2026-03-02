from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReviewInput(BaseModel):
    employee_name: str
    department: str
    review_text: str


class ReviewOutput(BaseModel):
    id: int
    employee_name: str
    department: str
    review_text: str
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None
    skills_found: Optional[list[str]] = None
    performance_score: Optional[str] = None
    score_confidence: Optional[float] = None
    recommendations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
