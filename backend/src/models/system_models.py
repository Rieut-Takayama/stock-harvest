"""
システム関連のデータモデル定義
Pydanticモデルを使用して型安全性を確保
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, Literal
from datetime import datetime


class SystemInfoModel(BaseModel):
    """
    システム情報のモデル
    """
    version: str = Field(..., description="システムバージョン", example="v1.0.0")
    status: Literal['healthy', 'degraded', 'down'] = Field(..., description="システムステータス")
    lastScanAt: str = Field(..., description="最後のスキャン実行時刻", example="2025-12-13T10:30:00Z")
    activeAlerts: int = Field(..., ge=0, description="アクティブなアラート数")
    totalUsers: int = Field(..., ge=0, description="総ユーザー数")
    databaseStatus: Literal['connected', 'disconnected'] = Field(..., description="データベース接続状態")
    lastUpdated: str = Field(..., description="最後の更新時刻", example="2025-12-13T10:30:00Z") 
    statusDisplay: str = Field(..., description="ステータスの日本語表示", example="正常稼働中")
    
    @field_validator('version')
    def validate_version(cls, v):
        """バージョン形式のバリデーション"""
        if not v.startswith('v'):
            raise ValueError('バージョンは "v" で開始する必要があります')
        return v
    
    @field_validator('lastScanAt', 'lastUpdated')
    def validate_datetime_format(cls, v):
        """日時形式のバリデーション"""
        if v == "未実行":
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('ISO 8601形式の日時である必要があります')
        return v
    
    class Config:
        """Pydanticの設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "version": "v1.0.0",
                "status": "healthy",
                "last_scan_at": "2025-12-13T10:30:00Z",
                "active_alerts": 5,
                "total_users": 1,
                "database_status": "connected",
                "last_updated": "2025-12-13T10:30:00Z",
                "status_display": "正常稼働中"
            }
        }


class HealthCheckItem(BaseModel):
    """
    ヘルスチェック項目のモデル
    """
    status: Literal['pass', 'fail'] = Field(..., description="チェック結果")
    message: str = Field(..., description="チェック結果メッセージ")
    response_time: Optional[float] = Field(None, ge=0, description="レスポンス時間(ms)")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "pass",
                "message": "データベース接続正常",
                "response_time": 12.5
            }
        }


class HealthCheckModel(BaseModel):
    """
    ヘルスチェック結果のモデル
    """
    healthy: bool = Field(..., description="全体的な健全性")
    checks: Dict[str, HealthCheckItem] = Field(..., description="個別チェック結果")
    timestamp: str = Field(..., description="チェック実行時刻")
    status: Literal['healthy', 'unhealthy'] = Field(..., description="ステータス")
    message: Optional[str] = Field(None, description="メッセージ")
    severity: Optional[Literal['info', 'warning', 'error']] = Field(None, description="重要度")
    
    @field_validator('timestamp')
    def validate_timestamp(cls, v):
        """タイムスタンプのバリデーション"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('ISO 8601形式のタイムスタンプである必要があります')
        return v
    
    @field_validator('checks')
    def validate_checks_not_empty(cls, v):
        """チェック項目が空でないことを確認"""
        if not v:
            raise ValueError('少なくとも一つのヘルスチェック項目が必要です')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "healthy": True,
                "checks": {
                    "database": {
                        "status": "pass",
                        "message": "データベース接続正常",
                        "response_time": 12.5
                    },
                    "system_data": {
                        "status": "pass", 
                        "message": "システムデータ取得正常",
                        "response_time": 8.2
                    }
                },
                "timestamp": "2025-12-13T10:30:00Z",
                "status": "healthy",
                "message": "すべてのサービスが正常に動作しています",
                "severity": "info"
            }
        }


class HealthCheckResponse(BaseModel):
    """
    ヘルスチェックAPIレスポンスのモデル
    """
    healthy: bool = Field(..., description="全体的な健全性")
    status: Literal['healthy', 'unhealthy'] = Field(..., description="ステータス")
    message: str = Field(..., description="メッセージ")
    checks: Dict[str, HealthCheckItem] = Field(..., description="個別チェック結果")
    timestamp: str = Field(..., description="チェック実行時刻")
    severity: Optional[Literal['info', 'warning', 'error']] = Field(None, description="重要度")
    error: Optional[str] = Field(None, description="エラー情報")
    
    class Config:
        schema_extra = {
            "example": {
                "healthy": True,
                "status": "healthy",
                "message": "すべてのサービスが正常に動作しています",
                "checks": {
                    "database": {
                        "status": "pass",
                        "message": "データベース接続正常"
                    }
                },
                "timestamp": "2025-12-13T10:30:00Z",
                "severity": "info"
            }
        }


class SystemStatusUpdateModel(BaseModel):
    """
    システムステータス更新リクエストのモデル
    """
    status: Literal['healthy', 'degraded', 'down'] = Field(..., description="新しいステータス")
    status_display: Optional[str] = Field(None, description="ステータス表示テキスト")
    message: Optional[str] = Field(None, description="更新理由・メッセージ")
    
    @field_validator('status_display')
    def validate_status_display_length(cls, v):
        """ステータス表示の長さをチェック"""
        if v and len(v) > 100:
            raise ValueError('ステータス表示は100文字以下である必要があります')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "status": "degraded",
                "status_display": "一部機能制限中",
                "message": "外部API接続に遅延が発生しています"
            }
        }