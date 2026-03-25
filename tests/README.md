# 测试指南

## 目录结构

```
tests/
├── __init__.py           # 测试包初始化
├── conftest.py           # pytest配置和夹具
├── test_bilibili/        # B站测试
│   ├── __init__.py
│   └── test_service.py
├── test_douyin/          # 抖音测试
│   ├── __init__.py
│   └── test_service.py
└── test_xiaohongshu/     # 小红书测试
    ├── __init__.py
    └── test_service.py

tools/
├── __init__.py
├── douyin_interactive_test.py  # 抖音交互式测试工具
└── run_all_tests.py            # 测试运行器
```

## 运行测试

### 运行所有测试

```bash
# 使用pytest
pytest

# 或使用工具脚本
python tools/run_all_tests.py
```

### 运行特定平台测试

```bash
# B站测试
pytest -m bilibili

# 抖音测试
pytest -m douyin

# 小红书测试
pytest -m xiaohongshu
```

### 跳过慢速测试

```bash
pytest -m "not slow"
```

### 详细输出

```bash
pytest -v --tb=long
```

## 测试标记

| 标记 | 说明 |
|------|------|
| `bilibili` | B站相关测试 |
| `douyin` | 抖音相关测试 |
| `xiaohongshu` | 小红书相关测试 |
| `slow` | 慢速测试（需要网络请求或浏览器） |
| `interactive` | 需要用户交互的测试 |
| `integration` | 集成测试 |

## 手动测试工具

### 抖音交互式测试

用于调试验证码问题，支持可见浏览器模式：

```bash
python tools/douyin_interactive_test.py
```

功能：
1. 可见浏览器模式 - 手动处理验证码
2. API模式 - 后台自动测试
3. Cookie状态检查

## 环境配置

确保 `.env` 文件包含以下配置：

```env
# B站
BILIBILI_SESSDATA=your_sessdata

# 抖音
DOUYIN_COOKIES=your_cookies

# 小红书（可选）
XIAOHONGSHU_COOKIES=your_cookies
```

## 注意事项

### 抖音测试

抖音搜索可能遇到验证码拦截，建议：
1. 先使用 `tools/douyin_interactive_test.py` 进行可见浏览器模式测试
2. 手动处理验证码后再运行自动化测试
3. 定期更新Cookie

### 小红书测试

小红书搜索需要安装 `xiaohongshu-cli`：

```bash
# 使用uv安装
uv tool install xiaohongshu-cli

# 或使用pipx安装
pipx install xiaohongshu-cli
```

如果CLI不可用，会自动回退到浏览器自动化方案。

## 清理的文件

以下冗余测试文件已被清理并整合到新的测试目录结构中：

- test_douyin_api.py
- test_douyin_complete.py
- test_douyin_detailed.py
- test_douyin_final.py
- test_douyin_fix.py
- test_douyin_fixed.py
- test_douyin_headless.py
- test_douyin_interactive.py (已移至 tools/)
- test_douyin_manual.py
- test_douyin_manual_captcha.py
- test_douyin_page_structure.py
- test_douyin_selectors.py
- test_douyin_service_fixed.py
- test_douyin_simple.py
- test_douyin_with_cookies.py
- check_douyin_captcha.py
- diagnose_douyin.py
