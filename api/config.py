"""
API配置管理
"""
from pydantic_settings import BaseSettings
from pydantic import Extra
from typing import List, Dict, Any
import os
import sys

# 修复 Windows 中文路径编码问题
if sys.platform == 'win32':
    # 设置标准输出编码为 UTF-8
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class Settings(BaseSettings):
    """应用配置"""
    # 应用信息
    APP_NAME: str = "Bilibili Video Search API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # B站配置
    BILIBILI_SESSDATA: str = ""

    # ============ AI 总结配置 ============
    LLM_API_KEY: str = ""  # DeepSeek / OpenAI 兼容 API Key
    LLM_API_BASE: str = "https://api.deepseek.com/v1"  # API Base URL
    LLM_MODEL: str = "deepseek-chat"  # 模型名称

    # API配置
    API_PREFIX: str = "/api/v1"

    # CORS配置
    CORS_ORIGINS: str = "*"

    # 配置类
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # 忽略额外的环境变量（兼容旧.env文件）
        extra = Extra.ignore

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        获取平台特定配置

        Args:
            platform: 平台标识

        Returns:
            平台配置字典
        """
        configs = {
            'bilibili': {
                'sessdata': self.BILIBILI_SESSDATA,
            },
        }
        return configs.get(platform.lower(), {})


# 尝试加载环境变量
try:
    # 使用 pathlib 处理路径编码问题
    from pathlib import Path
    api_dir = Path(__file__).resolve().parent
    project_root = api_dir.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        settings = Settings(_env_file=str(env_path))
    else:
        settings = Settings()
except Exception as e:
    # 如果加载失败，使用默认配置
    print(f"Warning: Failed to load .env file: {e}")
    print("Using default configuration.")
    settings = Settings()
