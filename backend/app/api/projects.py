from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..core.database import get_db
from ..models import Project, ProjectStatus

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    group_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    group_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ProjectStatus] = None


@router.get("/")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = result.scalars().all()
    return [
        {
            "id": p.id, "name": p.name, "description": p.description,
            "group_id": p.group_id, "status": p.status,
            "start_date": p.start_date, "end_date": p.end_date,
        }
        for p in projects
    ]


@router.post("/", status_code=201)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(**data.model_dump(exclude_none=True))
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return {"id": project.id, "name": project.name}


@router.get("/{project_id}")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.put("/{project_id}")
async def update_project(project_id: int, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(project, k, v)
    await db.commit()
    return {"ok": True}


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    await db.delete(project)
    await db.commit()
    return {"ok": True}
