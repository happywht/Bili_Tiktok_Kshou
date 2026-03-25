"""
抖音搜索交互式测试工具

支持非无头模式手动处理验证码

使用方法:
    python tools/douyin_interactive_test.py
"""
import os
import sys
import time
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 配置控制台编码
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / '.env')


def test_with_visible_browser():
    """使用可见浏览器测试（可手动处理验证码）"""
    from api.services.douyin_service import DouyinService

    cookies = os.getenv('DOUYIN_COOKIES', '')

    print("=" * 60)
    print("抖音搜索测试 - 可见浏览器模式")
    print("=" * 60)
    print("\n提示: 浏览器窗口将显示，如遇到验证码请手动完成验证")
    print("      完成验证后，搜索将继续进行\n")

    # 创建服务实例（非无头模式）
    service = DouyinService(
        cookies=cookies,
        headless=False,  # 显示浏览器窗口
        auto_fallback=True
    )

    keyword = input("请输入搜索关键词 (默认: Python): ").strip() or "Python"

    print(f"\n开始搜索: {keyword}")
    print("-" * 40)

    # 直接使用浏览器方案
    items = service._fallback_search(keyword, 1, 10)

    print(f"\n搜索结果: {len(items)} 条")
    print("-" * 40)

    for i, item in enumerate(items):
        print(f"\n[{i+1}] {item.title}")
        if item.author:
            print(f"    作者: {item.author}")
        if item.like_count:
            print(f"    点赞: {item.like_count}")
        if item.url:
            print(f"    链接: {item.url}")

    return len(items) > 0


def test_api_search():
    """测试API搜索方式"""
    from api.services.douyin_service import DouyinService

    cookies = os.getenv('DOUYIN_COOKIES', '')

    print("=" * 60)
    print("抖音搜索测试 - API模式")
    print("=" * 60)

    service = DouyinService(cookies=cookies)

    # 检查Cookie
    print("\n检查Cookie...")
    result = service.check_cookie(force=True)
    print(f"  有效: {result.get('valid')}")
    print(f"  消息: {result.get('message')}")

    # 执行搜索
    print("\n执行搜索...")
    items = service.search('Python', 1, 5)

    print(f"\n搜索结果: {len(items)} 条")

    for i, item in enumerate(items):
        print(f"\n[{i+1}] {item.title}")

    return len(items) > 0


def test_cookie_status():
    """测试Cookie状态"""
    from api.services.douyin_service import DouyinService

    cookies = os.getenv('DOUYIN_COOKIES', '')

    print("=" * 60)
    print("抖音Cookie状态检查")
    print("=" * 60)

    if not cookies:
        print("\n错误: 未配置DOUYIN_COOKIES")
        print("请在.env文件中添加: DOUYIN_COOKIES=your_cookie_string")
        return False

    print(f"\nCookie长度: {len(cookies)}")

    service = DouyinService(cookies=cookies)
    result = service.check_cookie(force=True)

    print(f"\nCookie状态:")
    print(f"  有效: {result.get('valid')}")
    print(f"  消息: {result.get('message')}")

    if result.get('user_info'):
        user = result['user_info']
        print(f"\n用户信息:")
        print(f"  昵称: {user.get('nickname', 'N/A')}")
        print(f"  ID: {user.get('uid', 'N/A')}")

    return result.get('valid', False)


def main():
    """主函数"""
    print("抖音搜索交互式测试")
    print("=" * 60)

    print("\n请选择测试模式:")
    print("  1. 可见浏览器模式（推荐 - 可手动处理验证码）")
    print("  2. API模式（后台自动）")
    print("  3. Cookie状态检查")
    print("  0. 退出")

    choice = input("\n请选择 [0-3]: ").strip()

    if choice == '1':
        test_with_visible_browser()
    elif choice == '2':
        test_api_search()
    elif choice == '3':
        test_cookie_status()
    elif choice == '0':
        print("退出测试")
    else:
        print("无效选择")

    input("\n按回车键退出...")


if __name__ == '__main__':
    main()
