"""
Discord通知設定モデル定義
Stock Harvest AI - Discord通知機能
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator, Field
from enum import Enum


class NotificationFormat(str, Enum):
    """通知フォーマット形式"""
    STANDARD = "standard"
    COMPACT = "compact"
    DETAILED = "detailed"


class ConnectionStatus(str, Enum):
    """接続ステータス"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class DiscordConfigModel(BaseModel):
    """Discord通知設定モデル"""
    id: Optional[int] = None
    webhookUrl: Optional[str] = None
    isEnabled: bool = True
    channelName: Optional[str] = None
    serverName: Optional[str] = None
    notificationTypes: List[str] = Field(default_factory=list)
    mentionRole: Optional[str] = None
    notificationFormat: NotificationFormat = NotificationFormat.STANDARD
    rateLimitPerHour: int = 60  # デフォルト: 1時間に60通知まで
    lastNotificationAt: Optional[datetime] = None
    notificationCountToday: int = 0
    totalNotificationsSent: int = 0
    errorCount: int = 0
    lastErrorMessage: Optional[str] = None
    lastErrorAt: Optional[datetime] = None
    connectionStatus: ConnectionStatus = ConnectionStatus.DISCONNECTED
    webhookTestResult: Optional[Dict[str, Any]] = None
    customMessageTemplate: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    @validator('webhookUrl')
    def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
        """WebhookURLのバリデーション"""
        if v is None:
            return v
        if not v.startswith('https://discord.com/api/webhooks/'):
            raise ValueError('有効なDiscord Webhook URLを入力してください')
        return v

    @validator('rateLimitPerHour')
    def validate_rate_limit(cls, v: int) -> int:
        """レート制限のバリデーション"""
        if v < 1 or v > 1000:
            raise ValueError('レート制限は1〜1000の範囲で設定してください')
        return v

    @validator('notificationTypes')
    def validate_notification_types(cls, v: List[str]) -> List[str]:
        """通知タイプのバリデーション"""
        allowed_types = [
            'logic_a_match',
            'logic_b_match',
            'price_alert',
            'scan_complete',
            'system_error'
        ]
        for notification_type in v:
            if notification_type not in allowed_types:
                raise ValueError(f'無効な通知タイプ: {notification_type}')
        return v

    class Config:
        """Pydantic設定"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DiscordConfigCreateRequest(BaseModel):
    """Discord設定作成リクエスト"""
    webhookUrl: str
    channelName: str
    serverName: str
    notificationTypes: List[str] = Field(default_factory=lambda: ['logic_a_match', 'logic_b_match'])
    mentionRole: Optional[str] = None
    notificationFormat: NotificationFormat = NotificationFormat.STANDARD
    customMessageTemplate: Optional[str] = None

    @validator('webhookUrl')
    def validate_webhook_url(cls, v: str) -> str:
        """WebhookURLのバリデーション"""
        if not v.startswith('https://discord.com/api/webhooks/'):
            raise ValueError('有効なDiscord Webhook URLを入力してください')
        return v

    @validator('channelName', 'serverName')
    def validate_names(cls, v: str) -> str:
        """名前のバリデーション"""
        if not v or len(v.strip()) == 0:
            raise ValueError('チャンネル名・サーバー名は必須です')
        return v.strip()


class DiscordConfigUpdateRequest(BaseModel):
    """Discord設定更新リクエスト"""
    webhookUrl: Optional[str] = None
    isEnabled: Optional[bool] = None
    channelName: Optional[str] = None
    serverName: Optional[str] = None
    notificationTypes: Optional[List[str]] = None
    mentionRole: Optional[str] = None
    notificationFormat: Optional[NotificationFormat] = None
    customMessageTemplate: Optional[str] = None

    @validator('webhookUrl')
    def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
        """WebhookURLのバリデーション"""
        if v is not None and not v.startswith('https://discord.com/api/webhooks/'):
            raise ValueError('有効なDiscord Webhook URLを入力してください')
        return v


class DiscordNotificationMessage(BaseModel):
    """Discord通知メッセージ"""
    stockCode: str
    stockName: str
    logicType: str
    price: float
    changeRate: float
    volume: int
    detectionTime: datetime
    additionalInfo: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DiscordWebhookTestResult(BaseModel):
    """Webhook接続テスト結果"""
    success: bool
    message: str
    responseStatus: Optional[int] = None
    responseData: Optional[Dict[str, Any]] = None
    errorDetail: Optional[str] = None
    testedAt: datetime

    class Config:
        """Pydantic設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DiscordNotificationHistory(BaseModel):
    """Discord通知履歴"""
    id: Optional[int] = None
    configId: int
    notificationType: str
    stockCode: Optional[str] = None
    messageContent: str
    success: bool
    responseStatus: Optional[int] = None
    errorMessage: Optional[str] = None
    sentAt: datetime
    retryCount: int = 0

    class Config:
        """Pydantic設定"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DiscordRateLimit(BaseModel):
    """Discord レート制限管理"""
    hourlyLimit: int
    currentHourlyCount: int
    dailyLimit: int = 1440  # デフォルト: 1日1440通知 (1分1通知)
    currentDailyCount: int
    lastResetHour: datetime
    lastResetDay: datetime
    isRateLimited: bool

    class Config:
        """Pydantic設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }