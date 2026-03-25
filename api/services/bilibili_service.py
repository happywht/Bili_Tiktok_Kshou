"""
Bilibili服务层 - 封装业务逻辑
"""
import sys
import os
from typing import List, Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from bilibili_search import BilibiliSearchAgent, BilibiliVideo
from ..models.schemas import VideoItem, VideoDetail, VideoSummary, VideoSummaryInfo, VideoStats
from .base import PlatformService, PlatformType, ContentItem


class BilibiliService(PlatformService):
    """B站服务封装"""

    platform = PlatformType.BILIBILI

    def __init__(self, sessdata: str = None):
        self.agent = BilibiliSearchAgent(sessdata=sessdata)

    def search_videos(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        order: str = "totalrank"
    ) -> List[Dict[str, Any]]:
        """
        搜索视频

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            order: 排序方式

        Returns:
            视频列表
        """
        videos = self.agent.search_videos_sync(
            keyword=keyword,
            page=page,
            page_size=page_size,
            order=order
        )

        return [self._video_to_dict(v) for v in videos]

    def search(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        **kwargs
    ) -> List[ContentItem]:
        """
        实现基类的搜索方法

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            **kwargs: 其他参数（如order排序方式）

        Returns:
            ContentItem列表
        """
        order = kwargs.get('order', 'totalrank')
        videos = self.search_videos(keyword, page, page_size, order)

        # 转换为 ContentItem 列表
        items = []
        for v in videos:
            items.append(ContentItem(
                id=v.get('bvid', ''),
                title=v.get('title', ''),
                author=v.get('author', ''),
                cover_url=v.get('cover_url', ''),
                url=v.get('video_url', ''),
                platform=PlatformType.BILIBILI,
                play_count=v.get('play_count', 0),
                like_count=v.get('like_count', 0),
                comment_count=0,
                share_count=0,
                description=v.get('description', ''),
                tags=v.get('tags', []),
                publish_time=str(v.get('pubdate', '')),
                duration=v.get('duration', ''),
            ))
        return items

    def get_detail(self, content_id: str) -> Dict[str, Any]:
        """
        实现基类的获取详情方法

        Args:
            content_id: 内容ID（BV号）

        Returns:
            详情数据
        """
        return self.get_video_detail(content_id)

    def get_video_detail(self, bvid: str) -> Dict[str, Any]:
        """
        获取视频详情

        Args:
            bvid: 视频BV号

        Returns:
            视频详情
        """
        detail = self.agent.get_video_detail(bvid)

        if "error" in detail:
            return detail

        # 转换为标准格式
        return {
            "bvid": detail.get("bvid", bvid),
            "title": detail.get("title", ""),
            "description": detail.get("description", ""),
            "owner": detail.get("owner", ""),
            "pubdate": detail.get("pubdate", 0),
            "duration": detail.get("duration", 0),
            "stats": {
                "view": detail.get("view", 0),
                "like": detail.get("like", 0),
                "coin": detail.get("coin", 0),
                "favorite": detail.get("favorite", 0),
                "share": detail.get("share", 0),
                "reply": detail.get("reply", 0),
            },
            "tags": detail.get("tags", []),
            "cover": detail.get("pic", ""),
            "url": f"https://www.bilibili.com/video/{bvid}",
        }

    def get_video_summary(self, bvid: str) -> Dict[str, Any]:
        """
        获取视频总结

        Args:
            bvid: 视频BV号

        Returns:
            视频总结
        """
        summary = self.agent.summarize_video(bvid)

        if "error" in summary:
            return summary

        video_info = summary.get("video_info", {})
        stats = video_info.get("stats", {})

        return {
            "video_info": {
                "title": video_info.get("title", ""),
                "author": video_info.get("author", ""),
                "description": video_info.get("description", ""),
                "duration": video_info.get("duration", 0),
                "stats": {
                    "view": stats.get("view", 0),
                    "like": stats.get("like", 0),
                    "coin": stats.get("coin", 0),
                    "favorite": stats.get("favorite", 0),
                    "share": stats.get("share", 0),
                    "reply": stats.get("reply", 0),
                },
                "tags": video_info.get("tags", []),
                "cover": video_info.get("cover", ""),
                "url": video_info.get("url", ""),
            },
            "subtitle_available": summary.get("subtitle_available", False),
            "subtitle_preview": summary.get("subtitle_preview"),
        }

    def _video_to_dict(self, video: BilibiliVideo) -> Dict[str, Any]:
        """将BilibiliVideo对象转换为字典"""
        return {
            "bvid": video.bvid,
            "title": video.title,
            "description": video.description,
            "author": video.author,
            "author_id": video.author_id,
            "play_count": video.play_count,
            "like_count": video.like_count,
            "duration": video.duration,
            "pubdate": video.pubdate,
            "cover_url": video.cover_url,
            "video_url": video.video_url,
            "tags": video.tags,
        }
