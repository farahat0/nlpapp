from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
from backend.modules.reviews.model import ReviewRecord


def _compute_skill_counts(reviews, field="skills_found", top_n=5):
    """Extract top N skills/gaps from comma-separated field across reviews."""
    all_items = []
    for r in reviews:
        value = getattr(r, field, None)
        if value:
            all_items.extend([s.strip() for s in value.split(",") if s.strip()])
    counts = Counter(all_items).most_common(top_n)
    return [{"skill": skill, "count": count} for skill, count in counts]


def get_overview_stats(db: Session) -> dict:
    """Get overall system statistics."""
    reviews = db.query(ReviewRecord).all()
    total_reviews = len(reviews)

    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_behavioral_rating": 0.0,
            "average_performance_rating": 0.0,
            "sentiment_distribution": {"Positive": 0, "Negative": 0, "Neutral": 0},
            "top_skills": [],
            "top_gaps": [],
        }

    avg_behavioral = sum(r.behavioral_rating or 0 for r in reviews) / total_reviews
    avg_performance = sum(r.performance_rating or 0 for r in reviews) / total_reviews

    sentiment_counts = Counter(r.sentiment for r in reviews if r.sentiment)
    # Ensure all three keys exist
    distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    distribution.update(dict(sentiment_counts))

    return {
        "total_reviews": total_reviews,
        "average_behavioral_rating": round(avg_behavioral, 2),
        "average_performance_rating": round(avg_performance, 2),
        "sentiment_distribution": distribution,
        "top_skills": _compute_skill_counts(reviews, "skills_found"),
        "top_gaps": _compute_skill_counts(reviews, "skill_gaps"),
    }


def get_employee_trend(employee_name: str, db: Session) -> list[dict]:
    """Get review trend for an employee, ordered by date ascending."""
    reviews = (
        db.query(ReviewRecord)
        .filter(ReviewRecord.employee_name == employee_name)
        .order_by(ReviewRecord.created_at.asc())
        .all()
    )
    return [
        {
            "date": r.created_at.isoformat() if r.created_at else "",
            "behavioral_rating": r.behavioral_rating or 0,
            "performance_rating": r.performance_rating or 0,
            "sentiment": r.sentiment or "N/A",
        }
        for r in reviews
    ]


def get_department_stats(department: str, db: Session) -> dict:
    """Get stats for a specific department."""
    reviews = (
        db.query(ReviewRecord)
        .filter(ReviewRecord.department == department)
        .all()
    )

    if not reviews:
        return {
            "department": department,
            "total_reviews": 0,
            "average_behavioral_rating": 0.0,
            "average_performance_rating": 0.0,
            "sentiment_distribution": {"Positive": 0, "Negative": 0, "Neutral": 0},
            "top_skills": [],
            "top_gaps": [],
        }

    total = len(reviews)
    avg_behavioral = sum(r.behavioral_rating or 0 for r in reviews) / total
    avg_performance = sum(r.performance_rating or 0 for r in reviews) / total

    sentiment_counts = Counter(r.sentiment for r in reviews if r.sentiment)
    distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    distribution.update(dict(sentiment_counts))

    return {
        "department": department,
        "total_reviews": total,
        "average_behavioral_rating": round(avg_behavioral, 2),
        "average_performance_rating": round(avg_performance, 2),
        "sentiment_distribution": distribution,
        "top_skills": _compute_skill_counts(reviews, "skills_found"),
        "top_gaps": _compute_skill_counts(reviews, "skill_gaps"),
    }


def get_employee_stats(employee_name: str, db: Session) -> dict:
    """Get stats for a specific employee."""
    reviews = (
        db.query(ReviewRecord)
        .filter(ReviewRecord.employee_name == employee_name)
        .all()
    )

    if not reviews:
        return {
            "employee_name": employee_name,
            "total_reviews": 0,
            "sentiments": [],
            "all_skills": [],
            "scores": [],
        }

    sentiments = [r.sentiment for r in reviews if r.sentiment]
    scores = [r.performance_rating for r in reviews if r.performance_rating]

    all_skills = []
    for r in reviews:
        if r.skills_found:
            all_skills.extend([s.strip() for s in r.skills_found.split(",")])
    unique_skills = list(set(all_skills))

    return {
        "employee_name": employee_name,
        "total_reviews": len(reviews),
        "sentiments": sentiments,
        "all_skills": unique_skills,
        "scores": scores,
    }
