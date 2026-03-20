import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .core.database import engine, Base
from .core.redis_client import close_redis
from .api import feishu, projects, tasks, reports, statistics, config as config_router

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    # Start scheduler
    from .services.reminder_service import start_scheduler
    start_scheduler()

    yield

    # Shutdown
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="飞书项目进度管理机器人",
    description="通过飞书群聊自动收集、记录和更新项目进度",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feishu.router, prefix="/api/v1/feishu", tags=["飞书回调"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目管理"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务管理"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["日报管理"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["统计分析"])
app.include_router(config_router.router, prefix="/api/v1/config", tags=["系统配置"])


@app.get("/health")
async def health():
    return {"status": "ok"}
