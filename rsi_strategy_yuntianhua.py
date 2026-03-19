# -*- coding: utf-8 -*-
"""
RSI策略回测 - 云天化(600096.SH)

策略逻辑:
  - RSI < 30 (超卖) -> 买入
  - RSI > 70 (超买) -> 卖出

参数:
  - RSI周期: 14
  - 超卖线: 30
  - 超买线: 70

运行: python rsi_strategy_yuntianhua.py
"""
import backtrader as bt
from data_loader import run_and_report


class RSIStrategy(bt.Strategy):
    """RSI超买超卖策略"""
    params = (
        ('period', 14),      # RSI周期
        ('oversold', 30),    # 超卖阈值
        ('overbought', 70),  # 超买阈值
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.period)

    def next(self):
        if not self.position:
            # 无持仓时，RSI低于超卖线则买入
            if self.rsi < self.p.oversold:
                self.buy()
        else:
            # 有持仓时，RSI高于超买线则卖出
            if self.rsi > self.p.overbought:
                self.close()


if __name__ == '__main__':
    # 云天化 2024年至今的数据
    run_and_report(
        RSIStrategy,
        stock_code='600096.SH',
        start_date='2024-01-01',
        end_date='2026-03-17',
        label='RSI策略-云天化',
        plot=True
    )
