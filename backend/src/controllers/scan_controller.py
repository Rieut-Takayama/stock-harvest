"""
スキャンコントローラー
スキャン機能のHTTPエンドポイントを提供
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..services.scan_service import ScanService
from ..services.logic_detection_service import LogicDetectionService
from ..repositories.scan_repository import ScanRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])

class LogicAEnhancedRequest(BaseModel):
    """ロジックA強化版リクエスト"""
    stock_code: str
    stock_name: str = ""
    detection_mode: str = "enhanced"  # "enhanced" または "legacy"

def get_scan_service() -> ScanService:
    """スキャンサービスの依存性注入"""
    scan_repository = ScanRepository()
    return ScanService(scan_repository)

def get_logic_detection_service() -> LogicDetectionService:
    """ロジック検出サービスの依存性注入"""
    return LogicDetectionService()

@router.post("/execute")
async def execute_scan(scan_service: ScanService = Depends(get_scan_service)):
    """
    全銘柄スキャンを実行
    
    - **戻り値**: スキャンIDと開始メッセージ
    - **処理**: 全銘柄に対してロジックA・Bを適用してスキャン
    """
    try:
        result = await scan_service.start_scan()
        logger.info(f"スキャン開始: {result}")
        return result
        
    except Exception as e:
        logger.error(f"スキャン実行エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"スキャンの実行に失敗しました: {str(e)}"
        )

@router.get("/status")
async def get_scan_status(scan_service: ScanService = Depends(get_scan_service)):
    """
    現在のスキャン状況を取得
    
    - **戻り値**: スキャンの進捗状況
    - **情報**: 実行中フラグ、進捗率、処理銘柄数、推定残り時間等
    """
    try:
        result = await scan_service.get_scan_status()
        return result
        
    except Exception as e:
        logger.error(f"スキャン状況取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"スキャン状況の取得に失敗しました: {str(e)}"
        )

@router.get("/results")
async def get_scan_results(scan_service: ScanService = Depends(get_scan_service)):
    """
    最新のスキャン結果を取得
    
    - **戻り値**: ロジックA・Bで検出された銘柄一覧
    - **情報**: 銘柄コード、名前、価格、変動率、出来高
    """
    try:
        result = await scan_service.get_scan_results()
        return result
        
    except Exception as e:
        logger.error(f"スキャン結果取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"スキャン結果の取得に失敗しました: {str(e)}"
        )

@router.post("/logic-a-enhanced")
async def detect_logic_a_enhanced(
    request: LogicAEnhancedRequest,
    logic_service: LogicDetectionService = Depends(get_logic_detection_service)
):
    """
    ロジックA強化版（ストップ高張り付き精密検出）を実行
    
    - **stock_code**: 銘柄コード（必須）
    - **stock_name**: 銘柄名（オプション）
    - **detection_mode**: 検出モード（"enhanced" または "legacy"）
    
    戻り値: 詳細な検出結果・売買シグナル・リスク評価
    """
    try:
        from ..services.stock_data_service import StockDataService
        from ..services.technical_analysis_service import TechnicalAnalysisService
        
        # 株価データを取得
        stock_data_service = StockDataService()
        tech_analysis_service = TechnicalAnalysisService()
        
        # 基本株価データ取得
        stock_data = await stock_data_service.fetch_stock_data(
            request.stock_code, 
            request.stock_name
        )
        
        if not stock_data:
            raise HTTPException(
                status_code=404,
                detail=f"銘柄データが取得できませんでした: {request.stock_code}"
            )
        
        # テクニカル指標を生成（stock_dataに signals が含まれていない場合）
        if 'signals' not in stock_data:
            stock_data['signals'] = tech_analysis_service.generate_technical_signals(
                stock_data=stock_data
            )
        
        # 検出モードに応じて処理分岐
        if request.detection_mode == "enhanced":
            # ロジックA強化版を実行
            result = await logic_service.detect_logic_a_enhanced(stock_data)
            
            logger.info(f"ロジックA強化版実行: {request.stock_code} - 検出結果: {result.get('detected', False)}")
            
            return {
                "success": True,
                "detection_mode": "enhanced",
                "stock_code": request.stock_code,
                "stock_name": stock_data.get('name', request.stock_name),
                "detection_result": result,
                "stock_data": {
                    "price": stock_data.get('price'),
                    "change": stock_data.get('change'),
                    "changeRate": stock_data.get('changeRate'),
                    "volume": stock_data.get('volume'),
                    "signals": stock_data.get('signals')
                }
            }
        else:
            # 従来版（レガシー）を実行
            is_detected = await logic_service.detect_logic_a(stock_data)
            
            logger.info(f"ロジックA従来版実行: {request.stock_code} - 検出結果: {is_detected}")
            
            return {
                "success": True,
                "detection_mode": "legacy",
                "stock_code": request.stock_code,
                "stock_name": stock_data.get('name', request.stock_name),
                "detected": is_detected,
                "stock_data": {
                    "price": stock_data.get('price'),
                    "change": stock_data.get('change'),
                    "changeRate": stock_data.get('changeRate'),
                    "volume": stock_data.get('volume'),
                    "signals": stock_data.get('signals')
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ロジックA強化版検出エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"検出処理に失敗しました: {str(e)}"
        )

@router.get("/logic-a-history/{stock_code}")
async def get_logic_a_history(
    stock_code: str,
    logic_service: LogicDetectionService = Depends(get_logic_detection_service)
):
    """
    指定銘柄のロジックA検出履歴を取得
    
    - **stock_code**: 銘柄コード
    
    戻り値: 検出履歴リスト
    """
    try:
        history = logic_service.get_stock_history(stock_code)
        
        logger.info(f"履歴取得: {stock_code} - {len(history)}件")
        
        return {
            "success": True,
            "stock_code": stock_code,
            "history_count": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"履歴取得エラー {stock_code}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"履歴の取得に失敗しました: {str(e)}"
        )

@router.get("/logic-a-all-detected")
async def get_all_detected_logic_a(
    detection_type: Optional[str] = None,
    logic_service: LogicDetectionService = Depends(get_logic_detection_service)
):
    """
    すべてのロジックA検出銘柄を取得
    
    - **detection_type**: 検出タイプフィルター（"logic_a_enhanced", "logic_a", "logic_b" など）
    
    戻り値: 検出された全銘柄のリスト
    """
    try:
        detected_stocks = logic_service.get_all_detected_stocks(detection_type)
        
        logger.info(f"全検出銘柄取得: {len(detected_stocks)}件")
        
        return {
            "success": True,
            "detection_type_filter": detection_type,
            "total_count": len(detected_stocks),
            "detected_stocks": detected_stocks
        }
        
    except Exception as e:
        logger.error(f"全検出銘柄取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"検出銘柄の取得に失敗しました: {str(e)}"
        )

@router.get("/logic-a-config")
async def get_logic_a_config(
    logic_service: LogicDetectionService = Depends(get_logic_detection_service)
):
    """
    ロジックAの設定を取得
    
    戻り値: 現在の検出設定
    """
    try:
        configs = logic_service.get_logic_configs()
        
        return {
            "success": True,
            "configs": configs,
            "enhanced_config": logic_service.logic_a_enhanced_config
        }
        
    except Exception as e:
        logger.error(f"設定取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"設定の取得に失敗しました: {str(e)}"
        )