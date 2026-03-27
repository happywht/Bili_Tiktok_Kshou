"""
AI 视频总结路由
"""
import logging

from fastapi import APIRouter, Query

from ..models.schemas import ApiResponse
from ..config import settings
from ..exceptions import PlatformError, InvalidParameterError
from ..services.summary_service import summarize_video

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/summarize", response_model=ApiResponse)
async def summarize_video_endpoint(
    url: str = Query(..., min_length=5, description="视频URL（支持B站/抖音/小红书）"),
):
    """
    AI 视频内容总结

    输入视频 URL，自动提取字幕并通过 AI 生成内容总结。

    - **url**: 视频链接
        - B站: https://www.bilibili.com/video/BVxxxxxx
        - 抖音: https://www.douyin.com/video/xxxxxx
        - 小红书: https://www.xiaohongshu.com/explore/xxxxxx

    需要:
    - 安装 yt-dlp: `pip install yt-dlp`
    - 配置 LLM_API_KEY 环境变量（支持 DeepSeek/OpenAI 兼容接口）
    """
    if not settings.LLM_API_KEY:
        raise PlatformError(
            message="未配置 LLM API Key",
            suggestion="请在 .env 文件中设置 LLM_API_KEY",
            code=503,
        )

    try:
        result = await summarize_video(
            url=url,
            api_key=settings.LLM_API_KEY,
            api_base=settings.LLM_API_BASE,
            model=settings.LLM_MODEL,
            sessdata=settings.BILIBILI_SESSDATA,
            timeout=30,
        )
        return ApiResponse(
            success=True,
            code=200,
            message="success",
            data=result,
        )
    except ValueError as e:
        raise InvalidParameterError(
            message=str(e),
            suggestion="请提供 B站/抖音/小红书 的视频链接",
        )
    except PlatformError:
        raise
    except RuntimeError as e:
        raise PlatformError(
            message=f"视频总结失败: {e}",
            code=500,
        )
    except Exception as e:
        logger.error(f"视频总结异常: {e}", exc_info=True)
        raise PlatformError(
            message=f"视频总结失败: {e}",
            code=500,
        )
