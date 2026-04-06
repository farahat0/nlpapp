from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.modules.reviews.model import ReviewRecord, Employee
from backend.modules.nlp.service import full_analysis


def create_employee(data, db: Session) -> Employee:
    """Create a new employee. Raises 400 if name already exists."""
    existing = db.query(Employee).filter(Employee.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with name '{data.name}' already exists",
        )
    employee = Employee(name=data.name, department=data.department)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_all_employees(db: Session) -> list[Employee]:
    """Get all employees ordered by name."""
    return db.query(Employee).order_by(Employee.name).all()


def save_analysis(
    employee_name: str,
    department: str,
    review_text: str,
    behavioral_rating: int,
    performance_rating: int,
    db: Session,
    reviewer_username: str = "",
) -> ReviewRecord:
    """Run NLP analysis on review text and save results to database."""
    results = full_analysis(review_text, behavioral_rating, performance_rating)

    record = ReviewRecord(
        employee_name=employee_name,
        department=department,
        review_text=review_text,
        sentiment=results["sentiment"]["label"],
        sentiment_confidence=results["sentiment"]["confidence"],
        skills_found=", ".join(results["skills_found"]),
        skill_gaps=", ".join(results.get("skill_gaps", [])),
        behavioral_rating=results["behavioral_rating"],
        performance_rating=results["performance_rating"],
        recommendations=results["recommendations"],
        created_by=reviewer_username,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_reviews(db: Session, employee_name: str = None) -> list[ReviewRecord]:
    """Get all reviews ordered by most recent first, optionally filtered by employee."""
    query = db.query(ReviewRecord)
    if employee_name:
        query = query.filter(ReviewRecord.employee_name == employee_name)
    return query.order_by(ReviewRecord.created_at.desc()).all()


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



