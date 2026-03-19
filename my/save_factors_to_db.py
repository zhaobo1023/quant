# -*- coding: utf-8 -*-
"""
计算因子并保存到数据库

运行: python save_factors_to_db.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import talib
from datetime import datetime, date
from time import time

from db_config import execute_query
from factor_storage import (
    create_factor_table, batch_save_factors,
    load_factors, get_factor_dates, get_latest_factor_date
)


def batch_load_daily(start_date, end_date, min_bars=60):
    """批量加载日K线数据"""
    sql = """
        SELECT stock_code, trade_date, open_price, high_price, low_price,
               close_price, volume
        FROM trade_stock_daily
        WHERE trade_date >= %s AND trade_date <= %s
        ORDER BY stock_code, trade_date ASC
    """
    rows = execute_query(sql, [start_date, end_date])
    if not rows:
        return {}

    df_all = pd.DataFrame(rows)
    df_all['trade_date'] = pd.to_datetime(df_all['trade_date'])
    for col in ['open_price', 'high_price', 'low_price', 'close_price', 'volume']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

    result = {}
    codes = df_all['stock_code'].unique()

    for i, code in enumerate(codes):
        if (i + 1) % 100 == 0:
            print(f"  加载数据: {i+1}/{len(codes)}")
        group = df_all[df_all['stock_code'] == code]
        sub = group.set_index('trade_date').sort_index()
        sub = sub[['open_price', 'high_price', 'low_price', 'close_price', 'volume']]
        sub.columns = ['open', 'high', 'low', 'close', 'volume']
        if len(sub) >= min_bars:
            result[code] = sub

    return result


def calc_all_factors(df):
    """计算单只股票的全部因子"""
    if len(df) < 60:
        return None

    h = df['high'].values.astype(np.float64)
    l = df['low'].values.astype(np.float64)
    c = df['close'].values.astype(np.float64)
    v = df['volume'].values.astype(np.float64)

    if c[-1] <= 0 or np.isnan(c[-1]):
        return None

    try:
        roc_20 = talib.ROC(c, timeperiod=20)
        roc_60 = talib.ROC(c, timeperiod=60)
        atr = talib.ATR(h, l, c, timeperiod=14)
        rsi = talib.RSI(c, timeperiod=14)
        adx = talib.ADX(h, l, c, timeperiod=14)
        vol_ma = talib.SMA(v, timeperiod=20)
        macd_line, macd_signal, macd_hist = talib.MACD(c)

        high_60 = np.nanmax(h[-60:])
        low_60 = np.nanmin(l[-60:])
        price_range = high_60 - low_60

        vol_ma_val = vol_ma[-1] if not np.isnan(vol_ma[-1]) and vol_ma[-1] > 0 else 1

        factors = {
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
        return factors
    except Exception:
        return None


def batch_calc_factors(all_data):
    """批量计算所有股票的因子"""
    factor_dict = {}
    codes = list(all_data.keys())
    total = len(codes)

    for i, code in enumerate(codes):
        if (i + 1) % 100 == 0:
            print(f"  计算因子: {i+1}/{total}")
        df = all_data[code]
        f = calc_all_factors(df)
        if f is not None:
            factor_dict[code] = f

    return pd.DataFrame(factor_dict).T


def main():
    print("=" * 60)
    print("因子计算入库程序")
    print("=" * 60)

    # 确保表存在
    print("\n[1] 初始化因子表...")
    create_factor_table()

    # 设置日期
    calc_date = date.today()
    start_date = '2024-01-01'
    end_date = calc_date.strftime('%Y-%m-%d')

    # 检查是否已有当天数据
    print(f"\n[2] 检查已有数据...")
    latest = get_latest_factor_date()
    print(f"  最新因子日期: {latest or '无'}")
    if latest == calc_date:
        print(f"  ⚠️ {calc_date} 的因子数据已存在，将覆盖更新")

    # 加载数据
    print(f"\n[3] 加载K线数据 ({start_date} ~ {end_date})...")
    t0 = time()
    all_data = batch_load_daily(start_date, end_date)
    print(f"  加载完成: {len(all_data)} 只股票, 耗时 {time()-t0:.1f}s")

    if not all_data:
        print("  ❌ 未加载到数据")
        return

    # 计算因子
    print(f"\n[4] 计算技术因子...")
    t0 = time()
    factor_df = batch_calc_factors(all_data)
    print(f"  计算完成: {len(factor_df)} 只股票, 耗时 {time()-t0:.1f}s")

    if factor_df.empty:
        print("  ❌ 因子计算失败")
        return

    # 显示因子统计
    print(f"\n[5] 因子统计:")
    factor_cols = ['momentum_20d', 'momentum_60d', 'volatility', 'rsi_14',
                   'adx_14', 'turnover_ratio', 'price_position', 'macd_signal']
    for col in factor_cols:
        if col in factor_df.columns:
            vals = factor_df[col].dropna()
            print(f"  {col:<16} mean={vals.mean():>8.3f}  std={vals.std():>8.3f}")

    # 保存到数据库
    print(f"\n[6] 保存到数据库 (calc_date={calc_date})...")
    t0 = time()
    count = batch_save_factors(factor_df, calc_date)
    print(f"  保存完成: {count} 条记录, 耗时 {time()-t0:.1f}s")

    # 验证数据
    print(f"\n[7] 验证数据...")
    saved_df = load_factors(calc_date)
    if len(saved_df) == len(factor_df):
        print(f"  ✅ 数据验证通过: {len(saved_df)} 条记录")

        # 显示前5条
        print(f"\n  前5只股票因子:")
        print(f"  {'代码':<14} {'20D动量':>10} {'RSI':>8} {'波动率':>10} {'收盘价':>10}")
        print(f"  {'-'*56}")
        for i, (code, row) in enumerate(saved_df.head(5).iterrows()):
            print(f"  {code:<14} {row.get('momentum_20d', 0):>+9.2f}% "
                  f"{row.get('rsi_14', 0):>8.1f} {row.get('volatility', 0):>10.4f} "
                  f"{row.get('close', 0):>10.2f}")
    else:
        print(f"  ❌ 数据验证失败: 保存{len(factor_df)}条, 读取{len(saved_df)}条")

    # 显示所有因子日期
    print(f"\n[8] 因子数据汇总:")
    dates = get_factor_dates()
    for d in dates:
        print(f"  {d['calc_date']}: {d['stock_count']} 只股票")

    print("\n" + "=" * 60)
    print("✅ 因子计算入库完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
