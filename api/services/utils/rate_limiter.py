"""
速率限制器 - 请求频率控制

提供多种速率限制策略，防止请求过于频繁导致被封禁。
"""
import time
import random
import threading
from typing import Callable, Optional, Dict
from functools import wraps
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


def rate_limit(
    min_delay: float = 1.0,
    max_delay: float = 3.0,
    jitter: bool = True
):
    """
    简单的请求频率控制装饰器

    通过随机延迟模拟人类行为，避免被反爬虫检测。

    Args:
        min_delay: 最小延迟，单位秒（默认1.0秒）
        max_delay: 最大延迟，单位秒（默认3.0秒）
        jitter: 是否添加随机抖动（默认True）

    Returns:
        装饰后的函数

    Example:
        @rate_limit(min_delay=1.0, max_delay=3.0)
        def fetch_page():
            return requests.get('https://example.com')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if jitter:
                delay = random.uniform(min_delay, max_delay)
            else:
                delay = (min_delay + max_delay) / 2

            logger.debug(f"速率限制: 等待 {delay:.2f} 秒")
            time.sleep(delay)
            return func(*args, **kwargs)

        return wrapper
    return decorator


class TokenBucket:
    """
    令牌桶算法实现

    适用于需要精确控制请求速率的场景。

    Attributes:
        capacity: 桶容量（最大令牌数）
        tokens: 当前令牌数
        refill_rate: 令牌补充速率（令牌/秒）
        last_refill: 上次补充时间

    Example:
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        if bucket.consume(1):
            # 执行请求
            pass
        else:
            # 等待或跳过
            time.sleep(bucket.time_until_available(1))
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶

        Args:
            capacity: 桶容量
            refill_rate: 令牌补充速率（令牌/秒）
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌

        Args:
            tokens: 需要消费的令牌数

        Returns:
            是否成功消费
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def time_until_available(self, tokens: int = 1) -> float:
        """
        计算需要等待的时间

        Args:
            tokens: 需要的令牌数

        Returns:
            等待时间（秒）
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                return 0.0

            needed = tokens - self.tokens
            return needed / self.refill_rate

    def wait_and_consume(self, tokens: int = 1, timeout: float = None) -> bool:
        """
        等待并消费令牌

        Args:
            tokens: 需要消费的令牌数
            timeout: 最大等待时间（None表示无限等待）

        Returns:
            是否成功消费
        """
        start_time = time.time()

        while True:
            if self.consume(tokens):
                return True

            wait_time = self.time_until_available(tokens)

            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + wait_time > timeout:
                    return False

            time.sleep(min(wait_time, 0.1))


class SlidingWindowLimiter:
    """
    滑动窗口限流器

    在指定时间窗口内限制请求次数。

    Example:
        limiter = SlidingWindowLimiter(max_requests=100, window_seconds=60)
        if limiter.is_allowed():
            # 执行请求
            pass
    """

    def __init__(self, max_requests: int, window_seconds: float):
        """
        初始化滑动窗口限流器

        Args:
            max_requests: 窗口内最大请求数
            window_seconds: 窗口时间（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()

    def _clean_old_requests(self):
        """清理过期的请求记录"""
        cutoff = datetime.now() - timedelta(seconds=self.window_seconds)
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

    def is_allowed(self) -> bool:
        """
        检查是否允许请求

        Returns:
            是否允许
        """
        with self.lock:
            self._clean_old_requests()

            if len(self.requests) < self.max_requests:
                self.requests.append(datetime.now())
                return True
            return False

    def get_remaining(self) -> int:
        """
        获取剩余可用请求数

        Returns:
            剩余请求数
        """
        with self.lock:
            self._clean_old_requests()
            return max(0, self.max_requests - len(self.requests))

    def get_reset_time(self) -> float:
        """
        获取窗口重置时间

        Returns:
            重置时间（秒）
        """
        with self.lock:
            self._clean_old_requests()

            if not self.requests:
                return 0.0

            oldest = self.requests[0]
            reset_time = oldest + timedelta(seconds=self.window_seconds)
            remaining = (reset_time - datetime.now()).total_seconds()
            return max(0.0, remaining)


class AdaptiveRateLimiter:
    """
    自适应速率限制器

    根据响应状态动态调整请求速率。

    Example:
        limiter = AdaptiveRateLimiter(
            initial_rate=10,  # 初始10请求/秒
            min_rate=1,
            max_rate=20
        )

        # 正常请求
        limiter.record_success()

        # 遇到429错误
        limiter.record_failure(status_code=429)
    """

    def __init__(
        self,
        initial_rate: float = 10.0,
        min_rate: float = 1.0,
        max_rate: float = 20.0,
        increase_factor: float = 1.1,
        decrease_factor: float = 0.5
    ):
        """
        初始化自适应限流器

        Args:
            initial_rate: 初始速率（请求/秒）
            min_rate: 最小速率
            max_rate: 最大速率
            increase_factor: 成功时的增长因子
            decrease_factor: 失败时的降低因子
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.increase_factor = increase_factor
        self.decrease_factor = decrease_factor
        self.token_bucket = TokenBucket(
            capacity=int(initial_rate * 2),
            refill_rate=initial_rate
        )
        self.lock = threading.Lock()

    def record_success(self):
        """记录成功请求，适当提高速率"""
        with self.lock:
            self.current_rate = min(
                self.max_rate,
                self.current_rate * self.increase_factor
            )
            self._update_bucket()

    def record_failure(self, status_code: int = 429):
        """
        记录失败请求，降低速率

        Args:
            status_code: HTTP状态码
        """
        with self.lock:
            if status_code == 429:
                # 429错误，大幅降低
                self.current_rate = max(
                    self.min_rate,
                    self.current_rate * self.decrease_factor
                )
            elif status_code >= 500:
                # 服务器错误，小幅降低
                self.current_rate = max(
                    self.min_rate,
                    self.current_rate * 0.8
                )
            self._update_bucket()

    def _update_bucket(self):
        """更新令牌桶参数"""
        self.token_bucket.refill_rate = self.current_rate
        self.token_bucket.capacity = int(self.current_rate * 2)

    def is_allowed(self) -> bool:
        """检查是否允许请求"""
        return self.token_bucket.consume(1)

    def wait_for_token(self, timeout: float = None) -> bool:
        """等待获取令牌"""
        return self.token_bucket.wait_and_consume(1, timeout)

    def get_current_rate(self) -> float:
        """获取当前速率"""
        return self.current_rate


# 全局限流器注册表
_limiters: Dict[str, object] = {}


def get_limiter(name: str, limiter_class: type = TokenBucket, **kwargs):
    """
    获取或创建限流器实例

    Args:
        name: 限流器名称
        limiter_class: 限流器类
        **kwargs: 限流器参数

    Returns:
        限流器实例
    """
    if name not in _limiters:
        _limiters[name] = limiter_class(**kwargs)
    return _limiters[name]
