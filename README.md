# VideoHub - 多平台视频搜索 API

一个现代化的多平台视频/内容搜索 API 服务，支持 B站、抖音、小红书等主流平台的内容检索。

## 功能特性

- **多平台搜索** - 统一 API 接口支持 B站、抖音、小红书
- **关键词搜索** - 支持关键词搜索、分页、多种排序方式
- **视频详情** - 获取视频详细信息、统计数据
- **视频总结** - B站视频字幕预览和总结
- **图片代理** - 绕过防盗链，支持跨域图片访问
- **统一错误处理** - 友好的错误信息和解决建议
- **Swagger 文档** - 自动生成的 API 文档

## 支持的平台

| 平台 | 标识 | 状态 | 功能支持 |
|------|------|------|----------|
| B站 (哔哩哔哩) | `bilibili` | 可用 | 搜索、详情、总结 |
| 抖音 | `douyin` | 可用 | 搜索 |
| 小红书 | `xiaohongshu` | 即将支持 | - |

## 快速开始

### 环境要求

- Python 3.8+
- pip 或 conda

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd bilibili_search

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制环境变量模板
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置平台 Cookie（详见 [配置文档](docs/CONFIGURATION.md)）

```env
# B站配置（必需）
BILIBILI_SESSDATA=your_sessdata_here

# 抖音配置（可选）
DOUYIN_COOKIES=your_cookies_here
```

### 运行

```bash
# 开发模式（支持热重载）
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或直接运行
python api/main.py
```

### 访问

- **API 服务**: http://localhost:8000
- **Swagger 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc

## 环境变量配置

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `BILIBILI_SESSDATA` | B站登录 Cookie | 是（B站搜索） | - |
| `DOUYIN_COOKIES` | 抖音完整 Cookie | 否 | - |
| `DOUYIN_TTWID` | 抖音 ttwid | 否 | - |
| `XIAOHONGSHU_COOKIES` | 小红书 Cookie | 否 | - |
| `DEBUG` | 调试模式 | 否 | false |
| `API_PREFIX` | API 路由前缀 | 否 | /api/v1 |
| `CORS_ORIGINS` | CORS 允许源 | 否 | * |

详细的 Cookie 获取方法请参考 [配置文档](docs/CONFIGURATION.md)。

## API 端点概览

### 平台信息

```
GET /api/v1/platforms
```
获取支持的平台列表及状态。

### 多平台搜索

```
GET /api/v1/search?keyword=Python&platform=bilibili&page=1&page_size=20
```
统一的多平台搜索接口。

### B站搜索

```
GET /api/v1/search/bilibili?keyword=Python&order=totalrank
```
B站专用搜索接口，支持排序：`totalrank`(综合)、`click`(播放量)、`pubdate`(发布时间)、`dm`(弹幕数)。

### 抖音搜索

```
GET /api/v1/search/douyin?keyword=Python&sort_type=0
```
抖音搜索接口，排序：`0`(综合)、`1`(最多点赞)、`2`(最新)。

### 视频详情（B站）

```
GET /api/v1/videos/{bvid}
```
获取 B站视频详情。

### 视频总结（B站）

```
GET /api/v1/videos/{bvid}/summary
```
获取 B站视频总结和字幕预览。

### 图片代理

```
GET /api/v1/proxy-image?url=<encoded_url>
```
代理图片请求，绕过防盗链。

### 健康检查

```
GET /api/v1/health
```
服务健康状态检查。

完整的 API 文档请参考 [API 文档](docs/API.md)。

## 项目结构

```
bilibili_search/
├── api/                        # 后端 API 服务
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── exceptions.py           # 异常定义
│   ├── models/
│   │   └── schemas.py          # Pydantic 数据模型
│   ├── routers/
│   │   ├── search.py           # 搜索路由
│   │   └── videos.py           # 视频详情路由
│   ├── services/
│   │   ├── base.py             # 服务基类
│   │   ├── bilibili_service.py # B站服务
│   │   ├── douyin_service.py   # 抖音服务
│   │   └── xiaohongshu_service.py
│   └── middleware/
│       ├── cors.py             # CORS 中间件
│       └── error_handler.py    # 错误处理中间件
│
├── docs/                       # 文档目录
│   ├── API.md                  # API 详细文档
│   ├── CONFIGURATION.md        # 配置说明
│   └── TROUBLESHOOTING.md      # 故障排除
│
├── tests/                      # 测试目录
├── web/                        # 前端应用（可选）
├── .env.example                # 环境变量模板
├── requirements.txt            # Python 依赖
└── README.md                   # 项目说明
```

## 技术栈

- **FastAPI** - 高性能 Python Web 框架
- **Pydantic** - 数据验证和序列化
- **Uvicorn** - ASGI 服务器
- **httpx** - 异步 HTTP 客户端
- **Requests** - HTTP 请求库

## 常见问题

### Q: 搜索返回 "登录状态已过期"

Cookie 已过期，需要重新获取。参考 [配置文档](docs/CONFIGURATION.md) 更新对应平台的 Cookie。

### Q: 搜索返回 "请求过于频繁"

触发了平台的频率限制，请降低请求频率，建议每次请求间隔 1-2 秒。

### Q: B站搜索无结果

1. 检查 `BILIBILI_SESSDATA` 是否正确配置
2. 确认 Cookie 未过期（B站 Cookie 有效期约 30 天）
3. 检查关键词是否有效

### Q: 抖音搜索需要验证码

抖音有较强的反爬机制，遇到验证码时需要：
1. 在浏览器中手动完成验证
2. 更新 Cookie 后重试

更多问题请参考 [故障排除指南](docs/TROUBLESHOOTING.md)。

## 开发指南

### 运行测试

```bash
pytest tests/
```

### 代码风格

项目使用 Python 标准代码风格，建议使用 `black` 和 `isort` 格式化代码。

### 添加新平台

1. 在 `api/services/` 创建新的服务类，继承 `BasePlatformService`
2. 在 `api/services/factory.py` 注册新平台
3. 在 `api/routers/search.py` 添加路由支持
4. 更新文档

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**文档导航**: [API 文档](docs/API.md) | [配置说明](docs/CONFIGURATION.md) | [故障排除](docs/TROUBLESHOOTING.md)
