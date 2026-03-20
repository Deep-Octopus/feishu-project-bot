import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import DailyReport, Project
from ..core.config import get_settings
from .ai_service import SiliconFlowService
from .progress_service import update_progress_from_report
from ..utils.card_builder import build_report_confirm_card

settings = get_settings()
logger = logging.getLogger(__name__)
ai_service = SiliconFlowService()


async def submit_daily_report(
    db: AsyncSession,
    project_id: int,
    user_id: str,
    user_name: str,
    content: str,
    message_id: str,
    is_external: bool = False,
) -> dict:
    """Save daily report and trigger AI parsing + progress update."""
    report = DailyReport(
        project_id=project_id,
        user_id=user_id,
        user_name=user_name,
        content=content,
        submit_time=datetime.utcnow(),
        message_id=message_id,
        is_external=is_external,
    )
    db.add(report)
    await db.flush()

    parsed_data = {}
    if settings.enable_ai_parsing:
        try:
            parsed_data = await ai_service.parse_daily_report(content)
            report.ai_parsed = True
            report.parsed_data = json.dumps(parsed_data, ensure_ascii=False)
            await update_progress_from_report(db, project_id, parsed_data, user_name)
        except Exception as e:
            logger.error(f"AI parsing failed for report {report.id}: {e}")

    await db.commit()
    await db.refresh(report)
    return {"report_id": report.id, "parsed_data": parsed_data}


async def get_reports(
    db: AsyncSession,
    project_id: int,
    user_name: str = None,
    date_str: str = None,
    days: int = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = select(DailyReport).where(DailyReport.project_id == project_id)

    if user_name:
        query = query.where(DailyReport.user_name.ilike(f"%{user_name}%"))
    if date_str:
        from datetime import date
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        query = query.where(DailyReport.submit_time >= datetime.combine(d, datetime.min.time()))
        query = query.where(DailyReport.submit_time < datetime.combine(d, datetime.max.time()))
    if days:
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)
        query = query.where(DailyReport.submit_time >= since)

    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    query = query.order_by(DailyReport.submit_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    reports = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "user_name": r.user_name,
                "content": r.content,
                "submit_time": r.submit_time.isoformat(),
                "ai_parsed": r.ai_parsed,
            }
            for r in reports
        ],
    }
