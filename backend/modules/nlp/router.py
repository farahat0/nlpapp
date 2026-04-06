from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import verify_token
from backend.modules.nlp.schemas import AnalyzeInput, AnalyzeOutput, BatchAnalyzeInput
from backend.modules.nlp.service import full_analysis
from backend.modules.reviews.service import save_analysis

router = APIRouter(prefix="/api/v1/nlp", tags=["NLP Analysis"])


@router.post("/analyze", response_model=AnalyzeOutput)
async def analyze_review(
    input_data: AnalyzeInput,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Run full NLP analysis on a single HR review.
    Saves the result to the database and returns the analysis.
    """
    # Save to database (also runs analysis internally)
    save_analysis(
        input_data.employee_name,
        input_data.department,
        input_data.review_text,
        input_data.behavioral_rating,
        input_data.performance_rating,
        db,
        reviewer_username=username,
    )

    # Return the raw analysis result
    result = full_analysis(
        input_data.review_text,
        input_data.behavioral_rating,
        input_data.performance_rating,
    )
    return result


@router.post("/batch-analyze", response_model=list[AnalyzeOutput])
async def batch_analyze_reviews(
    input_data: BatchAnalyzeInput,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Run NLP analysis on multiple HR reviews at once.
    Saves each result to the database.
    """
    results = []
    for review in input_data.reviews:
        save_analysis(
            review.employee_name,
            review.department,
            review.review_text,
            review.behavioral_rating,
            review.performance_rating,
            db,
            reviewer_username=username,
        )
        result = full_analysis(
            review.review_text,
            review.behavioral_rating,
            review.performance_rating,
        )
        results.append(result)
    return results
