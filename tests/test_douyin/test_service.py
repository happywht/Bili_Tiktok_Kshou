"""
抖音服务测试

测试抖音搜索功能的核心测试用例

注意：抖音搜索可能遇到验证码，建议使用可见浏览器模式进行调试
"""
import pytest
from api.services.base import PlatformType


@pytest.mark.douyin
@pytest.mark.integration
class TestDouyinService:
    """抖音服务测试类"""

    def test_service_initialization(self, douyin_service):
        """测试服务初始化"""
        assert douyin_service is not None
        assert douyin_service.platform == PlatformType.DOUYIN

    @pytest.mark.slow
    def test_search_returns_results(self, douyin_service, sample_keyword):
        """测试搜索返回结果（可能受验证码影响）"""
        results = douyin_service.search(sample_keyword, page=1, page_size=10)

        # 注意：抖音搜索可能因验证码而失败
        # 这里我们检查结果类型，但不强制要求有结果
        assert results is not None
        assert isinstance(results, list)

        if len(results) == 0:
            pytest.skip("抖音搜索未返回结果，可能遇到验证码或Cookie问题")

    @pytest.mark.slow
    def test_search_result_structure(self, douyin_service, sample_keyword):
        """测试搜索结果结构"""
        results = douyin_service.search(sample_keyword, page=1, page_size=5)

        if not results:
            pytest.skip("抖音搜索未返回结果，跳过结构验证")

        item = results[0]
        assert item.title, "结果应有标题"
        assert item.platform == PlatformType.DOUYIN

    @pytest.mark.slow
    def test_cookie_check(self, douyin_service):
        """测试Cookie有效性检查"""
        result = douyin_service.check_cookie()

        assert result is not None
        assert 'valid' in result


@pytest.mark.douyin
@pytest.mark.slow
class TestDouyinServiceBrowser:
    """抖音浏览器自动化测试"""

    @pytest.mark.skip(reason="需要手动验证码处理，仅在调试时启用")
    def test_visible_browser_search(self, douyin_service_visible, sample_keyword):
        """
        使用可见浏览器搜索（用于调试验证码问题）

        此测试会打开浏览器窗口，允许用户手动处理验证码
        """
        results = douyin_service_visible.search(sample_keyword, page=1, page_size=10)

        assert results is not None
        assert len(results) > 0, "可见模式应能获取结果（如已手动处理验证码）"


@pytest.mark.douyin
class TestDouyinServiceUtilities:
    """抖音服务工具函数测试"""

    def test_parse_count(self, douyin_service):
        """测试数字解析"""
        # 测试各种格式
        assert douyin_service.parse_count("1.2万") == 12000
        assert douyin_service.parse_count("100") == 100
        assert douyin_service.parse_count(1000) == 1000
