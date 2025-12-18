"""
システム関連のコントローラー層
HTTPリクエスト処理を担当
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from ..lib.logger import logger, track_performance, transaction_scope
from ..services.system_service import SystemService
from ..models.system_models import SystemInfoModel, HealthCheckResponse
from ..validators.system_validators import SystemValidator

# ルーター作成
router = APIRouter(prefix="/api/system", tags=["system"])

# サービス初期化
system_service = SystemService()

@router.get("/info", response_model=SystemInfoModel)
async def get_system_info():
    """
    システム情報取得エンドポイント
    
    Returns:
        SystemInfoModel: システムのバージョンと稼働状況
    """
    with transaction_scope("get_system_info"):
        try:
            with track_performance("get_system_info_request"):
                logger.info("GET /api/system/info リクエスト受信")
                
                # サービスからシステム情報を取得
                system_info = await system_service.get_system_information()
                
                # データのバリデーション
                is_valid, validation_errors = SystemValidator.validate_system_info(system_info)
                if not is_valid:
                    logger.error("システム情報データバリデーションエラー", {
                        "errors": validation_errors
                    })
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "message": "システム情報データに問題があります",
                            "validation_errors": validation_errors,
                            "endpoint": "/api/system/info"
                        }
                    )
                
                logger.info("システム情報レスポンス送信完了", {
                    "version": system_info.get("version"),
                    "status": system_info.get("status")
                })
                return system_info
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error("システム情報取得エラー", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "システム情報の取得に失敗しました",
                    "error": str(e),
                    "endpoint": "/api/system/info"
                }
            )

@router.get("/status", response_model=HealthCheckResponse)
async def get_system_status():
    """
    システムヘルスチェックエンドポイント
    
    Returns:
        HealthCheckResponse: システムの健全性情報
    """
    with transaction_scope("get_system_status"):
        try:
            with track_performance("health_check_request"):
                logger.info("GET /api/system/status リクエスト受信")
                
                # サービスからヘルスチェック実行
                health_status = await system_service.get_health_check()
                
                # レスポンスデータのバリデーション
                is_valid, validation_errors = SystemValidator.validate_health_check_response(health_status)
                if not is_valid:
                    logger.warning("ヘルスチェックレスポンスバリデーション警告", {
                        "errors": validation_errors
                    })
                    # ヘルスチェックの場合は警告レベルに留める
                
                # ヘルス状態に応じたステータスコード
                status_code = status.HTTP_200_OK if health_status.get("healthy", False) else status.HTTP_503_SERVICE_UNAVAILABLE
                
                logger.info("ヘルスチェックレスポンス送信完了", {
                    "healthy": health_status.get("healthy"),
                    "status": health_status.get("status"),
                    "checks_count": len(health_status.get("checks", {}))
                })
                
                return JSONResponse(
                    status_code=status_code,
                    content=health_status
                )
                
        except Exception as e:
            logger.error("ヘルスチェック実行エラー", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            # ヘルスチェックエラー専用レスポンス
            error_response = {
                "healthy": False,
                "status": "unhealthy",
                "message": "ヘルスチェック実行失敗",
                "error": str(e),
                "checks": {},
                "timestamp": "2025-12-13T10:30:00Z",  # 現在時刻を設定
                "severity": "error",
                "endpoint": "/api/system/status"
            }
            
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=error_response
            )