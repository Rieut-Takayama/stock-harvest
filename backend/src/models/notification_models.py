"""
通知設定モデル定義
LINE Notify設定情報のデータモデル
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LineNotificationConfig(BaseModel):
    """LINE通知設定情報モデル"""

    is_connected: bool = Field(
        ...,
        description="LINE連携状態（True: 連携済み, False: 未連携）"
    )
    token: str = Field(
        ...,
        description="LINEトークン（マスキング済み）",
        examples=["abcd***masked***", ""]
    )
    status: str = Field(
        ...,
        description="接続ステータス（connected, disconnected, error）"
    )
    last_notification: Optional[str] = Field(
        None,
        description="最後の通知送信日時（ISO 8601形式）",
        examples=["2025-11-07T09:30:00Z"]
    )
    notification_count: Optional[int] = Field(
        None,
        description="通知送信回数"
    )
    error_count: Optional[int] = Field(
        None,
        description="エラー発生回数"
    )
    last_error_message: Optional[str] = Field(
        None,
        description="最後のエラーメッセージ"
    )

    class Config:
        """Pydantic設定"""
        json_schema_extra = {
            "example": {
                "is_connected": True,
                "token": "abcd***masked***",
                "status": "connected",
                "last_notification": "2025-11-07T09:30:00Z",
                "notification_count": 42,
                "error_count": 0,
                "last_error_message": None
            }
        }


class LineNotificationConfigUpdate(BaseModel):
    """LINE通知設定更新リクエストモデル"""

    token: Optional[str] = Field(
        None,
        description="新しいLINEトークン",
        min_length=1
    )
    is_connected: Optional[bool] = Field(
        None,
        description="LINE連携状態の更新"
    )

    class Config:
        """Pydantic設定"""
        json_schema_extra = {
            "example": {
                "token": "your-line-notify-token-here",
                "is_connected": True
            }
        }


class LineNotificationTestResponse(BaseModel):
    """LINE通知テストレスポンスモデル"""

    success: bool = Field(
        ...,
        description="テスト送信成功フラグ"
    )
    message: str = Field(
        ...,
        description="テスト結果メッセージ"
    )
    sent_at: Optional[str] = Field(
        None,
        description="送信日時（ISO 8601形式）"
    )

    class Config:
        """Pydantic設定"""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "LINE通知テスト送信成功",
                "sent_at": "2025-11-07T10:00:00Z"
            }
        }
