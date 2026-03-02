from pydantic import BaseModel


class DepartmentStats(BaseModel):
    department: str
    total_reviews: int
    average_sentiment_confidence: float
    most_common_sentiment: str
    average_score_confidence: float
    top_skills: list[str]


class OverviewStats(BaseModel):
    total_reviews: int
    total_employees: int
    total_departments: int
    sentiment_distribution: dict[str, int]
    average_score_confidence: float


class EmployeeStats(BaseModel):
    employee_name: str
    total_reviews: int
    sentiments: list[str]
    all_skills: list[str]
    scores: list[str]
