from pydantic import BaseModel


class SkillCount(BaseModel):
    skill: str
    count: int


class OverviewStats(BaseModel):
    total_reviews: int
    average_behavioral_rating: float
    average_performance_rating: float
    sentiment_distribution: dict[str, int]
    top_skills: list[SkillCount]
    top_gaps: list[SkillCount]


class DepartmentStats(BaseModel):
    department: str
    total_reviews: int
    average_behavioral_rating: float
    average_performance_rating: float
    sentiment_distribution: dict[str, int]
    top_skills: list[SkillCount]
    top_gaps: list[SkillCount]


class EmployeeTrendPoint(BaseModel):
    date: str
    behavioral_rating: int
    performance_rating: int
    sentiment: str


class EmployeeStats(BaseModel):
    employee_name: str
    total_reviews: int
    sentiments: list[str]
    all_skills: list[str]
    scores: list[str]
