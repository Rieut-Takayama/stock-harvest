"""
通知設定リポジトリ
LINE Notify設定のデータアクセス層
"""

from typing import Optional, Dict, Any
from datetime import datetime
from databases import Database

from ..lib.logger import logger
from ..database.config import get_db


class NotificationRepository:
    """通知設定リポジトリ"""

    def __init__(self, db: Optional[Database] = None):
        """
        コンストラクタ

        Args:
            db: データベース接続（テスト用）
        """
        self.db = db

    async def _get_db(self) -> Database:
        """
        データベース接続を取得

        Returns:
            Database: データベース接続オブジェクト
        """
        if self.db:
            return self.db
        return await get_db()

    async def get_line_config(self) -> Optional[Dict[str, Any]]:
        """
        LINE通知設定を取得

        Returns:
            Optional[Dict[str, Any]]: LINE通知設定（存在しない場合はNone）
        """
        try:
            db = await self._get_db()

            query = """
                SELECT
                    id,
                    is_connected,
                    token,
                    status,
                    last_notification_at,
                    notification_count,
                    error_count,
                    last_error_message,
                    created_at,
                    updated_at
                FROM line_notification_config
                ORDER BY id DESC
                LIMIT 1
            """

            result = await db.fetch_one(query)

            if result:
                logger.debug("LINE通知設定を取得", {
                    "config_id": result["id"],
                    "status": result["status"]
                })
                return dict(result)
            else:
                logger.debug("LINE通知設定が見つかりません（初期状態）")
                return None

        except Exception as e:
            logger.error("LINE通知設定の取得に失敗", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise

    async def create_default_line_config(self) -> Dict[str, Any]:
        """
        デフォルトのLINE通知設定を作成

        Returns:
            Dict[str, Any]: 作成されたLINE通知設定
        """
        try:
            db = await self._get_db()

            query = """
                INSERT INTO line_notification_config (
                    is_connected,
                    token,
                    status,
                    last_notification_at,
                    notification_count,
                    error_count,
                    last_error_message,
                    created_at,
                    updated_at
                ) VALUES (
                    :is_connected,
                    :token,
                    :status,
                    :last_notification_at,
                    :notification_count,
                    :error_count,
                    :last_error_message,
                    :created_at,
                    :updated_at
                )
            """

            values = {
                "is_connected": False,
                "token": "",
                "status": "disconnected",
                "last_notification_at": None,
                "notification_count": 0,
                "error_count": 0,
                "last_error_message": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            await db.execute(query, values)

            logger.info("デフォルトLINE通知設定を作成")

            # 作成した設定を取得して返す
            return await self.get_line_config()

        except Exception as e:
            logger.error("デフォルトLINE通知設定の作成に失敗", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise

    async def update_line_config(
        self,
        token: Optional[str] = None,
        is_connected: Optional[bool] = None,
        status: Optional[str] = None,
        last_notification_at: Optional[datetime] = None,
        notification_count: Optional[int] = None,
        error_count: Optional[int] = None,
        last_error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        LINE通知設定を更新

        Args:
            token: 新しいLINEトークン
            is_connected: 連携状態
            status: ステータス
            last_notification_at: 最後の通知送信日時
            notification_count: 通知送信回数
            error_count: エラー発生回数
            last_error_message: 最後のエラーメッセージ

        Returns:
            Dict[str, Any]: 更新されたLINE通知設定
        """
        try:
            db = await self._get_db()

            # 既存設定を取得
            existing_config = await self.get_line_config()

            if not existing_config:
                # 設定が存在しない場合はデフォルト設定を作成
                existing_config = await self.create_default_line_config()

            # 更新用の値を準備
            update_values = {
                "id": existing_config["id"],
                "updated_at": datetime.now()
            }

            # 指定されたフィールドのみ更新
            if token is not None:
                update_values["token"] = token
            else:
                update_values["token"] = existing_config["token"]

            if is_connected is not None:
                update_values["is_connected"] = is_connected
            else:
                update_values["is_connected"] = existing_config["is_connected"]

            if status is not None:
                update_values["status"] = status
            else:
                update_values["status"] = existing_config["status"]

            if last_notification_at is not None:
                update_values["last_notification_at"] = last_notification_at
            else:
                update_values["last_notification_at"] = existing_config["last_notification_at"]

            if notification_count is not None:
                update_values["notification_count"] = notification_count
            else:
                update_values["notification_count"] = existing_config["notification_count"]

            if error_count is not None:
                update_values["error_count"] = error_count
            else:
                update_values["error_count"] = existing_config["error_count"]

            if last_error_message is not None:
                update_values["last_error_message"] = last_error_message
            else:
                update_values["last_error_message"] = existing_config["last_error_message"]

            # 更新クエリ実行
            query = """
                UPDATE line_notification_config
                SET
                    is_connected = :is_connected,
                    token = :token,
                    status = :status,
                    last_notification_at = :last_notification_at,
                    notification_count = :notification_count,
                    error_count = :error_count,
                    last_error_message = :last_error_message,
                    updated_at = :updated_at
                WHERE id = :id
            """

            await db.execute(query, update_values)

            logger.info("LINE通知設定を更新", {
                "config_id": existing_config["id"],
                "token_updated": token is not None,
                "status": update_values["status"]
            })

            # 更新後の設定を取得して返す
            return await self.get_line_config()

        except Exception as e:
            logger.error("LINE通知設定の更新に失敗", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise

    async def increment_notification_count(self) -> None:
        """
        通知送信回数をインクリメント
        """
        try:
            db = await self._get_db()

            query = """
                UPDATE line_notification_config
                SET
                    notification_count = notification_count + 1,
                    last_notification_at = :last_notification_at,
                    updated_at = :updated_at
                WHERE id = (SELECT id FROM line_notification_config ORDER BY id DESC LIMIT 1)
            """

            values = {
                "last_notification_at": datetime.now(),
                "updated_at": datetime.now()
            }

            await db.execute(query, values)

            logger.debug("通知送信回数をインクリメント")

        except Exception as e:
            logger.error("通知送信回数のインクリメントに失敗", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise

    async def increment_error_count(self, error_message: str) -> None:
        """
        エラー発生回数をインクリメント

        Args:
            error_message: エラーメッセージ
        """
        try:
            db = await self._get_db()

            query = """
                UPDATE line_notification_config
                SET
                    error_count = error_count + 1,
                    last_error_message = :last_error_message,
                    updated_at = :updated_at
                WHERE id = (SELECT id FROM line_notification_config ORDER BY id DESC LIMIT 1)
            """

            values = {
                "last_error_message": error_message,
                "updated_at": datetime.now()
            }

            await db.execute(query, values)

            logger.debug("エラー発生回数をインクリメント", {
                "error_message": error_message[:100]  # ログには100文字まで
            })

        except Exception as e:
            logger.error("エラー発生回数のインクリメントに失敗", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
