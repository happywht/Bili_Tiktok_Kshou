#!/usr/bin/env python3
"""
B站视频搜索 Agent - CLI版本
支持命令行参数、批量搜索、结果导出

安装依赖:
    pip install bilibili-api-python aiohttp click rich

使用示例:
    # 基础搜索
    python bilibili_cli.py "Python教程"
    
    # 按播放量排序，获取50个结果
    python bilibili_cli.py "Python教程" --order click --limit 50
    
    # 保存为CSV
    python bilibili_cli.py "Python教程" --format csv --output result.csv
    
    # 获取视频详情
    python bilibili_cli.py --detail BV1xx411c7mD
"""

import asyncio
import json
import csv
import click
from typing import List
from dataclasses import asdict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from bilibili_search import BilibiliSearchAgent, BilibiliVideo


console = Console()


def print_table(videos: List[BilibiliVideo]):
    """使用 Rich 打印表格"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", width=4)
    table.add_column("标题", width=40)
    table.add_column("UP主", width=12)
    table.add_column("播放量", width=10)
    table.add_column("点赞", width=8)
    table.add_column("时长", width=8)
    table.add_column("BV号", width=14)
    
    for i, v in enumerate(videos, 1):
        table.add_row(
            str(i),
            v.title[:37] + "..." if len(v.title) > 40 else v.title,
            v.author,
            f"{v.play_count:,}",
            f"{v.like_count:,}",
            v.duration,
            v.bvid
        )
    
    console.print(table)


def save_to_csv(videos: List[BilibiliVideo], filepath: str):
    """保存到CSV"""
    if not videos:
        console.print("[yellow]没有数据可保存[/yellow]")
        return
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=asdict(videos[0]).keys())
        writer.writeheader()
        for v in videos:
            writer.writerow(asdict(v))
    
    console.print(f"[green]✓ 已保存到 {filepath}[/green]")


@click.command()
@click.argument('keyword', required=False)
@click.option('--detail', '-d', help='获取指定BV号的视频详情')
@click.option('--order', '-o', default='totalrank', 
              type=click.Choice(['totalrank', 'click', 'pubdate', 'dm']),
              help='排序方式: totalrank(综合), click(点击量), pubdate(发布时间), dm(弹幕)')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--limit', '-l', default=20, help='每页数量(最大50)')
@click.option('--pages', default=1, help='爬取页数')
@click.option('--format', '-f', 'output_format', default='table',
              type=click.Choice(['table', 'json', 'csv']),
              help='输出格式')
@click.option('--output', '-O', help='输出文件路径')
async def main(keyword, detail, order, page, limit, pages, output_format, output):
    """
    B站视频搜索工具
    
    KEYWORD: 搜索关键词
    """
    agent = BilibiliSearchAgent()
    
    # 获取视频详情模式
    if detail:
        console.print(f"[blue]正在获取视频 {detail} 的详情...[/blue]")
        info = await agent.get_video_detail(detail)
        if info:
            console.print_json(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            console.print("[red]获取失败[/red]")
        return
    
    # 检查关键词
    if not keyword:
        console.print("[red]错误: 请提供搜索关键词或使用 --detail 参数[/red]")
        return
    
    # 执行搜索
    all_videos = []
    
    with Progress() as progress:
        task = progress.add_task(f"[cyan]搜索 '{keyword}'...", total=pages)
        
        for p in range(page, page + pages):
            videos = await agent.search_videos(
                keyword=keyword,
                page=p,
                page_size=min(limit, 50),
                order=order
            )
            all_videos.extend(videos)
            progress.update(task, advance=1)
    
    if not all_videos:
        console.print("[yellow]未找到相关视频[/yellow]")
        return
    
    # 输出结果
    if output_format == 'table':
        print_table(all_videos)
        console.print(f"\n[dim]共找到 {len(all_videos)} 个视频[/dim]")
        
    elif output_format == 'json':
        filepath = output or f"bilibili_{keyword}.json"
        data = [asdict(v) for v in all_videos]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        console.print(f"[green]✓ 已保存到 {filepath}[/green]")
        
    elif output_format == 'csv':
        filepath = output or f"bilibili_{keyword}.csv"
        save_to_csv(all_videos, filepath)


if __name__ == "__main__":
    asyncio.run(main())
