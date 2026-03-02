"""
NLP Service — MOCK VERSION

This file is the ONLY file that touches the NLP models.
Right now it returns hardcoded mock data for development.
When fine-tuned models are ready, replace the function bodies below —
nothing else in the project needs to change.
"""


def analyze_sentiment(text: str) -> dict:
    """Mock sentiment analysis."""
    return {"label": "Positive", "confidence": 0.91}


def extract_skills(text: str) -> list[str]:
    """Mock skill/competency extraction."""
    return ["leadership", "communication", "teamwork"]


def score_performance(text: str) -> dict:
    """Mock performance scoring."""
    return {"score": "4/5", "confidence": 0.88}


def generate_recommendations(
    sentiment: str, skills: list[str], score: str
) -> str:
    """Mock recommendation generation."""
    return (
        "1. Continue developing leadership skills through mentorship programs. "
        "2. Consider advanced communication workshops to further strengthen team collaboration. "
        "3. Set specific measurable goals for the next review period to maintain high performance."
    )


def full_analysis(text: str) -> dict:
    """
    Run all four NLP tasks on the given review text.
    Returns a dict with sentiment, skills_found, performance_score, recommendations.
    """
    sentiment = analyze_sentiment(text)
    skills = extract_skills(text)
    score = score_performance(text)
    recommendations = generate_recommendations(
        sentiment["label"], skills, score["score"]
    )
    return {
        "sentiment": sentiment,
        "skills_found": skills,
        "performance_score": score,
        "recommendations": recommendations,
    }
