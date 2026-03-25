"""
统一异常类定义

定义平台相关的异常类型，用于统一错误处理
"""
from typing import Optional, Dict, Any


class PlatformError(Exception):
    """
    平台错误基类

    所有平台相关异常的基类，提供统一的错误信息结构
    """

    # 默认错误码
    default_code: int = 500
    # 默认错误类型标识
    error_type: str = "PlatformError"
    # 默认用户提示
    default_message: str = "平台服务异常"
    # 默认解决建议
    default_suggestion: str = "请稍后重试"

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[int] = None,
        suggestion: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        初始化异常

        Args:
            message: 错误信息（用户友好）
            code: HTTP状态码
            suggestion: 解决建议
            details: 详细错误信息
            original_error: 原始异常
        """
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.suggestion = suggestion or self.default_suggestion
        self.details = details or {}
        self.original_error = original_error

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（用于API响应）

        Returns:
            包含错误信息的字典
        """
        return {
            "success": False,
            "code": self.code,
            "message": self.message,
            "error_type": self.error_type,
            "suggestion": self.suggestion,
            "details": self.details
        }


class CookieExpiredError(PlatformError):
    """Cookie过期异常"""

    default_code: int = 401
    error_type: str = "CookieExpiredError"
    default_message: str = "登录状态已过期"
    default_suggestion: str = "请更新相应的Cookie环境变量后重试"


class BilibiliCookieExpiredError(CookieExpiredError):
    """B站Cookie过期"""

    default_suggestion: str = "请更新BILIBILI_SESSDATA环境变量后重试（参考: https://github.com/your-repo/wiki/bilibili-cookie）"


class DouyinCookieExpiredError(CookieExpiredError):
    """抖音Cookie过期"""

    default_suggestion: str = "请更新DOUYIN_COOKIE环境变量后重试"


class XiaohongshuCookieExpiredError(CookieExpiredError):
    """小红书Cookie过期"""

    default_suggestion: str = "请更新XIAOHONGSHU_COOKIE环境变量后重试"


class RateLimitError(PlatformError):
    """速率限制异常"""

    default_code: int = 429
    error_type: str = "RateLimitError"
    default_message: str = "请求过于频繁"
    default_suggestion: str = "请稍后重试，建议降低请求频率"

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[int] = None,
        suggestion: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message, code, suggestion, details, original_error)
        self.retry_after = retry_after  # 建议等待秒数

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.retry_after:
            result["retry_after"] = self.retry_after
        return result


class CaptchaDetectedError(PlatformError):
    """验证码拦截异常"""

    default_code: int = 403
    error_type: str = "CaptchaDetectedError"
    default_message: str = "需要完成验证码验证"
    default_suggestion: str = "请在浏览器中手动完成验证后重试"


class PlatformNotAvailableError(PlatformError):
    """平台不可用异常"""

    default_code: int = 503
    error_type: str = "PlatformNotAvailableError"
    default_message: str = "平台服务暂时不可用"
    default_suggestion: str = "请稍后重试或切换到其他平台"


class BilibiliNotAvailableError(PlatformNotAvailableError):
    """B站服务不可用"""

    default_message: str = "B站服务暂时不可用"
    default_suggestion: str = "请稍后重试，或检查B站服务状态"


class DouyinNotAvailableError(PlatformNotAvailableError):
    """抖音服务不可用"""

    default_message: str = "抖音服务暂时不可用"
    default_suggestion: str = "抖音平台需要登录态支持，请配置DOUYIN_COOKIE环境变量"


class XiaohongshuNotAvailableError(PlatformNotAvailableError):
    """小红书服务不可用"""

    default_message: str = "小红书服务暂时不可用"
    default_suggestion: str = "请确保 Playwright 已安装（pip install playwright && playwright install chromium），且已通过扫码完成首次登录"


class ContentNotFoundError(PlatformError):
    """内容不存在异常"""

    default_code: int = 404
    error_type: str = "ContentNotFoundError"
    default_message: str = "请求的内容不存在"
    default_suggestion: str = "请检查内容ID是否正确"


class InvalidParameterError(PlatformError):
    """参数无效异常"""

    default_code: int = 400
    error_type: str = "InvalidParameterError"
    default_message: str = "请求参数无效"
    default_suggestion: str = "请检查请求参数是否符合要求"


class NetworkError(PlatformError):
    """网络错误异常"""

    default_code: int = 502
    error_type: str = "NetworkError"
    default_message: str = "网络连接失败"
    default_suggestion: str = "请检查网络连接后重试"


class TimeoutError(PlatformError):
    """请求超时异常"""

    default_code: int = 504
    error_type: str = "TimeoutError"
    default_message: str = "请求超时"
    default_suggestion: str = "服务响应较慢，请稍后重试"


class ParseError(PlatformError):
    """数据解析错误"""

    default_code: int = 500
    error_type: str = "ParseError"
    default_message: str = "数据解析失败"
    default_suggestion: str = "平台数据格式可能已变更，请联系管理员"


class AuthenticationRequiredError(PlatformError):
    """需要登录认证"""

    default_code: int = 401
    error_type: str = "AuthenticationRequiredError"
    default_message: str = "此操作需要登录认证"
    default_suggestion: str = "请配置相应的Cookie环境变量"


# ============ 异常映射工具 ============

def create_platform_error(
    platform: str,
    error_code: int,
    error_message: str,
    original_error: Optional[Exception] = None
) -> PlatformError:
    """
    根据平台和错误码创建对应的异常

    Args:
        platform: 平台标识 (bilibili, douyin, xiaohongshu)
        error_code: 错误码
        error_message: 错误信息
        original_error: 原始异常

    Returns:
        对应的平台异常
    """
    platform = platform.lower()

    # B站错误码映射
    if platform == "bilibili":
        if error_code in [-412, -101]:
            return BilibiliCookieExpiredError(
                message="B站登录状态已过期或无效",
                original_error=original_error
            )
        if error_code == -403:
            return RateLimitError(
                message="B站请求频率过高",
                original_error=original_error
            )
        if error_code == -400:
            return InvalidParameterError(
                message="请求参数无效",
                original_error=original_error
            )
        if error_code == -404:
            return ContentNotFoundError(
                message="视频不存在或已删除",
                original_error=original_error
            )

    # 抖音错误码映射
    if platform == "douyin":
        if error_code in [8, 2154]:
            return DouyinCookieExpiredError(
                message="抖音登录状态已过期",
                original_error=original_error
            )
        if error_code == 2151:
            return RateLimitError(
                message="抖音请求频率过高",
                original_error=original_error
            )

    # 通用错误码映射
    if error_code in [401, 403]:
        if platform == "bilibili":
            return BilibiliCookieExpiredError(original_error=original_error)
        if platform == "douyin":
            return DouyinCookieExpiredError(original_error=original_error)
        if platform == "xiaohongshu":
            return XiaohongshuCookieExpiredError(original_error=original_error)

    if error_code == 404:
        return ContentNotFoundError(
            message=error_message or "内容不存在",
            original_error=original_error
        )

    if error_code == 429:
        return RateLimitError(
            message=error_message or "请求过于频繁",
            original_error=original_error
        )

    if error_code in [500, 502, 503]:
        return PlatformNotAvailableError(
            message=error_message or "平台服务暂时不可用",
            original_error=original_error
        )

    if error_code == 504:
        return TimeoutError(
            message=error_message or "请求超时",
            original_error=original_error
        )

    # 默认返回通用平台错误
    return PlatformError(
        message=error_message or "平台服务异常",
        code=error_code if error_code > 0 else 500,
        original_error=original_error
    )


def detect_error_from_response(
    platform: str,
    response_data: Dict[str, Any],
    status_code: int = 200
) -> Optional[PlatformError]:
    """
    从响应数据中检测错误

    Args:
        platform: 平台标识
        response_data: 响应数据
        status_code: HTTP状态码

    Returns:
        检测到的异常，如果没有错误则返回None
    """
    # 检查HTTP状态码
    if status_code >= 500:
        return PlatformNotAvailableError(
            message="平台服务异常",
            details={"status_code": status_code}
        )

    if status_code == 429:
        return RateLimitError()

    # B站响应格式
    if platform == "bilibili":
        code = response_data.get("code", 0)
        if code != 0:
            return create_platform_error(
                platform=platform,
                error_code=code,
                error_message=response_data.get("message", "未知错误")
            )

    # 抖音响应格式
    if platform == "douyin":
        status_code_inner = response_data.get("status_code", 0)
        if status_code_inner != 0:
            return create_platform_error(
                platform=platform,
                error_code=status_code_inner,
                error_message=response_data.get("status_msg", "未知错误")
            )

    return None
