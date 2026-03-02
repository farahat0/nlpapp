from pydantic import BaseModel


class AnalyzeInput(BaseModel):
    employee_name: str
    department: str
    review_text: str


class SentimentResult(BaseModel):
    label: str
    confidence: float


class ScoreResult(BaseModel):
    score: str
    confidence: float


class AnalyzeOutput(BaseModel):
    sentiment: SentimentResult
    skills_found: list[str]
    performance_score: ScoreResult
    recommendations: str


class BatchAnalyzeInput(BaseModel):
    reviews: list[AnalyzeInput]
