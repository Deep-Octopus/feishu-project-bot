import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import DailyReport, Task, TaskStatus

logger = logging.getLogger(__name__)


async def generate_weekly_report(db: AsyncSession, project_id: int, user_name: str = None) -> dict:
    """Generate weekly report by aggregating daily reports."""
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    query = select(DailyReport).where(
        DailyReport.project_id == project_id,
        DailyReport.submit_time >= week_start,
    )
    if user_name:
        query = query.where(DailyReport.user_name.ilike(f"%{user_name}%"))

    result = await db.execute(query)
    reports = result.scalars().all()

    # Aggregate members
    members = list({r.user_name for r in reports})

    # Count completed tasks this week
    completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.status == TaskStatus.completed,
            Task.updated_at >= week_start,
        )
    )
    completed_count = completed_result.scalar() or 0

    # Collect issues from parsed data
    import json
    issues = []
    for r in reports:
        if r.parsed_data:
            try:
                data = json.loads(r.parsed_data)
                issues.extend(data.get("issues", []))
            except Exception:
                pass

    return {
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": now.strftime("%Y-%m-%d"),
        "report_count": len(reports),
        "member_count": len(members),
        "members": members,
        "completed_tasks": completed_count,
        "issues": issues[:10],  # top 10
        "reports": [
            {"user_name": r.user_name, "submit_time": r.submit_time.isoformat(), "content": r.content[:200]}
            for r in reports
        ],
    }
