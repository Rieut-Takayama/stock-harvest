"""
アラート関連のモデル定義
データ構造とバリデーションを担当
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Dict, Any
from datetime import datetime


class AlertCondition(BaseModel):
    """アラート条件"""
    # 価格到達アラートの場合
    targetPrice: Optional[float] = Field(None, description="目標価格")
    priceDirection: Optional[Literal['above', 'below']] = Field(None, description="価格方向")

    # ロジック発動アラートの場合
    logic: Optional[Literal['logic_a', 'logic_b']] = Field(None, description="ロジックタイプ")
    logicName: Optional[str] = Field(None, description="ロジック名")


class Alert(BaseModel):
    """アラート情報"""
    id: str
    stockCode: str
    stockName: str
    type: Literal['price', 'logic']
    condition: AlertCondition
    isActive: bool
    createdAt: str
    lineNotificationEnabled: bool


class AlertFormData(BaseModel):
    """アラート作成フォームデータ"""
    alertType: Literal['price', 'logic'] = Field(..., description="アラートタイプ")
    stockCode: str = Field(..., min_length=4, max_length=10, description="銘柄コード")
    targetPrice: Optional[float] = Field(None, gt=0, description="目標価格")

    @field_validator('stockCode')
    @classmethod
    def validate_stock_code(cls, v: str) -> str:
        """銘柄コードのバリデーション"""
        if not v.isdigit():
            raise ValueError('銘柄コードは数字のみ許可されます')
        return v

    @field_validator('alertType', 'targetPrice')
    @classmethod
    def validate_price_alert(cls, v: Any, info: Any) -> Any:
        """価格アラートの場合はtargetPriceが必須"""
        values = info.data
        if values.get('alertType') == 'price' and info.field_name == 'targetPrice' and v is None:
            raise ValueError('価格到達アラートの場合、目標価格は必須です')
        return v


class LineNotificationConfig(BaseModel):
    """LINE通知設定"""
    isConnected: bool
    token: Optional[str] = None
    status: Literal['connected', 'disconnected', 'error']
    lastNotificationAt: Optional[str] = None


class AlertCreateRequest(BaseModel):
    """アラート作成リクエスト（内部処理用）"""
    type: Literal['price', 'logic']
    stockCode: str
    stockName: str
    condition: Dict[str, Any]
    lineNotificationEnabled: bool = True

    @field_validator('stockCode')
    @classmethod
    def validate_stock_code(cls, v: str) -> str:
        """銘柄コードのバリデーション"""
        if not v or len(v) < 4:
            raise ValueError('銘柄コードは4文字以上必要です')
        return v
