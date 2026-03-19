# -*- coding: utf-8 -*-
"""
简化版因子计算入库脚本
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import talib
from datetime import date
from time import time

print("开始因子计算入库...")

# 导入模块
from db_config import execute_query, get_connection
from factor_storage import create_factor_table, batch_save_factors, load_factors, get_factor_dates

# 1. 创建表
print("\n[1] 初始化因子表...")
create_factor_table()

# 2. 加载K线数据
print("\n[2] 加载K线数据...")
sql = """
    SELECT stock_code, trade_date, open_price, high_price, low_price,
           close_price, volume
    FROM trade_stock_daily
    WHERE trade_date >= '2024-01-01' AND trade_date <= '2026-03-19'
    ORDER BY stock_code, trade_date ASC
"""
rows = execute_query(sql)
print(f"  查询到 {len(rows)} 条K线记录")

df_all = pd.DataFrame(rows)
df_all['trade_date'] = pd.to_datetime(df_all['trade_date'])
for col in ['open_price', 'high_price', 'low_price', 'close_price', 'volume']:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# 3. 计算因子
print("\n[3] 计算因子...")
factor_dict = {}
codes = df_all['stock_code'].unique()
total = len(codes)
t0 = time()

for i, code in enumerate(codes):
    if (i + 1) % 50 == 0:
        print(f"  进度: {i+1}/{total} ({(i+1)/total*100:.1f}%)")

    group = df_all[df_all['stock_code'] == code]
    sub = group.set_index('trade_date').sort_index()

    if len(sub) < 60:
        continue

    h = sub['high_price'].values.astype(np.float64)
    l = sub['low_price'].values.astype(np.float64)
    c = sub['close_price'].values.astype(np.float64)
    v = sub['volume'].values.astype(np.float64)

    if c[-1] <= 0 or np.isnan(c[-1]):
        continue

    try:
        roc_20 = talib.ROC(c, timeperiod=20)
        roc_60 = talib.ROC(c, timeperiod=60)
        atr = talib.ATR(h, l, c, timeperiod=14)
        rsi = talib.RSI(c, timeperiod=14)
        adx = talib.ADX(h, l, c, timeperiod=14)
        vol_ma = talib.SMA(v, timeperiod=20)
        _, _, macd_hist = talib.MACD(c)

        high_60 = np.nanmax(h[-60:])
        low_60 = np.nanmin(l[-60:])
        price_range = high_60 - low_60

        vol_ma_val = vol_ma[-1] if not np.isnan(vol_ma[-1]) and vol_ma[-1] > 0 else 1

        factor_dict[code] = {
            'momentum_20d': float(roc_20[-1]) if not np.isnan(roc_20[-1]) else 0,
            'momentum_60d': float(roc_60[-1]) if not np.isnan(roc_60[-1]) else 0,
            'volatility': float(atr[-1] / c[-1]) if not np.isnan(atr[-1]) and c[-1] > 0 else 0,
            'rsi_14': float(rsi[-1]) if not np.isnan(rsi[-1]) else 50,
            'adx_14': float(adx[-1]) if not np.isnan(adx[-1]) else 0,
            'turnover_ratio': float(v[-1] / vol_ma_val) if vol_ma_val > 0 else 1,
            'price_position': float((c[-1] - low_60) / price_range) if price_range > 0 else 0.5,
            'macd_signal': float(macd_hist[-1]) if not np.isnan(macd_hist[-1]) else 0,
            'close': float(c[-1]),
        }
    except Exception as e:
        continue

print(f"  计算完成: {len(factor_dict)} 只股票, 耗时 {time()-t0:.1f}s")

# 4. 保存到数据库
print("\n[4] 保存到数据库...")
factor_df = pd.DataFrame(factor_dict).T
calc_date = date.today()
count = batch_save_factors(factor_df, calc_date)
print(f"  保存完成: {count} 条记录")

# 5. 验证
print("\n[5] 验证数据...")
saved_df = load_factors(calc_date)
print(f"  读取到 {len(saved_df)} 条记录")

if len(saved_df) == len(factor_df):
    print("  ✅ 数据验证通过!")
else:
    print(f"  ⚠️ 数据不一致: 保存{len(factor_df)}条, 读取{len(saved_df)}条")

# 6. 显示汇总
print("\n[6] 因子数据汇总:")
dates = get_factor_dates()
for d in dates:
    print(f"  {d['calc_date']}: {d['stock_count']} 只股票")

# 显示示例
print("\n示例数据:")
print(saved_df.head(5)[['momentum_20d', 'rsi_14', 'volatility', 'close']])

print("\n✅ 完成!")
