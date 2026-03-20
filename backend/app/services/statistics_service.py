import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import DailyReport, Task, TaskStatus

logger = logging.getLogger(__name__)


async def get_statistics(db: AsyncSession, project_id: int, period: str = "week") -> dict:
    """Generate project statistics."""
    now = datetime.utcnow()
    if period == "month":
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=7)

    # Member activity (report count per member)
    activity_result = await db.execute(
        select(DailyReport.user_name, func.count(DailyReport.id).label("count"))
        .where(DailyReport.project_id == project_id, DailyReport.submit_time >= since)
        .group_by(DailyReport.user_name)
        .order_by(func.count(DailyReport.id).desc())
    )
    member_activity = [{"user_name": row[0], "report_count": row[1]} for row in activity_result]

    # Task completion rate
    total_result = await db.execute(
        select(func.count(Task.id)).where(Task.project_id == project_id)
    )
    total_tasks = total_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id, Task.status == TaskStatus.completed
        )
    )
    completed_tasks = completed_result.scalar() or 0

    # Module progress
    module_result = await db.execute(
        select(Task.module, func.avg(Task.progress).label("avg_progress"))
        .where(Task.project_id == project_id)
        .group_by(Task.module)
    )
    module_progress = [
        {"module": row[0] or "未分类", "avg_progress": round(row[1], 1)}
        for row in module_result
    ]

    return {
        "period": period,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks else 0,
        "member_activity": member_activity,
        "module_progress": module_progress,
    }
