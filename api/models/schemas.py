"""
Pydantic数据模型定义
"""
from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
import time


T = TypeVar('T')


# ============ 基础响应模型 ============

class PaginationInfo(BaseModel):
    """分页信息"""
    page: int = 1
    page_size: int = 20
    total: Optional[int] = None
    has_more: bool = False


class ErrorDetail(BaseModel):
    """错误详情"""
    field: Optional[str] = None
    message: str


class ErrorInfo(BaseModel):
    """错误信息"""
    type: str
    details: Optional[List[ErrorDetail]] = None


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    success: bool = True
    code: int = 200
    message: str = "success"
    platform: Optional[str] = None
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))
    data: Optional[T] = None
    pagination: Optional[PaginationInfo] = None
    error: Optional[ErrorInfo] = None


# ============ 视频数据模型 ============

class VideoStats(BaseModel):
    """视频统计数据"""
    view: int = 0
    like: int = 0
    coin: int = 0
    favorite: int = 0
    share: int = 0
    reply: int = 0


class VideoItem(BaseModel):
    """视频列表项"""
    bvid: str
    title: str
    description: str = ""
    author: str
    author_id: int = 0
    play_count: int = 0
    like_count: int = 0
    duration: str = ""
    pubdate: str = ""
    cover_url: str = ""
    video_url: str
    tags: List[str] = []


class VideoDetail(BaseModel):
    """视频详情"""
    bvid: str
    title: str
    description: str = ""
    owner: str = ""
    pubdate: int = 0
    duration: int = 0
    stats: VideoStats
    tags: List[str] = []
    cover: str = ""
    url: str


class VideoSummaryInfo(BaseModel):
    """视频摘要信息"""
    title: str
    author: str
    description: str
    duration: int
    stats: VideoStats
    tags: List[str]
    cover: str
    url: str


class VideoSummary(BaseModel):
    """视频总结"""
    video_info: VideoSummaryInfo
    subtitle_available: bool
    subtitle_preview: Optional[str] = None


class SearchData(BaseModel):
    """搜索结果数据"""
    videos: List[VideoItem]


# ============ 通用内容模型（多平台） ============

class ContentStats(BaseModel):
    """通用内容统计数据"""
    play_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    collect_count: int = 0


class ContentItem(BaseModel):
    """通用内容项（支持多平台）"""
    id: str = Field(..., description="内容ID")
    title: str
    description: str = ""
    author: str
    author_id: str = ""
    cover_url: str = ""
    url: str
    platform: str = Field(..., description="平台标识: bilibili, douyin, xiaohongshu")
    # 统计数据
    stats: ContentStats = ContentStats()
    # 元数据
    tags: List[str] = []
    publish_time: str = ""
    duration: str = ""
    content_type: str = Field("video", description="内容类型: video, note, article")


class MultiSearchData(BaseModel):
    """多平台搜索结果数据"""
    items: List[ContentItem]
    platform: str


class PlatformInfo(BaseModel):
    """平台信息"""
    id: str
    name: str
    available: bool
    icon: Optional[str] = None


class PlatformsData(BaseModel):
    """平台列表数据"""
    platforms: List[PlatformInfo]


# ============ 请求参数模型 ============

class SearchParams(BaseModel):
    """搜索参数"""
    keyword: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    page: int = Field(1, ge=1, le=50, description="页码")
    page_size: int = Field(20, ge=1, le=50, description="每页数量")
    order: str = Field("totalrank", description="排序方式")
    platform: str = Field("bilibili", description="平台标识")
