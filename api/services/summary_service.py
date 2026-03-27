"""
AI 视频总结服务

通过 yt-dlp 提取视频字幕，调用 LLM 生成内容总结。
支持 B站/抖音/小红书视频 URL。
"""
import json
import re
import logging
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# 支持的视频平台
PLATFORM_PATTERNS = {
    'bilibili': [
        r'bilibili\.com/video/',
        r'b23\.tv/',
        r'BV[a-zA-Z0-9]+',
    ],
    'douyin': [
        r'douyin\.com/video/',
        r'iesdouyin\.com/share/video/',
    ],
    'xiaohongshu': [
        r'xiaohongshu\.com/explore/',
        r'xiaohongshu\.com/discovery/item/',
        r'xhslink\.com/',
    ],
}


def detect_platform(url: str) -> Optional[str]:
    """从 URL 检测视频平台"""
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url):
                return platform
    return None


async def extract_subtitles_ytdlp(url: str, timeout: int = 30) -> str:
    """通过 yt-dlp 提取视频字幕"""
    cmd = [
        'yt-dlp',
        '--skip-download',
        '--write-auto-sub',
        '--write-sub',
        '--sub-langs', 'zh', 'zh-Hans', 'zh-CN', 'zh-Hans-CN', 'zh-TW', 'en',
        '--sub-format', 'srt',
        '--convert-subs', 'srt',
        '--print', 'to_native',
        '--no-warnings',
        '--no-progress',
        '--no-check-certificates',
        '--playlist-items', '1',
        '-o', '-',
        url,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise RuntimeError(f"字幕提取超时（{timeout}秒）")

    if process.returncode != 0:
        raise RuntimeError(f"yt-dlp 执行失败: {stderr.decode('utf-8', errors='replace')[:500]}")

    text = stdout.decode('utf-8', errors='replace').strip()

    if not text or text == '-':
        raise RuntimeError("该视频没有可用字幕")

    return text


async def extract_subtitles_bilibili_api(bvid: str, sessdata: str = "") -> str:
    """通过 B站 API 获取字幕（备用方案）"""
    import httpx

    headers = {}
    if sessdata:
        headers['Cookie'] = f'SESSDATA={sessdata}'

    async with httpx.AsyncClient(timeout=15, headers=headers) as client:
        # 获取视频 cid
        resp = await client.get(
            'https://api.bilibili.com/x/web-interface/view',
            params={'bvid': bvid},
        )
        data = resp.json()
        if data.get('code') != 0:
            raise RuntimeError(f"B站 API 错误: {data.get('message', '未知错误')}")

        cid = data['data']['cid']
        aid = data['data']['aid']

        # 获取字幕列表
        resp = await client.get(
            'https://api.bilibili.com/x/player/v2',
            params={'aid': aid, 'cid': cid},
        )
        subtitle_data = resp.json().get('data', {}).get('subtitle', {})

        if not subtitle_data.get('subtitles'):
            raise RuntimeError("该视频没有可用字幕")

        subtitle_url = subtitle_data['subtitles'][0].get('subtitle_url', '')
        if not subtitle_url:
            raise RuntimeError("字幕 URL 为空")

        # 下载字幕
        if subtitle_url.startswith('//'):
            subtitle_url = 'https:' + subtitle_url

        resp = await client.get(subtitle_url)
        subtitle_json = resp.json()

        # 解析 JSON 字幕
        body = subtitle_json.get('body', [])
        lines = []
        for item in body:
            content = item.get('content', '')
            if content:
                lines.append(content)

        if not lines:
            raise RuntimeError("字幕内容为空")

        return '\n'.join(lines)


async def call_llm(prompt: str, api_key: str, api_base: str = "https://api.deepseek.com/v1",
                   model: str = "deepseek-chat") -> str:
    """调用 OpenAI 兼容的 LLM API"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': '你是一个视频内容分析助手。请根据提供的视频字幕，生成简洁、准确的内容总结。用中文回复。'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 2000,
        'temperature': 0.3,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f'{api_base}/chat/completions',
            headers=headers,
            json=payload,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"LLM API 调用失败: HTTP {resp.status_code} - {resp.text[:300]}")

        data = resp.json()
        return data['choices'][0]['message']['content'].strip()


async def summarize_video(url: str, api_key: str, api_base: str = "https://api.deepseek.com/v1",
                           model: str = "deepseek-chat", sessdata: str = "",
                           timeout: int = 30) -> Dict[str, Any]:
    """
    总结视频内容

    Args:
        url: 视频 URL
        api_key: LLM API Key
        api_base: LLM API Base URL
        model: LLM 模型名
        sessdata: B站 SESSDATA（备用字幕提取）
        timeout: 字幕提取超时秒数

    Returns:
        包含总结结果的字典
    """
    platform = detect_platform(url)
    if not platform:
        raise ValueError(f"不支持的视频链接: {url}")

    # 提取字幕
    subtitle_text = ""
    extraction_method = ""

    # 方案1: yt-dlp
    try:
        subtitle_text = await extract_subtitles_ytdlp(url, timeout)
        extraction_method = "yt-dlp"
    except Exception as e:
        logger.warning(f"yt-dlp 提取失败: {e}")

    # 方案2: B站 API（备用）
    if not subtitle_text and platform == 'bilibili':
        try:
            bvid_match = re.search(r'BV[a-zA-Z0-9]+', url)
            if bvid_match:
                subtitle_text = await extract_subtitles_bilibili_api(bvid_match.group(), sessdata)
                extraction_method = "bilibili-api"
        except Exception as e:
            logger.warning(f"B站 API 提取失败: {e}")

    if not subtitle_text:
        raise RuntimeError("无法提取视频字幕，该视频可能没有字幕/CC 字幕")

    # 截取前 8000 字符（避免 token 超限）
    truncated = len(subtitle_text) > 8000
    content_for_llm = subtitle_text[:8000]
    if truncated:
        content_for_llm += "\n\n[字幕已截断]"

    # 调用 LLM
    prompt = f"""请根据以下视频字幕，生成一份结构化的视频内容总结。

要求：
1. 用 3-5 句话概括视频主要内容
2. 列出 3-5 个关键要点
3. 提取视频中提到的所有工具、框架、技术名词

视频字幕：
{content_for_llm}"""

    ai_summary = await call_llm(prompt, api_key, api_base, model)

    return {
        'platform': platform,
        'url': url,
        'extraction_method': extraction_method,
        'subtitle_length': len(subtitle_text),
        'subtitle_preview': subtitle_text[:500] + ('...' if len(subtitle_text) > 500 else ''),
        'ai_summary': ai_summary,
    }
