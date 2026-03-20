import os
import yaml
from functools import lru_cache
from pydantic_settings import BaseSettings


def load_yaml_config():
    config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_yaml = load_yaml_config()


class Settings(BaseSettings):
    # Feishu
    feishu_app_id: str = _yaml.get("feishu", {}).get("app_id", "")
    feishu_app_secret: str = _yaml.get("feishu", {}).get("app_secret", "")
    feishu_verification_token: str = _yaml.get("feishu", {}).get("verification_token", "")
    feishu_encrypt_key: str = _yaml.get("feishu", {}).get("encrypt_key", "")

    # SiliconFlow
    siliconflow_api_key: str = _yaml.get("siliconflow", {}).get("api_key", "")
    siliconflow_base_url: str = _yaml.get("siliconflow", {}).get("base_url", "https://api.siliconflow.cn/v1")
    siliconflow_model: str = _yaml.get("siliconflow", {}).get("model", "Qwen/Qwen2.5-7B-Instruct")
    siliconflow_temperature: float = _yaml.get("siliconflow", {}).get("temperature", 0.7)
    siliconflow_max_tokens: int = _yaml.get("siliconflow", {}).get("max_tokens", 2000)

    # Database
    db_host: str = _yaml.get("database", {}).get("host", "localhost")
    db_port: int = _yaml.get("database", {}).get("port", 5432)
    db_name: str = _yaml.get("database", {}).get("name", "feishu_bot")
    db_user: str = _yaml.get("database", {}).get("user", "postgres")
    db_password: str = _yaml.get("database", {}).get("password", "")

    # Redis
    redis_host: str = _yaml.get("redis", {}).get("host", "localhost")
    redis_port: int = _yaml.get("redis", {}).get("port", 6379)
    redis_db: int = _yaml.get("redis", {}).get("db", 0)
    redis_password: str = _yaml.get("redis", {}).get("password", "")

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # Features
    enable_ai_parsing: bool = True
    enable_auto_reminder: bool = True
    enable_risk_warning: bool = True

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
