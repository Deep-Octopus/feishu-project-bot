import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Task, ProgressLog, TaskStatus
from .ai_service import SiliconFlowService

logger = logging.getLogger(__name__)
ai_service = SiliconFlowService()

RISK_KEYWORDS = ["问题", "阻塞", "延期", "风险", "困难", "卡住", "blocked", "delay"]


async def update_progress_from_report(
    db: AsyncSession, project_id: int, parsed_data: dict, trigger_by: str
):
    """Update task progress based on AI-parsed report data."""
    result = await db.execute(select(Task).where(Task.project_id == project_id))
    tasks = result.scalars().all()
    if not tasks:
        return

    task_names = [t.name for t in tasks]
    matched = await ai_service.match_tasks(parsed_data, task_names)

    task_map = {t.name: t for t in tasks}
    for match in matched:
        task = task_map.get(match.get("task_name"))
        if not task or match.get("confidence", 0) < 0.6:
            continue

        old_status = task.status
        old_progress = task.progress

        if match.get("status") == "completed":
            task.status = TaskStatus.completed
            task.progress = 100.0
        elif match.get("status") == "in_progress":
            task.status = TaskStatus.in_progress
            if task.progress < 50:
                task.progress = min(task.progress + 20, 90)

        # Check risk keywords
        issues = parsed_data.get("issues", [])
        risk_keywords = parsed_data.get("risk_keywords", [])
        all_text = " ".join(issues + risk_keywords)
        if any(kw in all_text for kw in RISK_KEYWORDS):
            task.risk_flag = True

        # Log the change
        if task.status != old_status or task.progress != old_progress:
            log = ProgressLog(
                task_id=task.id,
                change_type="progress_update",
                old_value=f"status={old_status},progress={old_progress}",
                new_value=f"status={task.status},progress={task.progress}",
                trigger_by=trigger_by,
                trigger_source="report",
            )
            db.add(log)

    await db.flush()


async def get_project_progress(db: AsyncSession, project_id: int, module: str = None) -> dict:
    query = select(Task).where(Task.project_id == project_id)
    if module:
        query = query.where(Task.module.ilike(f"%{module}%"))

    result = await db.execute(query)
    tasks = result.scalars().all()
    if not tasks:
        return {"overall_progress": 0, "tasks": [], "risk_count": 0}

    overall = sum(t.progress for t in tasks) / len(tasks)
    risk_count = sum(1 for t in tasks if t.risk_flag)

    return {
        "overall_progress": round(overall, 1),
        "risk_count": risk_count,
        "tasks": [
            {
                "id": t.id,
                "module": t.module,
                "name": t.name,
                "assignee": t.assignee,
                "status": t.status,
                "progress": t.progress,
                "risk_flag": t.risk_flag,
                "plan_end": t.plan_end.isoformat() if t.plan_end else None,
            }
            for t in tasks
        ],
    }
