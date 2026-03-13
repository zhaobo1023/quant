#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
持仓管理系统 - 命令行工具

用法:
    python position_cli.py add-position --code 600096.SH --name 云天化 --shares 1000 --cost 22.50
    python position_cli.py sync-indicators --all
    python position_cli.py generate-report --daily
    python position_cli.py push-message --text "测试消息"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.db import execute_query, execute_update
    from src.technical_indicators import TechnicalIndicatorCalculator
    from src.ocr_service import BaiduOCRService, MockOCRService
    from src.push_service import FeishuPushService, MockPushService
    from src.report_service import ReportService

    # 使用OCR服务(优先真实服务,降级到Mock)
    try:
        OCRService = BaiduOCRService
    except:
        OCRService = MockOCRService

    # 使用推送服务(优先真实服务,降级到Mock)
    try:
        PushService = PushService
    except:
        PushService = MockPushService

except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


def add_position(args):
    """添加持仓"""
    sql = """
    INSERT INTO model_trade_position
        (stock_code, stock_name, shares, cost_price, is_margin, account_tag, notes)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        stock_name = VALUES(stock_name),
        shares = VALUES(shares),
        cost_price = VALUES(cost_price),
        is_margin = VALUES(is_margin),
        notes = VALUES(notes)
    """

    count = execute_update(sql, (
        args.code,
        args.name,
        args.shares,
        args.cost,
        1 if args.margin else 0,
        args.account,
        args.notes
    ))

    print(f"✓ 持仓已添加/更新: {args.name} ({args.code})")


def list_positions(args):
    """列出持仓"""
    sql = """
    SELECT
        p.stock_code,
        p.stock_name,
        p.shares,
        p.cost_price,
        d.close_price as current_price,
        ROUND((d.close_price - p.cost_price) / p.cost_price * 100, 2) as pnl_pct
    FROM model_trade_position p
    LEFT JOIN (
        SELECT stock_code, close_price
        FROM trade_stock_daily d1
        WHERE trade_date = (
            SELECT MAX(trade_date) FROM trade_stock_daily
        )
    ) d ON p.stock_code = d.stock_code
    WHERE p.status = 1
    ORDER BY pnl_pct DESC
    """

    positions = execute_query(sql)

    if not positions:
        print("暂无持仓")
        return

    print("\n" + "="*80)
    print("持仓列表")
    print("="*80)
    print(f"{'代码':<12s} {'名称':<10s} {'数量':<8s} {'成本价':<10s} {'现价':<10s} {'盈亏%':<10s}")
    print("-"*80)

    for pos in positions:
        pnl = pos.get('pnl_pct', 0) or 0
        pnl_color = '\033[92m' if pnl > 0 else '\033[91m' if pnl < 0 else '\033[0m'
        reset_color = '\033[0m'

        print(f"{pos['stock_code']:<12s} {pos['stock_name']:<10s} "
              f"{pos['shares']:<8d} {pos['cost_price']:<10.2f} "
              f"{pos.get('current_price', 0) or 0:<10.2f} "
              f"{pnl_color}{pnl:+.2f}%{reset_color}")

    print("="*80 + "\n")


def sync_indicators(args):
    """同步技术指标"""
    calculator = TechnicalIndicatorCalculator()

    if args.all:
        print("开始计算所有股票的技术指标...")
        count = calculator.calculate_for_all_stocks()
        print(f"✓ 完成,共处理 {count} 只股票")
    elif args.code:
        print(f"开始计算 {args.code} 的技术指标...")
        count = calculator.calculate_for_stock(args.code)
        print(f"✓ 完成,共 {count} 条记录")
    else:
        print("请指定 --code 或 --all")


def generate_report(args):
    """生成分析报告"""
    service = ReportService()

    if args.daily:
        print("生成每日报告...")
        report = service.generate_daily_report()

        print("\n" + "="*80)
        print("每日持仓分析报告")
        print("="*80)
        print(f"报告日期: {report.get('report_date', 'N/A')}")
        print(f"持仓数量: {report.get('position_count', 0)}")
        print(f"总市值: {report.get('total_value', 0):.2f}")
        print(f"总盈亏: {report.get('total_pnl', 0):.2f} ({report.get('total_pnl_pct', 0):.2f}%)")
        print("="*80 + "\n")

    elif args.code:
        print(f"生成 {args.code} 的分析报告...")
        report = service.analyze_single_stock(args.code)

        print("\n" + "="*80)
        print(f"{report.get('stock_name', args.code)} 分析报告")
        print("="*80)
        print(f"当前价格: {report.get('current_price', 0):.2f}")
        print(f"MA20: {report.get('ma20', 0):.2f}")
        print(f"MACD: {report.get('macd_signal', 'N/A')}")
        print(f"RSI: {report.get('rsi_6', 0):.2f}")
        print(f"风险等级: {report.get('risk_level', 'N/A')}")
        print("="*80 + "\n")


def push_message(args):
    """推送消息到飞书"""
    # 优先使用飞书推送,不可用时使用Mock服务
    try:
        service = FeishuPushService()
        if not service.is_configured():
            print("飞书Webhook未配置,使用Mock服务")
            service = MockPushService()
    except:
        print("使用Mock推送服务")
        service = MockPushService()

    if args.text:
        print("推送文本消息...")
        success = service.send_text_message(args.text)
        if success:
            print("✓ 消息推送成功")
        else:
            print("✗ 消息推送失败")

    elif args.report:
        print("推送每日报告...")
        report_service = ReportService()
        report = report_service.generate_daily_report()

        success = service.send_position_report(
            report.get('positions', []),
            report.get('signals', [])
        )

        if success:
            print("✓ 报告推送成功")
        else:
            print("✗ 报告推送失败")


def ocr_parse(args):
    """OCR识别持仓截图"""
    if not args.image:
        print("请指定图片路径 --image")
        return

    # 优先使用百度OCR,不可用时使用Mock服务
    try:
        service = BaiduOCRService()
        if not service.is_available():
            print("百度OCR未配置,使用Mock服务")
            service = MockOCRService()
    except:
        print("使用Mock OCR服务")
        service = MockOCRService()

    print(f"正在识别图片: {args.image}")
    result = service.recognize_position_screenshot(args.image)

    if result.get('success'):
        positions = result.get('positions', [])
        print(f"\n✓ 识别成功,发现 {len(positions)} 个持仓:\n")

        for pos in positions:
            print(f"  {pos.get('stock_name', 'N/A')} ({pos.get('stock_code', 'N/A')})")
            print(f"    数量: {pos.get('shares', 0)}")
            print(f"    成本: {pos.get('cost_price', 0):.2f}")
            print()

        if args.save:
            print("保存到数据库...")
            # TODO: 实现保存逻辑
    else:
        print(f"✗ 识别失败: {result.get('error', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(
        description='持仓管理系统命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # add-position 命令
    add_parser = subparsers.add_parser('add-position', help='添加持仓')
    add_parser.add_argument('--code', required=True, help='股票代码')
    add_parser.add_argument('--name', required=True, help='股票名称')
    add_parser.add_argument('--shares', type=int, required=True, help='持仓数量')
    add_parser.add_argument('--cost', type=float, required=True, help='成本价')
    add_parser.add_argument('--margin', action='store_true', help='是否融资')
    add_parser.add_argument('--account', default='default', help='账户标签')
    add_parser.add_argument('--notes', default='', help='备注')

    # list-positions 命令
    list_parser = subparsers.add_parser('list-positions', help='列出持仓')

    # sync-indicators 命令
    sync_parser = subparsers.add_parser('sync-indicators', help='同步技术指标')
    sync_parser.add_argument('--code', help='股票代码')
    sync_parser.add_argument('--all', action='store_true', help='所有股票')

    # generate-report 命令
    report_parser = subparsers.add_parser('generate-report', help='生成分析报告')
    report_parser.add_argument('--daily', action='store_true', help='每日报告')
    report_parser.add_argument('--code', help='股票代码')

    # push-message 命令
    push_parser = subparsers.add_parser('push-message', help='推送消息')
    push_parser.add_argument('--text', help='文本消息')
    push_parser.add_argument('--report', action='store_true', help='推送每日报告')

    # ocr-parse 命令
    ocr_parser = subparsers.add_parser('ocr-parse', help='OCR识别持仓截图')
    ocr_parser.add_argument('--image', required=True, help='图片路径')
    ocr_parser.add_argument('--save', action='store_true', help='保存到数据库')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 执行对应命令
    commands = {
        'add-position': add_position,
        'list-positions': list_positions,
        'sync-indicators': sync_indicators,
        'generate-report': generate_report,
        'push-message': push_message,
        'ocr-parse': ocr_parse
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"未知命令: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
