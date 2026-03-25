"""
错误处理中间件

统一处理所有异常，返回标准化的错误响应
"""
import time
import logging
import traceback
from typing import Callable, Dict, Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# 尝试导入异常类（支持不同运行方式）
try:
    from ..exceptions import (
        PlatformError,
        CookieExpiredError,
        RateLimitError,
        CaptchaDetectedError,
        PlatformNotAvailableError,
        ContentNotFoundError,
        InvalidParameterError,
        NetworkError,
        TimeoutError,
        ParseError,
        AuthenticationRequiredError,
    )
except ImportError:
    from api.exceptions import (
        PlatformError,
        CookieExpiredError,
        RateLimitError,
        CaptchaDetectedError,
        PlatformNotAvailableError,
        ContentNotFoundError,
        InvalidParameterError,
        NetworkError,
        TimeoutError,
        ParseError,
        AuthenticationRequiredError,
    )

# 配置日志
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    错误处理中间件

    捕获所有异常并返回统一格式的错误响应
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """
        处理请求

        Args:
            request: 请求对象
            call_next: 下一个处理函数

        Returns:
            响应对象
        """
        try:
            return await call_next(request)
        except Exception as exc:
            return self._handle_exception(request, exc)

    def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        处理异常

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSON响应
        """
        # 记录错误日志
        self._log_error(request, exc)

        # 根据异常类型生成响应
        if isinstance(exc, PlatformError):
            return self._create_platform_error_response(exc)
        elif isinstance(exc, RequestValidationError):
            return self._create_validation_error_response(exc)
        elif isinstance(exc, HTTPException):
            return self._create_http_error_response(exc)
        else:
            return self._create_generic_error_response(exc)

    def _create_platform_error_response(self, exc: PlatformError) -> JSONResponse:
        """
        创建平台错误响应

        Args:
            exc: 平台异常

        Returns:
            JSON响应
        """
        response_data = {
            "success": False,
            "code": exc.code,
            "message": exc.message,
            "error_type": exc.error_type,
            "suggestion": exc.suggestion,
            "timestamp": int(time.time() * 1000)
        }

        # 添加详细信息（如果有）
        if exc.details:
            response_data["details"] = exc.details

        # 添加重试时间（如果是速率限制错误）
        if isinstance(exc, RateLimitError) and hasattr(exc, 'retry_after') and exc.retry_after:
            response_data["retry_after"] = exc.retry_after

        return JSONResponse(
            status_code=exc.code,
            content=response_data
        )

    def _create_validation_error_response(self, exc: RequestValidationError) -> JSONResponse:
        """
        创建参数验证错误响应

        Args:
            exc: 验证异常

        Returns:
            JSON响应
        """
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error.get("type", "value_error")
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "code": 422,
                "message": "请求参数验证失败",
                "error_type": "ValidationError",
                "suggestion": "请检查请求参数是否符合要求",
                "details": {
                    "errors": errors
                },
                "timestamp": int(time.time() * 1000)
            }
        )

    def _create_http_error_response(self, exc: HTTPException) -> JSONResponse:
        """
        创建HTTP错误响应

        Args:
            exc: HTTP异常

        Returns:
            JSON响应
        """
        # 尝试识别常见错误类型
        error_type = "HTTPError"
        suggestion = "请检查请求是否正确"

        if exc.status_code == 400:
            error_type = "BadRequestError"
            suggestion = "请求参数有误，请检查后重试"
        elif exc.status_code == 401:
            error_type = "UnauthorizedError"
            suggestion = "需要登录认证，请配置相应的Cookie环境变量"
        elif exc.status_code == 403:
            error_type = "ForbiddenError"
            suggestion = "没有权限访问此资源"
        elif exc.status_code == 404:
            error_type = "NotFoundError"
            suggestion = "请求的资源不存在"
        elif exc.status_code == 429:
            error_type = "TooManyRequestsError"
            suggestion = "请求过于频繁，请稍后重试"
        elif exc.status_code >= 500:
            error_type = "ServerError"
            suggestion = "服务器内部错误，请稍后重试"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": exc.status_code,
                "message": str(exc.detail),
                "error_type": error_type,
                "suggestion": suggestion,
                "timestamp": int(time.time() * 1000)
            }
        )

    def _create_generic_error_response(self, exc: Exception) -> JSONResponse:
        """
        创建通用错误响应

        Args:
            exc: 异常对象

        Returns:
            JSON响应
        """
        # 检查是否是已知的异常类型
        error_message = str(exc)

        # 网络相关错误
        if any(keyword in error_message.lower() for keyword in ["connection", "network", "timeout", "timed out"]):
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={
                    "success": False,
                    "code": 502,
                    "message": "网络连接失败",
                    "error_type": "NetworkError",
                    "suggestion": "请检查网络连接后重试",
                    "timestamp": int(time.time() * 1000)
                }
            )

        # Cookie相关错误
        if any(keyword in error_message for keyword in ["SESSDATA", "Cookie", "cookie", "登录"]):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "code": 401,
                    "message": "登录状态已过期或无效",
                    "error_type": "CookieExpiredError",
                    "suggestion": "请更新相应的Cookie环境变量后重试",
                    "timestamp": int(time.time() * 1000)
                }
            )

        # 速率限制错误
        if any(keyword in error_message for keyword in ["429", "rate limit", "频率"]):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "code": 429,
                    "message": "请求过于频繁",
                    "error_type": "RateLimitError",
                    "suggestion": "请稍后重试，建议降低请求频率",
                    "timestamp": int(time.time() * 1000)
                }
            )

        # 默认服务器错误
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "code": 500,
                "message": "服务器内部错误",
                "error_type": "InternalError",
                "suggestion": "服务出现异常，请稍后重试或联系管理员",
                "details": {
                    "error": error_message
                } if logger.isEnabledFor(logging.DEBUG) else None,
                "timestamp": int(time.time() * 1000)
            }
        )

    def _log_error(self, request: Request, exc: Exception):
        """
        记录错误日志

        Args:
            request: 请求对象
            exc: 异常对象
        """
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"

        # 构建日志信息
        log_data = {
            "method": method,
            "url": url,
            "client_ip": client_ip,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        }

        # 根据错误类型选择日志级别
        if isinstance(exc, (PlatformError, HTTPException)):
            if isinstance(exc, (CookieExpiredError, ContentNotFoundError)):
                # 预期的错误，使用INFO级别
                logger.info(f"Client error: {log_data}")
            else:
                # 其他平台错误，使用WARNING级别
                logger.warning(f"Platform error: {log_data}")
        else:
            # 未预期的错误，使用ERROR级别并包含堆栈信息
            logger.error(
                f"Unexpected error: {log_data}",
                exc_info=True,
                extra={"traceback": traceback.format_exc()}
            )


# ============ 异常处理器函数 ============

async def platform_exception_handler(request: Request, exc: PlatformError) -> JSONResponse:
    """
    平台异常处理器

    Args:
        request: 请求对象
        exc: 平台异常

    Returns:
        JSON响应
    """
    logger.warning(f"Platform error: {exc.error_type} - {exc.message}")

    response_data = {
        "success": False,
        "code": exc.code,
        "message": exc.message,
        "error_type": exc.error_type,
        "suggestion": exc.suggestion,
        "timestamp": int(time.time() * 1000)
    }

    if exc.details:
        response_data["details"] = exc.details

    return JSONResponse(
        status_code=exc.code,
        content=response_data
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    参数验证异常处理器

    Args:
        request: 请求对象
        exc: 验证异常

    Returns:
        JSON响应
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error.get("type", "value_error")
        })

    logger.info(f"Validation error for {request.url}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "code": 422,
            "message": "请求参数验证失败",
            "error_type": "ValidationError",
            "suggestion": "请检查请求参数是否符合要求",
            "details": {
                "errors": errors
            },
            "timestamp": int(time.time() * 1000)
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP异常处理器

    Args:
        request: 请求对象
        exc: HTTP异常

    Returns:
        JSON响应
    """
    # 尝试识别常见错误类型
    error_type = "HTTPError"
    suggestion = "请检查请求是否正确"

    if exc.status_code == 400:
        error_type = "BadRequestError"
        suggestion = "请求参数有误，请检查后重试"
    elif exc.status_code == 401:
        error_type = "UnauthorizedError"
        suggestion = "需要登录认证，请配置相应的Cookie环境变量"
    elif exc.status_code == 403:
        error_type = "ForbiddenError"
        suggestion = "没有权限访问此资源"
    elif exc.status_code == 404:
        error_type = "NotFoundError"
        suggestion = "请求的资源不存在"
    elif exc.status_code == 429:
        error_type = "TooManyRequestsError"
        suggestion = "请求过于频繁，请稍后重试"
    elif exc.status_code >= 500:
        error_type = "ServerError"
        suggestion = "服务器内部错误，请稍后重试"

    logger.warning(f"HTTP error {exc.status_code} for {request.url}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.status_code,
            "message": str(exc.detail),
            "error_type": error_type,
            "suggestion": suggestion,
            "timestamp": int(time.time() * 1000)
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSON响应
    """
    logger.error(
        f"Unexpected error for {request.url}: {type(exc).__name__} - {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "code": 500,
            "message": "服务器内部错误",
            "error_type": "InternalError",
            "suggestion": "服务出现异常，请稍后重试或联系管理员",
            "timestamp": int(time.time() * 1000)
        }
    )


# ============ 设置函数 ============

def setup_error_handlers(app):
    """
    设置异常处理器

    Args:
        app: FastAPI应用实例
    """
    # 使用已在文件顶部导入的 PlatformError
    # 注册异常处理器
    app.add_exception_handler(PlatformError, platform_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Error handlers configured successfully")
