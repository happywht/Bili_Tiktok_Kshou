"""
综合视频推送服务

根据多个关键词检索B站视频，筛选优质内容，整合成Markdown格式推送。
"""
import asyncio
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..config import settings
from .factory import get_bilibili_service
from .base import ContentItem


class VideoDigestService:
    """视频综合推送服务"""

    def __init__(self):
        self.bilibili_service = get_bilibili_service(sessdata=settings.BILIBILI_SESSDATA)

    def search_by_keywords(self, keywords: List[str], per_keyword: int = 5) -> List[ContentItem]:
        """
        根据多个关键词搜索视频

        Args:
            keywords: 关键词列表
            per_keyword: 每个关键词获取的视频数量

        Returns:
            所有搜索结果的视频列表
        """
        all_videos = []
        seen_bvids = set()

        for keyword in keywords:
            try:
                videos = self.bilibili_service.search(
                    keyword=keyword,
                    page=1,
                    page_size=per_keyword,
                    order="totalrank"  # 综合排序
                )

                # 去重（按BV号）
                for video in videos:
                    bvid = getattr(video, 'bvid', None) or video.id
                    if bvid and bvid not in seen_bvids:
                        seen_bvids.add(bvid)
                        all_videos.append(video)

            except Exception as e:
                print(f"搜索关键词 '{keyword}' 失败: {e}")
                continue

        return all_videos

    def filter_quality_videos(self, videos: List[ContentItem], min_play: int = 10000,
                              min_like: int = 500) -> List[ContentItem]:
        """
        筛选优质视频

        Args:
            videos: 视频列表
            min_play: 最小播放量
            min_like: 最小点赞数

        Returns:
            筛选后的优质视频列表
        """
        filtered = []
        for video in videos:
            play_count = video.play_count or 0
            like_count = video.like_count or 0

            # 筛选条件：播放量达标，或者点赞比例较高
            if play_count >= min_play or (play_count >= 1000 and like_count / max(play_count, 1) >= 0.1):
                filtered.append(video)

        return filtered

    def sort_videos(self, videos: List[ContentItem], sort_by: str = "score") -> List[ContentItem]:
        """
        对视频进行排序

        Args:
            videos: 视频列表
            sort_by: 排序方式
                - score: 综合评分（默认）
                - play: 播放量
                - like: 点赞数

        Returns:
            排序后的视频列表
        """
        def calculate_score(video: ContentItem) -> float:
            """计算综合评分"""
            play = video.play_count or 0
            like = video.like_count or 0
            comment = video.comment_count or 0

            # 综合评分公式：播放量*0.5 + 点赞*10 + 评论*5
            # 这样可以让新视频（点赞比例高）也有机会
            score = (play * 0.5) + (like * 10) + (comment * 5)
            return score

        if sort_by == "score":
            videos.sort(key=calculate_score, reverse=True)
        elif sort_by == "play":
            videos.sort(key=lambda v: v.play_count or 0, reverse=True)
        elif sort_by == "like":
            videos.sort(key=lambda v: v.like_count or 0, reverse=True)

        return videos

    def generate_markdown_digest(self, videos: List[ContentItem], keywords: List[str],
                                  title: str = "📺 B站精选视频推送",
                                  max_videos: int = 20) -> str:
        """
        生成Markdown格式的视频推送

        Args:
            videos: 视频列表
            keywords: 搜索关键词
            title: 推送标题
            max_videos: 最大视频数量

        Returns:
            Markdown格式的推送内容
        """
        # 限制数量
        videos = videos[:max_videos]

        # 当前时间
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")

        # 构建Markdown
        md_lines = [
            f"# {title}",
            "",
            f"**生成时间**: {now}",
            f"**搜索关键词**: {' | '.join(keywords)}",
            f"**视频数量**: {len(videos)}",
            "",
            "---",
            "",
            f"## 📋 目录",
        ]

        # 添加目录
        for i, video in enumerate(videos[:15], 1):
            video_title = video.title[:30] + "..." if len(video.title) > 30 else video.title
            md_lines.append(f"{i}. [{video_title}](#视频{i})")

        md_lines.extend(["", "---", ""])

        # 添加视频详情
        for i, video in enumerate(videos, 1):
            video_title = video.title
            bvid = video.bvid if hasattr(video, 'bvid') else video.id
            video_url = video.video_url if hasattr(video, 'video_url') else video.url
            author = video.author
            cover_url = video.cover_url
            play_count = video.play_count or 0
            like_count = video.like_count or 0
            comment_count = video.comment_count or 0
            duration = getattr(video, 'duration', '')
            pubdate = getattr(video, 'pubdate', '')
            description = video.description[:150] + "..." if len(video.description) > 150 else video.description

            md_lines.extend([
                f"## 视频{i}",
                "",
                f"### [{video_title}]({video_url})",
                "",
                f"**UP主**: {author}",
            ])

            if duration:
                md_lines.append(f"**时长**: {duration}")

            if pubdate:
                md_lines.append(f"**发布时间**: {pubdate}")

            md_lines.extend([
                "",
                "### 📊 数据统计",
                f"- 👀 播放: {play_count:,}",
                f"- 👍 点赞: {like_count:,}",
            ])

            if comment_count > 0:
                md_lines.append(f"- 💬 评论: {comment_count:,}")

            md_lines.extend(["", "### 📝 视频简介"])

            if description:
                md_lines.append(description)
            else:
                md_lines.append("暂无简介")

            if cover_url:
                md_lines.extend([
                    "",
                    f"![封面]({cover_url})",
                ])

            # 添加B站直链
            md_lines.extend([
                "",
                f"**🔗 直链**: https://www.bilibili.com/video/{bvid}",
                "",
                "---",
                "",
            ])

        # 添加结尾
        md_lines.extend([
            "## 📌 说明",
            "",
            "- 本推送基于B站API自动生成",
            f"- 筛选标准: 播放量≥1万 或 点赞比例≥10%",
            "- 按综合评分排序（播放量、点赞、评论综合）",
            "- 如有问题或建议，请联系管理员",
            "",
            "---",
            "",
            f"*本推送由 VideoHub 自动生成于 {now}*",
        ])

        return "\n".join(md_lines)

    def create_digest(self, keywords: List[str], per_keyword: int = 5,
                      min_play: int = 10000, min_like: int = 500,
                      max_videos: int = 20, sort_by: str = "score") -> Dict[str, Any]:
        """
        创建综合视频推送

        Args:
            keywords: 关键词列表（2-3个）
            per_keyword: 每个关键词获取的视频数量
            min_play: 最小播放量筛选
            min_like: 最小点赞数筛选
            max_videos: 最终保留的最大视频数
            sort_by: 排序方式（score/play/like）

        Returns:
            推送结果字典
        """
        if len(keywords) < 2:
            raise ValueError("至少需要提供2个关键词")
        if len(keywords) > 5:
            raise ValueError("最多支持5个关键词")

        # 1. 搜索视频
        videos = self.search_by_keywords(keywords, per_keyword)

        # 2. 筛选优质视频
        quality_videos = self.filter_quality_videos(videos, min_play, min_like)

        # 3. 排序
        sorted_videos = self.sort_videos(quality_videos, sort_by)

        # 4. 生成Markdown
        markdown_content = self.generate_markdown_digest(
            sorted_videos,
            keywords,
            f"📺 B站精选视频推送 - {' & '.join(keywords[:2])}",
            max_videos
        )

        return {
            "keywords": keywords,
            "total_found": len(videos),
            "after_filter": len(quality_videos),
            "final_count": len(sorted_videos[:max_videos]),
            "markdown": markdown_content,
            "videos": [
                {
                    "bvid": v.bvid if hasattr(v, 'bvid') else v.id,
                    "title": v.title,
                    "author": v.author,
                    "play_count": v.play_count,
                    "like_count": v.like_count,
                    "url": v.video_url if hasattr(v, 'video_url') else v.url,
                }
                for v in sorted_videos[:max_videos]
            ]
        }


# 创建服务实例
video_digest_service = VideoDigestService()
