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


def extract_skill_gaps(text: str) -> list[str]:
    """Mock skill gap extraction."""
    return ["public speaking", "time management"]


def generate_recommendations(
    sentiment: str, skills: list[str], score: str
) -> str:
    """Mock recommendation generation."""
    return (
        "1. Continue developing leadership skills through mentorship programs. "
        "2. Consider advanced communication workshops to further strengthen team collaboration. "
        "3. Set specific measurable goals for the next review period to maintain high performance."
    )


def full_analysis(text: str, behavioral_rating: int, performance_rating: int) -> dict:
    """
    Run all NLP tasks on the given review text.
    Returns a dict with sentiment, skills_found, skill_gaps, behavioral_rating,
    performance_rating, and recommendations.
    """
    sentiment = analyze_sentiment(text)
    skills = extract_skills(text)
    gaps = extract_skill_gaps(text)
    recommendations = generate_recommendations(
        sentiment["label"], skills, "N/A"
    )
    return {
        "sentiment": sentiment,
        "skills_found": skills,
        "skill_gaps": gaps,
        "behavioral_rating": behavioral_rating,
        "performance_rating": performance_rating,
        "recommendations": recommendations,
    }
