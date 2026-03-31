"""
搜索路由 - 支持多平台
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from typing import Optional, List
import asyncio
import httpx
import urllib.parse

from ..models.schemas import (
    ApiResponse, SearchData, PaginationInfo, VideoItem,
    ContentItem, ContentStats, MultiSearchData, PlatformInfo, PlatformsData
)
from ..services.factory import ServiceFactory
from ..services.base import PlatformType
from ..services.video_digest_service import video_digest_service
from ..config import settings
from ..exceptions import (
    PlatformError,
    CookieExpiredError,
    BilibiliCookieExpiredError,
    RateLimitError,
    PlatformNotAvailableError,
    BilibiliNotAvailableError,
    ContentNotFoundError,
    InvalidParameterError,
    NetworkError,
    TimeoutError,
)

router = APIRouter()


# ============ 平台列表 ============

@router.get("/platforms", response_model=ApiResponse[PlatformsData])
async def get_platforms():
    """
    获取支持的平台列表

    返回所有可用平台及其状态
    """
    try:
        platforms = ServiceFactory.get_supported_platforms()

        # 添加图标信息
        platform_icons = {
            "bilibili": "📺",
        }

        platform_infos = [
            PlatformInfo(
                id=p["id"],
                name=p["name"],
                available=p["available"],
                icon=platform_icons.get(p["id"])
            )
            for p in platforms
        ]

        return ApiResponse(
            success=True,
            code=200,
            message="success",
            data=PlatformsData(platforms=platform_infos)
        )
    except Exception as e:
        raise PlatformNotAvailableError(
            message="无法获取平台列表",
            original_error=e
        )


# ============ 多平台搜索 ============

@router.get("/search", response_model=ApiResponse[MultiSearchData])
async def search_videos(
    keyword: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    page: int = Query(1, ge=1, le=50, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    platform: str = Query("bilibili", description="平台标识: bilibili"),
    order: str = Query("totalrank", description="排序方式"),
):
    """
    多平台视频/内容搜索

    - **keyword**: 搜索关键词（必填，1-100字符）
    - **page**: 页码（1-50，默认1）
    - **page_size**: 每页数量（1-50，默认20）
    - **platform**: 平台标识
        - bilibili: 哔哩哔哩
    - **order**: 排序方式（各平台支持不同）
    """
    # 验证平台
    valid_platforms = ["bilibili"]
    if platform not in valid_platforms:
        raise InvalidParameterError(
            message=f"不支持的平台: {platform}",
            suggestion=f"请使用以下平台之一: {', '.join(valid_platforms)}",
            details={"valid_platforms": valid_platforms}
        )

    # 获取平台服务和配置
    try:
        config = settings.get_platform_config(platform)
        service = ServiceFactory.get_service(platform, config)
    except ValueError as e:
        raise PlatformNotAvailableError(
            message=f"平台 {platform} 不可用",
            suggestion="请检查平台配置或稍后重试",
            original_error=e
        )

    try:
        # 执行搜索（同步方法，用线程池避免阻塞事件循环）
        items = await asyncio.to_thread(
            service.search,
            keyword=keyword,
            page=page,
            page_size=page_size,
            order=order
        )

        # 转换为通用内容模型
        content_items = []
        for item in items:
            # B站特定转换
            content_items.append(ContentItem(
                id=item.bvid if hasattr(item, 'bvid') else item.id,
                title=item.title,
                description=getattr(item, 'description', ''),
                author=item.author,
                author_id=str(getattr(item, 'author_id', '')),
                cover_url=getattr(item, 'cover_url', ''),
                url=item.video_url if hasattr(item, 'video_url') else item.url,
                platform=platform,
                stats=ContentStats(
                    play_count=getattr(item, 'play_count', 0),
                    like_count=getattr(item, 'like_count', 0),
                    comment_count=0,
                    share_count=0,
                ),
                tags=getattr(item, 'tags', []),
                publish_time=str(getattr(item, 'pubdate', '')),
                duration=getattr(item, 'duration', ''),
                content_type="video"
            ))

        return ApiResponse(
            success=True,
            code=200,
            message="success",
            platform=platform,
            data=MultiSearchData(items=content_items, platform=platform),
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                has_more=len(items) == page_size
            )
        )

    except CookieExpiredError:
        # 重新抛出Cookie过期异常
        raise
    except RateLimitError:
        # 重新抛出速率限制异常
        raise
    except PlatformError:
        # 重新抛出平台异常
        raise
    except Exception as e:
        error_msg = str(e)
        # 检测并转换为适当的异常类型
        if "SESSDATA" in error_msg or "-412" in error_msg or "-101" in error_msg:
            raise BilibiliCookieExpiredError(
                message="B站登录状态已过期",
                original_error=e
            )
        if "429" in error_msg or "rate limit" in error_msg.lower():
            raise RateLimitError(
                message="请求过于频繁",
                original_error=e
            )
        if "timeout" in error_msg.lower():
            raise TimeoutError(
                message="请求超时",
                original_error=e
            )
        if "connection" in error_msg.lower() or "network" in error_msg.lower():
            raise NetworkError(
                message="网络连接失败",
                original_error=e
            )
        # 默认抛出通用平台错误
        raise PlatformError(
            message=f"搜索失败: {error_msg}",
            original_error=e
        )


# ============ B站搜索（兼容旧接口） ============

@router.get("/search/bilibili")
async def search_bilibili(
    keyword: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    page: int = Query(1, ge=1, le=50, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    order: str = Query("totalrank", description="排序方式"),
):
    """
    B站视频搜索（兼容旧接口）

    - **keyword**: 搜索关键词（必填，1-100字符）
    - **page**: 页码（1-50，默认1）
    - **page_size**: 每页数量（1-50，默认20）
    - **order**: 排序方式
    """
    # 直接调用新的多平台搜索接口
    return await search_videos(
        keyword=keyword,
        page=page,
        page_size=page_size,
        platform="bilibili",
        order=order
    )


# ============ 图片代理 ============

@router.get("/proxy-image")
async def proxy_image(
    url: str = Query(..., description="图片URL")
):
    """
    代理图片请求（绕过防盗链）

    - **url**: 原始图片URL（需要URL编码）
    """
    try:
        # URL 解码
        decoded_url = urllib.parse.unquote(url)

        # 处理无协议的 URL
        if decoded_url.startswith('//'):
            decoded_url = 'https:' + decoded_url

        # 允许的图片域名
        allowed_domains = [
            # B站
            'i0.hdslb.com', 'i1.hdslb.com', 'i2.hdslb.com',
            'hdslb.com', 'archive.biliimg.com', 'bili.bilivideo.com',
        ]
        parsed = urllib.parse.urlparse(decoded_url)

        # 检查域名是否在允许列表中
        is_allowed = any(domain in parsed.netloc for domain in allowed_domains)
        if not is_allowed:
            raise InvalidParameterError(
                message=f"不允许代理该域名的图片",
                suggestion="仅支持B站的图片",
                details={"netloc": parsed.netloc}
            )

        # 根据域名设置 Referer
        referer_map = {
            'hdslb.com': 'https://www.bilibili.com/',
            'biliimg.com': 'https://www.bilibili.com/',
            'bilivideo.com': 'https://www.bilibili.com/',
        }
        referer = 'https://www.bilibili.com/'  # 默认
        for domain, ref in referer_map.items():
            if domain in parsed.netloc:
                referer = ref
                break

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                decoded_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': referer,
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                },
                follow_redirects=True
            )

            if response.status_code == 404:
                raise ContentNotFoundError(
                    message="图片不存在",
                    details={"url": decoded_url}
                )

            if response.status_code != 200:
                raise NetworkError(
                    message=f"图片获取失败: HTTP {response.status_code}",
                    details={"status_code": response.status_code}
                )

            content_type = response.headers.get('content-type', 'image/jpeg')

            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    'Cache-Control': 'public, max-age=86400',  # 缓存1天
                    'Access-Control-Allow-Origin': '*',
                }
            )

    except httpx.TimeoutException:
        raise TimeoutError(
            message="图片获取超时",
            suggestion="请稍后重试"
        )
    except httpx.RequestError as e:
        raise NetworkError(
            message=f"图片获取失败: {str(e)}",
            original_error=e
        )
    except PlatformError:
        raise
    except Exception as e:
        raise PlatformError(
            message=f"图片代理失败: {str(e)}",
            original_error=e
        )


# ============ 综合视频推送 ============

@router.post("/digest", response_model=ApiResponse[dict])
async def create_video_digest(
    keywords: List[str] = Query(..., min_length=2, max_length=5, description="搜索关键词（2-5个）"),
    per_keyword: int = Query(5, ge=1, le=10, description="每个关键词获取的视频数量"),
    min_play: int = Query(10000, ge=0, description="最小播放量筛选"),
    min_like: int = Query(500, ge=0, description="最小点赞数筛选"),
    max_videos: int = Query(20, ge=5, le=50, description="最终保留的最大视频数"),
    sort_by: str = Query("score", description="排序方式: score(综合)/play(播放)/like(点赞)"),
):
    """
    综合视频推送

    根据多个关键词检索B站视频，筛选优质内容，生成Markdown格式推送。

    - **keywords**: 搜索关键词（必填，2-5个，建议2-3个）
    - **per_keyword**: 每个关键词获取的视频数量（1-10，默认5）
    - **min_play**: 最小播放量筛选（默认10000）
    - **min_like**: 最小点赞数筛选（默认500）
    - **max_videos**: 最终保留的最大视频数（5-50，默认20）
    - **sort_by**: 排序方式
        - score: 综合评分（默认，播放量×0.5 + 点赞×10 + 评论×5）
        - play: 按播放量排序
        - like: 按点赞数排序

    返回Markdown格式的视频推送内容。
    """
    try:
        # 验证排序方式
        valid_sort = ["score", "play", "like"]
        if sort_by not in valid_sort:
            raise InvalidParameterError(
                message=f"不支持的排序方式: {sort_by}",
                suggestion=f"请使用以下排序方式之一: {', '.join(valid_sort)}"
            )

        # 创建推送（同步操作，用线程池）
        result = await asyncio.to_thread(
            video_digest_service.create_digest,
            keywords=keywords,
            per_keyword=per_keyword,
            min_play=min_play,
            min_like=min_like,
            max_videos=max_videos,
            sort_by=sort_by
        )

        return ApiResponse(
            success=True,
            code=200,
            message="综合推送生成成功",
            data=result
        )

    except ValueError as e:
        raise InvalidParameterError(message=str(e))
    except Exception as e:
        error_msg = str(e)
        if "登录" in error_msg or "SESSDATA" in error_msg:
            raise BilibiliCookieExpiredError(
                message="B站登录状态可能已过期",
                original_error=e
            )
        if "429" in error_msg or "rate limit" in error_msg.lower():
            raise RateLimitError(
                message="请求过于频繁",
                original_error=e
            )
        if "timeout" in error_msg.lower():
            raise TimeoutError(
                message="搜索超时",
                original_error=e
            )
        raise PlatformError(
            message=f"综合推送生成失败: {error_msg}",
            original_error=e
        )

