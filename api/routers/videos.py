"""
视频详情路由
"""
from fastapi import APIRouter, HTTPException, Depends
import re

from ..models.schemas import ApiResponse, VideoDetail, VideoSummary
from ..services.bilibili_service import BilibiliService
from ..config import settings

router = APIRouter()


def get_bilibili_service():
    """获取Bilibili服务实例"""
    return BilibiliService(settings.BILIBILI_SESSDATA)


@router.get("/videos/{bvid}", response_model=ApiResponse[VideoDetail])
async def get_video_detail(
    bvid: str,
    service: BilibiliService = Depends(get_bilibili_service)
):
    """
    获取视频详情

    - **bvid**: 视频BV号（如 BV1xx411c7mD）
    """
    # 验证BV号格式
    if not re.match(r"^BV[a-zA-Z0-9]+$", bvid):
        raise HTTPException(status_code=400, detail="无效的BV号格式，应以BV开头")

    detail = service.get_video_detail(bvid)

    if "error" in detail:
        raise HTTPException(status_code=404, detail=detail["error"])

    return ApiResponse(
        success=True,
        code=200,
        message="success",
        platform="bilibili",
        data=VideoDetail(**detail)
    )


@router.get("/videos/{bvid}/summary", response_model=ApiResponse[VideoSummary])
async def get_video_summary(
    bvid: str,
    service: BilibiliService = Depends(get_bilibili_service)
):
    """
    获取视频总结（包含字幕预览）

    - **bvid**: 视频BV号（如 BV1xx411c7mD）
    """
    # 验证BV号格式
    if not re.match(r"^BV[a-zA-Z0-9]+$", bvid):
        raise HTTPException(status_code=400, detail="无效的BV号格式，应以BV开头")

    summary = service.get_video_summary(bvid)

    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])

    return ApiResponse(
        success=True,
        code=200,
        message="success",
        platform="bilibili",
        data=VideoSummary(**summary)
    )
