"""
Cookie管理器 - Cookie验证和管理

提供统一的Cookie验证、解析和管理功能。
"""
import json
import logging
from typing import Dict, Any, Optional, List
import requests

logger = logging.getLogger(__name__)


class CookieValidator:
    """
    Cookie有效性验证器基类

    提供通用的Cookie验证功能，各平台可继承并自定义验证逻辑。

    Example:
        class DouyinCookieValidator(CookieValidator):
            CHECK_URL = "https://www.douyin.com/passport/web/account/info/"
            REQUIRED_COOKIES = ['ttwid']

        validator = DouyinCookieValidator()
        result = validator.validate_cookie_format(cookie_string)
    """

    # 子类应覆盖以下属性
    CHECK_URL: str = None  # 登录状态检测URL
    REQUIRED_COOKIES: List[str] = []  # 必需的Cookie字段
    LOGIN_COOKIES: List[str] = []  # 登录状态下才有的Cookie字段

    @classmethod
    def parse_cookie_string(cls, cookie_str: str) -> Dict[str, str]:
        """
        解析Cookie字符串为字典

        Args:
            cookie_str: Cookie字符串（如 "name1=value1; name2=value2"）

        Returns:
            Cookie字典
        """
        if not cookie_str:
            return {}

        cookies = {}
        for item in cookie_str.split(';'):
            item = item.strip()
            if '=' in item:
                name, value = item.split('=', 1)
                cookies[name.strip()] = value.strip()

        return cookies

    @classmethod
    def dict_to_cookie_string(cls, cookie_dict: Dict[str, str]) -> str:
        """
        将Cookie字典转换为字符串

        Args:
            cookie_dict: Cookie字典

        Returns:
            Cookie字符串
        """
        return '; '.join(f'{k}={v}' for k, v in cookie_dict.items())

    @classmethod
    def validate_cookie_format(cls, cookie_str: str) -> Dict[str, Any]:
        """
        验证Cookie格式

        Args:
            cookie_str: Cookie字符串

        Returns:
            验证结果字典:
            {
                'valid': bool,
                'message': str,
                'has_login': bool,
                'cookie_count': int,
                'missing_fields': List[str]
            }
        """
        if not cookie_str or not cookie_str.strip():
            return {
                'valid': False,
                'message': 'Cookie为空',
                'has_login': False,
                'cookie_count': 0,
                'missing_fields': cls.REQUIRED_COOKIES.copy()
            }

        # 解析Cookie
        cookies = cls.parse_cookie_string(cookie_str)

        # 检查必需字段
        missing = [k for k in cls.REQUIRED_COOKIES if k not in cookies]

        if missing:
            return {
                'valid': False,
                'message': f'Cookie缺少必需字段: {", ".join(missing)}',
                'has_login': False,
                'cookie_count': len(cookies),
                'missing_fields': missing
            }

        # 检查是否有登录态
        has_login = any(k in cookies for k in cls.LOGIN_COOKIES)

        return {
            'valid': True,
            'message': 'Cookie格式有效' + ('，已检测到登录态' if has_login else '，未检测到登录态（部分功能可能受限）'),
            'has_login': has_login,
            'cookie_count': len(cookies),
            'missing_fields': []
        }

    @classmethod
    def check_cookie_alive(
        cls,
        session: requests.Session,
        check_url: str = None
    ) -> Dict[str, Any]:
        """
        检测Cookie是否仍然有效（需要网络请求）

        Args:
            session: 已配置Cookie的Session
            check_url: 检测URL（可选，默认使用类属性CHECK_URL）

        Returns:
            检测结果字典:
            {
                'valid': bool,
                'message': str,
                'need_login': bool,
                'user_info': Dict (可选)
            }
        """
        url = check_url or cls.CHECK_URL

        if not url:
            return {
                'valid': True,
                'message': '未配置检测URL，跳过在线验证',
                'need_login': False
            }

        try:
            response = session.get(url, timeout=10)

            if response.status_code == 403:
                return {
                    'valid': False,
                    'message': 'Cookie已失效或被封禁，请更新Cookie',
                    'need_login': True
                }

            if response.status_code == 200:
                try:
                    data = response.json()
                    return cls._parse_check_response(data)
                except json.JSONDecodeError:
                    pass

            return {
                'valid': True,
                'message': 'Cookie可能有效，建议测试实际请求',
                'need_login': False
            }

        except requests.RequestException as e:
            return {
                'valid': False,
                'message': f'Cookie验证网络错误: {str(e)}',
                'need_login': False
            }

    @classmethod
    def _parse_check_response(cls, data: dict) -> Dict[str, Any]:
        """
        解析检测响应（子类可覆盖）

        Args:
            data: JSON响应数据

        Returns:
            检测结果
        """
        return {
            'valid': True,
            'message': 'Cookie有效',
            'need_login': False
        }

    @classmethod
    def detect_login_expired(cls, response: requests.Response) -> bool:
        """
        从响应中检测登录是否过期

        Args:
            response: HTTP响应对象

        Returns:
            是否检测到登录过期
        """
        # 检查状态码
        if response.status_code in (401, 403):
            return True

        # 检查响应内容
        try:
            data = response.json()

            # 检查错误码
            if data.get('status_code') == 8:
                return True

            # 检查错误信息
            status_msg = data.get('status_msg', '').lower()
            login_expired_keywords = ['login', '登录', 'expired', '过期', 'unauthorized']
            if any(kw in status_msg for kw in login_expired_keywords):
                return True

        except (json.JSONDecodeError, AttributeError):
            pass

        return False


class DouyinCookieValidator(CookieValidator):
    """抖音Cookie验证器"""

    CHECK_URL = "https://www.douyin.com/passport/web/account/info/"
    REQUIRED_COOKIES = ['ttwid']
    LOGIN_COOKIES = ['sessionid', 'passport_csrf_token']

    @classmethod
    def _parse_check_response(cls, data: dict) -> Dict[str, Any]:
        """解析抖音检测响应"""
        if data.get('has_login'):
            return {
                'valid': True,
                'message': 'Cookie有效，已登录',
                'need_login': False,
                'user_info': data.get('data', {})
            }
        else:
            return {
                'valid': True,
                'message': 'Cookie有效但未登录，部分功能可能受限',
                'need_login': False
            }


class BilibiliCookieValidator(CookieValidator):
    """B站Cookie验证器"""

    CHECK_URL = "https://api.bilibili.com/x/web-interface/nav"
    REQUIRED_COOKIES = ['buvid3']
    LOGIN_COOKIES = ['SESSDATA', 'bili_jct']

    @classmethod
    def _parse_check_response(cls, data: dict) -> Dict[str, Any]:
        """解析B站检测响应"""
        if data.get('code') == 0:
            is_login = data.get('data', {}).get('isLogin', False)
            if is_login:
                return {
                    'valid': True,
                    'message': 'Cookie有效，已登录',
                    'need_login': False,
                    'user_info': data.get('data', {})
                }
            else:
                return {
                    'valid': True,
                    'message': 'Cookie有效但未登录',
                    'need_login': False
                }
        else:
            return {
                'valid': False,
                'message': data.get('message', '验证失败'),
                'need_login': True
            }


class XiaohongshuCookieValidator(CookieValidator):
    """小红书Cookie验证器"""

    REQUIRED_COOKIES = ['a1']
    LOGIN_COOKIES = ['web_session', 'websectiga']


class CookieManager:
    """
    Cookie管理器

    提供Cookie的加载、保存、更新等功能。

    Example:
        manager = CookieManager()
        manager.save_cookies('douyin', {'ttwid': 'xxx', 'sessionid': 'yyy'})
        cookies = manager.load_cookies('douyin')
    """

    def __init__(self, storage_dir: str = None):
        """
        初始化Cookie管理器

        Args:
            storage_dir: Cookie存储目录
        """
        self.storage_dir = storage_dir
        self._cache: Dict[str, Dict[str, str]] = {}

    def save_cookies(self, platform: str, cookies: Dict[str, str]):
        """
        保存Cookie

        Args:
            platform: 平台标识
            cookies: Cookie字典
        """
        self._cache[platform] = cookies.copy()
        logger.debug(f"已缓存 {platform} 的Cookie")

    def load_cookies(self, platform: str) -> Optional[Dict[str, str]]:
        """
        加载Cookie

        Args:
            platform: 平台标识

        Returns:
            Cookie字典或None
        """
        return self._cache.get(platform)

    def get_cookie_string(self, platform: str) -> Optional[str]:
        """
        获取Cookie字符串

        Args:
            platform: 平台标识

        Returns:
            Cookie字符串或None
        """
        cookies = self.load_cookies(platform)
        if cookies:
            return CookieValidator.dict_to_cookie_string(cookies)
        return None

    def update_cookie(self, platform: str, name: str, value: str):
        """
        更新单个Cookie

        Args:
            platform: 平台标识
            name: Cookie名称
            value: Cookie值
        """
        if platform not in self._cache:
            self._cache[platform] = {}
        self._cache[platform][name] = value

    def remove_cookie(self, platform: str, name: str = None):
        """
        删除Cookie

        Args:
            platform: 平台标识
            name: Cookie名称（None表示删除所有）
        """
        if name is None:
            self._cache.pop(platform, None)
        elif platform in self._cache:
            self._cache[platform].pop(name, None)

    def clear_all(self):
        """清空所有Cookie"""
        self._cache.clear()


# 平台验证器注册表
_validators: Dict[str, type] = {
    'douyin': DouyinCookieValidator,
    'bilibili': BilibiliCookieValidator,
    'xiaohongshu': XiaohongshuCookieValidator,
}


def get_validator(platform: str) -> type:
    """
    获取平台验证器

    Args:
        platform: 平台标识

    Returns:
        验证器类
    """
    return _validators.get(platform, CookieValidator)
