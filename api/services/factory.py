"""
服务工厂 - 统一管理平台服务实例
"""
from typing import Dict, Optional, Type
from .base import PlatformService, PlatformType
from .bilibili_service import BilibiliService
from .douyin_service import DouyinService
from .xiaohongshu_service import XiaohongshuService


class ServiceFactory:
    """
    平台服务工厂

    统一管理各平台服务实例的创建和获取
    """

    # 服务类注册表
    _service_classes: Dict[PlatformType, Type[PlatformService]] = {
        PlatformType.BILIBILI: BilibiliService,
        PlatformType.DOUYIN: DouyinService,
        PlatformType.XIAOHONGSHU: XiaohongshuService,
    }

    # 服务实例缓存
    _instances: Dict[str, PlatformService] = {}

    @classmethod
    def register_service(
        cls,
        platform: PlatformType,
        service_class: Type[PlatformService]
    ):
        """
        注册新的平台服务

        Args:
            platform: 平台类型
            service_class: 服务类
        """
        cls._service_classes[platform] = service_class

    @classmethod
    def get_service(
        cls,
        platform: str,
        config: Optional[Dict] = None
    ) -> PlatformService:
        """
        获取平台服务实例

        Args:
            platform: 平台标识 (bilibili, douyin, xiaohongshu)
            config: 配置参数（如Cookie等）

        Returns:
            平台服务实例

        Raises:
            ValueError: 不支持的平台
        """
        # 转换平台标识
        platform_type = cls._parse_platform(platform)

        if platform_type not in cls._service_classes:
            raise ValueError(f"不支持的平台: {platform}")

        # 生成缓存键
        config = config or {}
        cache_key = cls._generate_cache_key(platform_type, config)

        # 检查缓存
        if cache_key in cls._instances:
            return cls._instances[cache_key]

        # 创建新实例
        service_class = cls._service_classes[platform_type]
        service = cls._create_service(service_class, config)

        # 缓存实例
        cls._instances[cache_key] = service

        return service

    @classmethod
    def _parse_platform(cls, platform: str) -> PlatformType:
        """解析平台标识"""
        platform = platform.lower().strip()

        # 支持多种写法
        platform_map = {
            'bilibili': PlatformType.BILIBILI,
            'bili': PlatformType.BILIBILI,
            'b站': PlatformType.BILIBILI,
            'douyin': PlatformType.DOUYIN,
            'tiktok': PlatformType.DOUYIN,
            '抖音': PlatformType.DOUYIN,
            'xiaohongshu': PlatformType.XIAOHONGSHU,
            'red': PlatformType.XIAOHONGSHU,
            '小红书': PlatformType.XIAOHONGSHU,
        }

        if platform not in platform_map:
            raise ValueError(
                f"不支持的平台: {platform}。"
                f"支持的平台: {', '.join(platform_map.keys())}"
            )

        return platform_map[platform]

    @classmethod
    def _generate_cache_key(cls, platform: PlatformType, config: Dict) -> str:
        """生成缓存键"""
        # 使用配置的关键参数生成键
        key_parts = [platform.value]

        if 'sessdata' in config:
            key_parts.append(f"sessdata:{config['sessdata'][:8]}")
        if 'cookies' in config:
            key_parts.append(f"cookies:{hash(config['cookies']) % 10000}")
        if 'ttwid' in config:
            key_parts.append(f"ttwid:{config['ttwid'][:8]}")

        return ':'.join(key_parts)

    @classmethod
    def _create_service(
        cls,
        service_class: Type[PlatformService],
        config: Dict
    ) -> PlatformService:
        """创建服务实例"""
        # 根据不同服务类型传递不同的参数
        if service_class == BilibiliService:
            return BilibiliService(sessdata=config.get('sessdata'))

        elif service_class == DouyinService:
            return DouyinService(
                cookies=config.get('cookies'),
                ttwid=config.get('ttwid'),
                headless=config.get('headless', True),
            )

        elif service_class == XiaohongshuService:
            return XiaohongshuService(
                cookies=config.get('cookies'),
                headless=config.get('headless', True),
            )

        # 默认无参创建
        return service_class()

    @classmethod
    def clear_cache(cls):
        """清除服务实例缓存"""
        cls._instances.clear()

    @classmethod
    def get_supported_platforms(cls) -> list:
        """获取支持的平台列表"""
        return [
            {
                "id": p.value,
                "name": cls._get_platform_name(p),
                "available": p in cls._service_classes
            }
            for p in PlatformType
        ]

    @classmethod
    def _get_platform_name(cls, platform: PlatformType) -> str:
        """获取平台显示名称"""
        names = {
            PlatformType.BILIBILI: "哔哩哔哩",
            PlatformType.DOUYIN: "抖音",
            PlatformType.XIAOHONGSHU: "小红书",
        }
        return names.get(platform, platform.value)


# 便捷函数
def get_bilibili_service(sessdata: str = None) -> BilibiliService:
    """获取B站服务"""
    return ServiceFactory.get_service(
        'bilibili',
        {'sessdata': sessdata}
    )


def get_douyin_service(cookies: str = None, ttwid: str = None) -> DouyinService:
    """获取抖音服务"""
    return ServiceFactory.get_service(
        'douyin',
        {'cookies': cookies, 'ttwid': ttwid}
    )


def get_xiaohongshu_service(cookies: str = None) -> XiaohongshuService:
    """获取小红书服务"""
    return ServiceFactory.get_service(
        'xiaohongshu',
        {'cookies': cookies}
    )
