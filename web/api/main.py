# -*- coding: utf-8 -*-
"""
投研系统后端 API

FastAPI 服务，提供持仓管理接口

运行：uvicorn web.api.main:app --reload --port 8000
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from src.db import get_connection, execute_query, execute_update

app = FastAPI(
    title="投研系统 API",
    description="持仓管理与数据服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class PositionCreate(BaseModel):
    """创建持仓"""
    stock_code: str
    stock_name: Optional[str] = None
    shares: int
    cost_price: float
    is_margin: bool = False
    account_tag: str = "default"
    notes: Optional[str] = None


class PositionUpdate(BaseModel):
    """更新持仓"""
    stock_name: Optional[str] = None
    shares: Optional[int] = None
    cost_price: Optional[float] = None
    is_margin: Optional[bool] = None
    account_tag: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[int] = None


class PositionResponse(BaseModel):
    """持仓响应"""
    id: int
    stock_code: str
    stock_name: Optional[str]
    shares: int
    cost_price: float
    is_margin: bool
    account_tag: str
    notes: Optional[str]
    status: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# ==================== API 路由 ====================

@app.get("/")
def root():
    """健康检查"""
    return {"status": "ok", "message": "投研系统 API 运行中"}


@app.get("/api/positions", response_model=List[PositionResponse])
def list_positions(account_tag: Optional[str] = None, status: Optional[int] = None):
    """获取持仓列表"""
    sql = "SELECT * FROM model_trade_position WHERE 1=1"
    params = []

    if account_tag:
        sql += " AND account_tag = %s"
        params.append(account_tag)
    if status is not None:
        sql += " AND status = %s"
        params.append(status)

    sql += " ORDER BY updated_at DESC"

    rows = execute_query(sql, params if params else None)
    return rows


@app.get("/api/positions/{position_id}", response_model=PositionResponse)
def get_position(position_id: int):
    """获取单个持仓"""
    rows = execute_query(
        "SELECT * FROM model_trade_position WHERE id = %s",
        (position_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return rows[0]


@app.post("/api/positions", response_model=PositionResponse)
def create_position(position: PositionCreate):
    """创建持仓"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO model_trade_position
            (stock_code, stock_name, shares, cost_price, is_margin, account_tag, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            position.stock_code,
            position.stock_name,
            position.shares,
            position.cost_price,
            1 if position.is_margin else 0,
            position.account_tag,
            position.notes
        ))
        conn.commit()
        position_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="该账户下已存在此股票持仓")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    # 返回创建的记录
    rows = execute_query("SELECT * FROM model_trade_position WHERE id = %s", (position_id,))
    return rows[0]


@app.put("/api/positions/{position_id}", response_model=PositionResponse)
def update_position(position_id: int, position: PositionUpdate):
    """更新持仓"""
    # 检查是否存在
    rows = execute_query("SELECT * FROM model_trade_position WHERE id = %s", (position_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="持仓不存在")

    # 构建更新语句
    updates = []
    params = []

    if position.stock_name is not None:
        updates.append("stock_name = %s")
        params.append(position.stock_name)
    if position.shares is not None:
        updates.append("shares = %s")
        params.append(position.shares)
    if position.cost_price is not None:
        updates.append("cost_price = %s")
        params.append(position.cost_price)
    if position.is_margin is not None:
        updates.append("is_margin = %s")
        params.append(1 if position.is_margin else 0)
    if position.account_tag is not None:
        updates.append("account_tag = %s")
        params.append(position.account_tag)
    if position.notes is not None:
        updates.append("notes = %s")
        params.append(position.notes)
    if position.status is not None:
        updates.append("status = %s")
        params.append(position.status)

    if not updates:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")

    params.append(position_id)
    sql = f"UPDATE model_trade_position SET {', '.join(updates)} WHERE id = %s"

    execute_update(sql, params)

    # 返回更新后的记录
    rows = execute_query("SELECT * FROM model_trade_position WHERE id = %s", (position_id,))
    return rows[0]


@app.delete("/api/positions/{position_id}")
def delete_position(position_id: int):
    """删除持仓"""
    rows = execute_query("SELECT * FROM model_trade_position WHERE id = %s", (position_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="持仓不存在")

    execute_update("DELETE FROM model_trade_position WHERE id = %s", (position_id,))
    return {"message": "删除成功", "id": position_id}


@app.get("/api/accounts")
def list_accounts():
    """获取所有账户标签"""
    rows = execute_query(
        "SELECT DISTINCT account_tag FROM model_trade_position ORDER BY account_tag"
    )
    return [r["account_tag"] for r in rows]


# ==================== 技术指标 API ====================

class TechnicalIndicatorResponse(BaseModel):
    """技术指标响应"""
    id: int
    stock_code: str
    trade_date: str
    ma5: Optional[float]
    ma10: Optional[float]
    ma20: Optional[float]
    ma60: Optional[float]
    macd_dif: Optional[float]
    macd_dea: Optional[float]
    rsi_6: Optional[float]
    kdj_k: Optional[float]
    kdj_d: Optional[float]
    bollinger_upper: Optional[float]


@app.get("/api/indicators/{stock_code}")
def get_technical_indicators(stock_code: str, days: int = 30):
    """获取股票技术指标"""
    sql = """
    SELECT * FROM trade_technical_indicator
    WHERE stock_code = %s
    ORDER BY trade_date DESC
    LIMIT %s
    """
    rows = execute_query(sql, (stock_code, days))
    return rows


# ==================== 分析报告 API ====================

class AnalysisReportResponse(BaseModel):
    """分析报告响应"""
    id: int
    stock_code: str
    report_date: str
    signal_type: Optional[str]
    signal_strength: Optional[float]
    trend_direction: Optional[str]
    risk_level: Optional[str]
    recommendation: Optional[str]


@app.get("/api/reports/daily")
def get_daily_report():
    """获取每日报告"""
    from src.report_service import ReportService

    service = ReportService()
    report = service.generate_daily_report()

    return report


@app.get("/api/reports/stock/{stock_code}")
def get_stock_report(stock_code: str):
    """获取单只股票的分析报告"""
    from src.report_service import ReportService

    service = ReportService()
    report = service.generate_stock_report(stock_code)

    return report


# ==================== OCR API ====================

from fastapi import UploadFile, File
import shutil

@app.post("/api/ocr/upload")
async def upload_ocr_image(file: UploadFile = File(...)):
    """上传OCR图片并识别"""
    # 保存文件
    upload_dir = "uploads/ocr"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 调用OCR服务
    from src.ocr_service import MockOCRService

    ocr_service = MockOCRService()
    positions = ocr_service.process_position_image(file_path)

    return {
        "file_path": file_path,
        "positions": positions,
        "message": "OCR识别完成"
    }


# ==================== 定时任务 API ====================

@app.get("/api/scheduler/jobs")
def list_scheduled_jobs():
    """获取所有定时任务"""
    from src.scheduler_service import scheduler

    jobs = scheduler.get_jobs()
    return [
        {
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "trigger": str(job.trigger)
        }
        for job in jobs
    ]


@app.post("/api/scheduler/run/{job_id}")
def run_scheduled_job(job_id: str):
    """手动执行定时任务"""
    from src.scheduler_service import scheduler

    try:
        job = scheduler.scheduler.get_job(job_id)
        if job:
            job.func()
            return {"message": f"任务 {job_id} 执行成功"}
        else:
            raise HTTPException(status_code=404, detail="任务不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据同步 API ====================

@app.post("/api/sync/indicators")
def sync_technical_indicators(stock_code: Optional[str] = None):
    """同步技术指标"""
    from src.technical_indicators import TechnicalIndicatorCalculator

    calculator = TechnicalIndicatorCalculator()

    try:
        if stock_code:
            calculator.calculate_for_stock(stock_code)
        else:
            calculator.calculate_for_all_stocks()

        return {"message": "技术指标同步成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 启动入口 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    from src.scheduler_service import init_scheduler, scheduler

    # 初始化并启动定时任务
    init_scheduler()
    scheduler.start()
    print("定时任务调度器已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    from src.scheduler_service import scheduler

    scheduler.shutdown()
    print("定时任务调度器已关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
