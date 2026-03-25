"""
服务工具模块

提供公共的装饰器和工具类，用于各平台服务复用。

模块:
- retry_handler: 重试机制（指数退避）
- rate_limiter: 速率限制
- cookie_manager: Cookie验证和管理

Example:
    from api.services.utils import exponential_backoff_retry, rate_limit
    from api.services.utils import CookieValidator, TokenBucket

    @exponential_backoff_retry(max_retries=3)
    @rate_limit(min_delay=1.0, max_delay=3.0)
    def fetch_data():
        return requests.get('https://api.example.com')
"""

from .retry_handler import (
    exponential_backoff_retry,
    RetryContext,
)

from .rate_limiter import (
    rate_limit,
    TokenBucket,
    SlidingWindowLimiter,
    AdaptiveRateLimiter,
    get_limiter,
)

from .cookie_manager import (
    CookieValidator,
    DouyinCookieValidator,
    BilibiliCookieValidator,
    XiaohongshuCookieValidator,
    CookieManager,
    get_validator,
)

__all__ = [
    # 重试处理器
    'exponential_backoff_retry',
    'RetryContext',

    # 速率限制器
    'rate_limit',
    'TokenBucket',
    'SlidingWindowLimiter',
    'AdaptiveRateLimiter',
    'get_limiter',

    # Cookie管理
    'CookieValidator',
    'DouyinCookieValidator',
    'BilibiliCookieValidator',
    'XiaohongshuCookieValidator',
    'CookieManager',
    'get_validator',
]
