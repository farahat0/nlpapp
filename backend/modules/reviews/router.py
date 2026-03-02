from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import verify_token
from backend.modules.reviews.schemas import ReviewOutput
from backend.modules.reviews.service import get_all_reviews, get_employee_reviews, delete_review

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


@router.get("/", response_model=list[ReviewOutput])
async def list_reviews(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get all review records, most recent first."""
    reviews = get_all_reviews(db)
    # Convert comma-separated skills_found string to list for each review
    for review in reviews:
        if review.skills_found:
            review.skills_found = [s.strip() for s in review.skills_found.split(",")]
        else:
            review.skills_found = []
    return reviews


@router.get("/{employee_name}", response_model=list[ReviewOutput])
async def list_employee_reviews(
    employee_name: str,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get all reviews for a specific employee."""
    reviews = get_employee_reviews(employee_name, db)
    for review in reviews:
        if review.skills_found:
            review.skills_found = [s.strip() for s in review.skills_found.split(",")]
        else:
            review.skills_found = []
    return reviews


@router.delete("/{review_id}")
async def remove_review(
    review_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Delete a review by ID."""
    delete_review(review_id, db)
    return {"message": f"Review {review_id} deleted successfully"}
