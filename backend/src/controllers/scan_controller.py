"""
スキャンコントローラー
スキャン機能のHTTPエンドポイントを提供
"""

from fastapi import APIRouter, HTTPException, Depends
from ..services.scan_service import ScanService
from ..repositories.scan_repository import ScanRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])

def get_scan_service() -> ScanService:
    """スキャンサービスの依存性注入"""
    scan_repository = ScanRepository()
    return ScanService(scan_repository)

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