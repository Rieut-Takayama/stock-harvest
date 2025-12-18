"""
Charts Controller - チャートデータ取得API
GET /api/charts/data/:stockCode エンドポイント実装
バリデーション・モデル連携強化版
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Path, Query
from datetime import datetime

from ..lib.logger import logger, PerformanceTracker, transaction_scope
from ..services.charts_service import ChartsService
from ..validators.charts_validators import ChartsValidator
from ..models.charts_models import ChartDataModel, ChartHealthCheckModel

router = APIRouter(prefix="/api/charts", tags=["charts"])

# チャートサービス・バリデーターインスタンス
charts_service = ChartsService()
charts_validator = ChartsValidator()

@router.get("/data/{stock_code}", 
           summary="チャートデータ取得", 
           response_model=ChartDataModel)
async def get_chart_data(
    stock_code: str = Path(..., description="銘柄コード (例: 7203)", regex=r'^\d{4}$'),
    timeframe: str = Query("1d", description="タイムフレーム (1d, 1w, 1m, 3m)"),
    period: str = Query("30d", description="期間 (5d, 30d, 90d, 1y, 2y)"),
    indicators: Optional[str] = Query(None, description="テクニカル指標 (カンマ区切り: sma,rsi,macd,bollinger)")
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
        
    Raises:
        HTTPException: バリデーションエラーまたはデータ取得エラー
    """
    perf_tracker = PerformanceTracker(f"chart_controller_{stock_code}", logger)
    
    with transaction_scope(f"chart_data_request_{stock_code}"):
        try:
            logger.info("📊 チャートデータリクエスト開始", {
                "stock_code": stock_code,
                "timeframe": timeframe,
                "period": period,
                "indicators": indicators
            })
            
            # 事前バリデーション（FastAPIのPath/Query検証に加えて）
            is_valid_code, code_error = charts_validator.validate_stock_code(stock_code)
            if not is_valid_code:
                logger.warning(f"⚠️ バリデーションエラー - 銘柄コード: {code_error}")
                raise HTTPException(status_code=400, detail=code_error)
            
            # タイムフレーム・期間の組み合わせ確認
            combination_valid, combination_error = charts_validator.validate_timeframe_period_combination(
                timeframe, period
            )
            if not combination_valid:
                logger.warning(f"⚠️ 組み合わせエラー: {combination_error}")
                raise HTTPException(status_code=400, detail=combination_error)
            
            # 指標バリデーション
            is_valid_indicators, indicators_error, _ = charts_validator.validate_indicators(indicators)
            if not is_valid_indicators:
                logger.warning(f"⚠️ 指標バリデーションエラー: {indicators_error}")
                raise HTTPException(status_code=400, detail=indicators_error)
            
            # 指標パース
            indicator_list = []
            if indicators:
                indicator_list = [ind.strip() for ind in indicators.split(",") if ind.strip()]
            
            # チャートデータ取得
            chart_data = await charts_service.get_chart_data(
                stock_code=stock_code,
                timeframe=timeframe,
                period=period,
                indicators=indicator_list
            )
            
            # データが取得できなかった場合の処理（200で失敗レスポンスを返す）
            if not chart_data.get('success', False):
                error_message = chart_data.get('message', 'データ取得に失敗しました')
                logger.warning(f"⚠️ データ取得失敗（200レスポンス）: {error_message}")
                # 存在しない銘柄の場合も200で返し、successフラグで判別可能にする
                return chart_data
            
            logger.info("✅ チャートデータ取得成功", {
                "stock_code": stock_code,
                "data_count": chart_data.get('dataCount', 0),
                "indicators_count": len(chart_data.get('technicalIndicators', {}))
            })
            
            perf_tracker.end({
                "success": True,
                "data_points": chart_data.get('dataCount', 0)
            })
            
            return chart_data
            
        except HTTPException:
            # HTTPExceptionはそのまま再発生
            perf_tracker.end({"error": "http_exception"})
            raise
        except Exception as e:
            error_msg = f"チャートデータ取得処理エラー: {str(e)}"
            logger.error(error_msg, {
                "stock_code": stock_code,
                "timeframe": timeframe,
                "period": period,
                "error": str(e)
            })
            
            perf_tracker.end({"error": "unexpected_exception"})
            raise HTTPException(
                status_code=500,
                detail=f"チャートデータの取得に失敗しました: {str(e)}"
            )

@router.get("/health", 
           summary="チャート機能ヘルスチェック",
           response_model=ChartHealthCheckModel)
async def charts_health_check() -> Dict[str, Any]:
    """
    チャート機能のヘルスチェック（全層統合版）
    
    Returns:
        ヘルスチェック結果とサービス詳細情報
    """
    with transaction_scope("charts_health_check"):
        try:
            logger.info("🩺 チャート機能ヘルスチェック開始")
            
            # サービス層ヘルスチェック（リポジトリ・バリデーター含む）
            health_status = await charts_service.health_check()
            
            # 全体の健全性判定
            overall_status = "healthy"
            service_status = health_status.get("service_status", "unknown")
            repo_status = health_status.get("repository", {}).get("repository_status", "unknown")
            validator_status = health_status.get("validator", {}).get("status", "unknown")
            
            if any(status in ["error", "degraded"] for status in [service_status, repo_status, validator_status]):
                overall_status = "degraded"
            
            response = {
                "status": overall_status,
                "service": "charts",
                "timestamp": datetime.now().isoformat(),
                "details": health_status
            }
            
            logger.info("✅ ヘルスチェック完了", {
                "overall_status": overall_status,
                "service_status": service_status,
                "repository_status": repo_status,
                "validator_status": validator_status
            })
            
            return response
            
        except Exception as e:
            error_msg = f"チャート機能ヘルスチェック失敗: {str(e)}"
            logger.error(error_msg)
            
            # ヘルスチェック失敗時は503エラーを返す
            raise HTTPException(
                status_code=503,
                detail=f"チャート機能が利用できません: {str(e)}"
            )

@router.get("/validation-rules", summary="チャート機能バリデーションルール取得")
async def get_validation_rules() -> Dict[str, Any]:
    """
    チャート機能で使用されるバリデーションルールを取得
    
    Returns:
        バリデーションルール詳細
    """
    try:
        validation_summary = charts_validator.get_validation_summary()
        
        return {
            "success": True,
            "validation_rules": validation_summary,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"バリデーションルール取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"バリデーションルールの取得に失敗しました: {str(e)}"
        )