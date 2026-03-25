#!/usr/bin/env python3
"""
MediaCrawler Bridge - 子进程桥接脚本

通过子进程调用 MediaCrawler 进行平台搜索，将结果输出为 JSON。

使用方式:
    # 搜索抖音（默认无头模式，需先完成登录）
    python mediacrawler_bridge.py --platform dy --keyword "Python教程" --max-count 20

    # 搜索小红书
    python mediacrawler_bridge.py --platform xhs --keyword "美食推荐" --max-count 20

    # 首次登录（需要显示浏览器窗口，扫码登录）
    python mediacrawler_bridge.py --platform dy --keyword "test" --no-headless --max-count 1

    # 检查环境是否就绪
    python mediacrawler_bridge.py --check
"""
import sys
import os
import json
import asyncio
import types
import argparse
import traceback
from datetime import datetime


def setup_mocks():
    """预创建 mock 模块，避免导入不必要的重依赖（SQLAlchemy、OpenCV 等）"""
    # Mock 重依赖模块
    heavy_modules = [
        'aiomysql', 'sqlalchemy', 'motor', 'motor.motor_asyncio',
        'asyncmy', 'alembic', 'cv2', 'numpy',
        'database', 'database.db_session', 'database.models',
        'database.mongodb_store_base',
        'cache', 'cache.abs_cache', 'cache.cache_factory',
        'cache.local_cache', 'cache.redis_cache',
        'humps', 'pyhumps',
    ]
    for name in heavy_modules:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    # Mock aiomysql.Pool（var.py 的类型注解需要）
    sys.modules['aiomysql'].Pool = type('Pool', (), {})

    # Mock redis.Redis（cache/redis_cache.py 需要）
    mock_redis_mod = sys.modules.get('redis', types.ModuleType('redis'))
    if 'redis' not in sys.modules:
        sys.modules['redis'] = mock_redis_mod
    mock_redis_mod.Redis = type('Redis', (), {})
    mock_redis_mod.ConnectionPool = type('ConnectionPool', (), {})

    # Mock humps（xhs/extractor.py 需要）
    for mod_name in ('humps', 'pyhumps'):
        m = sys.modules.get(mod_name, sys.modules[mod_name])
        if not hasattr(m, 'camelize'):
            m.camelize = lambda s: s
            m.decamelize = lambda s: s
            m.pascalize = lambda s: s
            m.depascalize = lambda s: s

    # Mock cache 工厂
    sys.modules['cache.cache_factory'].CacheFactory = type('CacheFactory', (), {
        'create_cache': classmethod(lambda cls, **kw: None),
    })
    sys.modules['cache.cache_factory'].CACHE_TYPE_MEMORY = "memory"
    sys.modules['cache.cache_factory'].CACHE_TYPE_REDIS = "redis"

    # cache.abs_cache.AbstractCache 被 local_cache 和 redis_cache 引用
    sys.modules['cache.abs_cache'].AbstractCache = type('AbstractCache', (), {})

    # cache.local_cache 可能有其他引用
    sys.modules['cache.local_cache'].ExpiringLocalCache = type('ExpiringLocalCache', (), {})

    # Mock sqlalchemy 常用函数
    for func in ('select', 'update', 'delete', 'Column', 'String',
                 'Integer', 'Text', 'BigInteger', 'Float', 'Boolean'):
        setattr(sys.modules['sqlalchemy'], func, lambda *a, **kw: None)


def create_store_mocks(platform, results):
    """创建 mock store 模块，拦截数据写入并收集搜索结果"""

    # ---- 工具函数 ----
    def parse_count(value):
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                if '万' in value:
                    return int(float(value.replace('万', '')) * 10_000)
                if '亿' in value:
                    return int(float(value.replace('亿', '')) * 100_000_000)
                return int(float(value))
            except (ValueError, TypeError):
                return 0
        return 0

    def format_ts(ts):
        if not ts:
            return ""
        try:
            ts = int(ts)
            if ts < 1_000_000_000:
                ts = ts  # 秒级时间戳
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except (OSError, ValueError, OverflowError):
            return str(ts)

    # ---- mock store 父模块 ----
    mock_store_pkg = types.ModuleType('store')
    mock_store_pkg.__path__ = []  # 标记为 package
    sys.modules['store'] = mock_store_pkg

    # ---- mock store.excel_store_base ----
    mock_excel = types.ModuleType('store.excel_store_base')
    mock_excel.ExcelStoreBase = type('ExcelStoreBase', (), {
        'flush_all': classmethod(lambda cls: None),
        'get_instance': classmethod(lambda cls, **kw: types.SimpleNamespace()),
    })
    sys.modules['store.excel_store_base'] = mock_excel

    if platform == 'dy':
        # ---- 抖音 store mock ----
        mock_dy = types.ModuleType('store.douyin')
        _seen_ids = set()

        async def capture_dy_aweme(aweme_item):
            aweme_id = aweme_item.get("aweme_id", "")
            if aweme_id in _seen_ids:
                return  # 去重
            _seen_ids.add(aweme_id)
            user = aweme_item.get("author", {})
            stats = aweme_item.get("statistics", {})
            video = aweme_item.get("video", {})
            # 封面：优先 origin_cover / raw_cover
            cover_obj = video.get("origin_cover") or video.get("raw_cover") or {}
            cover_urls = cover_obj.get("url_list", [])
            cover = cover_urls[0] if cover_urls else ""

            results.append({
                "id": aweme_id,
                "title": aweme_item.get("desc", ""),
                "description": aweme_item.get("desc", ""),
                "author": user.get("nickname", ""),
                "author_id": str(user.get("uid", "")),
                "cover_url": cover,
                "url": f"https://www.douyin.com/video/{aweme_id}",
                "like_count": parse_count(stats.get("digg_count", 0)),
                "comment_count": parse_count(stats.get("comment_count", 0)),
                "share_count": parse_count(stats.get("share_count", 0)),
                "collect_count": parse_count(stats.get("collect_count", 0)),
                "publish_time": format_ts(aweme_item.get("create_time", 0)),
                "tags": [],
                "content_type": "video",
            })

        mock_dy.update_douyin_aweme = capture_dy_aweme
        mock_dy.batch_update_dy_aweme_comments = lambda *a, **kw: asyncio.sleep(0)
        mock_dy._extract_note_image_list = lambda x: []
        mock_dy._extract_content_cover_url = lambda x: ""
        mock_dy._extract_video_download_url = lambda x: ""
        mock_dy._extract_music_download_url = lambda x: ""
        mock_dy._extract_comment_image_list = lambda x: []
        mock_dy.save_creator = lambda *a, **kw: asyncio.sleep(0)
        mock_dy.update_dy_aweme_image = lambda *a, **kw: asyncio.sleep(0)
        mock_dy.update_dy_aweme_video = lambda *a, **kw: asyncio.sleep(0)
        # DouyinStoreFactory 不会被调用，但保留空壳以防
        mock_dy.DouyinStoreFactory = type('DouyinStoreFactory', (), {})
        mock_dy.DouyinCsvStoreImplement = type('D', (), {})
        mock_dy.DouyinDbStoreImplement = type('D', (), {})
        mock_dy.DouyinJsonStoreImplement = type('D', (), {})
        mock_dy.DouyinJsonlStoreImplement = type('D', (), {})
        mock_dy.DouyinSqliteStoreImplement = type('D', (), {})
        mock_dy.DouyinMongoStoreImplement = type('D', (), {})
        mock_dy.DouyinExcelStoreImplement = type('D', (), {})
        mock_dy.AbstractStore = type('A', (), {})
        mock_dy.utils = types.ModuleType('utils')
        mock_dy.utils.get_current_timestamp = lambda: int(datetime.now().timestamp())

        sys.modules['store.douyin'] = mock_dy
        mock_store_pkg.douyin = mock_dy

    elif platform == 'xhs':
        # ---- 小红书 store mock ----
        mock_xhs = types.ModuleType('store.xhs')
        _seen_ids = set()

        async def capture_xhs_note(note_item):
            note_id = note_item.get("note_id", "")
            if note_id in _seen_ids:
                return  # 去重
            _seen_ids.add(note_id)
            user = note_item.get("user", {})
            interact = note_item.get("interact_info", {})
            images = note_item.get("image_list", [])
            video = note_item.get("video", {})

            cover = ""
            if images:
                cover = images[0].get("url_default", images[0].get("url", ""))
            elif video:
                cover_obj = video.get("consumer", {}).get("cover", "")
                if isinstance(cover_obj, dict):
                    cover = cover_obj.get("url", "")

            tags = [
                t.get("name", "")
                for t in note_item.get("tag_list", [])
                if t.get("type") == "topic"
            ]

            results.append({
                "id": note_id,
                "title": (note_item.get("title") or note_item.get("desc", ""))[:255],
                "description": note_item.get("desc", ""),
                "author": user.get("nickname", ""),
                "author_id": str(user.get("user_id", "")),
                "cover_url": cover,
                "url": f"https://www.xiaohongshu.com/explore/{note_id}",
                "like_count": parse_count(interact.get("liked_count", 0)),
                "comment_count": parse_count(interact.get("comment_count", 0)),
                "share_count": parse_count(interact.get("share_count", 0)),
                "collect_count": parse_count(interact.get("collected_count", 0)),
                "publish_time": format_ts(note_item.get("time", 0)),
                "tags": tags,
                "content_type": "video" if note_item.get("type") == "video" else "note",
            })

        mock_xhs.update_xhs_note = capture_xhs_note
        mock_xhs.batch_update_xhs_note_comments = lambda *a, **kw: asyncio.sleep(0)
        mock_xhs.get_video_url_arr = lambda x: []
        mock_xhs.save_creator = lambda *a, **kw: asyncio.sleep(0)
        mock_xhs.update_xhs_note_image = lambda *a, **kw: asyncio.sleep(0)
        mock_xhs.update_xhs_note_video = lambda *a, **kw: asyncio.sleep(0)
        mock_xhs.XhsStoreFactory = type('XhsStoreFactory', (), {})
        mock_xhs.XhsCsvStoreImplement = type('X', (), {})
        mock_xhs.XhsDbStoreImplement = type('X', (), {})
        mock_xhs.XhsJsonStoreImplement = type('X', (), {})
        mock_xhs.XhsJsonlStoreImplement = type('X', (), {})
        mock_xhs.XhsSqliteStoreImplement = type('X', (), {})
        mock_xhs.XhsMongoStoreImplement = type('X', (), {})
        mock_xhs.XhsExcelStoreImplement = type('X', (), {})
        mock_xhs.AbstractStore = type('A', (), {})
        mock_xhs.utils = types.ModuleType('utils')
        mock_xhs.utils.get_current_timestamp = lambda: int(datetime.now().timestamp())
        mock_xhs.utils.logger = types.SimpleNamespace(info=print, error=print)

        sys.modules['store.xhs'] = mock_xhs
        mock_store_pkg.xhs = mock_xhs


def check_environment(mc_dir):
    """检查运行环境是否就绪，返回 (ok, message)"""
    # 1. 检查 MediaCrawler 目录
    if not os.path.isdir(mc_dir):
        return False, f"MediaCrawler 目录不存在: {mc_dir}"

    # 2. 检查关键 Python 包
    try:
        import playwright
    except ImportError:
        return False, "缺少 playwright，请运行: pip install playwright && playwright install chromium"

    try:
        from PIL import Image
    except ImportError:
        return False, "缺少 Pillow，请运行: pip install Pillow"

    try:
        import httpx
    except ImportError:
        return False, "缺少 httpx，请运行: pip install httpx"

    try:
        from tenacity import retry
    except ImportError:
        return False, "缺少 tenacity，请运行: pip install tenacity"

    try:
        import aiofiles
    except ImportError:
        return False, "缺少 aiofiles，请运行: pip install aiofiles"

    try:
        import parsel
    except ImportError:
        return False, "缺少 parsel，请运行: pip install parsel"

    # 3. 检查 Playwright 浏览器
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
            except Exception as e:
                if "Executable doesn't exist" in str(e) or "browserType.launch" in str(e):
                    return False, "Playwright 浏览器未安装，请运行: playwright install chromium"
                raise
    except Exception as e:
        return False, f"Playwright 浏览器检查失败: {e}"

    return True, "环境检查通过"


def _setup_browser_data_dir(mc_dir, platform):
    """将 browser_data 重定向到不含中文的安全路径（Chromium 不支持中文路径）"""
    import tempfile

    # 使用 %LOCALAPPDATA% 下的固定路径，确保持久化和无中文
    if sys.platform == 'win32':
        safe_base = os.path.join(
            os.environ.get('LOCALAPPDATA', os.environ.get('TEMP', tempfile.gettempdir())),
            'MediaCrawler', 'browser_data'
        )
    else:
        safe_base = os.path.join(os.path.expanduser('~'), '.mediacrawler', 'browser_data')

    safe_dir = os.path.join(safe_base, f'{platform}_user_data_dir')
    os.makedirs(safe_dir, exist_ok=True)

    # 迁移已有数据（如果有）
    mc_browser_data = os.path.join(mc_dir, 'browser_data')
    old_platform_dir = os.path.join(mc_browser_data, f'{platform}_user_data_dir')
    if os.path.isdir(old_platform_dir):
        try:
            import shutil
            for item in os.listdir(old_platform_dir):
                src = os.path.join(old_platform_dir, item)
                dst = os.path.join(safe_dir, item)
                if not os.path.exists(dst):
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            print(f"[Bridge] 已迁移 browser_data 到安全路径: {safe_dir}", file=sys.stderr)
        except Exception as e:
            print(f"[Bridge] 迁移 browser_data 失败（不影响搜索）: {e}", file=sys.stderr)

    return safe_dir


def run_search(args):
    """执行搜索"""
    bridge_dir = os.path.dirname(os.path.abspath(__file__))
    mc_dir = os.path.join(bridge_dir, 'MediaCrawler')

    # 添加 MediaCrawler 到 sys.path（必须在 import 之前）
    sys.path.insert(0, mc_dir)
    os.chdir(mc_dir)  # MC 部分代码使用相对路径（如 libs/stealth.min.js）

    # 重定向 browser_data 到不含中文的安全路径
    _setup_browser_data_dir(mc_dir, args.platform)

    # 重定向 browser_data 到不含中文的安全路径
    safe_data_dir = _setup_browser_data_dir(mc_dir, args.platform)

    # 设置 mock
    setup_mocks()

    # 数据收集列表
    results = []

    # 创建 mock store
    create_store_mocks(args.platform, results)

    # Mock tools.slider_util（依赖 cv2/numpy，搜索不需要）
    mock_slider = types.ModuleType('tools.slider_util')
    sys.modules['tools.slider_util'] = mock_slider

    # 补充 mock 其他可能缺少的模块
    extra_mocks = [
        'tools.httpx_util',
    ]
    for m in extra_mocks:
        if m not in sys.modules:
            sys.modules[m] = types.ModuleType(m)
    # httpx_util.make_async_client 被 client.py 以 async with 使用，不能是 async 函数
    if not hasattr(sys.modules['tools.httpx_util'], 'make_async_client'):
        def _make_async_client(**kw):
            import httpx
            return httpx.AsyncClient(**kw)
        sys.modules['tools.httpx_util'].make_async_client = _make_async_client

    # ---- Patch config ----
    import config as mc_config
    mc_config.PLATFORM = args.platform
    mc_config.KEYWORDS = args.keyword
    mc_config.CRAWLER_TYPE = "search"
    mc_config.HEADLESS = args.headless
    mc_config.CDP_HEADLESS = args.headless
    mc_config.SAVE_LOGIN_STATE = True
    mc_config.CRAWLER_MAX_NOTES_COUNT = args.max_count
    mc_config.ENABLE_GET_COMMENTS = False
    mc_config.ENABLE_GET_MEIDAS = False
    mc_config.CRAWLER_MAX_SLEEP_SEC = 0.5
    mc_config.MAX_CONCURRENCY_NUM = 1
    mc_config.ENABLE_CDP_MODE = False
    mc_config.SAVE_DATA_OPTION = "json"
    mc_config.ENABLE_IP_PROXY = False
    mc_config.START_PAGE = args.page
    mc_config.LOGIN_TYPE = "qrcode"
    mc_config.COOKIES = ""
    mc_config.DISABLE_SSL_VERIFY = False
    mc_config.ENABLE_GET_WORDCLOUD = False
    mc_config.ENABLE_GET_SUB_COMMENTS = False
    mc_config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 0
    mc_config.AUTO_CLOSE_BROWSER = True

    # 关键修复：Chromium 不支持 user-data-dir 包含中文路径
    # 通过 patch playwright 的 launch_persistent_context，在运行时替换 user_data_dir
    try:
        from playwright.async_api import BrowserType
        _original_launch = BrowserType.launch_persistent_context

        async def _patched_launch(self, user_data_dir=None, **kwargs):
            if user_data_dir:
                try:
                    user_data_dir.encode('ascii')
                except UnicodeEncodeError:
                    new_dir = safe_data_dir
                    os.makedirs(new_dir, exist_ok=True)
                    print(f"[Bridge] user-data-dir 含中文，重定向到: {new_dir}", file=sys.stderr)
                    user_data_dir = new_dir
            return await _original_launch(self, user_data_dir=user_data_dir, **kwargs)

        BrowserType.launch_persistent_context = _patched_launch
    except Exception as e:
        print(f"[Bridge] patch playwright 警告: {e}", file=sys.stderr)

    if args.platform == 'dy':
        mc_config.PUBLISH_TIME_TYPE = 0
        mc_config.DY_SPECIFIED_ID_LIST = []
        mc_config.DY_CREATOR_ID_LIST = []
    elif args.platform == 'xhs':
        mc_config.SORT_TYPE = ""
        mc_config.XHS_SPECIFIED_NOTE_URL_LIST = []
        mc_config.XHS_CREATOR_ID_LIST = []

    # Patch 小红书登录逻辑
    # MC 的二维码选择器已过时，改为：如果未登录则打开浏览器等待手动登录
    if args.platform == 'xhs':
        try:
            from media_platform.xhs.login import XiaoHongShuLogin
            _orig_begin = XiaoHongShuLogin.begin
            async def _patched_begin(self):
                # 先检查是否已登录
                try:
                    self_info = await self.xhs_client.query_self()
                    if self_info and self_info.get("data", {}).get("result", {}).get("success"):
                        return  # 已登录
                except Exception:
                    pass

                # 未登录：打开登录页等待手动操作
                print("[Bridge] 小红书未登录，请手动登录...", file=sys.stderr)
                await self.context_page.goto("https://www.xiaohongshu.com")
                await asyncio.sleep(2)

                # 尝试点击登录按钮（多种选择器）
                login_selectors = [
                    "xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button",
                    "xpath=//button[contains(text(),'登录')]",
                    "xpath=//div[contains(@class,'login-container')]//button",
                    ".login-btn",
                ]
                for sel in login_selectors:
                    try:
                        elem = self.context_page.locator(sel).first
                        if await elem.is_visible(timeout=3000):
                            await elem.click()
                            break
                    except Exception:
                        continue

                print("[Bridge] 请在浏览器中完成登录（扫码或手机号），登录成功后自动继续...", file=sys.stderr)
                print("[Bridge] 等待登录，最长120秒...", file=sys.stderr)

                # 等待登录成功（检查 cookie 中是否有 web_session）
                import json as _json
                for _ in range(120):
                    await asyncio.sleep(1)
                    cookies = await self.browser_context.cookies()
                    for c in cookies:
                        if c.get("name") == "web_session" and c.get("value"):
                            print("[Bridge] 小红书登录成功！", file=sys.stderr)
                            await asyncio.sleep(2)
                            return
                print("[Bridge] 等待登录超时", file=sys.stderr)
                raise RuntimeError("小红书登录超时，请在 --no-headless 模式下手动登录")

            XiaoHongShuLogin.begin = _patched_begin
        except ImportError:
            pass
        except Exception as e:
            print(f"[Bridge] patch xhs login 警告: {e}", file=sys.stderr)

    # ---- 设置 context var ----
    from var import crawler_type_var, source_keyword_var
    crawler_type_var.set("search")
    source_keyword_var.set(args.keyword)

    # ---- 导入并运行 crawler ----
    crawler = None
    try:
        if args.platform == 'dy':
            from media_platform.douyin.core import DouYinCrawler
            crawler = DouYinCrawler()
        elif args.platform == 'xhs':
            from media_platform.xhs.core import XiaoHongShuCrawler
            crawler = XiaoHongShuCrawler()

            # 重写 search 方法：从搜索结果直接提取数据，不依赖详情页
            _orig_search = XiaoHongShuCrawler.search
            async def _direct_search(self):
                from var import source_keyword_var, crawler_type_var
                from media_platform.xhs.field import SearchSortType
                from media_platform.xhs.help import get_search_id
                import store.xhs as xhs_store
                import config as _config

                xhs_limit_count = 20
                if _config.CRAWLER_MAX_NOTES_COUNT < xhs_limit_count:
                    _config.CRAWLER_MAX_NOTES_COUNT = xhs_limit_count
                start_page = _config.START_PAGE
                for keyword in _config.KEYWORDS.split(","):
                    source_keyword_var.set(keyword)
                    page = 1
                    search_id = get_search_id()
                    while (page - start_page + 1) * xhs_limit_count <= _config.CRAWLER_MAX_NOTES_COUNT:
                        if page < start_page:
                            page += 1
                            continue
                        try:
                            notes_res = await self.xhs_client.get_note_by_keyword(
                                keyword=keyword, search_id=search_id, page=page,
                                sort=(SearchSortType(_config.SORT_TYPE) if _config.SORT_TYPE != "" else SearchSortType.GENERAL),
                            )
                            if not notes_res or not notes_res.get("has_more", False):
                                break
                            items = notes_res.get("items", [])
                            for post_item in items:
                                if post_item.get("model_type") in ("rec_query", "hot_query"):
                                    continue
                                # 直接从搜索结果构建笔记数据
                                note_data = {
                                    "note_id": post_item.get("id", ""),
                                    "title": post_item.get("note_card", {}).get("display_title", ""),
                                    "desc": post_item.get("note_card", {}).get("desc", ""),
                                    "type": post_item.get("note_card", {}).get("type", "normal"),
                                    "user": {
                                        "nickname": post_item.get("note_card", {}).get("user", {}).get("nickname", ""),
                                        "user_id": post_item.get("note_card", {}).get("user", {}).get("user_id", ""),
                                    },
                                    "interact_info": post_item.get("note_card", {}).get("interact_info", {}),
                                    "image_list": post_item.get("note_card", {}).get("image_list", []),
                                    "video": post_item.get("note_card", {}).get("video", {}),
                                    "tag_list": post_item.get("note_card", {}).get("tag_list", []),
                                    "time": post_item.get("note_card", {}).get("time", 0),
                                    "xsec_token": post_item.get("xsec_token", ""),
                                    "xsec_source": post_item.get("xsec_source", ""),
                                }
                                await xhs_store.update_xhs_note(note_data)
                            page += 1
                            await asyncio.sleep(_config.CRAWLER_MAX_SLEEP_SEC)
                        except Exception as e:
                            import traceback
                            print(f"[Bridge] 小红书搜索页面出错: {e}\n{traceback.format_exc()}", file=sys.stderr)
                            break

            XiaoHongShuCrawler.search = _direct_search

        async def _run():
            try:
                await asyncio.wait_for(crawler.start(), timeout=args.timeout)
            except asyncio.TimeoutError:
                raise RuntimeError(f"搜索超时（{args.timeout}秒），浏览器启动或API响应过慢")

        asyncio.run(_run())

        output = {
            "success": True,
            "data": results,
            "count": len(results),
        }
        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        tb = traceback.format_exc()
        error_msg = str(e)

        # 友好化常见错误
        friendly_errors = {
            "login": "需要登录，请使用 --no-headless 参数首次运行以扫码登录",
            "qr": "二维码登录超时，请使用 --no-headless 参数并确保及时扫码",
            "cookie": "Cookie 已失效，请使用 --no-headless 重新登录",
            "captcha": "遇到验证码，请使用 --no-headless 手动完成验证",
            "timeout": f"操作超时（{args.timeout}秒），请增大 --timeout 值",
            "browser": "浏览器启动失败，请确保已运行 playwright install chromium",
        }
        suggestion = ""
        error_lower = error_msg.lower()
        for key, msg in friendly_errors.items():
            if key in error_lower:
                suggestion = msg
                break

        print(json.dumps({
            "success": False,
            "error": error_msg,
            "suggestion": suggestion,
            "traceback": tb if not suggestion else None,
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    finally:
        # 尝试清理浏览器
        if crawler:
            try:
                if hasattr(crawler, 'cdp_manager') and crawler.cdp_manager:
                    asyncio.run(crawler.cdp_manager.cleanup(force=True))
                elif hasattr(crawler, 'browser_context'):
                    asyncio.run(crawler.browser_context.close())
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(
        description='MediaCrawler Bridge - 平台搜索桥接工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--platform', choices=['dy', 'xhs'],
                        help='平台: dy=抖音, xhs=小红书')
    parser.add_argument('--keyword', help='搜索关键词')
    parser.add_argument('--max-count', type=int, default=20,
                        help='最大结果数（默认 20）')
    parser.add_argument('--page', type=int, default=1,
                        help='起始页码（默认 1）')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='无头模式（默认开启）')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                        help='显示浏览器窗口（用于首次登录）')
    parser.add_argument('--timeout', type=int, default=120,
                        help='超时秒数（默认 120）')
    parser.add_argument('--check', action='store_true',
                        help='仅检查环境，不执行搜索')

    args = parser.parse_args()

    bridge_dir = os.path.dirname(os.path.abspath(__file__))
    mc_dir = os.path.join(bridge_dir, 'MediaCrawler')

    if args.check:
        ok, msg = check_environment(mc_dir)
        result = {"success": ok, "message": msg}
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0 if ok else 1)

    if not args.platform:
        parser.error("--platform 是必填参数")
    if not args.keyword:
        parser.error("--keyword 是必填参数")

    run_search(args)


if __name__ == '__main__':
    main()
