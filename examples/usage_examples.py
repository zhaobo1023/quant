# -*- coding: utf-8 -*-
"""
使用示例 - 快速上手指南

演示如何使用系统的核心功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def example_1_database_operations():
    """示例1: 数据库基本操作"""
    print("=" * 60)
    print("示例1: 数据库基本操作")
    print("=" * 60)

    from src.db import execute_query, execute_update, test_connection

    # 测试连接
    success, message = test_connection()
    print(f"数据库连接: {message}")

    # 查询持仓
    positions = execute_query("SELECT * FROM model_trade_position WHERE status = 1")
    print(f"\n当前持仓数量: {len(positions)}")

    # 查询股票列表
    stocks = execute_query("SELECT DISTINCT stock_code FROM trade_stock_daily LIMIT 5")
    print(f"股票数据示例: {[s['stock_code'] for s in stocks]}")


def example_2_technical_indicators():
    """示例2: 技术指标计算"""
    print("\n" + "=" * 60)
    print("示例2: 技术指标计算")
    print("=" * 60)

    from src.technical_indicators import TechnicalIndicatorCalculator

    calculator = TechnicalIndicatorCalculator()

    # 计算单只股票的技术指标
    print("\n计算 600519.SH 的技术指标...")
    # calculator.calculate_for_stock('600519.SH')  # 如果有数据

    # 计算所有股票的技术指标
    print("计算所有股票的技术指标...")
    # calculator.calculate_for_all_stocks()  # 如果有数据

    print("提示: 需要先下载K线数据才能计算技术指标")


def example_3_ocr_service():
    """示例3: OCR识别服务"""
    print("\n" + "=" * 60)
    print("示例3: OCR识别服务")
    print("=" * 60)

    from src.ocr_service import MockOCRService

    # 使用模拟服务（测试用）
    ocr = MockOCRService()

    # 处理持仓截图
    positions = ocr.process_position_image('/tmp/test.png')

    print("\n识别结果:")
    for pos in positions:
        print(f"  {pos['stock_code']} - {pos['stock_name']}")
        print(f"    持仓: {pos['shares']}股")
        print(f"    成本: ¥{pos['cost_price']:.2f}")


def example_4_report_generation():
    """示例4: 报告生成"""
    print("\n" + "=" * 60)
    print("示例4: 报告生成")
    print("=" * 60)

    from src.report_service import ReportService

    service = ReportService()

    # 生成每日报告
    print("生成每日持仓报告...")
    # report = service.generate_daily_report()  # 如果有持仓数据

    # 生成单只股票报告
    print("生成 600519.SH 的分析报告...")
    # report = service.generate_stock_report('600519.SH')  # 如果有数据

    print("提示: 需要先有持仓数据和技术指标才能生成报告")


def example_5_scheduler():
    """示例5: 定时任务"""
    print("\n" + "=" * 60)
    print("示例5: 定时任务")
    print("=" * 60)

    from src.scheduler_service import scheduler

    # 定义一个简单的任务
    def my_task():
        print("执行定时任务...")
        return "任务完成"

    # 添加一个测试任务（每10秒执行一次）
    print("\n添加测试任务...")
    scheduler.add_interval_job(my_task, seconds=10, job_id='test_job')

    # 查看所有任务
    jobs = scheduler.get_jobs()
    print(f"\n当前定时任务:")
    for job in jobs:
        print(f"  - {job.id}: {job.next_run_time}")

    # 启动调度器（实际使用时）
    # scheduler.start()

    print("\n提示: 定时任务已在FastAPI启动时自动运行")


def example_6_push_notification():
    """示例6: 消息推送"""
    print("\n" + "=" * 60)
    print("示例6: 消息推送")
    print("=" * 60)

    from src.push_service import MockPushService

    push = MockPushService()

    # 发送文本消息
    print("\n发送文本消息...")
    push.send_text_message("这是一条测试消息")

    # 发送持仓报告
    print("\n发送持仓报告...")
    positions = [
        {'stock_code': '600519.SH', 'stock_name': '贵州茅台', 'shares': 100, 'cost_price': 1800.00}
    ]
    push.send_position_report(positions)

    print("提示: 配置飞书Webhook后可发送真实消息")


def example_7_api_usage():
    """示例7: API接口调用"""
    print("\n" + "=" * 60)
    print("示例7: API接口调用示例")
    print("=" * 60)

    print("\n使用curl测试API:")
    print("\n# 健康检查")
    print("curl http://localhost:8000/")

    print("\n# 获取持仓列表")
    print("curl http://localhost:8000/api/positions")

    print("\n# 创建持仓")
    print("""curl -X POST http://localhost:8000/api/positions \\
  -H "Content-Type: application/json" \\
  -d '{
    "stock_code": "600519.SH",
    "stock_name": "贵州茅台",
    "shares": 100,
    "cost_price": 1800.00,
    "account_tag": "default"
  }'""")

    print("\n# 获取每日报告")
    print("curl http://localhost:8000/api/reports/daily")

    print("\n# 获取技术指标")
    print("curl http://localhost:8000/api/indicators/600519.SH?days=30")

    print("\n# 查看定时任务")
    print("curl http://localhost:8000/api/scheduler/jobs")

    print("\n提示: 启动FastAPI服务后访问 http://localhost:8000/docs 查看完整API文档")


def example_8_complete_workflow():
    """示例8: 完整工作流"""
    print("\n" + "=" * 60)
    print("示例8: 完整工作流程")
    print("=" * 60)

    print("\n完整的使用流程:")
    print("\n1. 初始化数据库")
    print("   python src/init_db.py")

    print("\n2. 下载K线数据")
    print("   python CASE-1/1-tushare_download_data.py")

    print("\n3. 计算技术指标")
    print("   python src/technical_indicators.py")

    print("\n4. 添加持仓（通过API或前端）")
    print("   POST /api/positions")

    print("\n5. 生成分析报告")
    print("   GET /api/reports/daily")

    print("\n6. 推送到飞书（自动定时）")
    print("   每日20:00自动推送")

    print("\n7. 监控和优化")
    print("   - 查看定时任务状态")
    print("   - 检查API响应时间")
    print("   - 优化数据库查询")


def main():
    """运行所有示例"""
    print("\n" + "🎯 " + "=" * 58)
    print("个人持仓管理系统 - 使用示例")
    print("=" * 60 + "\n")

    try:
        example_1_database_operations()
        example_2_technical_indicators()
        example_3_ocr_service()
        example_4_report_generation()
        example_5_scheduler()
        example_6_push_notification()
        example_7_api_usage()
        example_8_complete_workflow()

        print("\n" + "=" * 60)
        print("✓ 所有示例运行完成！")
        print("=" * 60)

        print("\n📚 更多信息请查看:")
        print("  - QUICKSTART.md    快速启动指南")
        print("  - README_EXTENDED.md  完整文档")
        print("  - ARCHITECTURE.md  系统架构")
        print("  - http://localhost:8000/docs  API文档")

    except Exception as e:
        print(f"\n✗ 运行示例时出错: {e}")
        print("\n提示: 确保已安装所有依赖并配置好数据库")


if __name__ == "__main__":
    main()
