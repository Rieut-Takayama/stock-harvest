"""
Charts Controller - チャートデータ取得API
GET /api/charts/data/:stockCode エンドポイント実装
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Path, Query
from datetime import datetime

from ..services.charts_service import ChartsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/charts", tags=["charts"])

# チャートサービスインスタンス
charts_service = ChartsService()

@router.get("/data/{stock_code}", summary="チャートデータ取得")
async def get_chart_data(
    stock_code: str = Path(..., description="銘柄コード (例: 7203)"),
    timeframe: str = Query("1d", description="タイムフレーム (1d, 1w, 1m, 3m)"),
    period: str = Query("30d", description="期間 (30d, 90d, 1y, 2y)"),
    indicators: Optional[str] = Query(None, description="テクニカル指標 (カンマ区切り)")
) -> Dict[str, Any]:
    """
    指定した銘柄のチャートデータを取得
    
    Args:
        stock_code: 銘柄コード (4桁の数字)
        timeframe: データの時間軸
        period: データ取得期間
        indicators: 含めるテクニカル指標
    
    Returns:
        チャートデータとメタデータ
    """
    try:
        logger.info(f"📊 チャートデータ取得開始 - 銘柄: {stock_code}, 期間: {period}, フレーム: {timeframe}")
        
        # パラメータバリデーション
        if not stock_code.isdigit() or len(stock_code) != 4:
            raise HTTPException(
                status_code=400, 
                detail="銘柄コードは4桁の数字で入力してください"
            )
        
        # 指標パース
        indicator_list = []
        if indicators:
            indicator_list = [ind.strip() for ind in indicators.split(",")]
        
        # チャートデータ取得
        chart_data = await charts_service.get_chart_data(
            stock_code=stock_code,
            timeframe=timeframe,
            period=period,
            indicators=indicator_list
        )
        
        logger.info(f"✅ チャートデータ取得成功 - 銘柄: {stock_code}, データ件数: {len(chart_data.get('ohlc_data', []))}")
        
        return chart_data
        
    except HTTPException:
        # HTTPExceptionは再発生させる
        raise
    except Exception as e:
        logger.error(f"❌ チャートデータ取得エラー - 銘柄: {stock_code}, エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"チャートデータの取得に失敗しました: {str(e)}"
        )

@router.get("/health", summary="チャート機能ヘルスチェック")
async def charts_health_check() -> Dict[str, Any]:
    """
    チャート機能のヘルスチェック
    """
    try:
        # yfinanceの基本動作確認
        health_status = await charts_service.health_check()
        
        return {
            "status": "healthy",
            "service": "charts",
            "timestamp": datetime.now().isoformat(),
            "details": health_status
        }
        
    except Exception as e:
        logger.error(f"❌ チャート機能ヘルスチェック失敗: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"チャート機能が利用できません: {str(e)}"
        )