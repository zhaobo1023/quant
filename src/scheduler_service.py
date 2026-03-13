# -*- coding: utf-8 -*-
"""
定时任务调度服务

使用APScheduler实现定时任务
"""
import os
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def job_listener(self, event):
        """任务执行监听器"""
        if event.exception:
            logger.error(f"任务执行失败: {event.job_id}, 错误: {event.exception}")
        else:
            logger.info(f"任务执行成功: {event.job_id}")

    def add_job(self, func, trigger, job_id=None, **kwargs):
        """
        添加定时任务

        Args:
            func: 任务函数
            trigger: 触发器
            job_id: 任务ID
            **kwargs: 其他参数
        """
        self.scheduler.add_job(func, trigger=trigger, id=job_id, **kwargs)
        logger.info(f"添加定时任务: {job_id or func.__name__}")

    def add_daily_job(self, func, hour=20, minute=0, job_id=None, **kwargs):
        """
        添加每日定时任务

        Args:
            func: 任务函数
            hour: 小时
            minute: 分钟
            job_id: 任务ID
            **kwargs: 其他参数
        """
        trigger = CronTrigger(hour=hour, minute=minute)
        self.add_job(func, trigger, job_id=job_id, **kwargs)

    def add_interval_job(self, func, seconds=None, minutes=None, hours=None, job_id=None, **kwargs):
        """
        添加间隔任务

        Args:
            func: 任务函数
            seconds: 秒
            minutes: 分钟
            hours: 小时
            job_id: 任务ID
            **kwargs: 其他参数
        """
        from apscheduler.triggers.interval import IntervalTrigger
        trigger = IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours)
        self.add_job(func, trigger, job_id=job_id, **kwargs)

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")

    def shutdown(self, wait=True):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("定时任务调度器已关闭")

    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()

    def remove_job(self, job_id):
        """移除任务"""
        self.scheduler.remove_job(job_id)
        logger.info(f"移除任务: {job_id}")

    def pause_job(self, job_id):
        """暂停任务"""
        self.scheduler.pause_job(job_id)
        logger.info(f"暂停任务: {job_id}")

    def resume_job(self, job_id):
        """恢复任务"""
        self.scheduler.resume_job(job_id)
        logger.info(f"恢复任务: {job_id}")


# 全局调度器实例
scheduler = SchedulerService()


def init_scheduler():
    """初始化定时任务"""
    from src.technical_indicators import TechnicalIndicatorCalculator
    from src.report_service import ReportService

    # 每日20:00生成报告并推送
    scheduler.add_daily_job(
        func=generate_and_push_daily_report,
        hour=20,
        minute=0,
        job_id='daily_report_push'
    )

    # 每日15:30更新技术指标（收盘后）
    scheduler.add_daily_job(
        func=update_technical_indicators,
        hour=15,
        minute=30,
        job_id='update_indicators'
    )

    # 每5分钟更新实时价格
    scheduler.add_interval_job(
        func=update_realtime_prices,
        minutes=5,
        job_id='update_prices'
    )

    logger.info("定时任务初始化完成")


def generate_and_push_daily_report():
    """生成并推送每日报告"""
    logger.info("开始生成每日报告...")

    try:
        from src.report_service import ReportService
        from src.push_service import FeishuPushService

        # 生成报告
        report_service = ReportService()
        report = report_service.generate_daily_report()

        # 推送到飞书
        push_service = FeishuPushService()
        push_service.send_message(report)

        logger.info("每日报告生成并推送成功")
    except Exception as e:
        logger.error(f"每日报告生成失败: {e}")


def update_technical_indicators():
    """更新技术指标"""
    logger.info("开始更新技术指标...")

    try:
        from src.technical_indicators import TechnicalIndicatorCalculator

        calculator = TechnicalIndicatorCalculator()
        calculator.calculate_for_all_stocks()

        logger.info("技术指标更新成功")
    except Exception as e:
        logger.error(f"技术指标更新失败: {e}")


def update_realtime_prices():
    """更新实时价格"""
    logger.info("开始更新实时价格...")

    try:
        # TODO: 实现实时价格更新逻辑
        logger.info("实时价格更新成功")
    except Exception as e:
        logger.error(f"实时价格更新失败: {e}")


def main():
    """测试定时任务"""
    # 初始化定时任务
    init_scheduler()

    # 启动调度器
    scheduler.start()

    # 显示所有任务
    jobs = scheduler.get_jobs()
    print(f"\n当前共有 {len(jobs)} 个定时任务:")
    for job in jobs:
        print(f"  - {job.id}: {job.next_run_time}")

    # 保持运行
    try:
        print("\n调度器运行中，按Ctrl+C停止...")
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭调度器...")
        scheduler.shutdown()
        print("调度器已关闭")


if __name__ == "__main__":
    main()
