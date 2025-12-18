"""
Charts Models - チャートデータ関連モデル
Pydanticモデルによる型安全なデータ構造定義
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from enum import Enum


class TimeframeEnum(str, Enum):
    """タイムフレーム列挙型"""
    ONE_DAY = "1d"
    ONE_WEEK = "1w" 
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"


class PeriodEnum(str, Enum):
    """期間列挙型"""
    FIVE_DAYS = "5d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"


class TechnicalIndicatorEnum(str, Enum):
    """テクニカル指標列挙型"""
    SMA = "sma"
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER = "bollinger"


class ChartOHLCDataModel(BaseModel):
    """OHLCデータモデル"""
    date: str = Field(..., description="日付 (YYYY-MM-DD形式)")
    timestamp: int = Field(..., description="タイムスタンプ (ミリ秒)")
    open: float = Field(..., ge=0, description="始値")
    high: float = Field(..., ge=0, description="高値")
    low: float = Field(..., ge=0, description="安値")
    close: float = Field(..., ge=0, description="終値")
    volume: int = Field(..., ge=0, description="出来高")

    @model_validator(mode='after')
    def validate_ohlc_consistency(self) -> 'ChartOHLCDataModel':
        """OHLC価格の整合性を検証"""
        open_price = self.open
        high_price = self.high
        low_price = self.low
        close_price = self.close
        
        # 高値が全価格の最高値であることを確認
        if high_price < max(open_price, low_price, close_price):
            raise ValueError('高値は始値、安値、終値以上である必要があります')
        
        # 安値が全価格の最安値であることを確認
        if low_price > min(open_price, high_price, close_price):
            raise ValueError('安値は始値、高値、終値以下である必要があります')
        
        return self


class ChartCurrentPriceModel(BaseModel):
    """現在価格モデル"""
    price: float = Field(..., ge=0, description="現在価格")
    change: float = Field(..., description="価格変動額")
    changeRate: float = Field(..., description="変動率 (%)")
    volume: int = Field(..., ge=0, description="出来高")


class ChartPriceRangeModel(BaseModel):
    """価格レンジモデル"""
    min: float = Field(..., ge=0, description="最安値")
    max: float = Field(..., ge=0, description="最高値")
    period: str = Field(..., description="期間")

    @model_validator(mode='after')
    def validate_price_range(self) -> 'ChartPriceRangeModel':
        """価格レンジの整合性を検証"""
        if self.max < self.min:
            raise ValueError('最高値は最安値より大きい必要があります')
        return self


class ChartDataRequestModel(BaseModel):
    """チャートデータリクエストモデル"""
    stock_code: str = Field(..., pattern=r'^\d{4}$', description="銘柄コード (4桁)")
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.ONE_DAY, description="タイムフレーム")
    period: PeriodEnum = Field(default=PeriodEnum.THIRTY_DAYS, description="期間")
    indicators: Optional[List[TechnicalIndicatorEnum]] = Field(default=[], description="テクニカル指標")

    @field_validator('stock_code')
    @classmethod
    def validate_stock_code(cls, v: str) -> str:
        """銘柄コード検証"""
        if not v.isdigit():
            raise ValueError('銘柄コードは数字のみで構成される必要があります')
        if len(v) != 4:
            raise ValueError('銘柄コードは4桁である必要があります')
        return v


class ChartDataModel(BaseModel):
    """チャートデータレスポンスモデル"""
    success: bool = Field(..., description="成功フラグ")
    stockCode: str = Field(..., description="銘柄コード")
    symbol: str = Field(..., description="Yahoo Financeシンボル")
    stockName: str = Field(..., description="銘柄名")
    timeframe: str = Field(..., description="タイムフレーム")
    period: str = Field(..., description="期間")
    dataCount: int = Field(..., ge=0, description="データ件数")
    lastUpdated: str = Field(..., description="最終更新日時 (ISO形式)")
    ohlcData: List[ChartOHLCDataModel] = Field(..., description="OHLCデータ")
    technicalIndicators: Dict[str, Union[List[float], Dict[str, List[float]]]] = Field(
        default={}, description="テクニカル指標データ"
    )
    currentPrice: ChartCurrentPriceModel = Field(..., description="現在価格情報")
    priceRange: ChartPriceRangeModel = Field(..., description="価格レンジ情報")
    message: Optional[str] = Field(default=None, description="メッセージ")

    @field_validator('lastUpdated')
    @classmethod
    def validate_last_updated(cls, v: str) -> str:
        """日時形式検証"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('lastUpdatedはISO形式の日時文字列である必要があります')


class ChartHealthCheckModel(BaseModel):
    """チャート機能ヘルスチェックモデル"""
    status: str = Field(..., description="ステータス")
    service: str = Field(default="charts", description="サービス名")
    timestamp: str = Field(..., description="チェック実行時刻")
    details: Dict[str, Any] = Field(..., description="詳細情報")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "service": "charts",
                "timestamp": "2025-12-14T10:30:00.000Z",
                "details": {
                    "yfinance": "available",
                    "testSymbol": "7203.T",
                    "testDataPoints": 30,
                    "lastCheck": "2025-12-14T10:30:00.000Z"
                }
            }
        }
    }


class TechnicalIndicatorResultModel(BaseModel):
    """テクニカル指標結果モデル"""
    indicator_name: TechnicalIndicatorEnum = Field(..., description="指標名")
    data: Union[List[float], Dict[str, List[float]]] = Field(..., description="指標データ")
    calculation_params: Optional[Dict[str, Any]] = Field(default={}, description="計算パラメータ")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "indicator_name": "sma",
                "data": [100.5, 101.2, 102.0, 103.1, 104.5],
                "calculation_params": {"period": 20}
            }
        }
    }