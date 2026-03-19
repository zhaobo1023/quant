# -*- coding: utf-8 -*-
"""
MACD策略回测 - 云天化(600096.SH)

策略逻辑:
  - DIF上穿DEA (金叉) -> 买入
  - DIF下穿DEA (死叉) -> 卖出

参数:
  - 快线周期: 12
  - 慢线周期: 26
  - 信号线周期: 9

运行: python macd_strategy_yuntianhua.py
"""
import backtrader as bt
from data_loader import run_and_report


class MACDStrategy(bt.Strategy):
    """MACD金叉死叉策略"""
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.fast_period,
            period_me2=self.p.slow_period,
            period_signal=self.p.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position:
            # 金叉买入
            if self.crossover > 0:
                self.buy()
        else:
            # 死叉卖出
            if self.crossover < 0:
                self.close()


if __name__ == '__main__':
    run_and_report(
        MACDStrategy,
        stock_code='600096.SH',
        start_date='2025-09-17',
        end_date='2026-03-17',
        label='MACD策略-云天化',
        plot=True
    )
