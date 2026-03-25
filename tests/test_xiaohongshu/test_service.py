"""
小红书服务测试

测试小红书搜索功能的核心测试用例

注意：小红书搜索需要安装 xiaohongshu-cli 或使用浏览器自动化
"""
import pytest
from api.services.base import PlatformType


@pytest.mark.xiaohongshu
@pytest.mark.integration
class TestXiaohongshuService:
    """小红书服务测试类"""

    def test_service_initialization(self, xiaohongshu_service):
        """测试服务初始化"""
        assert xiaohongshu_service is not None
        assert xiaohongshu_service.platform == PlatformType.XIAOHONGSHU

    def test_cli_availability_check(self, xiaohongshu_service):
        """测试CLI可用性检查"""
        # 这个测试检查CLI是否已安装
        # 结果可能是True或False
        assert isinstance(xiaohongshu_service._cli_available, bool)

    @pytest.mark.slow
    def test_search_returns_results(self, xiaohongshu_service, sample_keyword):
        """测试搜索返回结果"""
        results = xiaohongshu_service.search(sample_keyword, page=1, page_size=10)

        assert results is not None
        assert isinstance(results, list)

        # 如果CLI未安装，可能返回空列表
        if not xiaohongshu_service._cli_available and len(results) == 0:
            pytest.skip("xiaohongshu-cli未安装，浏览器自动化可能失败")

    @pytest.mark.slow
    def test_search_result_structure(self, xiaohongshu_service, sample_keyword):
        """测试搜索结果结构"""
        results = xiaohongshu_service.search(sample_keyword, page=1, page_size=5)

        if not results:
            pytest.skip("小红书搜索未返回结果，跳过结构验证")

        item = results[0]
        assert item.title, "结果应有标题"
        assert item.platform == PlatformType.XIAOHONGSHU
        assert item.url, "结果应有URL"


@pytest.mark.xiaohongshu
@pytest.mark.slow
class TestXiaohongshuServiceExtended:
    """小红书服务扩展测试"""

    @pytest.mark.skip(reason="需要有效的笔记ID")
    def test_get_detail(self, xiaohongshu_service):
        """测试获取笔记详情"""
        # 需要一个有效的笔记ID
        note_id = "example_note_id"
        detail = xiaohongshu_service.get_detail(note_id)

        if 'error' in detail:
            pytest.skip(f"获取详情失败: {detail.get('error')}")

        assert detail is not None

    @pytest.mark.skip(reason="需要有效的笔记ID")
    def test_get_comments(self, xiaohongshu_service):
        """测试获取评论"""
        note_id = "example_note_id"
        comments = xiaohongshu_service.get_comments(note_id)

        assert isinstance(comments, list)


@pytest.mark.xiaohongshu
class TestXiaohongshuServiceUtilities:
    """小红书服务工具函数测试"""

    def test_parse_count(self, xiaohongshu_service):
        """测试数字解析"""
        # 测试各种格式
        assert xiaohongshu_service.parse_count("1.2万") == 12000
        assert xiaohongshu_service.parse_count("100") == 100
        assert xiaohongshu_service.parse_count(1000) == 1000
