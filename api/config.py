"""
API配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Dict, Any
import os


class Settings(BaseSettings):
    """应用配置"""
    # 应用信息
    APP_NAME: str = "Multi-Platform Video Search API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # B站配置
    BILIBILI_SESSDATA: str = ""

    # 抖音配置
    DOUYIN_COOKIES: str = ""
    DOUYIN_TTWID: str = ""
    DOUYIN_HEADLESS: bool = True  # 无头模式，设为False可手动处理验证码

    # 小红书配置
    XIAOHONGSHU_COOKIES: str = ""
    XIAOHONGSHU_HEADLESS: bool = True  # 无头模式，设为False可手动处理验证码

    # ============ MediaCrawler 配置 ============
    # MediaCrawler 桥接脚本路径（默认自动检测 tools/mediacrawler_bridge.py）
    MEDIACRAWLER_BRIDGE_PATH: str = ""
    # 搜索超时时间（秒），浏览器启动较慢建议设大一些
    MEDIACRAWLER_TIMEOUT: int = 150
    # 浏览器无头模式（False=显示窗口，用于首次扫码登录）
    MEDIACRAWLER_HEADLESS: bool = True

    # API配置
    API_PREFIX: str = "/api/v1"

    # CORS配置
    CORS_ORIGINS: str = "*"

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
            'douyin': {
                'cookies': self.DOUYIN_COOKIES,
                'ttwid': self.DOUYIN_TTWID,
                'headless': self.MEDIACRAWLER_HEADLESS,
                'timeout': self.MEDIACRAWLER_TIMEOUT,
            },
            'xiaohongshu': {
                'cookies': self.XIAOHONGSHU_COOKIES,
                'headless': self.MEDIACRAWLER_HEADLESS,
                'timeout': self.MEDIACRAWLER_TIMEOUT,
            },
            # MediaCrawler 公共配置
            '_mediacrawler': {
                'timeout': self.MEDIACRAWLER_TIMEOUT,
                'bridge_path': self.MEDIACRAWLER_BRIDGE_PATH,
                'headless': self.MEDIACRAWLER_HEADLESS,
            },
        }
        return configs.get(platform.lower(), {})

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
