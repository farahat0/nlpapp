from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EmployeeCreate(BaseModel):
    name: str
    department: str


class EmployeeOut(BaseModel):
    id: int
    name: str
    department: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewInput(BaseModel):
    employee_name: str
    department: str
    review_text: str
    behavioral_rating: int
    performance_rating: int


class ReviewOutput(BaseModel):
    id: int
    employee_name: str
    department: str
    review_text: str
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None
    skills_found: Optional[list[str]] = None
    skill_gaps: Optional[list[str]] = None
    behavioral_rating: Optional[int] = None
    performance_rating: Optional[int] = None
    recommendations: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
