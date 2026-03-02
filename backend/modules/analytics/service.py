from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
from backend.modules.reviews.model import ReviewRecord


def get_overview_stats(db: Session) -> dict:
    """Get overall system statistics."""
    total_reviews = db.query(ReviewRecord).count()
    total_employees = db.query(func.count(func.distinct(ReviewRecord.employee_name))).scalar()
    total_departments = db.query(func.count(func.distinct(ReviewRecord.department))).scalar()

    # Sentiment distribution
    sentiments = db.query(ReviewRecord.sentiment).all()
    sentiment_counts = Counter(s[0] for s in sentiments if s[0])

    # Average score confidence
    avg_confidence = db.query(func.avg(ReviewRecord.score_confidence)).scalar() or 0.0

    return {
        "total_reviews": total_reviews,
        "total_employees": total_employees,
        "total_departments": total_departments,
        "sentiment_distribution": dict(sentiment_counts),
        "average_score_confidence": round(avg_confidence, 2),
    }


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
            "average_sentiment_confidence": 0.0,
            "most_common_sentiment": "N/A",
            "average_score_confidence": 0.0,
            "top_skills": [],
        }

    total = len(reviews)
    avg_sentiment_conf = sum(r.sentiment_confidence or 0 for r in reviews) / total
    avg_score_conf = sum(r.score_confidence or 0 for r in reviews) / total

    sentiment_counts = Counter(r.sentiment for r in reviews if r.sentiment)
    most_common = sentiment_counts.most_common(1)[0][0] if sentiment_counts else "N/A"

    # Aggregate skills
    all_skills = []
    for r in reviews:
        if r.skills_found:
            all_skills.extend([s.strip() for s in r.skills_found.split(",")])
    top_skills = [skill for skill, _ in Counter(all_skills).most_common(5)]

    return {
        "department": department,
        "total_reviews": total,
        "average_sentiment_confidence": round(avg_sentiment_conf, 2),
        "most_common_sentiment": most_common,
        "average_score_confidence": round(avg_score_conf, 2),
        "top_skills": top_skills,
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
    scores = [r.performance_score for r in reviews if r.performance_score]

    all_skills = []
    for r in reviews:
        if r.skills_found:
            all_skills.extend([s.strip() for s in r.skills_found.split(",")])
    # Deduplicate skills
    unique_skills = list(set(all_skills))

    return {
        "employee_name": employee_name,
        "total_reviews": len(reviews),
        "sentiments": sentiments,
        "all_skills": unique_skills,
        "scores": scores,
    }
