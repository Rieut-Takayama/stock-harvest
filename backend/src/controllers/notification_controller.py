"""
通知設定コントローラー
LINE Notify設定のAPIエンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from ..lib.logger import logger, transaction_scope
from ..services.notification_config_service import NotificationConfigService
from ..models.notification_models import (
    LineNotificationConfig,
    LineNotificationConfigUpdate,
    LineNotificationTestResponse
)
from ..validators.notification_validators import LineConfigUpdateValidator


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get(
    "/line",
    response_model=LineNotificationConfig,
    summary="LINE通知設定取得",
    description="LINE通知の設定情報を取得します。トークンはマスキングされた状態で返されます。"
)
async def get_line_notification_config():
    """
    LINE通知設定取得エンドポイント

    Returns:
        LineNotificationConfig: LINE通知設定（トークンはマスキング済み）

    Raises:
        HTTPException: 設定取得に失敗した場合
    """
    with transaction_scope("GET /api/notifications/line"):
        try:
            logger.info("LINE通知設定取得APIが呼ばれました")

            service = NotificationConfigService()
            config = await service.get_line_config()

            logger.info("LINE通知設定取得APIが成功", {
                "is_connected": config.is_connected,
                "status": config.status
            })

            return config

        except Exception as e:
            logger.error("LINE通知設定取得APIでエラーが発生", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "LINE通知設定の取得に失敗しました",
                    "error": str(e)
                }
            )


@router.put(
    "/line",
    response_model=LineNotificationConfig,
    summary="LINE通知設定更新",
    description="LINE通知の設定を更新します。トークンや連携状態を変更できます。"
)
async def update_line_notification_config(
    update_data: LineNotificationConfigUpdate
):
    """
    LINE通知設定更新エンドポイント

    Args:
        update_data: 更新するLINE通知設定

    Returns:
        LineNotificationConfig: 更新後のLINE通知設定（トークンはマスキング済み）

    Raises:
        HTTPException: 設定更新に失敗した場合
    """
    with transaction_scope("PUT /api/notifications/line"):
        try:
            logger.info("LINE通知設定更新APIが呼ばれました", {
                "token_update": update_data.token is not None,
                "is_connected_update": update_data.is_connected is not None
            })

            # バリデーション
            validator = LineConfigUpdateValidator(
                token=update_data.token,
                is_connected=update_data.is_connected
            )

            # サービス層で更新処理
            service = NotificationConfigService()
            updated_config = await service.update_line_config(
                token=validator.token,
                is_connected=validator.is_connected
            )

            logger.info("LINE通知設定更新APIが成功", {
                "status": updated_config.status
            })

            return updated_config

        except ValueError as e:
            # バリデーションエラー
            logger.warning("LINE通知設定更新APIでバリデーションエラー", {
                "error": str(e)
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "入力データが不正です",
                    "error": str(e)
                }
            )

        except Exception as e:
            logger.error("LINE通知設定更新APIでエラーが発生", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "LINE通知設定の更新に失敗しました",
                    "error": str(e)
                }
            )


@router.post(
    "/line/test",
    response_model=LineNotificationTestResponse,
    summary="LINE通知テスト送信",
    description="LINE通知のテストメッセージを送信します。"
)
async def test_line_notification():
    """
    LINE通知テスト送信エンドポイント

    Returns:
        LineNotificationTestResponse: テスト送信結果

    Raises:
        HTTPException: テスト送信に失敗した場合
    """
    with transaction_scope("POST /api/notifications/line/test"):
        try:
            logger.info("LINE通知テスト送信APIが呼ばれました")

            service = NotificationConfigService()
            success = await service.test_line_notification()

            from datetime import datetime

            if success:
                logger.info("LINE通知テスト送信APIが成功")
                return LineNotificationTestResponse(
                    success=True,
                    message="LINE通知テスト送信成功",
                    sent_at=datetime.now().isoformat() + 'Z'
                )
            else:
                logger.warning("LINE通知テスト送信APIが失敗")
                return LineNotificationTestResponse(
                    success=False,
                    message="LINE通知テスト送信失敗。トークンが未設定または無効です。",
                    sent_at=None
                )

        except Exception as e:
            logger.error("LINE通知テスト送信APIでエラーが発生", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "LINE通知テスト送信に失敗しました",
                    "error": str(e)
                }
            )
