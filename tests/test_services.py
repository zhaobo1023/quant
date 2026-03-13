# -*- coding: utf-8 -*-
"""
系统测试脚本

测试各个服务的功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import test_connection, execute_query


def test_database_connection():
    """测试数据库连接"""
    print("1. 测试数据库连接...")
    success, message = test_connection()
    if success:
        print(f"   ✓ {message}")
        return True
    else:
        print(f"   ✗ {message}")
        return False


def test_tables_exist():
    """测试表是否存在"""
    print("\n2. 测试数据库表...")
    tables = [
        'model_trade_position',
        'trade_stock_daily',
        'trade_technical_indicator',
        'trade_analysis_report',
        'trade_ocr_record'
    ]

    all_exist = True
    for table in tables:
        try:
            execute_query(f"SELECT 1 FROM {table} LIMIT 1")
            print(f"   ✓ {table}")
        except:
            print(f"   ✗ {table}")
            all_exist = False

    return all_exist


def test_technical_indicator_service():
    """测试技术指标计算服务"""
    print("\n3. 测试技术指标计算服务...")
    try:
        from src.technical_indicators import TechnicalIndicatorCalculator
        calculator = TechnicalIndicatorCalculator()
        print("   ✓ 技术指标计算器初始化成功")
        return True
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False


def test_ocr_service():
    """测试OCR服务"""
    print("\n4. 测试OCR服务...")
    try:
        from src.ocr_service import MockOCRService
        ocr = MockOCRService()
        result = ocr.process_position_image("/tmp/test.png")
        if result:
            print(f"   ✓ OCR服务工作正常 (识别到{len(result)}个持仓)")
            return True
        else:
            print("   ✗ OCR服务返回空结果")
            return False
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False


def test_scheduler_service():
    """测试定时任务服务"""
    print("\n5. 测试定时任务服务...")
    try:
        from src.scheduler_service import scheduler
        print("   ✓ 定时任务调度器初始化成功")
        return True
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False


def test_push_service():
    """测试推送服务"""
    print("\n6. 测试推送服务...")
    try:
        from src.push_service import MockPushService
        push = MockPushService()
        push.send_text_message("测试消息")
        print("   ✓ 推送服务工作正常")
        return True
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False


def test_report_service():
    """测试报告服务"""
    print("\n7. 测试报告服务...")
    try:
        from src.report_service import ReportService
        service = ReportService()
        print("   ✓ 报告服务初始化成功")
        return True
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("个人持仓管理系统 - 功能测试")
    print("=" * 60)

    tests = [
        test_database_connection,
        test_tables_exist,
        test_technical_indicator_service,
        test_ocr_service,
        test_scheduler_service,
        test_push_service,
        test_report_service
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n测试异常: {e}")
            results.append(False)

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n✓ 所有测试通过！系统运行正常。")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
