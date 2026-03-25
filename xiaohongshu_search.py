#!/usr/bin/env python3
"""
小红书笔记搜索 Agent - DrissionPage版
基于DrissionPage实现小红书笔记搜索功能

安装依赖:
pip install DrissionPage DataRecorder loguru

使用方法:
1. 首次运行需要扫码登录: python xiaohongshu_search.py --init
2. 后续搜索: python xiaohongshu_search.py --keyword "Python教程"
"""

import time
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from loguru import logger
from DrissionPage import ChromiumPage


@dataclass
class XiaohongshuNote:
    """小红书笔记数据模型"""
    note_id: str
    title: str
    description: str
    author: str
    author_id: str
    like_count: int
    comment_count: int
    collect_count: int
    cover_url: str
    note_url: str
    tags: List[str]


class XiaohongshuSearchAgent:
    """小红书笔记搜索Agent - 基于DrissionPage"""

    def __init__(self):
        self.results: List[XiaohongshuNote] = []
        self.page = ChromiumPage()
        self.logged_in = False

    def login(self):
        """扫码登录小红书"""
        logger.info("正在打开小红书登录页面...")
        self.page.get('https://www.xiaohongshu.com/explore')

        # 等待用户扫码登录
        logger.info("请在浏览器中扫码登录小红书")
        logger.info("登录成功后,按回车继续...")
        input("登录完成后按回车继续: ")

        # 验证登录状态
        try:
            # 检查是否有登录后的元素
            self.page.wait.ele_displayed('xpath://div[contains(@class, "user-info")]', timeout=5)
            self.logged_in = True
            logger.success("登录成功!")
        except Exception as e:
            logger.warning(f"登录验证失败: {e}")
            logger.info("如果已经登录,可以继续...")

    def search_notes_sync(
        self,
        keyword: str,
        page_num: int = 1,
        page_size: int = 20
    ) -> List[XiaohongshuNote]:
        """
        同步搜索小红书笔记

        Args:
            keyword: 搜索关键词
            page_num: 页码
            page_size: 每页数量

        Returns:
            笔记列表
        """
        try:
            # 构造搜索URL
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_profile_page"
            logger.info(f"正在搜索: {keyword}")

            # 打开搜索页面
            self.page.get(search_url)
            self.page.wait.load_start()

            # 等待笔记列表加载
            time.sleep(2)

            # 监听网络请求(可选)
            # self.page.listen.start('web/v1/feed')

            # 获取笔记卡片列表
            notes = self._extract_notes_from_page()

            self.results = notes
            return notes

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def _extract_notes_from_page(self) -> List[XiaohongshuNote]:
        """
        从当前页面提取笔记信息

        注意: 这个方法需要根据实际页面结构调整XPath
        """
        notes = []

        try:
            # 这里需要根据实际页面结构调整选择器
            # 以下是一个示例结构,实际使用时需要调整
            cards = self.page.eles('xpath://section[contains(@class, "note-item")]')

            logger.info(f"找到 {len(cards)} 个笔记卡片")

            for card in cards[:20]:  # 限制数量
                try:
                    note = self._parse_note_card(card)
                    if note:
                        notes.append(note)
                except Exception as e:
                    logger.warning(f"解析笔记卡片失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"提取笔记失败: {e}")

        return notes

    def _parse_note_card(self, card) -> Optional[XiaohongshuNote]:
        """
        解析单个笔记卡片

        注意: 这个方法需要根据实际页面结构调整
        """
        try:
            # 示例解析逻辑,需要根据实际页面调整
            # 这里仅作为示例,实际使用需要调整选择器

            # 获取链接
            link = card.ele('xpath:.//a')
            if not link:
                return None

            note_url = link.attr('href')
            note_id = note_url.split('/')[-1] if note_url else ''

            # 获取标题
            title_elem = card.ele('xpath:.//div[contains(@class, "title")]')
            title = title_elem.text if title_elem else ''

            # 获取作者
            author_elem = card.ele('xpath:.//div[contains(@class, "author")]')
            author = author_elem.text if author_elem else ''

            # 获取封面
            img_elem = card.ele('xpath:.//img')
            cover_url = img_elem.attr('src') if img_elem else ''

            # 获取点赞数等信息
            # 注意: 这些数据可能需要点击进入详情页才能获取
            like_count = 0
            comment_count = 0
            collect_count = 0

            return XiaohongshuNote(
                note_id=note_id,
                title=title,
                description='',  # 需要进入详情页获取
                author=author,
                author_id='',
                like_count=like_count,
                comment_count=comment_count,
                collect_count=collect_count,
                cover_url=cover_url,
                note_url=f"https://www.xiaohongshu.com{note_url}",
                tags=[]
            )

        except Exception as e:
            logger.warning(f"解析笔记失败: {e}")
            return None

    def get_note_detail(self, note_id: str) -> Dict:
        """
        获取笔记详情

        Args:
            note_id: 笔记ID

        Returns:
            笔记详情字典
        """
        try:
            note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
            logger.info(f"正在获取笔记详情: {note_id}")

            # 打开详情页
            self.page.get(note_url)
            self.page.wait.load_start()
            time.sleep(2)

            # 提取详情信息
            # 注意: 需要根据实际页面结构调整

            detail = {
                "note_id": note_id,
                "url": note_url,
                # 需要添加更多字段的提取逻辑
            }

            return detail

        except Exception as e:
            logger.error(f"获取笔记详情失败: {e}")
            return {"error": str(e)}

    def print_results(self):
        """打印搜索结果"""
        print(f"\n{'='*80}")
        print(f"找到 {len(self.results)} 条笔记")
        print(f"{'='*80}\n")

        for i, note in enumerate(self.results[:10], 1):
            print(f"【{i}】{note.title[:60]}{'...' if len(note.title) > 60 else ''}")
            print(f"    作者: {note.author} | 点赞: {note.like_count} | 评论: {note.comment_count}")
            print(f"    链接: {note.note_url}")
            print()

    def save_to_csv(self, filename: str = "xiaohongshu_notes.csv"):
        """
        保存结果到CSV文件

        Args:
            filename: 文件名
        """
        try:
            import pandas as pd

            df = pd.DataFrame([asdict(note) for note in self.results])
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.success(f"结果已保存到: {filename}")

        except ImportError:
            logger.warning("需要安装pandas: pip install pandas")
        except Exception as e:
            logger.error(f"保存失败: {e}")


# ============ 命令行入口 ============

def main():
    parser = argparse.ArgumentParser(description='小红书笔记搜索工具')
    parser.add_argument('--init', action='store_true', help='初始化登录')
    parser.add_argument('--keyword', type=str, help='搜索关键词')
    parser.add_argument('--page', type=int, default=1, help='页码')
    parser.add_argument('--output', type=str, default='xiaohongshu_notes.csv', help='输出文件名')

    args = parser.parse_args()

    agent = XiaohongshuSearchAgent()

    # 初始化登录
    if args.init:
        agent.login()
        logger.info("初始化完成,下次可以跳过--init参数")
        return

    # 搜索笔记
    if args.keyword:
        notes = agent.search_notes_sync(
            keyword=args.keyword,
            page_num=args.page
        )

        if notes:
            agent.print_results()
            agent.save_to_csv(args.output)
        else:
            logger.warning("未找到相关笔记")
    else:
        logger.error("请使用 --keyword 参数指定搜索关键词")
        logger.info("示例: python xiaohongshu_search.py --keyword 'Python教程'")


if __name__ == "__main__":
    main()
