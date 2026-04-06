from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from backend.core.database import get_db
from backend.core.security import verify_token
from backend.modules.reviews.schemas import ReviewOutput, EmployeeCreate, EmployeeOut
from backend.modules.reviews.service import (
    get_all_reviews,
    get_employee_reviews,
    create_employee,
    get_all_employees,
)

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


def _convert_skills(reviews):
    """Convert comma-separated skills_found and skill_gaps strings to lists."""
    for review in reviews:
        if review.skills_found:
            review.skills_found = [s.strip() for s in review.skills_found.split(",")]
        else:
            review.skills_found = []
        if review.skill_gaps:
            review.skill_gaps = [s.strip() for s in review.skill_gaps.split(",")]
        else:
            review.skill_gaps = []
    return reviews


@router.post("/employees", response_model=EmployeeOut)
async def add_employee(
    data: EmployeeCreate,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Create a new employee."""
    return create_employee(data, db)


@router.get("/employees", response_model=list[EmployeeOut])
async def list_employees(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get all employees."""
    return get_all_employees(db)


@router.get("/", response_model=list[ReviewOutput])
async def list_reviews(
    employee_name: Optional[str] = None,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get all review records, most recent first. Optionally filter by employee_name."""
    reviews = get_all_reviews(db, employee_name=employee_name)
    return _convert_skills(reviews)


@router.get("/{employee_name}", response_model=list[ReviewOutput])
async def list_employee_reviews(
    employee_name: str,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get all reviews for a specific employee."""
    reviews = get_employee_reviews(employee_name, db)
    return _convert_skills(reviews)
