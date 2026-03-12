# -*- coding: utf-8 -*-
"""
QMT连接测试脚本
测试xtquant与QMT/miniQMT的连接状态

运行：python qmt_connect_test.py
环境：需先启动miniQMT客户端
"""
import sys
import time
from datetime import datetime


def test_xtquant_import():
    """测试1：导入xtquant模块"""
    print("=" * 60)
    print("测试1：导入xtquant模块")
    print("=" * 60)
    try:
        from xtquant import xtdata
        print("[OK] xtquant导入成功")
        return True, xtdata
    except ImportError as e:
        print(f"[FAIL] xtquant导入失败: {e}")
        print("  请确保已安装: pip install xtquant -i https://pypi.tuna.tsinghua.edu.cn/simple")
        return False, None


def test_connection(xtdata):
    """测试2：连接QMT数据服务"""
    print("\n" + "=" * 60)
    print("测试2：连接QMT数据服务")
    print("=" * 60)
    try:
        result = xtdata.connect()
        print(f"连接结果: {result}")
        # 返回值可能是0或者连接对象，都算成功
        if result is not None:
            print("[OK] 连接成功!")
            return True
        else:
            print(f"[FAIL] 连接失败，返回值: {result}")
            print("  请确保miniQMT客户端已启动")
            return False
    except Exception as e:
        print(f"[FAIL] 连接异常: {e}")
        return False


def test_get_stock_list(xtdata):
    """测试3：获取股票列表"""
    print("\n" + "=" * 60)
    print("测试3：获取股票列表")
    print("=" * 60)
    try:
        # 获取沪深A股列表
        stock_list = xtdata.get_stock_list_in_sector('沪深A股')
        if stock_list:
            print(f"[OK] 获取成功，共 {len(stock_list)} 只股票")
            print(f"  前10只: {stock_list[:10]}")
            return True, stock_list
        else:
            print("[FAIL] 获取股票列表为空")
            return False, []
    except Exception as e:
        print(f"[FAIL] 获取股票列表失败: {e}")
        return False, []


def test_download_daily_data(xtdata, stock_code='600519.SH'):
    """测试4：下载日线数据"""
    print("\n" + "=" * 60)
    print(f"测试4：下载日线数据 ({stock_code})")
    print("=" * 60)
    try:
        # 下载历史数据
        print(f"正在下载 {stock_code} 日线数据...")
        xtdata.download_history_data(
            stock_code=stock_code,
            period='1d',
            start_time='20250101'
        )
        time.sleep(1)
        print("[OK] 数据下载完成")
        return True
    except Exception as e:
        print(f"[FAIL] 下载日线数据失败: {e}")
        return False


def test_get_market_data(xtdata, stock_code='600519.SH'):
    """测试5：获取市场数据"""
    print("\n" + "=" * 60)
    print(f"测试5：获取市场数据 ({stock_code})")
    print("=" * 60)
    try:
        res = xtdata.get_market_data(
            stock_list=[stock_code],
            period='1d',
            start_time='20250101',
            end_time='',
            count=-1,
            dividend_type='front',
            fill_data=True
        )

        if not res or 'close' not in res:
            print("[FAIL] 获取数据为空")
            return False

        close_df = res['close']
        if stock_code not in close_df.index:
            print(f"[FAIL] 数据中未找到 {stock_code}")
            return False

        # 获取日期和收盘价
        dates = close_df.columns.tolist()
        prices = close_df.loc[stock_code].values

        print(f"[OK] 获取成功，共 {len(dates)} 个交易日")
        print(f"  日期范围: {dates[0]} ~ {dates[-1]}")
        print(f"  最新收盘价: {prices[-1]:.2f}")

        # 显示最近5天数据
        print("\n  最近5个交易日:")
        for i in range(-5, 0):
            print(f"    {dates[i]}: {prices[i]:.2f}")

        return True
    except Exception as e:
        print(f"[FAIL] 获取市场数据失败: {e}")
        return False


def test_get_full_tick(xtdata, stock_code='600519.SH'):
    """测试6：获取实时行情（全推数据）"""
    print("\n" + "=" * 60)
    print(f"测试6：获取实时行情 ({stock_code})")
    print("=" * 60)
    try:
        tick = xtdata.get_full_tick([stock_code])
        if tick and stock_code in tick:
            data = tick[stock_code]
            print(f"[OK] 获取实时行情成功")
            # 兼容字典和对象两种格式
            if isinstance(data, dict):
                print(f"  最新价: {data.get('lastPrice', 'N/A')}")
                print(f"  今开: {data.get('open', 'N/A')}")
                print(f"  最高: {data.get('high', 'N/A')}")
                print(f"  最低: {data.get('low', 'N/A')}")
                print(f"  成交量: {data.get('volume', 'N/A')}")
                print(f"  成交额: {data.get('amount', 'N/A')}")
            else:
                print(f"  最新价: {getattr(data, 'lastPrice', 'N/A')}")
                print(f"  今开: {getattr(data, 'open', 'N/A')}")
                print(f"  最高: {getattr(data, 'high', 'N/A')}")
                print(f"  最低: {getattr(data, 'low', 'N/A')}")
                print(f"  成交量: {getattr(data, 'volume', 'N/A')}")
                print(f"  成交额: {getattr(data, 'amount', 'N/A')}")
            return True
        else:
            print("[FAIL] 未获取到实时行情数据")
            return False
    except Exception as e:
        print(f"[FAIL] 获取实时行情失败: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "#" * 60)
    print("#" + " " * 20 + "QMT连接测试" + " " * 20 + "#")
    print("#" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []

    # 测试1：导入模块
    success, xtdata = test_xtquant_import()
    results.append(("导入xtquant", success))
    if not success:
        print("\n测试终止，请先安装xtquant")
        return

    # 测试2：连接服务
    success = test_connection(xtdata)
    results.append(("连接QMT服务", success))
    if not success:
        print("\n测试终止，请先启动miniQMT客户端")
        return

    # 测试3：获取股票列表
    success, _ = test_get_stock_list(xtdata)
    results.append(("获取股票列表", success))

    # 测试4：下载日线数据
    success = test_download_daily_data(xtdata)
    results.append(("下载日线数据", success))

    # 测试5：获取市场数据
    success = test_get_market_data(xtdata)
    results.append(("获取市场数据", success))

    # 测试6：获取实时行情
    success = test_get_full_tick(xtdata)
    results.append(("获取实时行情", success))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, success in results:
        status = "[OK] 通过" if success else "[FAIL] 失败"
        print(f"  {name}: {status}")

    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n恭喜! 所有测试通过，QMT连接正常!")
    else:
        print("\n部分测试未通过，请检查上述错误信息")


if __name__ == "__main__":
    main()
