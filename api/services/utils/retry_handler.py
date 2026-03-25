"""
重试处理器 - 指数退避重试机制

提供统一的请求重试策略，支持自定义重试次数、延迟时间和异常处理。
"""
import time
import random
import logging
from typing import Callable, Tuple, Type
from functools import wraps
import requests

logger = logging.getLogger(__name__)


def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (requests.RequestException,),
    retryable_status_codes: Tuple[int, ...] = (408, 429, 500, 502, 503, 504),
    on_retry: Callable = None
):
    """
    指数退避重试装饰器

    通过指数增长延迟时间和随机抖动，实现优雅的重试机制，避免请求风暴。

    Args:
        max_retries: 最大重试次数（默认3次）
        base_delay: 基础延迟时间，单位秒（默认1.0秒）
        max_delay: 最大延迟时间，单位秒（默认30.0秒）
        exponential_base: 指数基数（默认2.0，每次延迟翻倍）
        retryable_exceptions: 可触发重试的异常类型元组
        retryable_status_codes: 可触发重试的HTTP状态码元组
        on_retry: 重试前的回调函数，接收(attempt, delay, exception)参数

    Returns:
        装饰后的函数

    Example:
        @exponential_backoff_retry(max_retries=3, base_delay=1.0)
        def fetch_data():
            response = requests.get('https://api.example.com/data')
            return response.json()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            last_status_code = None

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)

                    # 检查是否是需要重试的状态码（针对返回字典的函数）
                    if isinstance(result, dict):
                        status_code = result.get('_status_code')
                        if status_code in retryable_status_codes:
                            last_status_code = status_code
                            if attempt < max_retries:
                                delay = _calculate_delay(
                                    attempt, base_delay, exponential_base, max_delay
                                )
                                logger.warning(
                                    f"请求返回状态码 {status_code}，"
                                    f"第 {attempt + 1}/{max_retries + 1} 次尝试，"
                                    f"{delay:.2f}秒后重试"
                                )
                                if on_retry:
                                    on_retry(attempt, delay, None)
                                time.sleep(delay)
                                continue

                    return result

                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = _calculate_delay(
                            attempt, base_delay, exponential_base, max_delay
                        )
                        logger.warning(
                            f"请求异常: {e}，"
                            f"第 {attempt + 1}/{max_retries + 1} 次尝试，"
                            f"{delay:.2f}秒后重试"
                        )
                        if on_retry:
                            on_retry(attempt, delay, e)
                        time.sleep(delay)
                    else:
                        logger.error(f"请求失败，已达到最大重试次数 {max_retries}: {e}")

            # 返回错误信息
            return _build_error_response(last_exception, last_status_code)

        return wrapper
    return decorator


def _calculate_delay(
    attempt: int,
    base_delay: float,
    exponential_base: float,
    max_delay: float
) -> float:
    """
    计算重试延迟时间（指数退避 + 随机抖动）

    Args:
        attempt: 当前尝试次数（从0开始）
        base_delay: 基础延迟
        exponential_base: 指数基数
        max_delay: 最大延迟

    Returns:
        延迟时间（秒）
    """
    # 指数退避
    delay = base_delay * (exponential_base ** attempt)
    # 限制最大延迟
    delay = min(delay, max_delay)
    # 添加随机抖动（50%-100%）
    delay = delay * (0.5 + random.random())
    return delay


def _build_error_response(
    exception: Exception,
    status_code: int
) -> dict:
    """
    构建错误响应

    Args:
        exception: 最后一次异常
        status_code: 最后一次状态码

    Returns:
        错误响应字典
    """
    if exception:
        return {
            'error': f'请求失败: {str(exception)}',
            'error_type': type(exception).__name__
        }
    if status_code:
        return {
            'error': f'请求返回状态码 {status_code}',
            'error_type': 'HTTPError',
            '_status_code': status_code
        }
    return {'error': '未知错误'}


class RetryContext:
    """
    重试上下文管理器

    用于需要更细粒度控制重试逻辑的场景。

    Example:
        with RetryContext(max_retries=3) as retry:
            while retry.should_retry():
                try:
                    response = requests.get(url)
                    if response.ok:
                        return response.json()
                    retry.record_failure(f"状态码: {response.status_code}")
                except Exception as e:
                    retry.record_failure(e)
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.attempt = 0
        self.last_error = None

    def should_retry(self) -> bool:
        """是否应该继续重试"""
        return self.attempt <= self.max_retries

    def record_failure(self, error):
        """记录失败"""
        self.last_error = error
        self.attempt += 1

    def get_delay(self) -> float:
        """获取下次重试延迟"""
        return _calculate_delay(
            self.attempt - 1,
            self.base_delay,
            2.0,
            self.max_delay
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False  # 不抑制异常
