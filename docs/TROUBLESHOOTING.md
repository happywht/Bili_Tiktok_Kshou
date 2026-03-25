# 故障排除指南

本文档提供 VideoHub 多平台搜索 API 的常见问题和解决方案。

## 目录

- [快速诊断](#快速诊断)
- [通用问题](#通用问题)
- [B站相关问题](#b站相关问题)
- [抖音相关问题](#抖音相关问题)
- [小红书相关问题](#小红书相关问题)
- [网络问题](#网络问题)
- [性能问题](#性能问题)
- [错误代码参考](#错误代码参考)

---

## 快速诊断

### 服务健康检查

```bash
# 检查服务是否运行
curl http://localhost:8000/api/v1/health

# 预期响应
{
  "success": true,
  "code": 200,
  "message": "healthy",
  "data": {
    "status": "running",
    "version": "2.0.0"
  }
}
```

### 检查平台状态

```bash
# 获取平台可用性
curl http://localhost:8000/api/v1/platforms
```

### 检查配置

```bash
# 确认 .env 文件存在
ls -la .env

# 检查关键配置（不要在生产环境执行）
grep "SESSDATA" .env
```

---

## 通用问题

### 1. 服务无法启动

**症状**: 运行 `uvicorn api.main:app` 后服务无法启动

**可能原因**:
- 端口被占用
- 依赖未安装
- Python 版本不兼容

**解决方案**:

```bash
# 检查端口占用（Windows）
netstat -ano | findstr :8000

# 检查端口占用（Linux/Mac）
lsof -i :8000

# 使用其他端口启动
uvicorn api.main:app --port 8001

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 检查 Python 版本（需要 3.8+）
python --version
```

### 2. API 返回 500 错误

**症状**: 所有请求都返回 500 内部服务器错误

**诊断步骤**:

1. 查看服务日志
2. 检查配置文件格式
3. 确认依赖完整

**解决方案**:

```bash
# 开启调试模式查看详细错误
# 在 .env 中设置
DEBUG=true

# 重启服务
uvicorn api.main:app --reload

# 查看详细日志
```

### 3. 请求超时

**症状**: 请求长时间无响应

**可能原因**:
- 网络问题
- 目标平台响应慢
- 服务器资源不足

**解决方案**:

```bash
# 增加超时时间（在代码中调整）
# 或使用异步请求

# 检查网络连接
ping www.bilibili.com
ping www.douyin.com

# 检查服务器资源
# Linux
top
# Windows
taskmgr
```

---

## B站相关问题

### 1. Cookie 过期

**症状**: 返回 `CookieExpiredError` 或 `BilibiliCookieExpiredError`

**错误响应示例**:
```json
{
  "success": false,
  "code": 401,
  "message": "B站登录状态已过期",
  "error": {
    "type": "BilibiliCookieExpiredError"
  }
}
```

**解决方案**:

1. 重新获取 SESSDATA（参考 [配置文档](CONFIGURATION.md#b站-cookie-获取)）
2. 更新 `.env` 文件中的 `BILIBILI_SESSDATA`
3. 重启服务

```bash
# 更新配置后重启
# 方式1: 手动重启
# Ctrl+C 停止服务，然后重新启动
uvicorn api.main:app --reload

# 方式2: 如果使用 --reload，保存 .env 后服务会自动重载
```

### 2. 请求频率过高

**症状**: 返回 `RateLimitError`，HTTP 状态码 429

**错误响应示例**:
```json
{
  "success": false,
  "code": 429,
  "message": "请求过于频繁",
  "error": {
    "type": "RateLimitError"
  }
}
```

**解决方案**:

1. 降低请求频率，每次请求间隔 1-2 秒
2. 实现请求队列
3. 添加重试机制

```python
import time
import requests

def search_with_retry(keyword, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(
                f'http://localhost:8000/api/v1/search/bilibili',
                params={'keyword': keyword}
            )
            if response.status_code == 429:
                wait_time = 2 ** i  # 指数退避
                print(f"触发限制，等待 {wait_time} 秒...")
                time.sleep(wait_time)
                continue
            return response.json()
        except Exception as e:
            print(f"请求失败: {e}")
            time.sleep(2)
    return None
```

### 3. 搜索无结果

**症状**: 搜索返回空列表，但确认有关键词相关内容

**可能原因**:
- Cookie 无效或未配置
- 关键词被过滤
- 搜索参数错误

**排查步骤**:

```bash
# 1. 测试简单关键词
curl "http://localhost:8000/api/v1/search/bilibili?keyword=Python"

# 2. 检查 Cookie 是否配置
# 查看启动日志是否有警告

# 3. 尝试不同排序方式
curl "http://localhost:8000/api/v1/search/bilibili?keyword=Python&order=click"
```

### 4. 视频详情获取失败

**症状**: 获取视频详情返回错误

**可能原因**:
- BV 号格式错误
- 视频已删除
- 权限限制

**解决方案**:

```bash
# 确认 BV 号格式正确
# 正确格式: BV1xx411c7mD（以 BV 开头）
curl "http://localhost:8000/api/v1/videos/BV1xx411c7mD"

# 错误格式
# curl "http://localhost:8000/api/v1/videos/1xx411c7mD"  # 缺少 BV 前缀
```

---

## 抖音相关问题

### 1. 需要验证码

**症状**: 返回 `CaptchaDetectedError`

**错误响应示例**:
```json
{
  "success": false,
  "code": 403,
  "message": "需要完成验证码验证",
  "error": {
    "type": "CaptchaDetectedError"
  }
}
```

**解决方案**:

1. 在浏览器中打开 https://www.douyin.com
2. 手动完成验证码验证
3. 重新获取 Cookie
4. 更新 `.env` 中的 `DOUYIN_COOKIES`
5. 重启服务

### 2. Cookie 过期

**症状**: 返回 `DouyinCookieExpiredError`

**解决方案**:

1. 重新登录抖音网页版
2. 获取新的完整 Cookie
3. 更新 `.env` 文件
4. 重启服务

### 3. 搜索结果为空

**可能原因**:
- Cookie 未配置或不完整
- 请求被拦截
- 网络问题

**解决方案**:

```bash
# 确保配置了完整 Cookie
# .env 文件
DOUYIN_COOKIES=ttwid=xxx; passport_csrf_token=yyy; ...

# 测试搜索
curl "http://localhost:8000/api/v1/search/douyin?keyword=test"
```

### 4. 抖音平台不可用

**症状**: 返回 `DouyinNotAvailableError`

**可能原因**:
- Cookie 未配置
- 服务初始化失败

**解决方案**:

```bash
# 检查配置
grep "DOUYIN" .env

# 确保至少配置了 ttwid
DOUYIN_TTWID=your_ttwid_here
# 或完整 Cookie
DOUYIN_COOKIES=your_cookies_here
```

---

## 小红书相关问题

### 平台暂未开放

**症状**: 返回 `XiaohongshuNotAvailableError`

**说明**: 小红书平台功能正在开发中，暂不可用。

**错误响应**:
```json
{
  "success": false,
  "code": 503,
  "message": "小红书服务暂时不可用",
  "error": {
    "type": "XiaohongshuNotAvailableError"
  }
}
```

---

## 网络问题

### 1. 连接超时

**症状**: `TimeoutError` 或请求无响应

**解决方案**:

```bash
# 检查网络连接
ping www.bilibili.com
ping www.douyin.com

# 检查防火墙设置
# Windows: 控制面板 -> Windows 防火墙
# Linux: sudo ufw status

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

### 2. DNS 解析失败

**症状**: 无法解析域名

**解决方案**:

```bash
# 测试 DNS 解析
nslookup www.bilibili.com
nslookup www.douyin.com

# 更换 DNS 服务器
# Windows: 网络适配器设置 -> DNS
# Linux: 编辑 /etc/resolv.conf
# nameserver 8.8.8.8
# nameserver 114.114.114.114
```

### 3. 图片加载失败

**症状**: 图片代理返回错误

**解决方案**:

```bash
# 检查图片 URL 是否正确编码
# 正确: URL 编码后的
curl "http://localhost:8000/api/v1/proxy-image?url=https%3A%2F%2Fi0.hdslb.com%2Fbfs%2Fxxx.jpg"

# 错误: 未编码的 URL
# curl "http://localhost:8000/api/v1/proxy-image?url=https://i0.hdslb.com/bfs/xxx.jpg"
```

---

## 性能问题

### 1. 响应缓慢

**可能原因**:
- 目标平台响应慢
- 服务器资源不足
- 并发请求过多

**解决方案**:

```bash
# 检查服务器资源
# Linux
top
free -h
df -h

# Windows
taskmgr

# 限制并发请求数
# 在代码中实现请求队列

# 使用生产模式启动（多 worker）
uvicorn api.main:app --workers 4
```

### 2. 内存占用过高

**解决方案**:

```bash
# 限制 worker 数量
uvicorn api.main:app --workers 2

# 监控内存使用
# Linux
ps aux | grep uvicorn

# 定期重启服务（使用进程管理器如 supervisor, pm2）
```

---

## 错误代码参考

### HTTP 状态码

| 状态码 | 说明 | 常见原因 |
|--------|------|---------|
| 200 | 成功 | 请求正常处理 |
| 400 | 参数错误 | 请求参数格式不正确 |
| 401 | 未授权 | Cookie 过期或无效 |
| 403 | 禁止访问 | 需要验证码、IP 被封 |
| 404 | 未找到 | 内容不存在 |
| 429 | 请求过多 | 触发频率限制 |
| 500 | 服务器错误 | 内部错误、配置问题 |
| 502 | 网关错误 | 上游服务不可用 |
| 503 | 服务不可用 | 平台服务暂停 |
| 504 | 网关超时 | 请求超时 |

### B站错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 0 | 成功 | - |
| -101 | 账号未登录 | 更新 SESSDATA |
| -400 | 请求错误 | 检查参数 |
| -403 | 权限不足 | 检查账号状态 |
| -404 | 未找到 | 内容不存在 |
| -412 | 请求被拦截 | 更新 Cookie，降低频率 |

### 抖音错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 0 | 成功 | - |
| 8 | 需要登录 | 更新 Cookie |
| 2151 | 频率限制 | 降低请求频率 |
| 2154 | 登录过期 | 更新 Cookie |

---

## 日志分析

### 查看服务日志

```bash
# 开发模式日志会直接输出到控制台
uvicorn api.main:app --reload

# 生产模式可重定向到文件
uvicorn api.main:app > app.log 2>&1 &

# 实时查看日志
tail -f app.log
```

### 常见日志信息

```
# 正常启动
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

# Cookie 配置警告
WARNING:  BILIBILI_SESSDATA not configured
WARNING:  DOUYIN_COOKIES not configured

# 请求错误
ERROR:    Exception in search: Cookie expired
ERROR:    Rate limit exceeded
```

---

## 获取帮助

如果以上方案都无法解决问题：

1. **查看 API 文档**: [API.md](API.md)
2. **检查配置**: [CONFIGURATION.md](CONFIGURATION.md)
3. **提交 Issue**: 在项目仓库提交 Issue，包含：
   - 错误信息（完整 JSON 响应）
   - 请求参数
   - 服务日志（去除敏感信息）
   - 环境信息（Python 版本、操作系统）

---

**相关文档**: [API 文档](API.md) | [配置说明](CONFIGURATION.md)
