"""
Bilibili Search API - FastAPI应用入口

启动方式:
    开发环境: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    生产环境: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
    直接运行: python api/main.py

API文档:
    Swagger UI: http://localhost:8000/docs
    ReDoc: http://localhost:8000/redoc
"""
# 支持直接运行 python api/main.py
import sys
import os
import logging

# 当直接运行此文件时，添加项目根目录到 sys.path
if __name__ == "__main__":
    # 获取项目根目录（api 的父目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

import time
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 根据运行方式选择导入方式
try:
    # 作为包运行（uvicorn）
    from .config import settings
    from .routers import search, videos
    from .middleware.cors import setup_cors
    from .middleware.error_handler import setup_error_handlers
    from .models.schemas import ApiResponse, ErrorInfo
    from .exceptions import PlatformError
except ImportError:
    # 直接运行（python api/main.py）
    from api.config import settings
    from api.routers import search, videos
    from api.middleware.cors import setup_cors
    from api.middleware.error_handler import setup_error_handlers
    from api.models.schemas import ApiResponse, ErrorInfo
    from api.exceptions import PlatformError

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## B站视频搜索 API

支持功能：
- 视频搜索（关键词、分页、排序）
- 视频详情获取
- 视频总结（含字幕预览）

平台支持：
- B站 (bilibili)
- 抖音 (douyin)
- 小红书 (xiaohongshu)

## 错误响应格式

所有错误响应都遵循统一格式：
```json
{
  "success": false,
  "code": 401,
  "message": "用户友好的错误信息",
  "error_type": "CookieExpiredError",
  "suggestion": "请更新BILIBILI_SESSDATA环境变量",
  "timestamp": 1234567890123
}
```

## 常见错误类型

| 错误类型 | 说明 | 解决方案 |
|---------|------|---------|
| CookieExpiredError | 登录状态过期 | 更新对应平台的Cookie环境变量 |
| RateLimitError | 请求频率过高 | 降低请求频率，稍后重试 |
| CaptchaDetectedError | 需要验证码 | 在浏览器中手动完成验证 |
| ContentNotFoundError | 内容不存在 | 检查内容ID是否正确 |
| InvalidParameterError | 参数无效 | 检查请求参数格式 |
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置CORS
setup_cors(app)

# 设置错误处理器
setup_error_handlers(app)

# 注册路由
app.include_router(search.router, prefix=settings.API_PREFIX, tags=["搜索"])
app.include_router(videos.router, prefix=settings.API_PREFIX, tags=["视频"])


# ============ 路由 ============

@app.get("/", tags=["首页"])
async def root():
    """API首页"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get(f"{settings.API_PREFIX}/health", response_model=ApiResponse, tags=["健康检查"])
async def health_check():
    """
    健康检查接口

    用于检测服务是否正常运行
    """
    return ApiResponse(
        success=True,
        code=200,
        message="healthy",
        data={
            "status": "running",
            "version": settings.APP_VERSION,
            "uptime": int(time.time())
        }
    )


@app.get(f"{settings.API_PREFIX}/platforms", response_model=ApiResponse, tags=["平台"])
async def get_platforms():
    """
    获取支持的平台列表

    返回当前支持的所有平台信息
    """
    return ApiResponse(
        success=True,
        code=200,
        message="success",
        data={
            "platforms": [
                {
                    "id": "bilibili",
                    "name": "B站",
                    "icon": "📺",
                    "status": "available",
                    "features": ["search", "detail", "summary"]
                },
                {
                    "id": "douyin",
                    "name": "抖音",
                    "icon": "🎵",
                    "status": "available",
                    "features": ["search"]
                },
                {
                    "id": "xiaohongshu",
                    "name": "小红书",
                    "icon": "📕",
                    "status": "coming_soon",
                    "features": []
                }
            ]
        }
    )


# ============ 启动提示 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 使用 UTF-8 编码输出，避免 Windows 控制台编码问题
    import sys
    try:
        startup_message = f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   {settings.APP_NAME} v{settings.APP_VERSION}
║                                                            ║
║   API文档: http://localhost:8000/docs
║   ReDoc:   http://localhost:8000/redoc
║                                                            ║
║   提示: 配置 BILIBILI_SESSDATA 环境变量以启用搜索功能
║   提示: 配置 DOUYIN_COOKIE 环境变量以启用抖音搜索
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"""
        # 尝试使用 UTF-8 输出
        if sys.stdout.encoding != 'utf-8':
            print(startup_message.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
        else:
            print(startup_message)
    except Exception:
        # 如果输出失败，使用简化版本
        print(f"Server started: {settings.APP_NAME} v{settings.APP_VERSION}")
        print(f"API Docs: http://localhost:8000/docs")


if __name__ == "__main__":
    import sys
    import os

    # 添加项目根目录到路径，支持直接运行
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
