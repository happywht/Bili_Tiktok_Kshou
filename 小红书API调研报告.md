# 小红书(Xiaohongshu)搜索API实现方案调研报告

## 📋 执行摘要

本报告针对小红书平台搜索功能的四种实现方案进行了深入调研,包括官方API、Web逆向、浏览器自动化和第三方库。基于技术可行性、维护成本、法律风险等维度,**推荐使用 DrissionPage 浏览器自动化方案**作为首选方案。

---

## 🎯 方案对比总览

| 方案 | 可行性评分 | 技术难度 | 维护成本 | 法律风险 | 推荐指数 |
|------|-----------|---------|---------|---------|---------|
| **1. 官方API** | 6/10 | 低 | 低 | 无 | ⭐⭐⭐ |
| **2. Web逆向(Shield)** | 8/10 | 极高 | 极高 | 中 | ⭐⭐ |
| **3. DrissionPage自动化** | **9/10** | 中 | 中 | 低 | ⭐⭐⭐⭐⭐ |
| **4. MediaCrawler库** | 8/10 | 低 | 中 | 低 | ⭐⭐⭐⭐ |

---

## 📊 方案一:官方API

### 基本信息
- **开放平台地址**: https://open.xiaohongshu.com
- **API文档**: https://xiaohongshu.apifox.cn/doc-2810914
- **适用对象**: 企业开发者、商家

### 申请条件
1. **企业资质**:
   - 需要营业执照
   - 企业实名认证
   - 年流水要求(部分API需500万+)

2. **应用审核**:
   - 详细的使用场景说明
   - 数据安全承诺
   - 等待审核周期(通常1-2周)

3. **接口权限**:
   - 笔记详情API
   - 商品详情API
   - 评论数据API(需额外申请)

### 可行性分析

**✅ 优势:**
- 合法合规,无法律风险
- 稳定性高,有官方支持
- 数据结构化,质量有保障
- 无需维护加密算法

**❌ 劣势:**
- **个人开发者无法申请**(需企业资质)
- 审核门槛高,流程复杂
- **搜索功能API可能不开放**
- 有调用频率限制
- 部分接口需要付费

### 官方API示例

```python
import requests

# 官方API调用示例(需申请权限)
url = 'https://api.xiaohongshu.com/api/notes'
headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
}

params = {
    'keyword': 'Python教程',
    'page': 1,
    'page_size': 20
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
```

### 评分:6/10

**结论**:如果是企业用户且预算充足,这是最稳妥的方案。但对于个人开发者或小型项目,门槛过高。

---

## 🔐 方案二:Web逆向(Shield签名)

### Shield机制概述

小红书的Shield签名是一个复杂的多层加密机制,包含:

1. **核心参数**:
   - `shield`: 主签名参数(XY前缀的Base64字符串)
   - `xy-common-params`: 通用参数
   - `xy-platform-info`: 平台信息
   - `xy-direction`: 请求方向
   - `x-s`: Web端签名参数
   - `x-t`: 时间戳参数

2. **加密流程**:
   ```
   xy-ter-str (Base64)
       ↓
   AES-128解密 (DeviceID作为密钥)
       ↓
   MD5-HMAC (URL + 参数 + 密钥)
       ↓
   RC4加密 + Base64编码
       ↓
   Shield签名 ("XY"前缀)
   ```

### 技术实现

#### 开源实现1:Xiaohongshu-Shield-Algorithm
- **GitHub**: https://github.com/kowrish/Xiaohongshu-Shield-Algorithm
- **最新验证**: 小红书安卓APP v9.19.2 (2026-03-10)
- **技术特点**:
  - 纯Python实现,无需模拟器
  - 完整还原AES白盒、MD5变种、RC4加密
  - 需要从真机提取HMAC密钥

#### 核心代码示例

```python
from shield_sdk import ShieldSdk, GlobalData
import asyncio

# 配置设备参数
GlobalData.build_id = "9192809"  # APP版本号
GlobalData.device_id = "your-device-uuid"
GlobalData.hmac = "base64-key"  # 需从真机提取

# 生成Shield签名
async def generate_shield():
    sdk = ShieldSdk(
        build_id="9192809",
        device_id="9932DAF2-0503-4D8C-A5DD-3D94F8F63C27",
        hmac_key="your-hmac-base64"
    )

    sign_input = "/api/sns/v5/note/comment/list?note_id=xxx&num=15"
    signature = await sdk.get_shield(sign_input)
    return signature

# 使用签名发起请求
async def search_notes(keyword):
    shield = await generate_shield()

    headers = {
        'shield': shield,
        'xy-common-params': 'SUE=1&active_ctry=CN&app_id=ECFAAF02...',
        'xy-platform-info': 'platform=iOS&version=9.19.2&build=9192809...',
        'xy-direction': '71',
    }

    url = f"https://edith.xiaohongshu.com/api/sns/v5/search/notes?keyword={keyword}"
    response = requests.get(url, headers=headers)
    return response.json()
```

### 关键难点

1. **HMAC密钥提取**:
   - 需要**Root权限**
   - 从`/data/data/com.xingin.xhs/shared_prefs/s.xml`提取
   - 命令: `adb shell "su -c 'cat /data/data/com.xingin.xhs/shared_prefs/s.xml'"`

2. **版本更新频繁**:
   - 小红书每1-2周更新一次
   - 加密算法可能随之改变
   - 需要持续维护

3. **设备指纹管理**:
   - DeviceID必须与请求头一致
   - 需要模拟真实设备特征
   - 防止被识别为爬虫

4. **白盒AES复杂度**:
   - 自定义T-Box查找表
   - 需要从SO文件提取常量
   - 逆向难度极大

### 可行性分析

**✅ 优势:**
- 性能高效,无需浏览器
- 可大规模并发请求
- 数据获取速度快

**❌ 劣势:**
- **技术门槛极高**(需要逆向SO文件)
- **需要Root真机**提取密钥
- **维护成本极高**(版本更新需重新逆向)
- 存在一定的法律风险
- 可能触发风控机制

### 评分:8/10(技术可行性) / 2/10(实际可用性)

**结论**:技术可行但维护成本过高,适合专业爬虫团队,不适合个人开发者。

---

## 🌐 方案三:DrissionPage浏览器自动化(⭐推荐方案)

### 技术概述

DrissionPage是一个创新的Python自动化工具,结合了浏览器自动化和HTTP请求的优势,特别适合处理小红书这类有复杂加密的网站。

### 核心优势

1. **无需逆向**:
   - 利用浏览器环境自动处理签名
   - 不需要破解Shield算法
   - 通过监听网络请求获取数据

2. **绕过检测**:
   - 使用真实浏览器环境
   - 难以被反爬虫系统识别
   - 支持Cookie持久化

3. **简单易用**:
   - API设计友好
   - 学习曲线平缓
   - 文档完善

### 实现方案

#### 基础实现

```python
from DrissionPage import ChromiumPage
from DataRecorder import Recorder
import time

class XiaohongshuCrawler:
    def __init__(self):
        self.page = ChromiumPage()
        self.recorder = Recorder('xiaohongshu_data.xlsx')

    def login(self):
        """扫码登录"""
        self.page.get('https://www.xiaohongshu.com/explore')
        input('请扫码登录,完成后按回车继续...')

    def search_notes(self, keyword, max_count=20):
        """搜索笔记"""
        # 监听数据接口
        self.page.listen.start('web/v1/feed')

        # 访问搜索页面
        search_url = f'https://www.xiaohongshu.com/search_result?keyword={keyword}'
        self.page.get(search_url)
        self.page.wait.load_start()

        notes = []
        crawled_ids = set()

        while len(notes) < max_count:
            # 获取笔记卡片
            cards = self.page.eles('xpath://section[@data-index]')

            for card in cards:
                if len(notes) >= max_count:
                    break

                # 去重
                index = card.attr('data-index')
                if index in crawled_ids:
                    continue
                crawled_ids.add(index)

                # 点击卡片获取详情
                card.click(by_js=True)
                res = self.page.listen.wait(count=1, timeout=3)

                if res and res.response:
                    data = res.response.body
                    note_info = self.parse_note_data(data)
                    notes.append(note_info)

                    # 保存数据
                    self.recorder.add_data(note_info)
                    self.recorder.record()

                # 关闭详情页
                self.page.ele('xpath:/html/body/div[5]/div[2]/div').click()
                self.page.wait.load_start()

            # 滚动加载更多
            self.page.scroll.down(1000)
            time.sleep(2)

        return notes

    def parse_note_data(self, data):
        """解析笔记数据"""
        return {
            'note_id': self.find_value(data, 'note_id'),
            'title': self.find_value(data, 'title'),
            'description': self.find_value(data, 'desc'),
            'author': self.find_value(data, 'nickname'),
            'likes': self.find_value(data, 'liked_count'),
            'comments': self.find_value(data, 'comment_count'),
            'cover_url': self.find_value(data, 'cover'),
            'note_url': f"https://www.xiaohongshu.com/explore/{self.find_value(data, 'note_id')}"
        }

    def find_value(self, data, key):
        """递归查找字典中的值"""
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key:
                    return v
                result = self.find_value(v, key)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_value(item, key)
                if result:
                    return result
        return None

# 使用示例
if __name__ == "__main__":
    crawler = XiaohongshuCrawler()
    crawler.login()

    notes = crawler.search_notes("Python教程", max_count=20)
    print(f"共爬取{len(notes)}条笔记")
```

#### 高级特性:Cookie持久化

```python
import json
import os

class PersistentXiaohongshuCrawler(XiaohongshuCrawler):
    COOKIE_FILE = os.path.expanduser('~/.xiaohongshu_cookies.json')

    def load_cookies(self):
        """加载已保存的Cookie"""
        if os.path.exists(self.COOKIE_FILE):
            with open(self.COOKIE_FILE, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    self.page.set.cookies(cookie)
            return True
        return False

    def save_cookies(self):
        """保存Cookie到文件"""
        cookies = self.page.cookies()
        with open(self.COOKIE_FILE, 'w') as f:
            json.dump(cookies, f)

    def login_with_cache(self):
        """带缓存的登录"""
        if not self.load_cookies():
            self.login()
            self.save_cookies()
```

### 完整项目参考

**GitHub**: https://github.com/Kihara-Ri/REDnote-crawler

该项目已实现:
- ✅ 扫码登录
- ✅ 关键词搜索
- ✅ 笔记详情获取
- ✅ 自动翻页
- ✅ Excel导出

### 可行性分析

**✅ 优势:**
- **无需逆向**,技术门槛低
- **稳定性高**,不受算法更新影响
- **维护成本低**,主要维护元素定位
- **法律风险低**,模拟真实用户行为
- 支持所有平台功能
- 数据质量高

**❌ 劣势:**
- 性能相对较低(需要启动浏览器)
- 资源占用较多
- 不适合超大规模爬取
- 需要处理登录态

### 评分:9/10

**结论**:这是**最推荐的方案**,平衡了技术难度、维护成本和稳定性。

---

## 📦 方案四:MediaCrawler第三方库

### 项目简介

**MediaCrawler**是一个开源的多平台爬虫项目,支持小红书、抖音、快手、B站等主流平台。

- **GitHub**: https://github.com/NanmiCoder/MediaCrawler
- **Stars**: 30,000+
- **最后更新**: 2026年3月(活跃维护)

### 核心特性

1. **多平台支持**:
   - 小红书、抖音、快手、B站、微博、贴吧、知乎

2. **功能丰富**:
   - ✅ 关键词搜索
   - ✅ 指定帖子爬取
   - ✅ 评论采集
   - ✅ 创作者主页
   - ✅ IP代理池
   - ✅ 评论词云生成

3. **技术架构**:
   - 基于Playwright浏览器自动化
   - 通过JS表达式获取签名参数
   - 无需逆向加密算法

### 快速使用

#### 安装

```bash
# 克隆项目
git clone https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler

# 安装依赖(推荐使用uv)
uv sync

# 安装浏览器驱动
uv run playwright install
```

#### 配置

```python
# config/base_config.py

# 平台配置
PLATFORM = "xhs"  # 小红书

# 登录方式
LOGIN_TYPE = "qrcode"  # 二维码登录

# 爬取类型
CRAWLER_TYPE = "search"  # 搜索模式

# 搜索关键词
KEYWORDS = ["Python教程", "数据分析", "机器学习"]

# 是否开启评论爬取
ENABLE_GET_COMMENTS = True

# 保存格式
SAVE_DATA_OPTION = "csv"  # csv/json/xlsx
```

#### 运行

```bash
# 搜索模式
uv run main.py --platform xhs --lt qrcode --type search

# 指定帖子详情
uv run main.py --platform xhs --lt qrcode --type detail
```

#### Python调用示例

```python
from media_crawler import XiaohongshuCrawler

# 初始化爬虫
crawler = XiaohongshuCrawler(
    platform="xhs",
    login_type="qrcode",
    crawler_type="search",
    keywords=["Python教程"]
)

# 执行爬取
results = await crawler.run()

# 处理结果
for note in results:
    print(f"标题: {note['title']}")
    print(f"作者: {note['author']}")
    print(f"点赞: {note['likes']}")
    print(f"链接: {note['url']}")
```

### 数据结构示例

```json
{
  "note_id": "64a1b2c3d4e5f6",
  "title": "Python数据分析入门教程",
  "description": "从零开始学习Python数据分析...",
  "author": "数据小王子",
  "author_id": "5f8d9a2b1c3e4d",
  "likes": 1520,
  "comments": 89,
  "collects": 234,
  "shares": 45,
  "cover_url": "https://sns-webpic-qc.xhscdn.com/...",
  "note_url": "https://www.xiaohongshu.com/explore/64a1b2c3d4e5f6",
  "publish_time": "2026-03-20 14:30:00",
  "tags": ["Python", "数据分析", "编程入门"]
}
```

### Pro版本特性

**MediaCrawlerPro**提供了更强大的功能:
- ✅ 去除Playwright依赖,更轻量
- ✅ 断点续爬功能
- ✅ 多账号+IP代理池
- ✅ 完整Linux支持
- ✅ 企业级代码架构

**获取方式**: 订阅制,详见 https://github.com/MediaCrawlerPro

### 可行性分析

**✅ 优势:**
- **开箱即用**,无需自己开发
- **功能完善**,覆盖常见需求
- **活跃维护**,社区支持好
- **文档详细**,易于上手
- 支持多平台

**❌ 劣势:**
- 定制化能力有限
- 依赖第三方项目更新
- Pro版本需要付费
- 可能包含不需要的功能

### 评分:8/10

**结论**:如果需求与项目功能匹配,这是最快的实现方式。适合快速原型开发和学习。

---

## 🎯 推荐方案

基于综合评估,**推荐使用方案三:DrissionPage浏览器自动化**

### 推荐理由

1. **技术可行性高**(9/10):
   - 无需逆向复杂算法
   - 技术门槛适中
   - 有完整开源参考

2. **维护成本低**:
   - 不受小红书算法更新影响
   - 主要维护页面元素定位
   - 社区活跃,问题易解决

3. **法律风险低**:
   - 模拟真实用户行为
   - 不破坏平台安全机制
   - 仅获取公开数据

4. **与现有B站项目兼容**:
   - 技术栈相似
   - 可复用部分代码
   - 易于集成

### 实现路线图

#### 第一阶段:原型开发(1-2天)
1. 实现基础登录功能
2. 完成关键词搜索
3. 提取笔记基本信息
4. 数据保存到CSV

#### 第二阶段:功能完善(2-3天)
1. Cookie持久化
2. 评论数据爬取
3. 异常处理机制
4. 翻页和滚动优化

#### 第三阶段:性能优化(1-2天)
1. 并发爬取
2. 代理IP支持
3. 数据去重
4. 断点续爬

### 参考你的B站实现

你的B站搜索代码结构非常清晰,小红书实现可以参考:

```python
# 参考bilibili_search.py的结构
class XiaohongshuSearchAgent:
    """小红书笔记搜索Agent - 使用DrissionPage"""

    def __init__(self):
        self.results: List[XiaohongshuNote] = []
        self.page = ChromiumPage()

    def search_notes_sync(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[XiaohongshuNote]:
        """同步搜索小红书笔记"""
        # 实现搜索逻辑
        pass

    def get_note_detail(self, note_id: str) -> Dict:
        """获取笔记详情"""
        pass

    def print_results(self):
        """打印搜索结果"""
        pass
```

---

## ⚠️ 注意事项

### 法律合规
1. **仅获取公开数据**
2. **遵守robots.txt**
3. **控制请求频率**
4. **尊重用户隐私**
5. **不用于商业用途**(除非获得授权)

### 技术建议
1. **设置请求间隔**: 1-3秒随机延迟
2. **使用代理IP**: 避免IP被封
3. **定期更新Cookie**: 保持登录态
4. **异常处理**: 网络错误、元素定位失败等
5. **数据验证**: 检查数据完整性

### 风险提示
1. **账号风险**: 频繁爬取可能导致账号受限
2. **数据准确性**: 页面结构变化可能导致爬取失败
3. **法律风险**: 大规模爬取需咨询法律意见

---

## 📚 参考资源

### 官方资源
- 小红书开放平台: https://open.xiaohongshu.com
- API文档: https://xiaohongshu.apifox.cn/doc-2810914

### 开源项目
1. **DrissionPage**: https://github.com/g1879/DrissionPage
   - 官网: https://www.drissionpage.cn
   - 文档详细,社区活跃

2. **MediaCrawler**: https://github.com/NanmiCoder/MediaCrawler
   - 30K+ stars
   - 多平台支持

3. **REDnote-crawler**: https://github.com/Kihara-Ri/REDnote-crawler
   - 专注于小红书
   - DrissionPage实现

4. **Xiaohongshu-Shield-Algorithm**: https://github.com/kowrish/Xiaohongshu-Shield-Algorithm
   - Shield算法纯Python实现
   - 技术研究价值高

5. **RedNote-MCP**: https://github.com/iFurySt/RedNote-MCP
   - MCP协议支持
   - 可集成到AI工具

### 技术文章
1. CSDN: [使用DrissionPage自动化采集小红书笔记](https://blog.csdn.net/2401_87328929/article/details/149253153)
2. CSDN: [Shield参数逆向分析与实现详解](https://blog.csdn.net/weixin_74305707/article/details/156013535)
3. 阿里云: [小红书商品与笔记详情API的申请及调用方法](https://developer.aliyun.com/article/1642615)

---

## 📝 总结

### 最终推荐

**方案**: DrissionPage浏览器自动化
**理由**: 技术可行性高、维护成本低、法律风险低
**预计开发时间**: 3-5天
**维护难度**: 低

### 实施建议

1. **短期(1周内)**:
   - 使用DrissionPage实现基础搜索功能
   - 参考REDnote-crawler项目
   - 完成MVP版本

2. **中期(1个月内)**:
   - 完善功能(评论爬取、详情页)
   - 优化性能(并发、代理)
   - 完善异常处理

3. **长期**:
   - 持续维护元素定位
   - 监控小红书页面变化
   - 考虑商业API(如果有预算)

### 技术栈建议

```yaml
核心依赖:
  - DrissionPage: ^4.0.0
  - DataRecorder: ^1.0.0
  - loguru: ^0.7.0

可选依赖:
  - playwright: ^1.40.0  # 如果使用MediaCrawler
  - pandas: ^2.0.0       # 数据分析
  - openpyxl: ^3.1.0     # Excel支持

开发环境:
  - Python: 3.9+
  - Chrome/Edge: 最新版
```

---

## 📞 技术支持

如果在实施过程中遇到问题,可以:
1. 查阅DrissionPage官方文档
2. 参考开源项目Issue
3. 加入相关技术社区

---

**报告生成时间**: 2026-03-24
**调研人员**: Claude Code Agent
**报告版本**: v1.0
