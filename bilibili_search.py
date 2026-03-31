#!/usr/bin/env python3
"""
B站视频搜索 Agent - Cookie版
需要先在浏览器登录B站，复制Cookie中的SESSDATA

获取Cookie方法:
1. 浏览器打开 https://search.bilibili.com
2. 按F12打开开发者工具 → Application/Storage → Cookies
3. 找到 search.bilibili.com 或 bilibili.com 域名
4. 复制 SESSDATA 的值
"""

import json
import requests
import os
import sys
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlencode
from hashlib import md5

# 添加 MediaCrawler 路径以导入 BilibiliSign
MC_PATH = os.path.join(os.path.dirname(__file__), 'tools', 'MediaCrawler')
if os.path.exists(MC_PATH):
    sys.path.insert(0, MC_PATH)
    try:
        from media_platform.bilibili.help import BilibiliSign
        HAS_WBI_SIGN = True
    except ImportError:
        HAS_WBI_SIGN = False
else:
    HAS_WBI_SIGN = False


@dataclass
class BilibiliVideo:
    """B站视频数据模型"""
    bvid: str
    title: str
    description: str
    author: str
    author_id: int
    play_count: int
    like_count: int
    duration: str
    pubdate: str
    cover_url: str
    video_url: str
    tags: List[str]


class BilibiliSearchAgent:
    """B站视频搜索Agent - 需要Cookie登录"""

    def __init__(self, sessdata: str = None):
        self.results: List[BilibiliVideo] = []
        self.session = requests.Session()

        # 设置请求头 - 只保留最基本的，避免 Windows 上的 Invalid argument 错误
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.bilibili.com/',
        })

        # 设置Cookie
        if sessdata:
            self.session.cookies.set('SESSDATA', sessdata, domain='.bilibili.com')
        else:
            # 尝试从环境变量读取
            env_sessdata = os.environ.get('BILIBILI_SESSDATA')
            if env_sessdata:
                self.session.cookies.set('SESSDATA', env_sessdata, domain='.bilibili.com')

        # 初始化 Wbi 签名（如果可用）
        self.wbi_sign = None
        if HAS_WBI_SIGN:
            try:
                self._init_wbi_sign()
            except Exception as e:
                print(f"[Warning] Wbi 签名初始化失败: {e}")

    def _init_wbi_sign(self):
        """初始化 Wbi 签名（B站 API 现在需要）"""
        try:
            # 从 API 获取最新的 img_key 和 sub_key
            nav_url = "https://api.bilibili.com/x/web-interface/nav"
            resp = self.session.get(nav_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get('code') != 0:
                print(f"[Warning] 无法获取 Wbi 密钥: {data.get('message')}")
                return

            if not data.get('data') or not data['data'].get('wbi_img'):
                print(f"[Warning] Wbi 密钥数据格式错误: {data}")
                return

            wbi_img = data['data']['wbi_img']
            img_url = wbi_img['img_url']
            sub_url = wbi_img['sub_url']

            img_key = img_url.rsplit('/', 1)[1].split('.')[0]
            sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]

            self.wbi_sign = BilibiliSign(img_key, sub_key)
            print(f"[Info] Wbi 签名初始化成功")
        except Exception as e:
            print(f"[Warning] Wbi 签名初始化失败: {e}")
            import traceback
            traceback.print_exc()
    
    def search_videos_sync(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        order: str = "totalrank"
    ) -> List[BilibiliVideo]:
        """同步搜索B站视频"""
        import time
        import random

        try:
            # 使用 Wbi 签名的 API 路径
            url = "https://api.bilibili.com/x/web-interface/wbi/search/type"

            # 基础参数
            params = {
                'keyword': keyword,
                'search_type': 'video',
                'page': page,
                'page_size': page_size,
                'order': order,
            }

            # 如果 Wbi 签名可用，添加签名
            if self.wbi_sign:
                params = self.wbi_sign.sign(params)
                print(f"[Debug] 使用 Wbi 签名: {list(params.keys())}")
            else:
                print(f"[Debug] 未使用 Wbi 签名")

            print(f"[Debug] 请求 URL: {url}")
            print(f"[Debug] 请求参数: {params}")

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            print(f"[Debug] API 响应 code: {data.get('code')}")

            if data.get('code') != 0:
                error_msg = data.get('message', '未知错误')
                if data.get('code') == -412:
                    print("错误: 需要登录Cookie。请提供SESSDATA。")
                    print("获取方法: 浏览器登录B站 → F12 → Application → Cookies → 复制SESSDATA")
                else:
                    print(f"API返回错误: {error_msg}")
                return []
            
            videos = []
            for item in data.get('data', {}).get('result', []):
                title = item.get('title', '')
                title = title.replace('<em class="keyword">', '').replace('</em>', '')
                
                video_info = BilibiliVideo(
                    bvid=item.get('bvid', ''),
                    title=title,
                    description=item.get('description', ''),
                    author=item.get('author', ''),
                    author_id=item.get('mid', 0),
                    play_count=self._parse_count(item.get('play', 0)),
                    like_count=self._parse_count(item.get('like', 0)),
                    duration=item.get('duration', ''),
                    pubdate=str(item.get('pubdate', '')),
                    cover_url=item.get('pic', ''),
                    video_url=f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    tags=item.get('tag', '').split(',') if item.get('tag') else []
                )
                videos.append(video_info)
            
            self.results = videos
            return videos
            
        except requests.RequestException as e:
            print(f"网络请求失败: {e}")
            return []
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def _parse_count(self, value) -> int:
        """解析播放量等数字"""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            if '万' in value:
                return int(float(value.replace('万', '')) * 10000)
            if value in ('-', ''):
                return 0
            try:
                return int(value)
            except:
                return 0
        return 0
    
    def print_results(self):
        """打印搜索结果"""
        print(f"\n{'='*80}")
        print(f"找到 {len(self.results)} 个视频")
        print(f"{'='*80}\n")
        
        for i, v in enumerate(self.results[:10], 1):
            print(f"【{i}】{v.title[:60]}{'...' if len(v.title) > 60 else ''}")
            print(f"    UP主: {v.author} | 播放: {v.play_count:,} | 点赞: {v.like_count}")
            print(f"    链接: {v.video_url}")
            print()
    
    def get_video_detail(self, bvid: str) -> Dict:
        """获取视频详情"""
        try:
            url = "https://api.bilibili.com/x/web-interface/view"
            response = self.session.get(url, params={'bvid': bvid}, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != 0:
                return {"error": data.get('message', '获取失败')}
            
            video_data = data.get('data', {})
            return {
                "bvid": bvid,
                "title": video_data.get('title', ''),
                "description": video_data.get('desc', ''),
                "owner": video_data.get('owner', {}).get('name', ''),
                "pubdate": video_data.get('pubdate', 0),
                "duration": video_data.get('duration', 0),
                "view": video_data.get('stat', {}).get('view', 0),
                "like": video_data.get('stat', {}).get('like', 0),
                "coin": video_data.get('stat', {}).get('coin', 0),
                "favorite": video_data.get('stat', {}).get('favorite', 0),
                "share": video_data.get('stat', {}).get('share', 0),
                "reply": video_data.get('stat', {}).get('reply', 0),
                "tags": [t.get('tag_name', '') for t in video_data.get('tags', [])],
                "pic": video_data.get('pic', ''),
                "cid": video_data.get('cid', 0),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_video_subtitle(self, bvid: str, cid: int = None) -> Dict:
        """获取视频字幕/CC字幕"""
        try:
            # 先获取cid（如果未提供）
            if not cid:
                detail = self.get_video_detail(bvid)
                if "error" in detail:
                    return detail
                cid = detail.get('cid', 0)
            
            if not cid:
                return {"error": "无法获取视频CID"}
            
            # 获取字幕列表
            url = "https://api.bilibili.com/x/player/wbi/v2"
            params = {'cid': cid, 'bvid': bvid}
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != 0:
                return {"error": data.get('message', '获取字幕失败')}
            
            subtitle_list = data.get('data', {}).get('subtitle', {}).get('subtitles', [])
            
            if not subtitle_list:
                return {"subtitles": [], "content": "该视频暂无字幕"}
            
            # 获取第一个字幕内容
            subtitle_url = subtitle_list[0].get('subtitle_url', '')
            if subtitle_url:
                if subtitle_url.startswith('//'):
                    subtitle_url = 'https:' + subtitle_url
                
                sub_resp = requests.get(subtitle_url, headers={'User-Agent': self.session.headers['User-Agent']}, timeout=30)
                sub_resp.raise_for_status()
                sub_data = sub_resp.json()
                
                # 提取纯文本
                body = sub_data.get('body', [])
                full_text = ' '.join([item.get('content', '') for item in body])
                
                return {
                    "subtitles": subtitle_list,
                    "content": full_text[:5000] + ('...' if len(full_text) > 5000 else '')
                }
            
            return {"subtitles": subtitle_list, "content": "无法获取字幕内容"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def summarize_video(self, bvid: str) -> Dict:
        """
        总结视频内容
        返回视频的核心信息、字幕摘要（如果有）、评论区洞察
        """
        try:
            # 获取视频详情
            detail = self.get_video_detail(bvid)
            if "error" in detail:
                return detail
            
            # 获取字幕
            cid = detail.get('cid', 0)
            subtitle = self.get_video_subtitle(bvid, cid)
            
            # 构建总结
            summary = {
                "video_info": {
                    "title": detail.get('title'),
                    "author": detail.get('owner'),
                    "description": detail.get('description', '')[:500] + ('...' if len(detail.get('description', '')) > 500 else ''),
                    "duration": detail.get('duration'),
                    "stats": {
                        "view": detail.get('view'),
                        "like": detail.get('like'),
                        "coin": detail.get('coin'),
                        "favorite": detail.get('favorite'),
                        "share": detail.get('share'),
                        "reply": detail.get('reply'),
                    },
                    "tags": detail.get('tags', []),
                    "cover": detail.get('pic'),
                    "url": f"https://www.bilibili.com/video/{bvid}",
                },
                "subtitle_available": "content" in subtitle and not subtitle.get("error"),
                "subtitle_preview": subtitle.get("content", "")[:800] + ('...' if len(subtitle.get("content", "")) > 800 else '') if subtitle.get("content") else None,
            }
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}


# ============ OpenClaw Skill 入口 ============

def search_bilibili_skill(keyword: str, limit: int = 10, sessdata: str = None) -> List[Dict]:
    """
    OpenClaw Skill 入口函数 - 搜索B站视频
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量
        sessdata: B站登录Cookie (可选，也可设置环境变量 BILIBILI_SESSDATA)
    """
    agent = BilibiliSearchAgent(sessdata=sessdata)
    videos = agent.search_videos_sync(keyword, page_size=min(limit, 50))
    
    return [{
        "title": v.title,
        "author": v.author,
        "plays": v.play_count,
        "likes": v.like_count,
        "duration": v.duration,
        "url": v.video_url,
        "bvid": v.bvid
    } for v in videos[:limit]]


def summarize_bilibili_video(bvid: str, sessdata: str = None) -> Dict:
    """
    OpenClaw Skill 入口函数 - 总结B站视频内容
    
    Args:
        bvid: 视频BV号（如 BV1uxA8zZEvG）
        sessdata: B站登录Cookie (可选)
    
    Returns:
        视频信息、字幕预览、数据指标
    """
    agent = BilibiliSearchAgent(sessdata=sessdata)
    return agent.summarize_video(bvid)


if __name__ == "__main__":
    # 使用方式:
    # 1. 设置环境变量: export BILIBILI_SESSDATA="你的sessdata"
    # 2. 或者直接传入: BilibiliSearchAgent(sessdata="xxx")
    
    agent = BilibiliSearchAgent()
    print("测试搜索: Python教程")
    print("(如果没有设置SESSDATA，会提示需要登录)\n")
    
    videos = agent.search_videos_sync("Python教程", page_size=5)
    agent.print_results()
