"""
API服务层
"""
from .base import PlatformService, PlatformType, ContentItem
from .bilibili_service import BilibiliService
from .douyin_service import DouyinService
from .xiaohongshu_service import XiaohongshuService
from .factory import ServiceFactory, get_bilibili_service, get_douyin_service, get_xiaohongshu_service

# 导出工具模块
from .utils import (
    exponential_backoff_retry,
    rate_limit,
    TokenBucket,
    SlidingWindowLimiter,
    CookieValidator,
    DouyinCookieValidator,
    BilibiliCookieValidator,
    XiaohongshuCookieValidator,
)

__all__ = [
    # 基类和类型
    'PlatformService',
    'PlatformType',
    'ContentItem',

    # 平台服务
    'BilibiliService',
    'DouyinService',
    'XiaohongshuService',

    # 服务工厂
    'ServiceFactory',
    'get_bilibili_service',
    'get_douyin_service',
    'get_xiaohongshu_service',

    # 工具 - 重试和限流
    'exponential_backoff_retry',
    'rate_limit',
    'TokenBucket',
    'SlidingWindowLimiter',

    # 工具 - Cookie管理
    'CookieValidator',
    'DouyinCookieValidator',
    'BilibiliCookieValidator',
    'XiaohongshuCookieValidator',
]
