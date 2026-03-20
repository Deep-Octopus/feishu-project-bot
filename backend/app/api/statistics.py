from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..core.database import get_db
from ..services.statistics_service import get_statistics
from ..services.progress_service import get_project_progress
from ..services.weekly_report_service import generate_weekly_report

router = APIRouter()


@router.get("/overview")
async def project_overview(project_id: int, db: AsyncSession = Depends(get_db)):
    return await get_project_progress(db, project_id)


@router.get("/stats")
async def project_stats(project_id: int, period: str = "week", db: AsyncSession = Depends(get_db)):
    return await get_statistics(db, project_id, period)


@router.get("/weekly")
async def weekly_report(project_id: int, user_name: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    return await generate_weekly_report(db, project_id, user_name)
