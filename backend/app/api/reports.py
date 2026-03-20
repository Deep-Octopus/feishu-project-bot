from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..core.database import get_db
from ..services.report_service import get_reports

router = APIRouter()


@router.get("/")
async def list_reports(
    project_id: int,
    user_name: Optional[str] = None,
    date_str: Optional[str] = Query(None, alias="date"),
    days: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await get_reports(db, project_id, user_name, date_str, days, page, page_size)
