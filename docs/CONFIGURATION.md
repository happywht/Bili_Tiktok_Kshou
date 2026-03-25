# 配置说明文档

本文档详细说明 VideoHub 多平台搜索 API 的配置方法，包括环境变量设置和各平台 Cookie 获取方法。

## 目录

- [环境变量概览](#环境变量概览)
- [配置文件设置](#配置文件设置)
- [B站 Cookie 获取](#b站-cookie-获取)
- [抖音 Cookie 获取](#抖音-cookie-获取)
- [小红书 Cookie 获取](#小红书-cookie-获取)
- [高级配置](#高级配置)

---

## 环境变量概览

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `DEBUG` | 调试模式 | 否 | `false` |
| `BILIBILI_SESSDATA` | B站登录 Cookie | 是（B站搜索） | - |
| `DOUYIN_COOKIES` | 抖音完整 Cookie | 否 | - |
| `DOUYIN_TTWID` | 抖音 ttwid | 否 | - |
| `XIAOHONGSHU_COOKIES` | 小红书 Cookie | 否 | - |
| `API_PREFIX` | API 路由前缀 | 否 | `/api/v1` |
| `CORS_ORIGINS` | CORS 允许源 | 否 | `*` |

---

## 配置文件设置

### 1. 创建配置文件

复制环境变量模板：

```bash
cp .env.example .env
```

### 2. 编辑配置文件

打开 `.env` 文件，填入你的配置：

```env
# 应用配置
DEBUG=false

# B站配置
BILIBILI_SESSDATA=your_sessdata_here

# 抖音配置
DOUYIN_COOKIES=your_full_cookies_here

# API 配置
API_PREFIX=/api/v1
CORS_ORIGINS=*
```

### 3. 配置文件示例

```env
# .env 文件示例

# ============ 应用配置 ============
DEBUG=false

# ============ B站配置 ============
BILIBILI_SESSDATA=a%2Bb%2Fc%3D%2A%2F...

# ============ 抖音配置 ============
DOUYIN_COOKIES=ttwid=1%7C...; passport_csrf_token=...; sid_guard=...
# 或者仅配置 ttwid（功能可能受限）
DOUYIN_TTWID=1%7Cxxx%7C...

# ============ 小红书配置（待实现） ============
XIAOHONGSHU_COOKIES=

# ============ API 配置 ============
API_PREFIX=/api/v1

# ============ CORS 配置 ============
# 多个源用逗号分隔，* 表示允许所有
CORS_ORIGINS=*
# 或指定允许的源
# CORS_ORIGINS=http://localhost:3000,https://example.com
```

---

## B站 Cookie 获取

B站搜索需要登录态，通过 `SESSDATA` Cookie 实现。

### 方法一：Chrome 浏览器

1. **打开 B站并登录**

   访问 https://www.bilibili.com 并登录你的账号。

2. **打开开发者工具**

   - 按 `F12` 键
   - 或右键页面 -> "检查"
   - 或菜单 -> "更多工具" -> "开发者工具"

3. **查看 Cookies**

   - 切换到 **Application** 标签页
   - 左侧菜单展开 **Cookies** -> 点击 `https://www.bilibili.com`
   - 在列表中找到 `SESSDATA`

4. **复制 SESSDATA 值**

   - 双击 `SESSDATA` 的值
   - 复制完整的值（类似 `a%2Bb%2Fc%3D...` 的字符串）

5. **配置到 .env 文件**

   ```env
   BILIBILI_SESSDATA=复制的SESSDATA值
   ```

### 方法二：Firefox 浏览器

1. 打开 https://www.bilibili.com 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 **存储** 标签页
4. 展开 **Cookie** -> `https://www.bilibili.com`
5. 找到 `SESSDATA`，双击复制值

### 方法三：Edge 浏览器

1. 打开 https://www.bilibili.com 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 **应用程序** 标签页
4. 左侧 **Cookie** -> `https://www.bilibili.com`
5. 找到 `SESSDATA`，复制值

### 注意事项

- **有效期**: SESSDATA 有效期约 30 天，过期后需要重新获取
- **安全**: 不要泄露你的 SESSDATA，它相当于登录凭证
- **编码**: SESSDATA 值包含 URL 编码字符（如 `%2B`），直接复制即可，无需解码

### 验证配置

启动服务后，访问 http://localhost:8000/api/v1/search/bilibili?keyword=test 验证是否配置成功。

---

## 抖音 Cookie 获取

抖音搜索需要登录态，推荐使用完整 Cookie 字符串。

### 方法一：完整 Cookie（推荐）

1. **打开抖音网页版并登录**

   访问 https://www.douyin.com 并登录（可扫码登录）。

2. **打开开发者工具**

   按 `F12` 打开开发者工具。

3. **获取完整 Cookie**

   **方法 A - 通过 Network 请求：**
   - 切换到 **Network** 标签页
   - 刷新页面
   - 点击任意一个请求
   - 在右侧 **Headers** 中找到 `Cookie` 字段
   - 复制完整的 Cookie 值

   **方法 B - 通过 Application：**
   - 切换到 **Application** 标签页
   - 左侧 **Cookies** -> `https://www.douyin.com`
   - 手动拼接所有 Cookie（格式：`name1=value1; name2=value2; ...`）

4. **配置到 .env 文件**

   ```env
   DOUYIN_COOKIES=ttwid=1%7Cxxx; passport_csrf_token=yyy; sid_guard=zzz; ...
   ```

### 方法二：仅 ttwid（功能受限）

如果只需要基本搜索功能，可以只配置 `ttwid`：

1. 按上述步骤打开 Cookie 列表
2. 找到 `ttwid` 并复制其值
3. 配置：

   ```env
   DOUYIN_TTWID=ttwid的值
   ```

**注意**: 仅使用 ttwid 可能会遇到更多限制和验证码。

### 关键 Cookie 说明

| Cookie 名称 | 说明 | 重要性 |
|------------|------|--------|
| `ttwid` | 设备标识 | 必需 |
| `passport_csrf_token` | CSRF 令牌 | 重要 |
| `sid_guard` | 会话保护 | 重要 |
| `uid_tt` | 用户标识 | 可选 |
| `sessionid` | 会话 ID | 可选 |

### 验证配置

```bash
curl "http://localhost:8000/api/v1/search/douyin?keyword=test"
```

---

## 小红书 Cookie 获取

小红书平台暂未完全实现，以下为预留配置说明。

### 获取方法

1. 访问 https://www.xiaohongshu.com 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 **Application** -> **Cookies**
4. 复制需要的 Cookie 值

### 配置

```env
XIAOHONGSHU_COOKIES=your_cookies_here
```

---

## 高级配置

### CORS 配置

控制跨域资源共享（CORS）设置。

```env
# 允许所有源（开发环境）
CORS_ORIGINS=*

# 允许特定源（生产环境推荐）
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# 允许多个源
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://example.com
```

### API 前缀

自定义 API 路由前缀：

```env
# 默认
API_PREFIX=/api/v1

# 自定义
API_PREFIX=/api/v2
```

### 调试模式

开启调试模式会输出更多日志信息：

```env
DEBUG=true
```

---

## 配置最佳实践

### 安全建议

1. **不要提交 .env 文件到版本控制**
   - 确保 `.gitignore` 包含 `.env`
   - 只提交 `.env.example` 模板

2. **定期更新 Cookie**
   - B站 Cookie 约 30 天过期
   - 抖音 Cookie 可能更短
   - 设置提醒定期更新

3. **使用环境变量**
   - 生产环境使用系统环境变量
   - 敏感信息不要硬编码

### 生产环境配置

```env
# 生产环境 .env 示例
DEBUG=false

# 从环境变量读取敏感信息
# 或使用密钥管理服务
BILIBILI_SESSDATA=${BILIBILI_SESSDATA}
DOUYIN_COOKIES=${DOUYIN_COOKIES}

# 限制 CORS 源
CORS_ORIGINS=https://yourdomain.com
```

### Docker 环境配置

使用 Docker 时，通过 `-e` 参数传递环境变量：

```bash
docker run -d \
  -p 8000:8000 \
  -e BILIBILI_SESSDATA=your_sessdata \
  -e DOUYIN_COOKIES=your_cookies \
  -e CORS_ORIGINS=https://yourdomain.com \
  videohub-api
```

或使用 `docker-compose.yml`：

```yaml
version: '3'
services:
  api:
    image: videohub-api
    ports:
      - "8000:8000"
    environment:
      - BILIBILI_SESSDATA=${BILIBILI_SESSDATA}
      - DOUYIN_COOKIES=${DOUYIN_COOKIES}
      - DEBUG=false
      - CORS_ORIGINS=*
```

---

## 常见问题

### Q: Cookie 配置正确但仍然报错？

1. 检查 Cookie 是否完整复制（没有多余空格）
2. 确认账号状态正常
3. 尝试重新登录并获取新 Cookie
4. 检查是否有特殊字符需要转义

### Q: Cookie 多久过期？

- **B站 SESSDATA**: 约 30 天
- **抖音 Cookie**: 约 7-14 天（取决于平台策略）
- **小红书 Cookie**: 待确认

### Q: 如何判断 Cookie 是否有效？

访问对应的搜索接口，如果返回 `CookieExpiredError` 则表示 Cookie 已过期。

### Q: 多个 Cookie 如何配置？

目前每个平台只支持单一 Cookie 配置。如需多账号，请部署多个实例。

---

**相关文档**: [API 文档](API.md) | [故障排除](TROUBLESHOOTING.md)
