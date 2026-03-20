from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..core.database import get_db
from ..models import Task, TaskStatus

router = APIRouter()


class TaskCreate(BaseModel):
    project_id: int
    module: Optional[str] = None
    name: str
    assignee: Optional[str] = None
    plan_start: Optional[datetime] = None
    plan_end: Optional[datetime] = None


class TaskUpdate(BaseModel):
    module: Optional[str] = None
    name: Optional[str] = None
    assignee: Optional[str] = None
    plan_start: Optional[datetime] = None
    plan_end: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    progress: Optional[float] = None
    latest_update: Optional[str] = None
    risk_flag: Optional[bool] = None


@router.get("/")
async def list_tasks(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.project_id == project_id))
    tasks = result.scalars().all()
    return [
        {
            "id": t.id, "module": t.module, "name": t.name, "assignee": t.assignee,
            "plan_start": t.plan_start, "plan_end": t.plan_end,
            "status": t.status, "progress": t.progress,
            "latest_update": t.latest_update, "risk_flag": t.risk_flag,
        }
        for t in tasks
    ]


@router.post("/", status_code=201)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(**data.model_dump(exclude_none=True))
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "name": task.name}


@router.put("/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")

    old_progress = task.progress
    old_status = task.status
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(task, k, v)

    # Log manual change
    if task.progress != old_progress or task.status != old_status:
        from ..models import ProgressLog
        log = ProgressLog(
            task_id=task.id,
            change_type="progress_update",
            old_value=f"status={old_status},progress={old_progress}",
            new_value=f"status={task.status},progress={task.progress}",
            trigger_by="admin",
            trigger_source="manual",
        )
        db.add(log)

    await db.commit()
    return {"ok": True}


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    await db.delete(task)
    await db.commit()
    return {"ok": True}
