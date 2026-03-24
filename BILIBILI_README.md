# B站视频搜索 Agent

## 状态: 需要配置 Cookie 才能使用

B站搜索 API 现在需要登录状态，必须使用 SESSDATA Cookie 才能访问。

## 文件说明

```
/workspace/
├── bilibili_search.py           # 核心Agent类
├── bilibili_cli.py              # 命令行工具 (可选)
├── BILIBILI_AGENT_README.md     # 详细文档
└── skills/
    └── bilibili-search/
        ├── SKILL.md             # OpenClaw Skill 定义
        └── search.py            # Skill 执行脚本
```

## 快速使用

### 1. 获取 SESSDATA

1. 登录 [bilibili.com](https://www.bilibili.com)
2. F12 → Application → Cookies → bilibili.com
3. 复制 `SESSDATA` 的值

### 2. 命令行测试

```bash
export BILIBILI_SESSDATA="你的SESSDATA值"
python3 bilibili_search.py
```

### 3. Skill 调用

```bash
cd skills/bilibili-search
python3 search.py '{"keyword":"Python","limit":5}'
```

## 备选方案

如果无法获取 SESSDATA，可以考虑：

1. **使用 Playwright/Selenium** - 模拟浏览器行为
2. **使用第三方 B站 API 服务** - 如 bili-api 等
3. **改用 RSS/Feed** - 只获取特定UP主的更新

## API 限制

- 需要登录 Cookie (SESSDATA)
- 有频率限制，建议添加延时
- 搜索结果最多返回约1000条
