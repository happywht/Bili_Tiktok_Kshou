"""
错误处理演示脚本

演示新的统一异常处理系统
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.exceptions import (
    PlatformError,
    CookieExpiredError,
    BilibiliCookieExpiredError,
    DouyinCookieExpiredError,
    RateLimitError,
    CaptchaDetectedError,
    PlatformNotAvailableError,
    ContentNotFoundError,
    InvalidParameterError,
    NetworkError,
    TimeoutError,
    create_platform_error,
    detect_error_from_response,
)


def test_exception_hierarchy():
    """测试异常继承关系"""
    print("=" * 60)
    print("异常继承关系测试")
    print("=" * 60)

    # 测试 BilibiliCookieExpiredError
    exc = BilibiliCookieExpiredError()
    print(f"\n1. BilibiliCookieExpiredError:")
    print(f"   - 错误类型: {exc.error_type}")
    print(f"   - 错误码: {exc.code}")
    print(f"   - 错误信息: {exc.message}")
    print(f"   - 解决建议: {exc.suggestion}")
    print(f"   - 是否为 PlatformError: {isinstance(exc, PlatformError)}")
    print(f"   - 是否为 CookieExpiredError: {isinstance(exc, CookieExpiredError)}")

    # 测试 RateLimitError
    exc = RateLimitError(retry_after=60)
    print(f"\n2. RateLimitError:")
    print(f"   - 错误类型: {exc.error_type}")
    print(f"   - 错误码: {exc.code}")
    print(f"   - 错误信息: {exc.message}")
    print(f"   - 解决建议: {exc.suggestion}")
    print(f"   - 重试等待时间: {exc.retry_after}秒")

    # 测试自定义消息
    exc = ContentNotFoundError(
        message="视频 BV1xx411c7mD 不存在",
        suggestion="请检查BV号是否正确",
        details={"bvid": "BV1xx411c7mD"}
    )
    print(f"\n3. ContentNotFoundError (自定义):")
    print(f"   - 错误类型: {exc.error_type}")
    print(f"   - 错误码: {exc.code}")
    print(f"   - 错误信息: {exc.message}")
    print(f"   - 解决建议: {exc.suggestion}")
    print(f"   - 详细信息: {exc.details}")


def test_to_dict():
    """测试异常转字典（用于API响应）"""
    print("\n" + "=" * 60)
    print("异常转字典测试")
    print("=" * 60)

    exc = BilibiliCookieExpiredError(
        message="B站登录状态已过期",
        details={"platform": "bilibili", "error_code": -412}
    )

    result = exc.to_dict()
    print("\n异常字典输出:")
    for key, value in result.items():
        print(f"  {key}: {value}")


def test_create_platform_error():
    """测试根据错误码创建异常"""
    print("\n" + "=" * 60)
    print("错误码映射测试")
    print("=" * 60)

    test_cases = [
        ("bilibili", -412, "请求被拦截"),
        ("bilibili", -101, "账号未登录"),
        ("bilibili", -403, "访问受限"),
        ("bilibili", -404, "视频不存在"),
        ("douyin", 8, "需要登录"),
        ("douyin", 2151, "请求过于频繁"),
        ("unknown", 429, "Too Many Requests"),
        ("unknown", 500, "Internal Server Error"),
    ]

    for platform, code, message in test_cases:
        exc = create_platform_error(platform, code, message)
        print(f"\n{platform.upper()} 错误码 {code}:")
        print(f"  -> 异常类型: {exc.__class__.__name__}")
        print(f"  -> HTTP状态码: {exc.code}")
        print(f"  -> 错误信息: {exc.message}")


def test_detect_error_from_response():
    """测试从响应数据检测错误"""
    print("\n" + "=" * 60)
    print("响应错误检测测试")
    print("=" * 60)

    # B站响应
    bilibili_response = {
        "code": -412,
        "message": "请求被拦截",
        "data": None
    }
    exc = detect_error_from_response("bilibili", bilibili_response)
    if exc:
        print(f"\nB站响应检测:")
        print(f"  -> 检测到异常: {exc.__class__.__name__}")
        print(f"  -> 错误信息: {exc.message}")

    # 正常响应
    normal_response = {
        "code": 0,
        "message": "success",
        "data": {"items": []}
    }
    exc = detect_error_from_response("bilibili", normal_response)
    print(f"\n正常响应检测:")
    print(f"  -> 检测到异常: {exc}")


def test_exception_chaining():
    """测试异常链"""
    print("\n" + "=" * 60)
    print("异常链测试")
    print("=" * 60)

    try:
        # 模拟原始错误
        raise ConnectionError("Network is unreachable")
    except Exception as e:
        # 包装为平台异常
        exc = NetworkError(
            message="无法连接到B站服务器",
            original_error=e
        )
        print(f"\n包装后的异常:")
        print(f"  -> 异常类型: {exc.__class__.__name__}")
        print(f"  -> 错误信息: {exc.message}")
        print(f"  -> 原始异常: {exc.original_error}")


def main():
    """主函数"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + " " * 15 + "错误处理系统演示" + " " * 15 + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")

    test_exception_hierarchy()
    test_to_dict()
    test_create_platform_error()
    test_detect_error_from_response()
    test_exception_chaining()

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    print("\nAPI错误响应格式示例:")
    print("-" * 60)
    import json
    exc = BilibiliCookieExpiredError()
    print(json.dumps(exc.to_dict(), indent=2, ensure_ascii=False))
    print("-" * 60)


if __name__ == "__main__":
    main()
