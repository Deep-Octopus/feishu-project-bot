import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..models import Task, DailyReport, Project, ReminderConfig, TaskStatus
from .feishu_service import send_card
from ..utils.card_builder import build_reminder_card, build_risk_card
from ..core.database import AsyncSessionLocal
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def check_task_reminders():
    """Check tasks approaching deadline and send reminders."""
    if not settings.enable_auto_reminder:
        return
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Task, Project)
            .join(Project, Task.project_id == Project.id)
            .where(Task.status != TaskStatus.completed)
            .where(Task.plan_end.isnot(None))
        )
        rows = result.all()
        now = datetime.utcnow()

        for task, project in rows:
            if not project.group_id:
                continue
            days_left = (task.plan_end - now).days
            if days_left in [3, 1]:
                card = build_reminder_card(task, project, days_left)
                await send_card(project.group_id, card)
            elif days_left < 0:
                card = build_reminder_card(task, project, days_left, overdue=True)
                await send_card(project.group_id, card)


async def check_risk_warnings():
    """Check for projects with no recent reports and send warnings."""
    if not settings.enable_risk_warning:
        return
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Project).where(Project.status == "active"))
        projects = result.scalars().all()

        for project in projects:
            if not project.group_id:
                continue
            # Check if no report in last 3 days
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            count_result = await db.execute(
                select(func.count(DailyReport.id))
                .where(DailyReport.project_id == project.id)
                .where(DailyReport.submit_time >= three_days_ago)
            )
            count = count_result.scalar()
            if count == 0:
                card = build_risk_card(project, "连续3天无日报提交，请及时跟进项目进展")
                await send_card(project.group_id, card)

            # Check tasks with risk flags
            risk_result = await db.execute(
                select(Task)
                .where(Task.project_id == project.id)
                .where(Task.risk_flag == True)
                .where(Task.status != TaskStatus.completed)
            )
            risk_tasks = risk_result.scalars().all()
            for task in risk_tasks:
                card = build_risk_card(project, f"任务「{task.name}」存在风险，负责人：{task.assignee or '未指定'}")
                await send_card(project.group_id, card)


def start_scheduler():
    scheduler.add_job(check_task_reminders, "cron", hour=9, minute=0, id="task_reminders")
    scheduler.add_job(check_risk_warnings, "cron", hour=10, minute=0, id="risk_warnings")
    if not scheduler.running:
        scheduler.start()
    logger.info("Scheduler started")
