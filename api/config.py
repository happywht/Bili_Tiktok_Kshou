"""
API配置管理
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""
    # 应用信息
    APP_NAME: str = "Bilibili Search API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # B站配置
    BILIBILI_SESSDATA: str = ""

    # API配置
    API_PREFIX: str = "/api/v1"

    # CORS配置
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 尝试加载环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    settings = Settings(_env_file=env_path)
else:
    settings = Settings()
