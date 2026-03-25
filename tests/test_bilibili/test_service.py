"""
B站服务测试

测试B站搜索功能的核心测试用例
"""
import pytest
from api.services.base import PlatformType


@pytest.mark.bilibili
@pytest.mark.integration
class TestBilibiliService:
    """B站服务测试类"""

    def test_service_initialization(self, bilibili_service):
        """测试服务初始化"""
        assert bilibili_service is not None
        assert bilibili_service.platform == PlatformType.BILIBILI

    def test_search_returns_results(self, bilibili_service, sample_keyword):
        """测试搜索返回结果"""
        results = bilibili_service.search(sample_keyword, page=1, page_size=10)

        assert results is not None
        assert isinstance(results, list)
        assert len(results) > 0, "搜索应返回至少1个结果"

    def test_search_result_structure(self, bilibili_service, sample_keyword):
        """测试搜索结果结构"""
        results = bilibili_service.search(sample_keyword, page=1, page_size=5)

        if results:
            item = results[0]
            assert item.title, "结果应有标题"
            assert item.url, "结果应有URL"
            assert item.platform == PlatformType.BILIBILI

    def test_search_pagination(self, bilibili_service, sample_keyword):
        """测试分页功能"""
        page1 = bilibili_service.search(sample_keyword, page=1, page_size=5)
        page2 = bilibili_service.search(sample_keyword, page=2, page_size=5)

        assert len(page1) > 0, "第1页应有结果"
        assert len(page2) > 0, "第2页应有结果"

    def test_get_video_detail(self, bilibili_service):
        """测试获取视频详情"""
        # 先搜索获取一个视频
        results = bilibili_service.search("Python", page=1, page_size=1)

        if results:
            bvid = results[0].id
            detail = bilibili_service.get_detail(bvid)

            assert detail is not None
            assert 'title' in detail or 'error' in detail


@pytest.mark.bilibili
@pytest.mark.slow
class TestBilibiliServiceExtended:
    """B站服务扩展测试（需要网络）"""

    def test_search_with_different_keywords(self, bilibili_service, sample_keywords):
        """测试不同关键词搜索"""
        for keyword in sample_keywords:
            results = bilibili_service.search(keyword, page=1, page_size=3)
            assert len(results) > 0, f"关键词'{keyword}'应返回结果"

    def test_search_result_content(self, bilibili_service):
        """测试搜索结果内容完整性"""
        results = bilibili_service.search("Python教程", page=1, page_size=5)

        for item in results:
            assert item.title, f"标题不应为空"
            assert item.author, f"作者不应为空"
            assert item.url, f"URL不应为空"
            assert item.id, f"ID不应为空"
