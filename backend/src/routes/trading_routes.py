"""
売買支援API関連ルート
Stock Harvest AI プロジェクト用
"""

from fastapi import APIRouter, Body, Query, HTTPException
from typing import Dict, Any, Optional

from ..controllers.trading_controller import TradingController
from ..lib.logger import logger

# ルーター作成
router = APIRouter(
    prefix="/api/trading",
    tags=["Trading Support"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# コントローラーインスタンス
trading_controller = TradingController()


@router.post("/entry-optimization", 
            summary="エントリーポイント最適化",
            description="過去データに基づく最適エントリー価格算出、リスクリワード比率自動計算")
async def optimize_entry_point(request_data: Dict[str, Any] = Body(...)):
    """
    エントリーポイント最適化API
    
    リクエストボディ:
    {
        "stock_code": "7203",
        "current_price": 1000.0,
        "logic_type": "logic_a",
        "investment_amount": 100000.0,
        "risk_tolerance": "medium",
        "timeframe": "1m",
        "market_conditions": {}
    }
    
    レスポンス:
    {
        "success": true,
        "data": {
            "stock_code": "7203",
            "stock_name": "トヨタ自動車",
            "current_price": 1000.0,
            "optimal_entry_price": 980.0,
            "optimal_entry_price_range": {
                "min": 975.0,
                "max": 985.0
            },
            "target_profit_price": 1200.0,
            "stop_loss_price": 920.0,
            "risk_reward_ratio": 2.5,
            "expected_return": 15.0,
            "confidence_level": "high",
            "position_size_recommendation": {
                "shares": 100,
                "investment_amount": 98000.0
            },
            "market_timing_score": 85,
            "analysis_factors": {},
            "recommended_order_type": "limit",
            "execution_notes": [],
            "historical_performance": {}
        }
    }
    """
    try:
        return await trading_controller.optimize_entry_point(request_data)
    except Exception as e:
        logger.error(f"エントリーポイント最適化APIエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ifdoco-guide",
            summary="IFDOCO注文ガイド生成", 
            description="エントリー・利確・損切り価格の推奨設定、注文方法ステップバイステップガイド")
async def generate_ifdoco_guide(request_data: Dict[str, Any] = Body(...)):
    """
    IFDOCO注文ガイド生成API
    
    リクエストボディ:
    {
        "stock_code": "7203",
        "entry_price": 1000.0,
        "investment_amount": 100000.0,
        "logic_type": "logic_a",
        "risk_level": "medium",
        "holding_period": "1m"
    }
    
    レスポンス:
    {
        "success": true,
        "data": {
            "stock_code": "7203",
            "stock_name": "トヨタ自動車",
            "entry_price": 1000.0,
            "investment_amount": 100000.0,
            "recommended_quantity": 100,
            "order_settings": {
                "entry_order": {},
                "profit_target_order": {},
                "stop_loss_order": {},
                "order_validity": "month",
                "execution_priority": "simultaneous"
            },
            "step_by_step_guide": [],
            "risk_analysis": {},
            "expected_scenarios": {},
            "broker_specific_notes": {},
            "monitoring_points": [],
            "exit_strategy": {}
        }
    }
    """
    try:
        return await trading_controller.generate_ifdoco_guide(request_data)
    except Exception as e:
        logger.error(f"IFDOCO注文ガイド生成APIエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 履歴管理API用ルーター
history_router = APIRouter(
    prefix="/api/history",
    tags=["Trading History"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@history_router.get("/trades",
                   summary="売買履歴取得",
                   description="全売買履歴、パフォーマンス分析・勝率計算")
async def get_trading_history(
    stock_code: Optional[str] = Query(None, description="銘柄コード", regex="^[0-9]{4}$"),
    logic_type: Optional[str] = Query(None, description="ロジック種別 (logic_a, logic_b, manual)"),
    trade_type: Optional[str] = Query(None, description="取引種別 (BUY, SELL)"),
    status: Optional[str] = Query(None, description="ステータス (open, closed, cancelled)"),
    date_from: Optional[str] = Query(None, description="開始日 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="終了日 (YYYY-MM-DD)"),
    min_profit_loss: Optional[float] = Query(None, description="最小損益"),
    max_profit_loss: Optional[float] = Query(None, description="最大損益"),
    page: int = Query(1, description="ページ番号", ge=1),
    limit: int = Query(20, description="取得件数", ge=1, le=100)
):
    """
    売買履歴取得API
    
    レスポンス:
    {
        "success": true,
        "data": {
            "trades": [
                {
                    "id": "trade-xxx",
                    "stock_code": "7203",
                    "stock_name": "トヨタ自動車",
                    "trade_type": "BUY",
                    "logic_type": "logic_a",
                    "entry_price": 1000.0,
                    "exit_price": 1100.0,
                    "quantity": 100,
                    "profit_loss": 10000.0,
                    "profit_loss_rate": 10.0,
                    "status": "closed"
                }
            ],
            "summary": {
                "total_trades": 10,
                "win_rate": 70.0,
                "total_profit_loss": 50000.0,
                "average_profit": 7500.0,
                "average_loss": -2500.0
            },
            "total": 10,
            "page": 1,
            "limit": 20,
            "has_next": false
        }
    }
    """
    try:
        return await trading_controller.get_trading_history(
            stock_code=stock_code,
            logic_type=logic_type,
            trade_type=trade_type,
            status=status,
            date_from=date_from,
            date_to=date_to,
            min_profit_loss=min_profit_loss,
            max_profit_loss=max_profit_loss,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"売買履歴取得APIエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@history_router.get("/signals",
                   summary="シグナル履歴取得", 
                   description="シグナル履歴、パフォーマンス分析・勝率計算")
async def get_signal_history(
    stock_code: Optional[str] = Query(None, description="銘柄コード", regex="^[0-9]{4}$"),
    signal_type: Optional[str] = Query(None, description="シグナル種別"),
    status: Optional[str] = Query(None, description="ステータス (pending, executed, cancelled)"),
    confidence_min: Optional[float] = Query(None, description="最小信頼度", ge=0, le=1),
    date_from: Optional[str] = Query(None, description="開始日 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="終了日 (YYYY-MM-DD)"),
    page: int = Query(1, description="ページ番号", ge=1),
    limit: int = Query(20, description="取得件数", ge=1, le=100)
):
    """
    シグナル履歴取得API
    
    レスポンス:
    {
        "success": true,
        "data": {
            "signals": [
                {
                    "id": "signal-xxx",
                    "stock_code": "7203",
                    "stock_name": "トヨタ自動車",
                    "signal_type": "BUY",
                    "confidence": 0.85,
                    "current_price": 1000.0,
                    "entry_price": 980.0,
                    "profit_target": 1200.0,
                    "stop_loss": 920.0,
                    "status": "executed",
                    "created_at": "2024-01-01T00:00:00"
                }
            ],
            "summary": {
                "total_signals": 20,
                "executed_signals": 15,
                "signal_accuracy": 80.0,
                "average_confidence": 0.75
            },
            "total": 20,
            "page": 1,
            "limit": 20,
            "has_next": false
        }
    }
    """
    try:
        return await trading_controller.get_signal_history(
            stock_code=stock_code,
            signal_type=signal_type,
            status=status,
            confidence_min=confidence_min,
            date_from=date_from,
            date_to=date_to,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"シグナル履歴取得APIエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record",
            summary="売買記録作成（内部使用）",
            description="売買記録の作成（内部システム用）")
async def create_trading_record(request_data: Dict[str, Any] = Body(...)):
    """
    売買記録作成API（内部使用）
    
    リクエストボディ:
    {
        "stock_code": "7203",
        "stock_name": "トヨタ自動車",
        "trade_type": "BUY",
        "logic_type": "logic_a",
        "entry_price": 1000.0,
        "quantity": 100,
        "total_cost": 100000.0,
        "order_method": "limit",
        "entry_reason": "ロジックA検出"
    }
    """
    try:
        return await trading_controller.create_trading_record(request_data)
    except Exception as e:
        logger.error(f"売買記録作成APIエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance",
           summary="パフォーマンスサマリー取得",
           description="売買パフォーマンスの統計情報取得")
async def get_trading_performance_summary(
    analysis_period: str = Query('3m', description="分析期間 (1w, 1m, 3m, 6m, 1y)"),
    logic_type: Optional[str] = Query(None, description="ロジック種別"),
    benchmark: str = Query('nikkei225', description="ベンチマーク")
):
    """
    パフォーマンスサマリー取得API
    
    レスポンス:
    {
        "success": true,
        "data": {
            "analysis_period": "3m",
            "summary": {
                "total_trades": 50,
                "win_rate": 68.0,
                "total_profit_loss": 150000.0,
                "profit_factor": 2.1,
                "max_profit": 25000.0,
                "max_loss": -8000.0
            },
            "benchmark": "nikkei225"
        }
    }
    """
    try:
        return await trading_controller.get_trading_performance_summary(
            analysis_period=analysis_period,
            logic_type=logic_type,
            benchmark=benchmark
        )
    except Exception as e:
        logger.error(f"パフォーマンスサマリー取得APIエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# エラーハンドリング用のヘルパー関数
def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
    """エラーレスポンス作成"""
    return {
        "success": False,
        "error_code": error_code,
        "error_message": message,
        "timestamp": "2024-12-14T22:30:00"  # 実際にはdatetime.now()を使用
    }