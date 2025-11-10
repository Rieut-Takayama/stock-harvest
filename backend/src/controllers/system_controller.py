"""
システム関連のコントローラー層
HTTPリクエスト処理を担当
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from ..services.system_service import SystemService

logger = logging.getLogger(__name__)

# ルーター作成
router = APIRouter(prefix="/api/system", tags=["system"])

# サービス初期化
system_service = SystemService()

@router.get("/info")
async def get_system_info():
    """
    システム情報取得エンドポイント
    
    Returns:
        SystemInfo: システムのバージョンと稼働状況
    """
    try:
        logger.info("📋 GET /api/system/info リクエスト受信")
        
        # サービスからシステム情報を取得
        system_info = await system_service.get_system_information()
        
        logger.info("✅ システム情報レスポンス送信")
        return system_info
        
    except Exception as e:
        logger.error(f"❌ システム情報取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "システム情報の取得に失敗しました",
                "error": str(e),
                "endpoint": "/api/system/info"
            }
        )

@router.get("/status")  
async def get_system_status():
    """
    システムヘルスチェックエンドポイント
    
    Returns:
        HealthStatus: システムの健全性情報
    """
    try:
        logger.info("🏥 GET /api/system/status リクエスト受信")
        
        # サービスからヘルスチェック実行
        health_status = await system_service.get_health_check()
        
        # ヘルス状態に応じたステータスコード
        status_code = status.HTTP_200_OK if health_status["healthy"] else status.HTTP_503_SERVICE_UNAVAILABLE
        
        logger.info(f"✅ ヘルスチェックレスポンス送信: {health_status['status']}")
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
        
    except Exception as e:
        logger.error(f"❌ ヘルスチェックエラー: {e}")
        
        # ヘルスチェックエラー専用レスポンス
        error_response = {
            "healthy": False,
            "status": "unhealthy",
            "message": "ヘルスチェック実行失敗",
            "error": str(e),
            "checks": {},
            "endpoint": "/api/system/status"
        }
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response
        )