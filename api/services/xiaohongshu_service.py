"""
小红书服务 - 基于 MediaCrawler 浏览器自动化实现

通过 MediaCrawler 桥接脚本，利用 Playwright 浏览器自动化完成小红书搜索。
桥接脚本处理浏览器启动、Cookie 管理、登录检查和 API 签名。

使用前须知:
1. 首次使用需运行登录流程（显示浏览器窗口扫码）
2. 登录状态会自动保存到 browser_data/ 目录
3. 后续搜索会自动复用已保存的登录态
"""
import subprocess
import sys
import os
import json
import logging
from typing import List, Dict, Any, Optional

from .base import PlatformService, PlatformType, ContentItem

logger = logging.getLogger(__name__)


class XiaohongshuService(PlatformService):
    """
    小红书搜索服务（基于 MediaCrawler）

    通过 subprocess 调用 MediaCrawler 桥接脚本完成搜索。
    """

    platform = PlatformType.XIAOHONGSHU

    def __init__(self, cookies: str = None, headless: bool = True):
        """
        初始化小红书服务

        Args:
            cookies: Cookie 字符串（桥接脚本通过浏览器自动管理）
            headless: 是否无头模式
        """
        self.cookies = cookies
        self.headless = headless
        self._bridge_path = self._resolve_bridge_path()

    @staticmethod
    def _resolve_bridge_path() -> str:
        """获取桥接脚本路径"""
        service_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(service_dir))
        return os.path.join(project_root, 'tools', 'mediacrawler_bridge.py')

    def search(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        **kwargs
    ) -> List[ContentItem]:
        """
        搜索小红书内容

        Args:
            keyword: 搜索关键词
            page: 页码（默认 1）
            page_size: 每页数量（默认 20）
            **kwargs: 额外参数

        Returns:
            ContentItem 列表
        """
        self.log_request("search", keyword=keyword, page=page, page_size=page_size)

        if not os.path.exists(self._bridge_path):
            raise FileNotFoundError(
                f"桥接脚本不存在: {self._bridge_path}。"
                f"请确保 tools/MediaCrawler 目录已克隆。"
            )

        timeout = kwargs.get('timeout', 150)

        cmd = [
            sys.executable,
            self._bridge_path,
            '--platform', 'xhs',
            '--keyword', keyword,
            '--max-count', str(page_size),
            '--page', str(page),
            '--timeout', str(timeout - 30),
        ]
        if self.headless:
            cmd.append('--headless')
        else:
            cmd.append('--no-headless')

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(self._bridge_path),
                encoding='utf-8',
                errors='replace',
            )
        except subprocess.TimeoutExpired:
            self.log_error("search", RuntimeError(f"搜索超时（{timeout}秒）"))
            raise RuntimeError(
                f"小红书搜索超时（{timeout}秒）。"
                f"浏览器启动可能较慢，请增大超时时间或确保 Playwright 已正确安装。"
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Python 解释器不存在: {sys.executable}")

        return self._parse_result(result)

    def _parse_result(self, result: subprocess.CompletedProcess) -> List[ContentItem]:
        """解析桥接脚本的输出"""
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            error_data = self._safe_json_parse(stderr or stdout)
            error_msg = error_data.get('error', f'进程退出码 {result.returncode}')
            suggestion = error_data.get('suggestion', '')
            msg = f"小红书搜索失败: {error_msg}"
            if suggestion:
                msg += f" ({suggestion})"
            self.log_error("search", RuntimeError(msg))
            raise RuntimeError(msg)

        data = self._safe_json_parse(stdout)
        if not data:
            self.log_error("search", RuntimeError("桥接脚本无输出"))
            raise RuntimeError("小红书搜索失败: 桥接脚本无有效输出")

        if not data.get('success', False):
            error_msg = data.get('error', '未知错误')
            suggestion = data.get('suggestion', '')
            msg = f"小红书搜索失败: {error_msg}"
            if suggestion:
                msg += f" ({suggestion})"
            self.log_error("search", RuntimeError(msg))
            raise RuntimeError(msg)

        items = data.get('data', [])
        logger.info(f"[XiaohongshuService] 搜索完成，获取 {len(items)} 条结果")

        return [self._to_content_item(item) for item in items]

    def _to_content_item(self, item: Dict) -> ContentItem:
        """将桥接脚本返回的数据转换为 ContentItem"""
        return ContentItem(
            id=item.get('id', ''),
            title=item.get('title', ''),
            description=item.get('description', ''),
            author=item.get('author', ''),
            cover_url=item.get('cover_url', ''),
            url=item.get('url', ''),
            platform=PlatformType.XIAOHONGSHU,
            play_count=0,
            like_count=int(item.get('like_count', 0) or 0),
            comment_count=int(item.get('comment_count', 0) or 0),
            share_count=int(item.get('share_count', 0) or 0),
            collect_count=int(item.get('collect_count', 0) or 0),
            tags=item.get('tags', []) or [],
            publish_time=item.get('publish_time', ''),
            duration=item.get('duration', ''),
            content_type=item.get('content_type', 'note'),
        )

    def get_detail(self, content_id: str) -> Dict[str, Any]:
        """获取内容详情（暂不实现）"""
        return {"id": content_id, "platform": "xiaohongshu", "detail": "暂不支持详情获取"}

    @staticmethod
    def _safe_json_parse(text: str) -> Optional[Dict]:
        """安全解析 JSON"""
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            for line in reversed(text.split('\n')):
                line = line.strip()
                if line.startswith('{'):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            return None

    @staticmethod
    def check_environment() -> Dict[str, Any]:
        """检查运行环境是否就绪"""
        bridge_path = XiaohongshuService._resolve_bridge_path()
        if not os.path.exists(bridge_path):
            return {"ready": False, "message": f"桥接脚本不存在: {bridge_path}"}

        cmd = [sys.executable, bridge_path, '--check']
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
                encoding='utf-8', errors='replace',
            )
            data = XiaohongshuService._safe_json_parse(result.stdout)
            if data:
                return {"ready": data.get('success', False), "message": data.get('message', '')}
            return {"ready": False, "message": f"环境检查失败: {result.stderr[:200]}"}
        except Exception as e:
            return {"ready": False, "message": str(e)}
