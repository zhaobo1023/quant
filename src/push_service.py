# -*- coding: utf-8 -*-
"""
飞书推送服务

通过飞书Webhook推送消息
"""
import os
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import execute_query
from dotenv import load_dotenv

load_dotenv()


class FeishuPushService:
    """飞书推送服务"""

    def __init__(self):
        self.webhook_url = os.getenv('FEISHU_WEBHOOK_URL')

        if not self.webhook_url:
            print("警告: 未配置飞书Webhook URL")

    def send_text_message(self, text: str) -> bool:
        """
        发送文本消息

        Args:
            text: 文本内容

        Returns:
            是否成功
        """
        if not self.webhook_url:
            print("未配置飞书Webhook URL，跳过推送")
            return False

        payload = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()

            if result.get('StatusCode') == 0:
                print("消息推送成功")
                return True
            else:
                print(f"消息推送失败: {result}")
                return False
        except Exception as e:
            print(f"消息推送异常: {e}")
            return False

    def send_card_message(self, title: str, content: List[List[Dict]]) -> bool:
        """
        发送卡片消息

        Args:
            title: 标题
            content: 卡片内容

        Returns:
            是否成功
        """
        if not self.webhook_url:
            print("未配置飞书Webhook URL，跳过推送")
            return False

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": content
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()

            if result.get('StatusCode') == 0:
                print("卡片消息推送成功")
                return True
            else:
                print(f"卡片消息推送失败: {result}")
                return False
        except Exception as e:
            print(f"卡片消息推送异常: {e}")
            return False

    def send_position_report(self, positions: List[Dict]) -> bool:
        """
        发送持仓报告

        Args:
            positions: 持仓列表

        Returns:
            是否成功
        """
        if not positions:
            return self.send_text_message("今日无持仓数据")

        # 构建卡片内容
        content = []

        # 添加持仓列表
        for pos in positions:
            element = {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{pos.get('stock_code', '')}** {pos.get('stock_name', '')}\n"
                               f"持仓: {pos.get('shares', 0)}股\n"
                               f"成本: ¥{pos.get('cost_price', 0):.2f}"
                }
            }
            content.append(element)
            content.append({"tag": "hr"})

        # 添加时间戳
        content.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })

        # 发送卡片消息
        return self.send_card_message("持仓报告", content)

    def send_analysis_report(self, report: Dict) -> bool:
        """
        发送分析报告

        Args:
            report: 分析报告

        Returns:
            是否成功
        """
        # 构建卡片内容
        content = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**股票代码**: {report.get('stock_code', '')}\n"
                               f"**信号类型**: {report.get('signal_type', '')}\n"
                               f"**信号强度**: {report.get('signal_strength', 0):.2f}\n"
                               f"**趋势方向**: {report.get('trend_direction', '')}\n"
                               f"**风险等级**: {report.get('risk_level', '')}"
                }
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**操作建议**:\n{report.get('recommendation', '')}"
                }
            },
            {"tag": "hr"},
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"报告时间: {report.get('report_date', '')}"
                    }
                ]
            }
        ]

        # 发送卡片消息
        return self.send_card_message("技术分析报告", content)


class MockPushService:
    """模拟推送服务（用于测试）"""

    def send_text_message(self, text: str) -> bool:
        print(f"[模拟] 发送文本消息: {text}")
        return True

    def send_card_message(self, title: str, content: List[List[Dict]]) -> bool:
        print(f"[模拟] 发送卡片消息: {title}")
        return True

    def send_position_report(self, positions: List[Dict]) -> bool:
        print(f"[模拟] 发送持仓报告: {len(positions)}个持仓")
        return True

    def send_analysis_report(self, report: Dict) -> bool:
        print(f"[模拟] 发送分析报告: {report.get('stock_code', '')}")
        return True


def main():
    """测试推送服务"""
    # 使用模拟服务（因为没有配置飞书Webhook）
    push_service = MockPushService()

    # 测试发送文本消息
    push_service.send_text_message("这是一条测试消息")

    # 测试发送持仓报告
    positions = [
        {
            'stock_code': '600519.SH',
            'stock_name': '贵州茅台',
            'shares': 100,
            'cost_price': 1800.00
        },
        {
            'stock_code': '000858.SZ',
            'stock_name': '五粮液',
            'shares': 200,
            'cost_price': 150.00
        }
    ]
    push_service.send_position_report(positions)

    # 测试发送分析报告
    report = {
        'stock_code': '600519.SH',
        'signal_type': 'MACD金叉',
        'signal_strength': 0.85,
        'trend_direction': '上升趋势',
        'risk_level': '中等',
        'recommendation': '建议逢低加仓',
        'report_date': '2025-03-13'
    }
    push_service.send_analysis_report(report)


if __name__ == "__main__":
    main()
