# Bilibili Search Skill

B站视频搜索与内容总结工具

## 说明

**重要**: B站API现在需要登录Cookie才能访问。使用前需要配置 SESSDATA。

### 获取 SESSDATA 方法

1. 浏览器登录 [B站](https://www.bilibili.com)
2. 按 F12 打开开发者工具
3. 切换到 Application/Storage → Cookies
4. 找到 `bilibili.com` 域名下的 `SESSDATA`
5. 复制其值

### 配置方式

**方式1: credentials.json（推荐）**
```json
{
  "bilibili": {
    "sessdata": "你的SESSDATA值",
    "updated_at": "2026-03-05T09:07:15+08:00"
  }
}
```

**方式2: 环境变量**
```bash
export BILIBILI_SESSDATA="你的SESSDATA值"
```

**方式3: 调用时传入**
在参数中提供 `sessdata` 字段

---

## 工具

### action: search

搜索B站视频

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 固定值 `"search"` |
| keyword | string | 是 | 搜索关键词 |
| limit | number | 否 | 返回数量，默认10，最大50 |
| order | string | 否 | 排序方式：综合`totalrank`(默认)、点击量`click`、发布时间`pubdate`、弹幕数`dm` |
| sessdata | string | 否 | B站Cookie（如不配置则读取credentials.json或环境变量） |

**返回：**
```json
{
  "success": true,
  "keyword": "AI",
  "count": 10,
  "videos": [
    {
      "title": "视频标题",
      "author": "UP主名称",
      "plays": 10000,
      "likes": 500,
      "duration": "10:30",
      "url": "https://www.bilibili.com/video/BVxxx",
      "bvid": "BVxxx"
    }
  ]
}
```

**示例：**
```bash
python3 search.py '{"action": "search", "keyword": "AI教程", "limit": 5}'
```

---

### action: summarize

总结B站视频内容（获取详情、字幕预览）

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 固定值 `"summarize"` |
| bvid | string | 是 | 视频BV号（如 `BV1uxA8zZEvG`） |
| sessdata | string | 否 | B站Cookie（如不配置则读取credentials.json或环境变量） |

**返回：**
```json
{
  "success": true,
  "bvid": "BV1uxA8zZEvG",
  "summary": {
    "video_info": {
      "title": "视频标题",
      "author": "UP主",
      "description": "视频简介...",
      "duration": 1200,
      "stats": {
        "view": 100000,
        "like": 5000,
        "coin": 1000,
        "favorite": 2000,
        "share": 500,
        "reply": 300
      },
      "tags": ["AI", "教程"],
      "cover": "封面图URL",
      "url": "https://www.bilibili.com/video/BVxxx"
    },
    "subtitle_available": true,
    "subtitle_preview": "字幕内容前800字..."
  }
}
```

**示例：**
```bash
python3 search.py '{"action": "summarize", "bvid": "BV1uxA8zZEvG"}'
```

---

## Python 直接调用

```python
from bilibili_search import search_bilibili_skill, summarize_bilibili_video

# 搜索视频
results = search_bilibili_skill(keyword="AI", limit=10)

# 总结视频
summary = summarize_bilibili_video(bvid="BV1uxA8zZEvG")
```

---

## 使用示例

**用户:** 帮我搜索B站上关于Python的视频
→ 调用 search_bilibili(keyword="Python")

**用户:** 找播放量最高的AI教程
→ 调用 search_bilibili(keyword="AI教程", order="click", limit=10)

**用户:** 总结一下这个视频讲了什么 BV1uxA8zZEvG
→ 调用 summarize_bilibili_video(bvid="BV1uxA8zZEvG")

---

## 功能边界与专一性

本Skill专注于**视频信息获取**，不包含以下功能：
- ❌ 视频下载
- ❌ 弹幕发送
- ❌ 点赞/投币/收藏
- ❌ 用户私信
- ❌ 评论区互动

如需上述功能，建议另行开发专用Skill。
