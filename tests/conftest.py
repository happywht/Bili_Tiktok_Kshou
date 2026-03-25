"""
pytest配置文件

提供测试夹具和通用配置
"""
import os
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / '.env')


# ============ 平台服务夹具 ============

@pytest.fixture
def bilibili_service():
    """B站服务夹具"""
    from api.services.bilibili_service import BilibiliService
    sessdata = os.getenv('BILIBILI_SESSDATA', '')
    return BilibiliService(sessdata=sessdata)


@pytest.fixture
def douyin_service():
    """抖音服务夹具"""
    from api.services.douyin_service import DouyinService
    cookies = os.getenv('DOUYIN_COOKIES', '')
    return DouyinService(cookies=cookies, auto_fallback=True)


@pytest.fixture
def douyin_service_headless():
    """抖音服务夹具（无头模式）"""
    from api.services.douyin_service import DouyinService
    cookies = os.getenv('DOUYIN_COOKIES', '')
    return DouyinService(cookies=cookies, headless=True, auto_fallback=True)


@pytest.fixture
def douyin_service_visible():
    """抖音服务夹具（可见浏览器模式，用于手动处理验证码）"""
    from api.services.douyin_service import DouyinService
    cookies = os.getenv('DOUYIN_COOKIES', '')
    return DouyinService(cookies=cookies, headless=False, auto_fallback=True)


@pytest.fixture
def xiaohongshu_service():
    """小红书服务夹具"""
    from api.services.xiaohongshu_service import XiaohongshuService
    cookies = os.getenv('XIAOHONGSHU_COOKIES', '')
    return XiaohongshuService(cookies=cookies)


# ============ 通用测试数据夹具 ============

@pytest.fixture
def sample_keyword():
    """通用搜索关键词"""
    return "Python"


@pytest.fixture
def sample_keywords():
    """多个测试关键词"""
    return ["Python", "人工智能", "编程教程"]


# ============ pytest配置 ============

def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "bilibili: B站相关测试"
    )
    config.addinivalue_line(
        "markers", "douyin: 抖音相关测试"
    )
    config.addinivalue_line(
        "markers", "xiaohongshu: 小红书相关测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试（需要网络请求或浏览器）"
    )
    config.addinivalue_line(
        "markers", "interactive: 需要用户交互的测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试集合"""
    # 为需要网络的测试添加slow标记
    for item in items:
        if "search" in item.nodeid or "browser" in item.nodeid:
            item.add_marker(pytest.mark.slow)
