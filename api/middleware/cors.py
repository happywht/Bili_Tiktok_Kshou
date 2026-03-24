"""
CORS中间件配置
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from ..config import settings


def setup_cors(app: FastAPI):
    """配置CORS中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
