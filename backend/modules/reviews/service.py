from sqlalchemy.orm import Session
from backend.modules.reviews.model import ReviewRecord
from backend.modules.nlp.service import full_analysis


def save_analysis(employee_name: str, department: str, review_text: str, db: Session) -> ReviewRecord:
    """Run NLP analysis on review text and save results to database."""
    results = full_analysis(review_text)

    record = ReviewRecord(
        employee_name=employee_name,
        department=department,
        review_text=review_text,
        sentiment=results["sentiment"]["label"],
        sentiment_confidence=results["sentiment"]["confidence"],
        skills_found=", ".join(results["skills_found"]),
        performance_score=results["performance_score"]["score"],
        score_confidence=results["performance_score"]["confidence"],
        recommendations=results["recommendations"],
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_reviews(db: Session) -> list[ReviewRecord]:
    """Get all reviews ordered by most recent first."""
    return db.query(ReviewRecord).order_by(ReviewRecord.created_at.desc()).all()


def get_employee_reviews(employee_name: str, db: Session) -> list[ReviewRecord]:
    """Get all reviews for a specific employee."""
    return (
        db.query(ReviewRecord)
        .filter(ReviewRecord.employee_name == employee_name)
        .order_by(ReviewRecord.created_at.desc())
        .all()
    )


def get_department_reviews(department: str, db: Session) -> list[ReviewRecord]:
    """Get all reviews for a specific department."""
    return (
        db.query(ReviewRecord)
        .filter(ReviewRecord.department == department)
        .order_by(ReviewRecord.created_at.desc())
        .all()
    )


def delete_review(review_id: int, db: Session) -> bool:
    """Delete a review by ID. Returns True if deleted, raises 404 if not found."""
    from fastapi import HTTPException, status

    record = db.query(ReviewRecord).filter(ReviewRecord.id == review_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id {review_id} not found",
        )
    db.delete(record)
    db.commit()
    return True
