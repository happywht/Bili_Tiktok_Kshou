"""
Bilibili Search API - FastAPI应用入口

启动方式:
    开发环境: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    生产环境: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

API文档:
    Swagger UI: http://localhost:8000/docs
    ReDoc: http://localhost:8000/redoc
"""
import time
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .routers import search, videos
from .middleware.cors import setup_cors
from .models.schemas import ApiResponse, ErrorInfo

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## B站视频搜索 API

支持功能：
- 🔍 视频搜索（关键词、分页、排序）
- 📺 视频详情获取
- 📝 视频总结（含字幕预览）

平台支持：
- ✅ B站 (bilibili)
- 🚧 抖音 (即将支持)
- 🚧 小红书 (即将支持)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置CORS
setup_cors(app)

# 注册路由
app.include_router(search.router, prefix=settings.API_PREFIX, tags=["🔍 搜索"])
app.include_router(videos.router, prefix=settings.API_PREFIX, tags=["📺 视频"])


# ============ 异常处理 ============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数验证异常处理"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "code": 422,
            "message": "参数验证失败",
            "error": {
                "type": "ValidationError",
                "details": [
                    {
                        "field": ".".join(str(loc) for loc in err["loc"]),
                        "message": err["msg"]
                    }
                    for err in exc.errors()
                ]
            },
            "timestamp": int(time.time() * 1000)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "code": 500,
            "message": f"服务器内部错误: {str(exc)}",
            "error": {
                "type": "InternalError",
                "details": [{"field": None, "message": str(exc)}]
            },
            "timestamp": int(time.time() * 1000)
        }
    )


# ============ 路由 ============

@app.get("/", tags=["🏠 首页"])
async def root():
    """API首页"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get(f"{settings.API_PREFIX}/health", response_model=ApiResponse, tags=["💚 健康检查"])
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


@app.get(f"{settings.API_PREFIX}/platforms", response_model=ApiResponse, tags=["📱 平台"])
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
                    "status": "coming_soon",
                    "features": []
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
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🚀 {settings.APP_NAME} v{settings.APP_VERSION}                   ║
║                                                            ║
║   📖 API文档: http://localhost:8000/docs                   ║
║   📖 ReDoc:   http://localhost:8000/redoc                  ║
║                                                            ║
║   💡 提示: 配置 BILIBILI_SESSDATA 环境变量以启用搜索功能   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
