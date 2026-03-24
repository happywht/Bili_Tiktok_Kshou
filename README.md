# B站视频搜索平台 - VideoHub

一个现代化的多平台视频搜索前端应用，当前支持B站视频搜索，预留抖音、小红书等平台扩展接口。

## ✨ 功能特性

- 🔍 **关键词搜索** - 支持B站视频关键词搜索
- 📊 **多维度排序** - 综合排序、播放量、发布时间、弹幕数
- 🎨 **现代化UI** - 深色主题、卡片式布局、流畅动画
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🔄 **无限滚动** - 支持加载更多结果
- 🌐 **多平台扩展** - 预留抖音、小红书平台接口

## 🛠 技术栈

### 后端
- **FastAPI** - 高性能Python Web框架
- **Pydantic** - 数据验证和序列化
- **Requests** - HTTP请求库

### 前端
- **React 18** - 现代化UI框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Tailwind CSS** - 原子化CSS框架
- **Zustand** - 轻量级状态管理
- **Axios** - HTTP客户端
- **Lucide Icons** - 精美图标库

## 📁 项目结构

```
bilibili_search/
├── api/                    # 后端API服务
│   ├── main.py            # FastAPI应用入口
│   ├── config.py          # 配置管理
│   ├── models/            # 数据模型
│   ├── routers/           # 路由
│   ├── services/          # 业务逻辑
│   └── middleware/        # 中间件
│
├── web/                    # 前端应用
│   ├── src/
│   │   ├── api/           # API调用
│   │   ├── components/    # UI组件
│   │   ├── pages/         # 页面
│   │   ├── store/         # 状态管理
│   │   ├── types/         # 类型定义
│   │   └── utils/         # 工具函数
│   └── ...
│
├── bilibili_search.py      # 原有搜索核心
├── bilibili_cli.py         # CLI工具
└── requirements.txt        # Python依赖
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd bilibili_search

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd web
npm install
```

### 2. 配置SESSDATA

B站搜索API需要登录Cookie，按以下步骤获取：

1. 浏览器打开 https://www.bilibili.com 并登录
2. 按F12打开开发者工具
3. Application → Cookies → bilibili.com
4. 复制 `SESSDATA` 的值

创建 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 SESSDATA
```

### 3. 启动服务

**启动后端API (端口8000)**
```bash
# 在项目根目录
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端开发服务器 (端口3000)**
```bash
# 在 web/ 目录
npm run dev
```

### 4. 访问应用

- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API接口

### 搜索视频
```
GET /api/v1/search?keyword=Python&page=1&page_size=20&order=totalrank
```

### 获取视频详情
```
GET /api/v1/videos/{bvid}
```

### 获取视频总结
```
GET /api/v1/videos/{bvid}/summary
```

### 健康检查
```
GET /api/v1/health
```

### 平台列表
```
GET /api/v1/platforms
```

## 🎨 扩展新平台

项目采用**平台适配器模式**，添加新平台只需：

### 1. 创建适配器 (后端)

```python
# api/services/douyin_service.py
class DouyinService:
    def search_videos(self, keyword, page, page_size, order):
        # 实现抖音搜索逻辑
        pass
```

### 2. 添加路由

```python
# api/routers/search.py
if platform == "douyin":
    videos = douyin_service.search_videos(...)
```

### 3. 更新前端

```typescript
// web/src/store/searchStore.ts
platforms: [
  { id: 'douyin', name: '抖音', icon: '🎵', status: 'available', ... },
  // ...
]
```

## 🔧 开发指南

### 前端开发
```bash
cd web
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览生产版本
```

### 后端开发
```bash
# 开发模式（热重载）
uvicorn api.main:app --reload

# 生产模式
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📝 注意事项

1. **SESSDATA有效期** - B站Cookie会过期，需要定期更新
2. **API限流** - B站有频率限制，建议添加请求延时
3. **搜索结果** - 最多返回约1000条结果

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
