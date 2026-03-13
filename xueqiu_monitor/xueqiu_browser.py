#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球用户帖子抓取 - Playwright 版本

使用真实浏览器模拟，绕过反爬机制

使用方法：
    python xueqiu_browser.py <用户ID> [帖子数量]

示例：
    python xueqiu_browser.py 2145302932 10
"""

import asyncio
import re
import html as html_module
from datetime import datetime
from typing import List, Dict, Optional
import sys


def clean_text(text: str) -> str:
    """清洗帖子文本"""
    if not text:
        return ""
    # 去除 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)
    # 处理 HTML 转义字符
    text = html_module.unescape(text)
    # 去除多余空白
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_time(timestamp_ms: int) -> str:
    """格式化时间戳"""
    if not timestamp_ms:
        return "未知时间"
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime("%Y-%m-%d %H:%M")


async def fetch_user_posts_browser(user_id: str, count: int = 10, headless: bool = True) -> tuple:
    """
    使用 Playwright 模拟浏览器抓取用户帖子

    Args:
        user_id: 雪球用户 ID
        count: 要获取的帖子数量
        headless: 是否无头模式运行

    Returns:
        (用户信息, 帖子列表)
    """
    from playwright.async_api import async_playwright

    user_info = None
    posts = []

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
        )

        page = await context.new_page()

        # 拦截 API 请求
        api_data = {}

        async def handle_response(response):
            url = response.url
            if 'user_timeline.json' in url:
                try:
                    data = await response.json()
                    api_data['timeline'] = data
                except:
                    pass

        page.on('response', handle_response)

        try:
            print(f"正在访问雪球首页...")
            # 先访问首页获取 cookie
            await page.goto('https://xueqiu.com/', wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)

            print(f"正在访问用户 {user_id} 的主页...")
            # 访问用户主页
            user_url = f'https://xueqiu.com/u/{user_id}'
            await page.goto(user_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)

            # 从 API 数据中解析
            if 'timeline' in api_data:
                data = api_data['timeline']

                # 获取用户信息
                if 'user' in data:
                    user = data['user']
                    user_info = {
                        'id': user_id,
                        'name': user.get('screen_name', '未知'),
                        'followers': user.get('followers_count', 0),
                        'description': user.get('description', '')
                    }

                # 获取帖子
                statuses = data.get('statuses', [])
                for status in statuses[:count]:
                    post = {
                        'id': str(status.get('id', '')),
                        'time': format_time(status.get('created_at', 0)),
                        'text': clean_text(status.get('text', '')),
                        'like_count': status.get('like_count', 0),
                        'reply_count': status.get('reply_count', 0),
                        'retweet_count': status.get('retweet_count', 0),
                        'url': f"https://xueqiu.com/{status.get('user_id', user_id)}/{status.get('id', '')}"
                    }
                    posts.append(post)

            # 如果 API 数据获取失败，尝试从页面直接抓取
            if not posts:
                print("从 API 获取失败，尝试从页面抓取...")
                posts = await scrape_from_page(page, count)
                user_info = await get_user_info_from_page(page, user_id)

        except Exception as e:
            print(f"抓取出错: {e}")
        finally:
            await browser.close()

    return user_info, posts


async def scrape_from_page(page, count: int) -> List[Dict]:
    """从页面直接抓取帖子"""
    posts = []

    try:
        # 等待页面加载
        await asyncio.sleep(2)

        # 尝试多种选择器
        selectors = ['.timeline__item', '.status-item', '.tweet-item', '[class*="timeline"]']
        items = []

        for selector in selectors:
            items = await page.query_selector_all(selector)
            if items:
                print(f"找到 {len(items)} 个帖子元素 (选择器: {selector})")
                break

        for i, item in enumerate(items[:count]):
            try:
                # 获取帖子内容
                content_el = await item.query_selector('.timeline__content, .content, .text')
                text = await content_el.inner_text() if content_el else ""

                # 获取时间
                time_el = await item.query_selector('.timeline__created, .time, .created_at')
                time_text = await time_el.inner_text() if time_el else ""

                # 获取链接
                link_el = await item.query_selector('a[href*="/"]')
                post_url = ""
                if link_el:
                    post_url = await link_el.get_attribute('href')
                    if post_url and not post_url.startswith('http'):
                        post_url = f"https://xueqiu.com{post_url}"

                if text:  # 只添加有内容的帖子
                    post = {
                        'id': '',
                        'time': time_text,
                        'text': text.strip()[:500],
                        'like_count': 0,
                        'reply_count': 0,
                        'retweet_count': 0,
                        'url': post_url
                    }
                    posts.append(post)
            except Exception as e:
                continue
    except Exception as e:
        print(f"页面抓取失败: {e}")

    return posts


async def get_user_info_from_page(page, user_id: str) -> Optional[Dict]:
    """从页面获取用户信息"""
    try:
        # 尝试多种选择器
        name_el = await page.query_selector('.user__name, .name, h1, .screen-name')
        name = await name_el.inner_text() if name_el else "未知"

        desc_el = await page.query_selector('.user__description, .description, .bio')
        description = await desc_el.inner_text() if desc_el else ""

        return {
            'id': user_id,
            'name': name.strip(),
            'followers': 0,
            'description': description.strip()
        }
    except:
        return None


def print_results(user_info: Optional[Dict], posts: List[Dict]):
    """打印结果"""
    if user_info:
        print(f"\n{'='*60}")
        print(f"用户: {user_info['name']}")
        if user_info['followers']:
            print(f"粉丝: {user_info['followers']:,}")
        if user_info['description']:
            desc = user_info['description']
            print(f"简介: {desc[:50]}..." if len(desc) > 50 else f"简介: {desc}")
        print(f"{'='*60}")

    if posts:
        for i, post in enumerate(posts, 1):
            print(f"\n【帖子 {i}】")
            print(f"时间: {post['time']}")
            if post['like_count'] or post['reply_count']:
                print(f"互动: 👍{post['like_count']} | 💬{post['reply_count']} | 🔄{post['retweet_count']}")
            text = post['text']
            print(f"内容: {text[:200]}..." if len(text) > 200 else f"内容: {text}")
            print(f"链接: {post['url']}")
    else:
        print("\n" + "="*60)
        print("❌ 未获取到帖子")
        print("="*60)
        print("\n可能的原因：")
        print("1. 用户 ID 不正确")
        print("2. 该用户没有发布帖子")
        print("3. 网络问题")


async def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("\n用法: python xueqiu_browser.py <用户ID> [帖子数量]")
        print("示例: python xueqiu_browser.py 2145302932 10")
        print("\n提示: 此版本使用真实浏览器模拟，首次运行需要安装 Chromium")
        print("      运行: pip install playwright && python -m playwright install chromium")
        sys.exit(1)

    user_id = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    count = min(max(count, 1), 20)

    print("\n" + "="*60)
    print("雪球用户帖子抓取工具 (Playwright 版)")
    print("="*60)
    print(f"\n正在抓取用户 {user_id} 的最近 {count} 条帖子...")

    user_info, posts = await fetch_user_posts_browser(user_id, count)
    print_results(user_info, posts)


if __name__ == "__main__":
    asyncio.run(main())
