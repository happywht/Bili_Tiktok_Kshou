# API 接口文档

本文档详细说明 VideoHub 多平台搜索 API 的所有端点、请求参数和响应格式。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 前缀**: `/api/v1`
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

## 通用响应格式

所有 API 响应都遵循统一的格式：

### 成功响应

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "platform": "bilibili",
  "timestamp": 1711334400000,
  "data": {
    // 响应数据
  },
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": null,
    "has_more": true
  }
}
```

### 错误响应

```json
{
  "success": false,
  "code": 401,
  "message": "B站登录状态已过期",
  "platform": "bilibili",
  "timestamp": 1711334400000,
  "error": {
    "type": "CookieExpiredError",
    "details": null
  }
}
```

---

## 端点列表

### 1. 获取平台列表

获取所有支持的平台及其状态信息。

**请求**

```
GET /api/v1/platforms
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "timestamp": 1711334400000,
  "data": {
    "platforms": [
      {
        "id": "bilibili",
        "name": "B站",
        "available": true,
        "icon": "📺"
      },
      {
        "id": "douyin",
        "name": "抖音",
        "available": true,
        "icon": "🎵"
      },
      {
        "id": "xiaohongshu",
        "name": "小红书",
        "available": false,
        "icon": "📕"
      }
    ]
  }
}
```

---

### 2. 多平台搜索

统一的搜索接口，通过 `platform` 参数指定搜索平台。

**请求**

```
GET /api/v1/search
```

**参数**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `keyword` | string | 是 | - | 搜索关键词（1-100字符） |
| `platform` | string | 否 | bilibili | 平台标识：bilibili, douyin, xiaohongshu |
| `page` | integer | 否 | 1 | 页码（1-50） |
| `page_size` | integer | 否 | 20 | 每页数量（1-50） |
| `order` | string | 否 | totalrank | 排序方式（各平台不同） |

**请求示例**

```bash
# B站搜索
curl "http://localhost:8000/api/v1/search?keyword=Python&platform=bilibili&page=1&page_size=20&order=totalrank"

# 抖音搜索
curl "http://localhost:8000/api/v1/search?keyword=Python&platform=douyin&page=1&page_size=20"
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "platform": "bilibili",
  "timestamp": 1711334400000,
  "data": {
    "items": [
      {
        "id": "BV1xx411c7mD",
        "title": "Python入门教程",
        "description": "零基础学Python...",
        "author": "UP主名称",
        "author_id": "123456",
        "cover_url": "https://i0.hdslb.com/bfs/...",
        "url": "https://www.bilibili.com/video/BV1xx411c7mD",
        "platform": "bilibili",
        "stats": {
          "play_count": 100000,
          "like_count": 5000,
          "comment_count": 200,
          "share_count": 100,
          "collect_count": 0
        },
        "tags": ["Python", "编程", "教程"],
        "publish_time": "1711334400",
        "duration": "10:30",
        "content_type": "video"
      }
    ],
    "platform": "bilibili"
  },
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": null,
    "has_more": true
  }
}
```

---

### 3. B站搜索

B站专用搜索接口，支持更多排序选项。

**请求**

```
GET /api/v1/search/bilibili
```

**参数**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `keyword` | string | 是 | - | 搜索关键词（1-100字符） |
| `page` | integer | 否 | 1 | 页码（1-50） |
| `page_size` | integer | 否 | 20 | 每页数量（1-50） |
| `order` | string | 否 | totalrank | 排序方式 |

**排序方式 (order)**

| 值 | 说明 |
|-----|------|
| `totalrank` | 综合排序（默认） |
| `click` | 播放量从高到低 |
| `pubdate` | 发布日期从新到旧 |
| `dm` | 弹幕数从高到低 |
| `stow` | 收藏数从高到低 |

**请求示例**

```bash
curl "http://localhost:8000/api/v1/search/bilibili?keyword=Python&order=click&page=1"
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "platform": "bilibili",
  "timestamp": 1711334400000,
  "data": {
    "items": [
      {
        "id": "BV1xx411c7mD",
        "title": "Python零基础入门教程",
        "description": "适合零基础学员...",
        "author": "程序员小张",
        "author_id": "12345678",
        "cover_url": "https://i0.hdslb.com/bfs/archive/xxx.jpg",
        "url": "https://www.bilibili.com/video/BV1xx411c7mD",
        "platform": "bilibili",
        "stats": {
          "play_count": 1500000,
          "like_count": 50000,
          "comment_count": 3000,
          "share_count": 2000,
          "collect_count": 0
        },
        "tags": ["Python", "编程", "教程", "入门"],
        "publish_time": "1700000000",
        "duration": "45:30",
        "content_type": "video"
      }
    ],
    "platform": "bilibili"
  },
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": null,
    "has_more": true
  }
}
```

---

### 4. 抖音搜索

抖音视频搜索接口。

**请求**

```
GET /api/v1/search/douyin
```

**参数**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `keyword` | string | 是 | - | 搜索关键词（1-100字符） |
| `page` | integer | 否 | 1 | 页码（1-50） |
| `page_size` | integer | 否 | 20 | 每页数量（1-50） |
| `sort_type` | integer | 否 | 0 | 排序类型 |

**排序类型 (sort_type)**

| 值 | 说明 |
|-----|------|
| `0` | 综合排序（默认） |
| `1` | 最多点赞 |
| `2` | 最新发布 |

**请求示例**

```bash
curl "http://localhost:8000/api/v1/search/douyin?keyword=美食&sort_type=0&page=1"
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "platform": "douyin",
  "timestamp": 1711334400000,
  "data": {
    "items": [
      {
        "id": "7xxxxxxxxxxxxxx",
        "title": "家常红烧肉做法",
        "description": "超简单的红烧肉...",
        "author": "美食博主",
        "author_id": "",
        "cover_url": "https://p3.douyinpic.com/...",
        "url": "https://www.douyin.com/video/7xxxxxxxxxxxxxx",
        "platform": "douyin",
        "stats": {
          "play_count": 500000,
          "like_count": 30000,
          "comment_count": 1500,
          "share_count": 800,
          "collect_count": 0
        },
        "tags": ["美食", "红烧肉", "家常菜"],
        "publish_time": "1711334400",
        "duration": "02:30",
        "content_type": "video"
      }
    ],
    "platform": "douyin"
  },
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": null,
    "has_more": true
  }
}
```

---

### 5. 视频详情（B站）

获取 B站视频的详细信息。

**请求**

```
GET /api/v1/videos/{bvid}
```

**参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `bvid` | string | 是 | 视频BV号（如 BV1xx411c7mD） |

**请求示例**

```bash
curl "http://localhost:8000/api/v1/videos/BV1xx411c7mD"
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "platform": "bilibili",
  "timestamp": 1711334400000,
  "data": {
    "bvid": "BV1xx411c7mD",
    "title": "Python零基础入门教程",
    "description": "本教程适合零基础学员...",
    "owner": "程序员小张",
    "pubdate": 1700000000,
    "duration": 2730,
    "stats": {
      "view": 1500000,
      "like": 50000,
      "coin": 8000,
      "favorite": 12000,
      "share": 2000,
      "reply": 3000
    },
    "tags": ["Python", "编程", "教程"],
    "cover": "https://i0.hdslb.com/bfs/archive/xxx.jpg",
    "url": "https://www.bilibili.com/video/BV1xx411c7mD"
  }
}
```

---

### 6. 视频总结（B站）

获取 B站视频的总结信息，包含字幕预览。

**请求**

```
GET /api/v1/videos/{bvid}/summary
```

**参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `bvid` | string | 是 | 视频BV号（如 BV1xx411c7mD） |

**请求示例**

```bash
curl "http://localhost:8000/api/v1/videos/BV1xx411c7mD/summary"
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "platform": "bilibili",
  "timestamp": 1711334400000,
  "data": {
    "video_info": {
      "title": "Python零基础入门教程",
      "author": "程序员小张",
      "description": "本教程适合零基础学员...",
      "duration": 2730,
      "stats": {
        "view": 1500000,
        "like": 50000,
        "coin": 8000,
        "favorite": 12000,
        "share": 2000,
        "reply": 3000
      },
      "tags": ["Python", "编程", "教程"],
      "cover": "https://i0.hdslb.com/bfs/archive/xxx.jpg",
      "url": "https://www.bilibili.com/video/BV1xx411c7mD"
    },
    "subtitle_available": true,
    "subtitle_preview": "大家好，欢迎来到Python教程...\n今天我们来讲..."
  }
}
```

---

### 7. 图片代理

代理图片请求，用于绕过防盗链限制。

**请求**

```
GET /api/v1/proxy-image
```

**参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `url` | string | 是 | 原始图片URL（需URL编码） |

**支持的域名**

- B站: `i0.hdslb.com`, `i1.hdslb.com`, `i2.hdslb.com`, `hdslb.com`, `archive.biliimg.com`, `bili.bilivideo.com`
- 抖音: `p3.douyinpic.com`, `p6.douyinpic.com`, `p9.douyinpic.com`, `douyinpic.com`, `v3-web.douyinvod.com`
- 小红书: `ci.xiaohongshu.com`, `sns-webpic-qc.xhscdn.com`, `xhscdn.com`

**请求示例**

```bash
# URL 需要编码
curl "http://localhost:8000/api/v1/proxy-image?url=https%3A%2F%2Fi0.hdslb.com%2Fbfs%2Farchive%2Fxxx.jpg"
```

**响应**

返回图片二进制数据，Content-Type 为对应的图片类型。

---

### 8. 健康检查

检查服务运行状态。

**请求**

```
GET /api/v1/health
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "healthy",
  "timestamp": 1711334400000,
  "data": {
    "status": "running",
    "version": "2.0.0",
    "uptime": 1711334400
  }
}
```

---

## 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "success": false,
  "code": 401,
  "message": "用户友好的错误信息",
  "platform": "bilibili",
  "timestamp": 1711334400000,
  "error": {
    "type": "CookieExpiredError",
    "details": null
  }
}
```

### 错误类型

| 错误类型 | HTTP 状态码 | 说明 | 解决方案 |
|---------|------------|------|---------|
| `CookieExpiredError` | 401 | 登录状态过期 | 更新对应平台的 Cookie 环境变量 |
| `BilibiliCookieExpiredError` | 401 | B站 Cookie 过期 | 更新 `BILIBILI_SESSDATA` |
| `DouyinCookieExpiredError` | 401 | 抖音 Cookie 过期 | 更新 `DOUYIN_COOKIES` |
| `XiaohongshuCookieExpiredError` | 401 | 小红书 Cookie 过期 | 更新 `XIAOHONGSHU_COOKIES` |
| `RateLimitError` | 429 | 请求频率过高 | 降低请求频率，稍后重试 |
| `CaptchaDetectedError` | 403 | 需要验证码 | 在浏览器中手动完成验证 |
| `ContentNotFoundError` | 404 | 内容不存在 | 检查内容 ID 是否正确 |
| `InvalidParameterError` | 400 | 参数无效 | 检查请求参数格式 |
| `PlatformNotAvailableError` | 503 | 平台服务不可用 | 稍后重试或切换平台 |
| `NetworkError` | 502 | 网络连接失败 | 检查网络连接 |
| `TimeoutError` | 504 | 请求超时 | 稍后重试 |

---

## 数据模型

### ContentItem（通用内容项）

```typescript
interface ContentItem {
  id: string;           // 内容ID
  title: string;        // 标题
  description: string;  // 描述
  author: string;       // 作者名称
  author_id: string;    // 作者ID
  cover_url: string;    // 封面图片URL
  url: string;          // 内容链接
  platform: string;     // 平台标识
  stats: ContentStats;  // 统计数据
  tags: string[];       // 标签列表
  publish_time: string; // 发布时间
  duration: string;     // 时长
  content_type: string; // 内容类型
}
```

### ContentStats（内容统计）

```typescript
interface ContentStats {
  play_count: number;    // 播放量
  like_count: number;    // 点赞数
  comment_count: number; // 评论数
  share_count: number;   // 分享数
  collect_count: number; // 收藏数
}
```

### PaginationInfo（分页信息）

```typescript
interface PaginationInfo {
  page: number;       // 当前页码
  page_size: number;  // 每页数量
  total: number | null; // 总数（可能为空）
  has_more: boolean;  // 是否有更多
}
```

---

## 使用示例

### JavaScript/TypeScript

```javascript
// 搜索 B站视频
async function searchBilibili(keyword) {
  const response = await fetch(
    `http://localhost:8000/api/v1/search/bilibili?keyword=${encodeURIComponent(keyword)}`
  );
  const data = await response.json();

  if (data.success) {
    console.log('搜索结果:', data.data.items);
  } else {
    console.error('搜索失败:', data.message);
  }
}

// 获取视频详情
async function getVideoDetail(bvid) {
  const response = await fetch(
    `http://localhost:8000/api/v1/videos/${bvid}`
  );
  return await response.json();
}
```

### Python

```python
import requests

# 搜索 B站视频
def search_bilibili(keyword, page=1):
    response = requests.get(
        'http://localhost:8000/api/v1/search/bilibili',
        params={'keyword': keyword, 'page': page}
    )
    data = response.json()

    if data['success']:
        return data['data']['items']
    else:
        raise Exception(data['message'])

# 使用示例
videos = search_bilibili('Python')
for video in videos:
    print(f"{video['title']} - {video['author']}")
```

---

## 速率限制建议

为避免触发平台限制，建议：

- 每次请求间隔 1-2 秒
- 批量操作时使用队列
- 实现请求重试机制（指数退避）
- 缓存已获取的数据

---

**相关文档**: [配置说明](CONFIGURATION.md) | [故障排除](TROUBLESHOOTING.md)
