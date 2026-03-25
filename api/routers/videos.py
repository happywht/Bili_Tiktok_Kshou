"""
视频详情路由
"""
from fastapi import APIRouter, Depends
import re

from ..models.schemas import ApiResponse, VideoDetail, VideoSummary
from ..services.bilibili_service import BilibiliService
from ..config import settings
from ..exceptions import (
    InvalidParameterError,
    ContentNotFoundError,
    BilibiliCookieExpiredError,
    BilibiliNotAvailableError,
    PlatformError,
)

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
        raise InvalidParameterError(
            message="无效的BV号格式",
            suggestion="BV号应以BV开头，如: BV1xx411c7mD",
            details={"bvid": bvid}
        )

    try:
        detail = service.get_video_detail(bvid)

        if "error" in detail:
            error_msg = detail["error"]
            # 根据错误信息判断异常类型
            if "不存在" in error_msg or "删除" in error_msg:
                raise ContentNotFoundError(
                    message=f"视频 {bvid} 不存在或已被删除",
                    details={"bvid": bvid}
                )
            if "登录" in error_msg or "SESSDATA" in error_msg:
                raise BilibiliCookieExpiredError(
                    message="B站登录状态已过期",
                    original_error=Exception(error_msg)
                )
            # 其他错误
            raise PlatformError(
                message=error_msg,
                code=404,
                suggestion="请检查BV号是否正确"
            )

        return ApiResponse(
            success=True,
            code=200,
            message="success",
            platform="bilibili",
            data=VideoDetail(**detail)
        )

    except InvalidParameterError:
        raise
    except ContentNotFoundError:
        raise
    except BilibiliCookieExpiredError:
        raise
    except PlatformError:
        raise
    except Exception as e:
        error_msg = str(e)
        if "SESSDATA" in error_msg or "-412" in error_msg or "-101" in error_msg:
            raise BilibiliCookieExpiredError(
                message="B站登录状态已过期",
                original_error=e
            )
        raise BilibiliNotAvailableError(
            message=f"获取视频详情失败: {error_msg}",
            original_error=e
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
        raise InvalidParameterError(
            message="无效的BV号格式",
            suggestion="BV号应以BV开头，如: BV1xx411c7mD",
            details={"bvid": bvid}
        )

    try:
        summary = service.get_video_summary(bvid)

        if "error" in summary:
            error_msg = summary["error"]
            # 根据错误信息判断异常类型
            if "不存在" in error_msg or "删除" in error_msg:
                raise ContentNotFoundError(
                    message=f"视频 {bvid} 不存在或已被删除",
                    details={"bvid": bvid}
                )
            if "登录" in error_msg or "SESSDATA" in error_msg:
                raise BilibiliCookieExpiredError(
                    message="B站登录状态已过期",
                    original_error=Exception(error_msg)
                )
            # 其他错误
            raise PlatformError(
                message=error_msg,
                code=404,
                suggestion="请检查BV号是否正确或确认视频是否有字幕"
            )

        return ApiResponse(
            success=True,
            code=200,
            message="success",
            platform="bilibili",
            data=VideoSummary(**summary)
        )

    except InvalidParameterError:
        raise
    except ContentNotFoundError:
        raise
    except BilibiliCookieExpiredError:
        raise
    except PlatformError:
        raise
    except Exception as e:
        error_msg = str(e)
        if "SESSDATA" in error_msg or "-412" in error_msg or "-101" in error_msg:
            raise BilibiliCookieExpiredError(
                message="B站登录状态已过期",
                original_error=e
            )
        raise BilibiliNotAvailableError(
            message=f"获取视频总结失败: {error_msg}",
            original_error=e
        )
