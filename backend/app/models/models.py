from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class ProjectStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    paused = "paused"


class TaskStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    delayed = "delayed"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    group_id = Column(String(100), unique=True, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("DailyReport", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    module = Column(String(100))
    name = Column(String(200), nullable=False)
    assignee = Column(String(100))
    plan_start = Column(DateTime)
    plan_end = Column(DateTime)
    status = Column(Enum(TaskStatus), default=TaskStatus.not_started)
    progress = Column(Float, default=0.0)
    latest_update = Column(Text)
    risk_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    progress_logs = relationship("ProgressLog", back_populates="task", cascade="all, delete-orphan")


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(100))
    user_name = Column(String(100))
    content = Column(Text, nullable=False)
    submit_time = Column(DateTime, default=datetime.utcnow)
    message_id = Column(String(200))
    is_external = Column(Boolean, default=False)
    ai_parsed = Column(Boolean, default=False)
    parsed_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="reports")


class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    change_type = Column(String(50))  # progress_update / status_change / risk_flag
    old_value = Column(String(500))
    new_value = Column(String(500))
    trigger_by = Column(String(100))
    trigger_source = Column(String(50))  # report / meeting / manual
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="progress_logs")


class ReminderConfig(Base):
    __tablename__ = "reminder_configs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    enabled = Column(Boolean, default=True)
    days_before = Column(String(50), default="3,1")  # comma-separated
    reminder_time = Column(String(10), default="09:00")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
