# 多平台视频搜索API

支持 **B站、抖音、小红书** 的统一搜索接口。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# 小红书CLI工具（推荐）
uv tool install xiaohongshu-cli
# 或
pipx install xiaohongshu-cli

# 浏览器自动化（备选方案）
pip install DrissionPage
```

### 2. 配置环境变量

复制示例配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入必要的Cookie：

```env
# B站配置
BILIBILI_SESSDATA=你的SESSDATA

# 抖音配置（二选一）
DOUYIN_COOKIES=完整Cookie字符串
# 或
DOUYIN_TTWID=ttwid值

# 小红书配置（可选，CLI会自动管理）
XIAOHONGSHU_COOKIES=
```

### 3. 启动服务

```bash
cd api
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 📡 API接口

### 获取支持的平台列表

```http
GET /api/v1/platforms
```

响应示例：
```json
{
  "success": true,
  "code": 200,
  "data": {
    "platforms": [
      {"id": "bilibili", "name": "哔哩哔哩", "available": true, "icon": "📺"},
      {"id": "douyin", "name": "抖音", "available": true, "icon": "🎵"},
      {"id": "xiaohongshu", "name": "小红书", "available": true, "icon": "📕"}
    ]
  }
}
```

### 统一搜索接口

```http
GET /api/v1/search?keyword=关键词&platform=bilibili
```

参数说明：
- `keyword` (必填): 搜索关键词
- `platform`: 平台标识 (bilibili, douyin, xiaohongshu)
- `page`: 页码 (默认1)
- `page_size`: 每页数量 (默认20)
- `order`: 排序方式

### B站搜索

```http
GET /api/v1/search/bilibili?keyword=关键词&order=totalrank
```

### 抖音搜索

```http
GET /api/v1/search/douyin?keyword=关键词&sort_type=0
```

参数说明：
- `sort_type`: 排序类型
  - `0`: 综合排序
  - `1`: 最多点赞
  - `2`: 最新发布

### 小红书搜索

```http
GET /api/v1/search?keyword=关键词&platform=xiaohongshu
```

## 🔑 获取Cookie

### B站 (SESSDATA)

1. 浏览器打开 https://www.bilibili.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 Application → Cookies → bilibili.com
4. 复制 `SESSDATA` 的值

### 抖音 (Cookie)

1. 浏览器打开 https://www.douyin.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 Application → Cookies → douyin.com
4. 方式1：复制整个 Cookie 字符串（推荐）
5. 方式2：仅复制 `ttwid` 的值（最低要求）

### 小红书

小红书服务使用 `xiaohongshu-cli` 工具，首次使用需要登录：

```bash
# 登录小红书（会弹出二维码）
xhs login

# 验证登录状态
xhs search "测试" --json
```

## 🏗️ 架构说明

```
api/
├── services/
│   ├── base.py              # 平台服务基类
│   ├── bilibili_service.py  # B站服务实现
│   ├── douyin_service.py    # 抖音服务实现
│   ├── xiaohongshu_service.py # 小红书服务实现
│   └── factory.py           # 服务工厂
├── models/
│   └── schemas.py           # 数据模型
├── routers/
│   └── search.py            # 搜索路由
└── config.py                # 配置管理
```

### 扩展新平台

1. 在 `services/` 下创建新服务类，继承 `PlatformService`
2. 实现必要的抽象方法：`search()`, `get_detail()`
3. 在 `factory.py` 中注册服务类
4. 在 `config.py` 中添加平台配置

## ⚠️ 注意事项

### B站搜索
- 需要有效的SESSDATA
- 可能遇到412错误，需要更新Cookie

### 抖音搜索
- 抖音API有严格的反爬虫机制
- 建议使用完整的Cookie字符串
- 可能需要定期更新Cookie

### 小红书搜索
- **推荐方案**: xiaohongshu-cli
  - 社区维护，自动处理签名
  - 安装: `uv tool install xiaohongshu-cli`
- **备选方案**: DrissionPage浏览器自动化
  - 需要安装: `pip install DrissionPage`
  - 速度较慢但稳定性高

## 📦 依赖说明

### 必需依赖
```
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.3
requests>=2.31.0
httpx>=0.26.0
```

### 可选依赖
```
# 小红书CLI（推荐）
# uv tool install xiaohongshu-cli

# 浏览器自动化
DrissionPage>=4.0.0

# 加密库（直接API签名需要）
pycryptodome>=3.20.0
```

## 📄 License

MIT
