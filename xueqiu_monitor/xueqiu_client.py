#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球用户帖子抓取客户端

使用方法：
1. 命令行模式: python xueqiu_client.py <用户ID> [帖子数量]
2. 交互模式: 直接运行，按提示输入

注意：由于雪球有反爬机制，建议使用登录Cookie
获取Cookie方法：
1. Chrome浏览器登录 https://xueqiu.com
2. 按F12打开开发者工具 -> Network标签
3. 刷新页面，点击任意XHR请求
4. 在Request Headers中找到Cookie字段，复制全部内容
"""

import requests
import re
import html
import time
import random
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class XueqiuClient:
    """雪球 API 客户端"""

    BASE_URL = "https://xueqiu.com"
    # 尝试多个可能的API端点
    TIMELINE_URL_V4 = "https://xueqiu.com/v4/statuses/user_timeline.json"
    TIMELINE_URL_V5 = "https://xueqiu.com/v5/statuses/user_timeline.json"
    USER_URL = "https://xueqiu.com/v4/user/show.json"

    def __init__(self, cookie: str = "", delay: tuple = (2, 4)):
        """
        初始化客户端

        Args:
            cookie: 雪球登录 Cookie（强烈建议提供）
            delay: 请求间隔秒数范围，默认 2-4 秒
        """
        self.session = requests.Session()
        self.delay = delay
        self.cookie = cookie

        # 设置请求头，模拟真实浏览器
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://xueqiu.com/",
            "Origin": "https://xueqiu.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        })

        if cookie:
            self.session.headers["Cookie"] = cookie

        # 获取 guest token
        self._get_guest_token()

    def _get_guest_token(self):
        """访问首页刷新 guest token"""
        try:
            resp = self.session.get(self.BASE_URL, timeout=15)
            # Cookie 会自动保存在 session 中
            # 检查是否有 xq_a_token
            cookies = self.session.cookies.get_dict()
            if 'xq_a_token' in cookies:
                print(f"✓ 已获取 xq_a_token")
        except Exception as e:
            print(f"⚠ 获取 guest token 时出错: {e}")

    def _random_delay(self):
        """随机延迟"""
        delay = random.uniform(*self.delay)
        time.sleep(delay)

    def _clean_text(self, text: str) -> str:
        """
        清洗帖子文本，去除 HTML 标签
        """
        if not text:
            return ""
        # 去除 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)
        # 处理 HTML 转义字符
        text = html.unescape(text)
        # 去除多余空白
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _format_time(self, timestamp_ms: int) -> str:
        """将毫秒时间戳格式化为可读字符串"""
        if not timestamp_ms:
            return "未知时间"
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%Y-%m-%d %H:%M")

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        self._random_delay()

        # 尝试从时间线API获取用户信息
        params = {
            "user_id": user_id,
            "page": 1,
            "count": 1
        }

        for url in [self.TIMELINE_URL_V5, self.TIMELINE_URL_V4]:
            try:
                resp = self.session.get(url, params=params, timeout=15)

                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if "user" in data:
                            user = data["user"]
                            return {
                                "id": user_id,
                                "name": user.get("screen_name", "未知"),
                                "followers": user.get("followers_count", 0),
                                "description": user.get("description", "")
                            }
                    except json.JSONDecodeError:
                        continue

            except Exception as e:
                continue

        # 如果从时间线获取失败，尝试用户API
        try:
            resp = self.session.get(self.USER_URL, params={"id": user_id}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "id": user_id,
                    "name": data.get("screen_name", "未知"),
                    "followers": data.get("followers_count", 0),
                    "description": data.get("description", "")
                }
        except:
            pass

        return None

    def get_user_posts(self, user_id: str, count: int = 10, since_hours: int = None) -> List[Dict]:
        """获取用户帖子列表"""
        self._random_delay()

        # 雪球 API 每次最多返回 20 条
        count = min(count, 20)

        params = {
            "user_id": user_id,
            "page": 1,
            "count": count
        }

        posts = []

        # 尝试不同的API端点
        for url in [self.TIMELINE_URL_V5, self.TIMELINE_URL_V4]:
            try:
                resp = self.session.get(url, params=params, timeout=15)

                if resp.status_code != 200:
                    continue

                # 检查是否返回了有效的JSON
                content_type = resp.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    continue

                try:
                    data = resp.json()
                except json.JSONDecodeError:
                    continue

                statuses = data.get("statuses", [])
                if not statuses:
                    continue

                cutoff_time = None
                if since_hours:
                    cutoff_time = datetime.now().timestamp() - since_hours * 3600

                for status in statuses:
                    created_at = status.get("created_at", 0) / 1000

                    # 时间过滤
                    if cutoff_time and created_at < cutoff_time:
                        continue

                    post = {
                        "id": str(status.get("id", "")),
                        "time": self._format_time(status.get("created_at", 0)),
                        "text": self._clean_text(status.get("text", "")),
                        "like_count": status.get("like_count", 0),
                        "reply_count": status.get("reply_count", 0),
                        "retweet_count": status.get("retweet_count", 0),
                        "url": f"https://xueqiu.com/{status.get('user_id', user_id)}/{status.get('id', '')}"
                    }
                    posts.append(post)

                if posts:
                    return posts

            except Exception as e:
                print(f"⚠ 请求 {url} 时出错: {e}")
                continue

        return posts


def get_cookie_from_env() -> str:
    """从环境变量获取Cookie"""
    return os.environ.get("XUEQIU_COOKIE", "")


def get_cookie_from_file() -> str:
    """从配置文件获取Cookie"""
    cookie_file = os.path.join(os.path.dirname(__file__), ".xueqiu_cookie")
    if os.path.exists(cookie_file):
        with open(cookie_file, "r") as f:
            return f.read().strip()
    return ""


def fetch_user_posts(user_id: str, count: int = 10, cookie: str = "") -> tuple:
    """
    抓取指定用户的最近帖子

    Args:
        user_id: 雪球用户 ID（从主页 URL 获取）
        count: 帖子数量，默认 10
        cookie: 登录 Cookie（可选）

    Returns:
        (用户信息, 帖子列表)
    """
    # 优先级：传入参数 > 环境变量 > 配置文件
    if not cookie:
        cookie = get_cookie_from_env()
    if not cookie:
        cookie = get_cookie_from_file()

    client = XueqiuClient(cookie=cookie)

    # 获取用户信息
    user_info = client.get_user_info(user_id)

    # 获取帖子
    posts = client.get_user_posts(user_id, count=count)

    return user_info, posts


def print_results(user_info: Optional[Dict], posts: List[Dict]):
    """打印结果"""
    if user_info:
        print(f"\n{'='*60}")
        print(f"用户: {user_info['name']}")
        print(f"粉丝: {user_info['followers']:,}")
        print(f"简介: {user_info['description'][:50]}..." if len(user_info['description']) > 50 else f"简介: {user_info['description']}")
        print(f"{'='*60}")

    if posts:
        for i, post in enumerate(posts, 1):
            print(f"\n【帖子 {i}】")
            print(f"时间: {post['time']}")
            print(f"互动: 👍{post['like_count']} | 💬{post['reply_count']} | 🔄{post['retweet_count']}")
            # 显示内容，超过150字符截断
            text = post['text']
            if len(text) > 150:
                print(f"内容: {text[:150]}...")
            else:
                print(f"内容: {text}")
            print(f"链接: {post['url']}")
    else:
        print("\n" + "="*60)
        print("❌ 未获取到帖子")
        print("="*60)
        print("\n可能的原因：")
        print("1. 用户 ID 不正确")
        print("2. 该用户设置了隐私保护")
        print("3. 需要提供登录 Cookie")
        print("\n获取Cookie方法：")
        print("1. Chrome浏览器登录 https://xueqiu.com")
        print("2. 按F12打开开发者工具 -> Network标签")
        print("3. 刷新页面，点击任意XHR请求")
        print("4. 在Request Headers中找到Cookie字段，复制全部内容")
        print("5. 设置环境变量: export XUEQIU_COOKIE='你的cookie'")
        print("   或创建 .xueqiu_cookie 文件保存cookie")


def main():
    """命令行入口"""
    import sys

    print("\n" + "="*60)
    print("雪球用户帖子抓取工具")
    print("="*60)

    # 检查命令行参数
    if len(sys.argv) < 2:
        print("\n用法: python xueqiu_client.py <用户ID> [帖子数量]")
        print("示例: python xueqiu_client.py 2145302932 10")
        print("\n提示: 可设置环境变量 XUEQIU_COOKIE 或创建 .xueqiu_cookie 文件")
        sys.exit(1)

    user_id = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    count = min(max(count, 1), 20)

    # 从环境变量或文件获取Cookie
    cookie = get_cookie_from_env() or get_cookie_from_file()
    if cookie:
        print("✓ 已从配置中加载Cookie")
    else:
        print("⚠ 未检测到Cookie，使用Guest模式（可能受限）")

    print(f"\n正在抓取用户 {user_id} 的最近 {count} 条帖子...")

    user_info, posts = fetch_user_posts(user_id, count, cookie)
    print_results(user_info, posts)


if __name__ == "__main__":
    main()
