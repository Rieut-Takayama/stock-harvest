"""
通知設定サービス
LINE Notify設定のビジネスロジック層
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime

from ..lib.logger import logger, track_performance
from ..repositories.notification_repository import NotificationRepository
from ..validators.notification_validators import mask_token
from ..models.notification_models import LineNotificationConfig


class NotificationConfigService:
    """通知設定サービス"""

    def __init__(self):
        """コンストラクタ"""
        self.repository = NotificationRepository()

    async def get_line_config(self) -> LineNotificationConfig:
        """
        LINE通知設定を取得（トークンはマスキング済み）

        Returns:
            LineNotificationConfig: LINE通知設定
        """
        with track_performance("get_line_config"):
            try:
                logger.info("LINE通知設定取得を開始")

                # データベースから設定を取得
                config_data = await self.repository.get_line_config()

                # 設定が存在しない場合はデフォルト設定を作成
                if not config_data:
                    logger.info("LINE通知設定が存在しないため、デフォルト設定を作成")
                    config_data = await self.repository.create_default_line_config()

                # 環境変数のLINE_NOTIFY_TOKENを参照
                env_token = os.getenv('LINE_NOTIFY_TOKEN', '')

                # トークンの決定（優先順位: DB > 環境変数）
                actual_token = config_data.get('token', '') or env_token

                # トークンの存在確認とマスキング
                masked_token = mask_token(actual_token, show_chars=4)
                is_token_configured = bool(actual_token and actual_token.strip())

                # 接続状態の判定
                is_connected = is_token_configured and config_data.get('is_connected', False)
                status = self._determine_status(is_token_configured, config_data)

                # 最後の通知送信日時をISO形式に変換
                last_notification = None
                if config_data.get('last_notification_at'):
                    last_notification_dt = config_data['last_notification_at']
                    if isinstance(last_notification_dt, datetime):
                        last_notification = last_notification_dt.isoformat() + 'Z'
                    else:
                        last_notification = str(last_notification_dt)

                # レスポンスモデルを作成
                response = LineNotificationConfig(
                    is_connected=is_connected,
                    token=masked_token,
                    status=status,
                    last_notification=last_notification,
                    notification_count=config_data.get('notification_count', 0),
                    error_count=config_data.get('error_count', 0),
                    last_error_message=config_data.get('last_error_message')
                )

                logger.info("LINE通知設定取得完了", {
                    "is_connected": is_connected,
                    "status": status,
                    "token_configured": is_token_configured,
                    "notification_count": response.notification_count
                })

                return response

            except Exception as e:
                logger.error("LINE通知設定の取得に失敗", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise

    def _determine_status(
        self,
        is_token_configured: bool,
        config_data: Dict[str, Any]
    ) -> str:
        """
        接続ステータスを判定

        Args:
            is_token_configured: トークンが設定されているか
            config_data: 設定データ

        Returns:
            str: ステータス（connected, disconnected, error）
        """
        # トークンが未設定の場合は disconnected
        if not is_token_configured:
            return "disconnected"

        # エラーが記録されている場合は error
        if config_data.get('error_count', 0) > 0:
            return "error"

        # is_connectedがTrueの場合は connected
        if config_data.get('is_connected', False):
            return "connected"

        # デフォルトは disconnected
        return "disconnected"

    async def update_line_config(
        self,
        token: Optional[str] = None,
        is_connected: Optional[bool] = None
    ) -> LineNotificationConfig:
        """
        LINE通知設定を更新

        Args:
            token: 新しいLINEトークン
            is_connected: 連携状態

        Returns:
            LineNotificationConfig: 更新後のLINE通知設定（トークンはマスキング済み）
        """
        with track_performance("update_line_config"):
            try:
                logger.info("LINE通知設定更新を開始", {
                    "token_update": token is not None,
                    "is_connected_update": is_connected is not None
                })

                # ステータスの決定
                status = None
                if token is not None and is_connected is not None:
                    status = "connected" if is_connected else "disconnected"
                elif token is not None:
                    # トークンのみ更新の場合は検証が必要
                    status = "disconnected"  # 検証前は disconnected
                elif is_connected is not None:
                    # 連携状態のみ更新
                    status = "connected" if is_connected else "disconnected"

                # リポジトリ層で更新
                await self.repository.update_line_config(
                    token=token,
                    is_connected=is_connected,
                    status=status
                )

                logger.info("LINE通知設定更新完了", {
                    "status": status
                })

                # 更新後の設定を取得して返す
                return await self.get_line_config()

            except Exception as e:
                logger.error("LINE通知設定の更新に失敗", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise

    async def test_line_notification(self) -> bool:
        """
        LINE通知のテスト送信

        Returns:
            bool: 送信成功フラグ
        """
        with track_performance("test_line_notification"):
            try:
                logger.info("LINE通知テスト送信を開始")

                # 現在の設定を取得
                config = await self.get_line_config()

                if not config.is_connected:
                    logger.warning("LINE通知が未接続のためテスト送信をスキップ")
                    return False

                # NotificationServiceを使用してテスト送信
                from ..services.notification_service import NotificationService
                notification_service = NotificationService()
                success = await notification_service.test_notification()

                if success:
                    logger.info("LINE通知テスト送信成功")
                    await self.repository.increment_notification_count()
                else:
                    logger.warning("LINE通知テスト送信失敗")
                    await self.repository.increment_error_count("テスト送信失敗")

                return success

            except Exception as e:
                logger.error("LINE通知テスト送信に失敗", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                await self.repository.increment_error_count(str(e))
                return False
