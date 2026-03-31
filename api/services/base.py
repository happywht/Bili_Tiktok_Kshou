"""
平台服务基类 - 定义统一接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# 配置日志
logger = logging.getLogger(__name__)


class PlatformType(str, Enum):
    """支持的平台类型"""
    BILIBILI = "bilibili"


@dataclass
class ContentItem:
    """通用内容项基类"""
    id: str
    title: str
    author: str
    cover_url: str
    url: str
    platform: PlatformType
    # 统计数据
    play_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    collect_count: int = 0
    # 元数据
    description: str = ""
    tags: List[str] = None
    publish_time: str = ""
    duration: str = ""  # 视频时长
    content_type: str = "video"  # video, note, article

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "cover_url": self.cover_url,
            "url": self.url,
            "platform": self.platform.value,
            "play_count": self.play_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "collect_count": self.collect_count,
            "description": self.description,
            "tags": self.tags,
            "publish_time": self.publish_time,
            "duration": self.duration,
            "content_type": self.content_type,
        }


class PlatformService(ABC):
    """平台服务抽象基类"""

    platform: PlatformType = None

    @abstractmethod
    def search(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        **kwargs
    ) -> List[ContentItem]:
        """
        搜索内容

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            **kwargs: 平台特定参数

        Returns:
            内容列表
        """
        pass

    @abstractmethod
    def get_detail(self, content_id: str) -> Dict[str, Any]:
        """
        获取内容详情

        Args:
            content_id: 内容ID

        Returns:
            详情数据
        """
        pass

    def get_proxy_image_url(self, original_url: str) -> str:
        """
        获取代理后的图片URL

        Args:
            original_url: 原始图片URL

        Returns:
            代理后的URL
        """
        if not original_url:
            return ""
        # 使用后端代理
        return f"/api/v1/proxy-image?url={original_url}"

    @staticmethod
    def parse_count(value: Any) -> int:
        """
        解析数字（支持万、亿等单位）

        Args:
            value: 原始值

        Returns:
            整数
        """
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            value = value.strip().lower()
            if not value or value == '-':
                return 0
            try:
                # 处理单位
                if '亿' in value:
                    return int(float(value.replace('亿', '')) * 100_000_000)
                if '万' in value:
                    return int(float(value.replace('万', '')) * 10_000)
                if 'w' in value:
                    return int(float(value.replace('w', '')) * 10_000)
                if 'k' in value:
                    return int(float(value.replace('k', '')) * 1_000)
                return int(float(value))
            except (ValueError, TypeError):
                return 0
        return 0

    @staticmethod
    def parse_duration(duration_str: str) -> int:
        """
        解析时长字符串为秒数

        Args:
            duration_str: 时长字符串 (如 "10:30", "1:20:30")

        Returns:
            秒数
        """
        if not duration_str:
            return 0
        try:
            parts = duration_str.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return int(duration_str)
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        将秒数格式化为时长字符串

        Args:
            seconds: 秒数

        Returns:
            时长字符串 (如 "10:30", "1:20:30")
        """
        if not seconds or seconds < 0:
            return "00:00"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def log_request(self, action: str, **kwargs):
        """
        记录请求日志

        Args:
            action: 操作名称
            **kwargs: 请求参数
        """
        params = ', '.join(f'{k}={v}' for k, v in kwargs.items())
        logger.info(f"[{self.platform.value}] {action} - {params}")

    def log_error(self, action: str, error: Exception):
        """
        记录错误日志

        Args:
            action: 操作名称
            error: 异常对象
        """
        logger.error(f"[{self.platform.value}] {action} 失败: {error}", exc_info=True)

    @staticmethod
    def safe_get(data: dict, *keys, default=None):
        """
        安全地从嵌套字典中获取值

        Args:
            data: 字典数据
            *keys: 键路径
            default: 默认值

        Returns:
            获取的值或默认值

        Example:
            value = safe_get(data, 'user', 'profile', 'name', default='Unknown')
        """
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return default
            if data is None:
                return default
        return data
