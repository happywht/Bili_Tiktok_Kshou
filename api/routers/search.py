"""
搜索路由
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import Response, StreamingResponse
from typing import Optional
import httpx
import urllib.parse

from ..models.schemas import ApiResponse, SearchData, PaginationInfo, VideoItem
from ..services.bilibili_service import BilibiliService
from ..config import settings

router = APIRouter()


def get_bilibili_service():
    """获取Bilibili服务实例"""
    return BilibiliService(settings.BILIBILI_SESSDATA)


@router.get("/search", response_model=ApiResponse[SearchData])
async def search_videos(
    keyword: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    page: int = Query(1, ge=1, le=50, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
    order: str = Query(
        "totalrank",
        regex="^(totalrank|click|pubdate|dm)$",
        description="排序方式: totalrank(综合), click(播放量), pubdate(发布时间), dm(弹幕)"
    ),
    platform: str = Query("bilibili", description="平台标识(当前仅支持bilibili)"),
    service: BilibiliService = Depends(get_bilibili_service)
):
    """
    搜索视频

    - **keyword**: 搜索关键词（必填，1-100字符）
    - **page**: 页码（1-50，默认1）
    - **page_size**: 每页数量（1-50，默认20）
    - **order**: 排序方式
        - totalrank: 综合排序
        - click: 播放量排序
        - pubdate: 发布时间排序
        - dm: 弹幕数排序
    - **platform**: 平台标识（当前仅支持bilibili）
    """
    try:
        videos = service.search_videos(
            keyword=keyword,
            page=page,
            page_size=page_size,
            order=order
        )

        video_items = [VideoItem(**video) for video in videos]

        return ApiResponse(
            success=True,
            code=200,
            message="success",
            platform=platform,
            data=SearchData(videos=video_items),
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                has_more=len(videos) == page_size
            )
        )

    except Exception as e:
        error_msg = str(e)
        if "SESSDATA" in error_msg or "-412" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="需要登录认证，请配置BILIBILI_SESSDATA环境变量"
            )
        raise HTTPException(status_code=500, detail=f"搜索失败: {error_msg}")


@router.get("/proxy-image")
async def proxy_image(
    url: str = Query(..., description="图片URL")
):
    """
    代理图片请求（绕过B站防盗链）

    - **url**: 原始图片URL（需要URL编码）
    """
    try:
        # URL 解码
        decoded_url = urllib.parse.unquote(url)

        # 处理无协议的 URL（如 //i1.hdslb.com/...）
        if decoded_url.startswith('//'):
            decoded_url = 'https:' + decoded_url

        # 验证 URL 是否为 B站图片域名
        allowed_domains = ['i0.hdslb.com', 'i1.hdslb.com', 'i2.hdslb.com',
                          'hdslb.com', 'archive.biliimg.com', 'bili.bilivideo.com']
        parsed = urllib.parse.urlparse(decoded_url)

        # 检查域名是否在允许列表中
        is_allowed = any(domain in parsed.netloc for domain in allowed_domains)
        if not is_allowed:
            raise HTTPException(status_code=400, detail=f"仅允许代理B站图片, netloc: {parsed.netloc}")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                decoded_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://www.bilibili.com/',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                },
                follow_redirects=True
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"图片获取失败: HTTP {response.status_code}")

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
        raise HTTPException(status_code=504, detail="图片获取超时")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"图片获取失败: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代理失败: {str(e)}")
