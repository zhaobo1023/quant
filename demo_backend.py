#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
后端完整功能演示脚本

演示所有后端服务的使用方法
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.db import execute_query, execute_update
from src.technical_indicators import TechnicalIndicatorCalculator
from src.ocr_service import MockOCRService
from src.push_service import MockPushService
from src.report_service import ReportService
from src.scheduler_service import SchedulerService


def demo_technical_indicators():
    """演示技术指标计算"""
    print("\n" + "="*80)
    print("【1】技术指标计算演示")
    print("="*80)

    calculator = TechnicalIndicatorCalculator()

    # 模拟添加一些K线数据
    print("\n添加测试K线数据...")
    test_data = [
        ('600096.SH', '2024-01-01', 20.0, 20.5, 19.8, 20.3, 1000000),
        ('600096.SH', '2024-01-02', 20.3, 20.8, 20.2, 20.6, 1200000),
        ('600096.SH', '2024-01-03', 20.6, 21.0, 20.5, 20.9, 1100000),
        ('600096.SH', '2024-01-04', 20.9, 21.2, 20.8, 21.1, 1300000),
        ('600096.SH', '2024-01-05', 21.1, 21.5, 21.0, 21.3, 1500000),
    ]

    sql = """
    INSERT INTO trade_stock_daily
        (stock_code, trade_date, open_price, high_price, low_price, close_price, volume)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        open_price = VALUES(open_price),
        high_price = VALUES(high_price),
        low_price = VALUES(low_price),
        close_price = VALUES(close_price),
        volume = VALUES(volume)
    """

    for data in test_data:
        execute_update(sql, data)

    print("✓ 已添加5条测试K线数据")

    # 计算技术指标
    print("\n计算技术指标...")
    count = calculator.calculate_for_stock('600096.SH')
    print(f"✓ 成功计算并保存 {count} 条技术指标")

    # 查询结果
    print("\n查询最新技术指标:")
    indicators = execute_query("""
        SELECT trade_date, close_price, ma5, ma10, macd_dif, macd_dea, rsi_6
        FROM trade_stock_daily d
        LEFT JOIN trade_technical_indicator i
            ON d.stock_code = i.stock_code AND d.trade_date = i.trade_date
        WHERE d.stock_code = '600096.SH'
        ORDER BY d.trade_date DESC
        LIMIT 3
    """)

    for ind in indicators:
        print(f"  {ind['trade_date']}: 收盘{ind['close_price']:.2f}, "
              f"MA5={ind.get('ma5', 0) or 0:.2f}, "
              f"MACD={ind.get('macd_dif', 0) or 0:.2f}")


def demo_position_management():
    """演示持仓管理"""
    print("\n" + "="*80)
    print("【2】持仓管理演示")
    print("="*80)

    # 添加测试持仓
    print("\n添加测试持仓...")
    positions = [
        ('600096.SH', '云天化', 1000, 22.50, 0, 'default', '测试持仓1'),
        ('300274.SZ', '阳光电源', 500, 65.00, 0, 'default', '测试持仓2'),
    ]

    sql = """
    INSERT INTO model_trade_position
        (stock_code, stock_name, shares, cost_price, is_margin, account_tag, notes)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        stock_name = VALUES(stock_name),
        shares = VALUES(shares),
        cost_price = VALUES(cost_price),
        notes = VALUES(notes)
    """

    for pos in positions:
        execute_update(sql, pos)

    print("✓ 已添加2个测试持仓")

    # 查询持仓
    print("\n当前持仓:")
    result = execute_query("""
        SELECT stock_code, stock_name, shares, cost_price, status
        FROM model_trade_position
        WHERE status = 1
        ORDER BY stock_code
    """)

    for pos in result:
        print(f"  {pos['stock_name']} ({pos['stock_code']}): "
              f"{pos['shares']}股 @ {pos['cost_price']:.2f}")


def demo_ocr_service():
    """演示OCR服务"""
    print("\n" + "="*80)
    print("【3】OCR识别演示")
    print("="*80)

    service = MockOCRService()

    print("\n模拟识别持仓截图...")
    result = service.recognize_position_screenshot('/tmp/test.png')

    if result.get('success'):
        print("✓ 识别成功")
        print(f"  发现 {len(result['positions'])} 个持仓:")
        for pos in result['positions']:
            print(f"    - {pos.get('stock_name')} ({pos.get('stock_code')}): "
                  f"{pos.get('shares')}股 @ {pos.get('cost_price'):.2f}")
    else:
        print(f"✗ 识别失败: {result.get('error')}")


def demo_report_service():
    """演示报告服务"""
    print("\n" + "="*80)
    print("【4】报告生成演示")
    print("="*80)

    service = ReportService()

    print("\n生成每日报告...")
    report = service.generate_daily_report()

    print("✓ 报告生成成功")
    print(f"  报告日期: {report.get('report_date')}")
    print(f"  持仓数量: {report.get('position_count')}")
    print(f"  总市值: {report.get('total_value', 0):.2f}")
    print(f"  总盈亏: {report.get('total_pnl', 0):.2f} ({report.get('total_pnl_pct', 0):.2f}%)")

    # 生成单只股票分析
    print("\n生成单只股票分析...")
    analysis = service.analyze_single_stock('600096.SH')

    print("✓ 分析完成")
    print(f"  股票: {analysis.get('stock_name', '600096.SH')}")
    print(f"  当前价: {analysis.get('current_price', 0):.2f}")
    print(f"  MA20: {analysis.get('ma20', 0):.2f}")
    print(f"  MACD信号: {analysis.get('macd_signal', 'N/A')}")
    print(f"  风险等级: {analysis.get('risk_level', 'N/A')}")


def demo_push_service():
    """演示推送服务"""
    print("\n" + "="*80)
    print("【5】消息推送演示")
    print("="*80)

    service = MockPushService()

    print("\n发送测试消息...")
    success = service.send_text_message("这是一条测试消息")

    if success:
        print("✓ 消息推送成功 (Mock模式)")
    else:
        print("✗ 消息推送失败")


def demo_scheduler():
    """演示定时任务"""
    print("\n" + "="*80)
    print("【6】定时任务演示")
    print("="*80)

    scheduler = SchedulerService()

    print("\n当前定时任务:")
    jobs = scheduler.get_jobs()

    for job in jobs:
        print(f"  - {job['id']}: {job['name']}")
        print(f"    触发时间: {job['trigger']}")
        print(f"    下次执行: {job['next_run_time']}")

    print(f"\n✓ 定时任务调度器就绪 (共{len(jobs)}个任务)")


def main():
    """主演示流程"""
    print("\n" + "="*80)
    print("持仓管理系统 - 后端完整功能演示")
    print("="*80)

    try:
        # 1. 技术指标计算
        demo_technical_indicators()

        # 2. 持仓管理
        demo_position_management()

        # 3. OCR识别
        demo_ocr_service()

        # 4. 报告生成
        demo_report_service()

        # 5. 消息推送
        demo_push_service()

        # 6. 定时任务
        demo_scheduler()

        print("\n" + "="*80)
        print("✓ 所有演示完成!")
        print("="*80)

        print("\n后续步骤:")
        print("1. 启动Web服务: python start_backend.py")
        print("2. 访问API文档: http://localhost:8000/docs")
        print("3. 使用CLI工具: python position_cli.py --help")
        print("4. 查看完整文档: cat README_EXTENDED.md")

    except Exception as e:
        print(f"\n✗ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
