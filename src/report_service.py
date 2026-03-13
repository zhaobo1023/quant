# -*- coding: utf-8 -*-
"""
报告生成服务

生成持仓报告、分析报告等
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import execute_query


class ReportService:
    """报告生成服务"""

    def __init__(self):
        pass

    def get_positions(self, account_tag: Optional[str] = None) -> List[Dict]:
        """
        获取持仓信息

        Args:
            account_tag: 账户标签（可选）

        Returns:
            持仓列表
        """
        sql = "SELECT * FROM model_trade_position WHERE status = 1"
        params = []

        if account_tag:
            sql += " AND account_tag = %s"
            params.append(account_tag)

        rows = execute_query(sql, params if params else None)
        return rows

    def get_technical_indicators(self, stock_code: str, days: int = 30) -> List[Dict]:
        """
        获取技术指标

        Args:
            stock_code: 股票代码
            days: 天数

        Returns:
            技术指标列表
        """
        sql = """
        SELECT * FROM trade_technical_indicator
        WHERE stock_code = %s
        ORDER BY trade_date DESC
        LIMIT %s
        """
        rows = execute_query(sql, (stock_code, days))
        return rows

    def analyze_signal(self, indicators: List[Dict]) -> Dict:
        """
        分析技术指标，生成信号

        Args:
            indicators: 技术指标列表

        Returns:
            信号分析结果
        """
        if not indicators:
            return {}

        latest = indicators[0]
        signal = {
            'signal_type': None,
            'signal_strength': 0,
            'trend_direction': 'neutral',
            'trend_strength': 0,
            'risk_level': 'medium',
            'recommendation': ''
        }

        # MACD信号
        if latest.get('macd_dif') and latest.get('macd_dea'):
            if latest['macd_dif'] > latest['macd_dea']:
                signal['signal_type'] = 'MACD金叉'
                signal['signal_strength'] = min((latest['macd_dif'] - latest['macd_dea']) / latest['macd_dea'] * 100, 100)
            else:
                signal['signal_type'] = 'MACD死叉'
                signal['signal_strength'] = min((latest['macd_dea'] - latest['macd_dif']) / latest['macd_dif'] * 100, 100)

        # RSI信号
        if latest.get('rsi_6'):
            if latest['rsi_6'] > 80:
                signal['risk_level'] = 'high'
                signal['recommendation'] = 'RSI超买，注意风险'
            elif latest['rsi_6'] < 20:
                signal['risk_level'] = 'low'
                signal['recommendation'] = 'RSI超卖，可能反弹'

        # KDJ信号
        if latest.get('kdj_k') and latest.get('kdj_d'):
            if latest['kdj_k'] > latest['kdj_d']:
                signal['trend_direction'] = 'up'
            else:
                signal['trend_direction'] = 'down'

        # 均线信号
        if latest.get('ma5') and latest.get('ma20'):
            if latest['ma5'] > latest['ma20']:
                signal['trend_strength'] = min((latest['ma5'] - latest['ma20']) / latest['ma20'] * 100, 100)

        return signal

    def generate_stock_report(self, stock_code: str) -> Dict:
        """
        生成单只股票的分析报告

        Args:
            stock_code: 股票代码

        Returns:
            分析报告
        """
        # 获取持仓信息
        positions = execute_query(
            "SELECT * FROM model_trade_position WHERE stock_code = %s AND status = 1",
            (stock_code,)
        )

        # 获取技术指标
        indicators = self.get_technical_indicators(stock_code)

        # 分析信号
        signal = self.analyze_signal(indicators)

        # 获取最新价格
        latest_price_sql = """
        SELECT close_price, trade_date FROM trade_stock_daily
        WHERE stock_code = %s
        ORDER BY trade_date DESC
        LIMIT 1
        """
        price_data = execute_query(latest_price_sql, (stock_code,))

        report = {
            'stock_code': stock_code,
            'stock_name': positions[0]['stock_name'] if positions else '',
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'current_price': price_data[0]['close_price'] if price_data else 0,
            'latest_indicators': indicators[0] if indicators else {},
            'signal': signal,
            'positions': positions
        }

        if positions:
            pos = positions[0]
            report['cost_price'] = pos['cost_price']
            report['shares'] = pos['shares']
            report['profit_loss'] = (report['current_price'] - pos['cost_price']) * pos['shares']
            report['profit_loss_pct'] = (report['current_price'] - pos['cost_price']) / pos['cost_price'] * 100

        return report

    def generate_daily_report(self) -> Dict:
        """
        生成每日持仓报告

        Returns:
            每日报告
        """
        # 获取所有持仓
        positions = self.get_positions()

        # 为每只股票生成报告
        stock_reports = []
        total_profit_loss = 0
        total_market_value = 0

        for pos in positions:
            report = self.generate_stock_report(pos['stock_code'])
            stock_reports.append(report)

            if 'profit_loss' in report:
                total_profit_loss += report['profit_loss']
                total_market_value += report['current_price'] * report['shares']

        # 生成汇总报告
        daily_report = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'report_time': datetime.now().strftime('%H:%M:%S'),
            'total_positions': len(positions),
            'total_market_value': total_market_value,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_pct': (total_profit_loss / (total_market_value - total_profit_loss) * 100) if total_market_value > 0 else 0,
            'stock_reports': stock_reports
        }

        return daily_report

    def save_report_to_db(self, report: Dict) -> int:
        """
        保存报告到数据库

        Args:
            report: 报告数据

        Returns:
            记录ID
        """
        from src.db import get_connection

        sql = """
        INSERT INTO trade_analysis_report
        (stock_code, report_date, report_type, signal_type, signal_strength,
         current_price, trend_direction, trend_strength, risk_level, recommendation, analysis_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # 如果是单只股票的报告
            if 'stock_code' in report and report.get('signal'):
                cursor.execute(sql, (
                    report['stock_code'],
                    report['report_date'],
                    'daily',
                    report['signal'].get('signal_type'),
                    report['signal'].get('signal_strength'),
                    report.get('current_price'),
                    report['signal'].get('trend_direction'),
                    report['signal'].get('trend_strength'),
                    report['signal'].get('risk_level'),
                    report['signal'].get('recommendation'),
                    json.dumps(report, ensure_ascii=False)
                ))
                conn.commit()
                record_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return record_id

            return 0
        except Exception as e:
            print(f"保存报告失败: {e}")
            return 0


def main():
    """测试报告生成"""
    import json

    service = ReportService()

    # 生成每日报告
    print("生成每日报告...")
    daily_report = service.generate_daily_report()

    print("\n每日报告:")
    print(json.dumps(daily_report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
