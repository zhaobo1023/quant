# -*- coding: utf-8 -*-
"""
持仓管理系统 - 后端服务启动入口

整合所有服务:
- FastAPI Web服务
- 定时任务调度
- 技术指标计算
- OCR识别
- 消息推送
"""
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 导入服务
from src.scheduler_service import SchedulerService
from src.technical_indicators import TechnicalIndicatorCalculator
from src.ocr_service import OCRService
from src.push_service import PushService
from src.report_service import ReportService

# 导入API路由
from web.api.main import app as api_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("="*60)
    logger.info("持仓管理系统启动中...")
    logger.info("="*60)

    # 1. 启动定时任务调度器
    try:
        scheduler = SchedulerService()
        scheduler.start()
        logger.info("✓ 定时任务调度器已启动")
        logger.info("  - 每日20:00: 推送持仓报告")
        logger.info("  - 每日15:30: 更新技术指标")
        logger.info("  - 每5分钟: 更新实时价格")
    except Exception as e:
        logger.warning(f"⚠ 定时任务启动失败: {e}")

    # 2. 初始化技术指标计算器
    try:
        calculator = TechnicalIndicatorCalculator()
        logger.info("✓ 技术指标计算器已初始化")
    except Exception as e:
        logger.warning(f"⚠ 技术指标计算器初始化失败: {e}")

    # 3. 初始化OCR服务
    try:
        ocr_service = OCRService()
        if ocr_service.is_available():
            logger.info("✓ OCR服务已初始化 (百度API)")
        else:
            logger.info("✓ OCR服务已初始化 (Mock模式)")
    except Exception as e:
        logger.warning(f"⚠ OCR服务初始化失败: {e}")

    # 4. 初始化推送服务
    try:
        push_service = PushService()
        if push_service.is_configured():
            logger.info("✓ 推送服务已初始化 (飞书Webhook)")
        else:
            logger.info("✓ 推送服务已初始化 (Mock模式)")
    except Exception as e:
        logger.warning(f"⚠ 推送服务初始化失败: {e}")

    # 5. 初始化报告服务
    try:
        report_service = ReportService()
        logger.info("✓ 报告服务已初始化")
    except Exception as e:
        logger.warning(f"⚠ 报告服务初始化失败: {e}")

    logger.info("="*60)
    logger.info("所有服务启动完成!")
    logger.info("="*60)
    logger.info("访问地址:")
    logger.info("  - API文档: http://localhost:8000/docs")
    logger.info("  - 健康检查: http://localhost:8000/")
    logger.info("="*60)

    yield

    # 关闭时清理
    logger.info("正在关闭服务...")
    try:
        scheduler.shutdown()
        logger.info("✓ 定时任务已停止")
    except:
        pass
    logger.info("服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="持仓管理系统",
    description="个人持仓管理、技术分析、定时推送",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入所有API路由
app.mount("/", api_app)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='持仓管理系统后端服务')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8000, help='监听端口')
    parser.add_argument('--reload', action='store_true', help='开发模式(自动重载)')
    parser.add_argument('--no-scheduler', action='store_true', help='禁用定时任务')

    args = parser.parse_args()

    # 如果禁用定时任务,移除lifespan
    if args.no_scheduler:
        app.router.lifespan_context = None

    # 启动服务
    uvicorn.run(
        "start_backend:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
