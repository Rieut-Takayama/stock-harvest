"""
売買支援関連データモデル
Stock Harvest AI プロジェクト用
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from decimal import Decimal


# エントリーポイント最適化関連モデル
class EntryOptimizationRequest(BaseModel):
    """エントリーポイント最適化リクエスト"""
    stock_code: str = Field(..., description="銘柄コード", pattern="^[0-9]{4}$")
    current_price: Decimal = Field(..., description="現在価格", gt=0)
    logic_type: Optional[str] = Field("manual", description="ロジック種別")
    investment_amount: Optional[Decimal] = Field(None, description="投資金額", gt=0)
    risk_tolerance: str = Field("medium", description="リスク許容度", pattern="^(low|medium|high)$")
    timeframe: str = Field("1m", description="投資期間", pattern="^(1w|1m|3m|6m)$")
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="市場状況")

    @field_validator('stock_code')
    @classmethod
    def validate_stock_code(cls, v: str) -> str:
        if not v or len(v) != 4 or not v.isdigit():
            raise ValueError("銘柄コードは4桁の数字である必要があります")
        return v


class EntryOptimizationResponse(BaseModel):
    """エントリーポイント最適化レスポンス"""
    success: bool = True
    stock_code: str
    stock_name: str
    current_price: Decimal
    optimal_entry_price: Decimal
    optimal_entry_price_range: Dict[str, Decimal]  # {"min": price, "max": price}
    target_profit_price: Decimal
    stop_loss_price: Decimal
    risk_reward_ratio: Decimal
    expected_return: Decimal  # 期待リターン（%）
    confidence_level: str  # "high", "medium", "low"
    position_size_recommendation: Dict[str, Any]  # {"shares": int, "investment_amount": Decimal}
    market_timing_score: int  # 1-100のスコア
    analysis_factors: Dict[str, Any]  # 分析要因の詳細
    recommended_order_type: str  # "market", "limit", "stop"
    execution_notes: List[str]  # 実行時の注意事項
    historical_performance: Optional[Dict[str, Any]] = None  # 過去の類似パターンの成績
    created_at: datetime = Field(default_factory=datetime.now)


# IFDOCO注文ガイド関連モデル
class IfdocoGuideRequest(BaseModel):
    """IFDOCO注文ガイドリクエスト"""
    stock_code: str = Field(..., description="銘柄コード", pattern="^[0-9]{4}$")
    entry_price: Decimal = Field(..., description="エントリー価格", gt=0)
    investment_amount: Decimal = Field(..., description="投資金額", gt=0)
    logic_type: Optional[str] = Field("manual", description="ロジック種別")
    risk_level: str = Field("medium", description="リスクレベル", pattern="^(conservative|medium|aggressive)$")
    holding_period: str = Field("1m", description="保有期間予定", pattern="^(1w|1m|3m|6m)$")

    @field_validator('stock_code')
    @classmethod
    def validate_stock_code(cls, v: str) -> str:
        if not v or len(v) != 4 or not v.isdigit():
            raise ValueError("銘柄コードは4桁の数字である必要があります")
        return v

    @field_validator('investment_amount')
    @classmethod
    def validate_investment_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("投資金額は0より大きい値である必要があります")
        return v


class IfdocoOrderSettings(BaseModel):
    """IFDOCO注文設定"""
    entry_order: Dict[str, Any]  # {"type": "limit", "price": Decimal, "quantity": int}
    profit_target_order: Dict[str, Any]  # {"type": "limit", "price": Decimal, "trigger_condition": str}
    stop_loss_order: Dict[str, Any]  # {"type": "stop", "price": Decimal, "trigger_condition": str}
    order_validity: str  # "day", "week", "month"
    execution_priority: str  # "profit_first", "loss_first", "simultaneous"


class IfdocoGuideResponse(BaseModel):
    """IFDOCO注文ガイドレスポンス"""
    success: bool = True
    stock_code: str
    stock_name: str
    entry_price: Decimal
    investment_amount: Decimal
    recommended_quantity: int
    order_settings: IfdocoOrderSettings
    step_by_step_guide: List[Dict[str, Any]]  # ステップバイステップ手順
    risk_analysis: Dict[str, Any]  # リスク分析結果
    expected_scenarios: Dict[str, Any]  # 想定シナリオ（最良・標準・最悪）
    broker_specific_notes: Dict[str, List[str]]  # 証券会社別注意事項
    monitoring_points: List[str]  # 監視ポイント
    exit_strategy: Dict[str, Any]  # 出口戦略
    created_at: datetime = Field(default_factory=datetime.now)


# 履歴管理関連モデル
class TradingHistoryFilter(BaseModel):
    """売買履歴フィルタ"""
    stock_code: Optional[str] = Field(None, description="銘柄コード")
    logic_type: Optional[str] = Field(None, description="ロジック種別")
    trade_type: Optional[str] = Field(None, description="取引種別", pattern="^(BUY|SELL)$")
    status: Optional[str] = Field(None, description="ステータス", pattern="^(open|closed|cancelled)$")
    date_from: Optional[datetime] = Field(None, description="開始日")
    date_to: Optional[datetime] = Field(None, description="終了日")
    min_profit_loss: Optional[Decimal] = Field(None, description="最小損益")
    max_profit_loss: Optional[Decimal] = Field(None, description="最大損益")
    page: int = Field(1, description="ページ番号", ge=1)
    limit: int = Field(20, description="取得件数", ge=1, le=100)


class TradingHistorySummary(BaseModel):
    """売買履歴サマリー"""
    total_trades: int
    open_positions: int
    closed_positions: int
    total_profit_loss: Decimal
    total_profit_loss_rate: Decimal
    win_rate: Decimal  # 勝率（%）
    average_profit: Decimal
    average_loss: Decimal
    max_profit: Decimal
    max_loss: Decimal
    profit_factor: Decimal  # プロフィットファクター
    average_holding_period: Decimal  # 平均保有期間（日）


class TradingHistoryResponse(BaseModel):
    """売買履歴レスポンス"""
    success: bool = True
    trades: List[Dict[str, Any]]  # 売買履歴リスト
    summary: TradingHistorySummary
    total: int
    page: int
    limit: int
    has_next: bool


class SignalHistoryFilter(BaseModel):
    """シグナル履歴フィルタ"""
    stock_code: Optional[str] = Field(None, description="銘柄コード")
    signal_type: Optional[str] = Field(None, description="シグナル種別")
    status: Optional[str] = Field(None, description="ステータス")
    confidence_min: Optional[Decimal] = Field(None, description="最小信頼度", ge=0, le=1)
    date_from: Optional[datetime] = Field(None, description="開始日")
    date_to: Optional[datetime] = Field(None, description="終了日")
    page: int = Field(1, description="ページ番号", ge=1)
    limit: int = Field(20, description="取得件数", ge=1, le=100)


class SignalHistorySummary(BaseModel):
    """シグナル履歴サマリー"""
    total_signals: int
    executed_signals: int
    pending_signals: int
    cancelled_signals: int
    signal_accuracy: Decimal  # シグナル精度（%）
    average_confidence: Decimal  # 平均信頼度
    profitable_signals: int
    loss_signals: int
    neutral_signals: int


class SignalHistoryResponse(BaseModel):
    """シグナル履歴レスポンス"""
    success: bool = True
    signals: List[Dict[str, Any]]  # シグナル履歴リスト
    summary: SignalHistorySummary
    total: int
    page: int
    limit: int
    has_next: bool


# パフォーマンス分析関連モデル
class PerformanceAnalysisRequest(BaseModel):
    """パフォーマンス分析リクエスト"""
    analysis_period: str = Field("3m", description="分析期間", pattern="^(1m|3m|6m|1y|all)$")
    logic_type: Optional[str] = Field(None, description="ロジック種別")
    benchmark: str = Field("nikkei225", description="ベンチマーク", pattern="^(nikkei225|topix|sp500)$")
    include_open_positions: bool = Field(True, description="未決済ポジション含む")


class PerformanceMetrics(BaseModel):
    """パフォーマンス指標"""
    total_return: Decimal  # 総リターン（%）
    annualized_return: Decimal  # 年率リターン（%）
    volatility: Decimal  # ボラティリティ（%）
    sharpe_ratio: Decimal  # シャープレシオ
    max_drawdown: Decimal  # 最大ドローダウン（%）
    win_rate: Decimal  # 勝率（%）
    profit_factor: Decimal  # プロフィットファクター
    calmar_ratio: Decimal  # カルマーレシオ
    beta: Optional[Decimal] = None  # ベータ（ベンチマーク対比）
    alpha: Optional[Decimal] = None  # アルファ（超過リターン）


class PerformanceAnalysisResponse(BaseModel):
    """パフォーマンス分析レスポンス"""
    success: bool = True
    analysis_period: str
    total_trades: int
    performance_metrics: PerformanceMetrics
    monthly_returns: List[Dict[str, Any]]  # 月次リターン
    drawdown_analysis: Dict[str, Any]  # ドローダウン分析
    trade_distribution: Dict[str, Any]  # 取引分布
    logic_performance_comparison: Dict[str, PerformanceMetrics]  # ロジック別パフォーマンス
    benchmark_comparison: Dict[str, Any]  # ベンチマーク比較
    improvement_suggestions: List[str]  # 改善提案
    risk_analysis: Dict[str, Any]  # リスク分析
    created_at: datetime = Field(default_factory=datetime.now)


# 共通レスポンスモデル
class TradingApiResponse(BaseModel):
    """売買支援API共通レスポンス"""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# エラーレスポンスモデル
class TradingApiError(BaseModel):
    """売買支援APIエラーレスポンス"""
    success: bool = False
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)