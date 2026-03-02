from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import verify_token
from backend.modules.analytics.schemas import DepartmentStats, OverviewStats, EmployeeStats
from backend.modules.analytics.service import get_overview_stats, get_department_stats, get_employee_stats

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewStats)
async def overview(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get overall system analytics."""
    return get_overview_stats(db)


@router.get("/department/{department}", response_model=DepartmentStats)
async def department_analytics(
    department: str,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get analytics for a specific department."""
    return get_department_stats(department, db)


@router.get("/employee/{name}", response_model=EmployeeStats)
async def employee_analytics(
    name: str,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get analytics for a specific employee."""
    return get_employee_stats(name, db)
