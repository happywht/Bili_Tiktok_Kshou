#!/usr/bin/env python3
"""
Bilibili Search Skill - OpenClaw Tool Entry
"""

import sys
import json
import os

# 添加workspace目录到路径
sys.path.insert(0, '/root/.openclaw/workspace')

from bilibili_search import BilibiliSearchAgent


def search_action(args, sessdata):
    """搜索视频"""
    keyword = args.get("keyword")
    limit = int(args.get("limit", 10))
    order = args.get("order", "totalrank")
    
    if not keyword:
        return {"error": "keyword 参数必填", "success": False}
    
    agent = BilibiliSearchAgent(sessdata=sessdata)
    videos = agent.search_videos_sync(keyword, page_size=min(limit, 50), order=order)
    
    if not videos:
        return {
            "error": "未找到视频或需要登录。请设置 BILIBILI_SESSDATA 环境变量或在参数中提供 sessdata",
            "success": False
        }
    
    results = [{
        "title": v.title,
        "author": v.author,
        "plays": v.play_count,
        "likes": v.like_count,
        "duration": v.duration,
        "url": v.video_url,
        "bvid": v.bvid
    } for v in videos[:limit]]
    
    return {
        "success": True,
        "keyword": keyword,
        "count": len(results),
        "videos": results
    }


def summarize_action(args, sessdata):
    """总结视频内容"""
    bvid = args.get("bvid")
    
    if not bvid:
        return {"error": "bvid 参数必填 (如 BV1uxA8zZEvG)", "success": False}
    
    agent = BilibiliSearchAgent(sessdata=sessdata)
    summary = agent.summarize_video(bvid)
    
    if "error" in summary:
        return {"error": summary["error"], "success": False}
    
    return {
        "success": True,
        "bvid": bvid,
        "summary": summary
    }


def main():
    """OpenClaw Tool 入口"""
    try:
        # 解析参数
        if len(sys.argv) < 2:
            print(json.dumps({
                "error": "缺少参数",
                "usage": "{action: 'search', keyword: 'xxx'} 或 {action: 'summarize', bvid: 'BVxxx'}",
                "success": False
            }, ensure_ascii=False))
            return
        
        args = json.loads(sys.argv[1])
        action = args.get("action", "search")
        sessdata = args.get("sessdata") or os.environ.get("BILIBILI_SESSDATA")
        
        # 从credentials.json读取sessdata
        if not sessdata:
            try:
                creds_path = "/root/.openclaw/workspace/config/credentials.json"
                if os.path.exists(creds_path):
                    with open(creds_path) as f:
                        creds = json.load(f)
                        sessdata = creds.get("bilibili", {}).get("sessdata")
            except:
                pass
        
        # 执行对应操作
        if action == "search":
            result = search_action(args, sessdata)
        elif action == "summarize":
            result = summarize_action(args, sessdata)
        else:
            result = {"error": f"未知的action: {action}", "success": False}
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "success": False
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
