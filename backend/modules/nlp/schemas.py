from pydantic import BaseModel


class AnalyzeInput(BaseModel):
    employee_name: str
    department: str
    review_text: str
    behavioral_rating: int
    performance_rating: int


class SentimentResult(BaseModel):
    label: str
    confidence: float


class AnalyzeOutput(BaseModel):
    sentiment: SentimentResult
    skills_found: list[str]
    skill_gaps: list[str]
    behavioral_rating: int
    performance_rating: int
    recommendations: str


class BatchAnalyzeInput(BaseModel):
    reviews: list[AnalyzeInput]
