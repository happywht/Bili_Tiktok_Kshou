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


class BilibiliService:
    """B站服务封装"""

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
