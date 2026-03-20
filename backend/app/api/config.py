from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/")
async def get_config():
    return {
        "feishu": {
            "app_id": settings.feishu_app_id,
            "app_secret": "***" if settings.feishu_app_secret else "",
        },
        "siliconflow": {
            "base_url": settings.siliconflow_base_url,
            "model": settings.siliconflow_model,
            "temperature": settings.siliconflow_temperature,
            "max_tokens": settings.siliconflow_max_tokens,
        },
        "features": {
            "enable_ai_parsing": settings.enable_ai_parsing,
            "enable_auto_reminder": settings.enable_auto_reminder,
            "enable_risk_warning": settings.enable_risk_warning,
        },
    }
