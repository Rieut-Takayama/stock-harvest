"""
銘柄アーカイブモデル
Stock Harvest AI - 過去合致銘柄の履歴保存・管理
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ArchiveStockModel(BaseModel):
    """銘柄アーカイブエントリモデル"""
    id: str = Field(..., description="アーカイブID")
    stock_code: str = Field(..., min_length=4, max_length=10, description="銘柄コード")
    stock_name: str = Field(..., min_length=1, max_length=100, description="銘柄名")
    logic_type: str = Field(..., description="検出ロジック")
    detection_date: datetime = Field(..., description="検出日時")
    scan_id: str = Field(..., description="スキャンID")
    price_at_detection: float = Field(..., gt=0, description="検出時価格")
    volume_at_detection: int = Field(..., ge=0, description="検出時出来高")
    market_cap_at_detection: Optional[float] = Field(None, ge=0, description="検出時時価総額")
    technical_signals_snapshot: Optional[Dict[str, Any]] = Field(None, description="検出時テクニカル指標")
    logic_specific_data: Optional[Dict[str, Any]] = Field(None, description="ロジック固有データ")
    performance_after_1d: Optional[float] = Field(None, description="1日後パフォーマンス(%)")
    performance_after_1w: Optional[float] = Field(None, description="1週間後パフォーマンス(%)")
    performance_after_1m: Optional[float] = Field(None, description="1ヶ月後パフォーマンス(%)")
    max_gain: Optional[float] = Field(None, description="最大利益(%)")
    max_loss: Optional[float] = Field(None, description="最大損失(%)")
    outcome_classification: Optional[str] = Field(None, description="結果分類")
    manual_score: Optional[ManualScoreValue] = Field(None, description="手動スコア")
    manual_score_reason: Optional[str] = Field(None, description="手動スコア理由")
    trade_execution: Optional[Dict[str, Any]] = Field(None, description="売買実行情報")
    lessons_learned: Optional[str] = Field(None, max_length=2000, description="学習事項・改善点")
    market_conditions_snapshot: Optional[Dict[str, Any]] = Field(None, description="市場状況スナップショット")
    follow_up_notes: Optional[str] = Field(None, max_length=1000, description="フォローアップメモ")
    archive_status: str = Field(default="active", description="アーカイブステータス")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    @validator('logic_type')
    def validate_logic_type(cls, v: str) -> str:
        """ロジックタイプのバリデーション"""
        allowed_types = ['logic_a', 'logic_b']
        if v not in allowed_types:
            raise ValueError(f'logic_type must be one of {allowed_types}')
        return v

    @validator('outcome_classification')
    def validate_outcome_classification(cls, v: Optional[str]) -> Optional[str]:
        """結果分類のバリデーション"""
        if v is None:
            return v
        allowed_values = ['success', 'failure', 'neutral', 'pending']
        if v not in allowed_values:
            raise ValueError(f'outcome_classification must be one of {allowed_values}')
        return v

    @validator('archive_status')
    def validate_archive_status(cls, v: str) -> str:
        """アーカイブステータスのバリデーション"""
        allowed_statuses = ['active', 'archived', 'deleted']
        if v not in allowed_statuses:
            raise ValueError(f'archive_status must be one of {allowed_statuses}')
        return v


class ArchiveSearchRequestModel(BaseModel):
    """アーカイブ検索リクエストモデル"""
    stock_code: Optional[str] = Field(None, min_length=4, max_length=10, description="銘柄コード")
    logic_type: Optional[str] = Field(None, description="検出ロジック")
    date_from: Optional[datetime] = Field(None, description="検索開始日")
    date_to: Optional[datetime] = Field(None, description="検索終了日")
    outcome_classification: Optional[str] = Field(None, description="結果分類")
    manual_score: Optional[ManualScoreValue] = Field(None, description="手動スコア")
    page: int = Field(default=1, ge=1, description="ページ番号")
    limit: int = Field(default=20, ge=1, le=100, description="1ページあたりの件数")

    @validator('logic_type')
    def validate_logic_type(cls, v: Optional[str]) -> Optional[str]:
        """ロジックタイプのバリデーション"""
        if v is None:
            return v
        allowed_types = ['logic_a', 'logic_b']
        if v not in allowed_types:
            raise ValueError(f'logic_type must be one of {allowed_types}')
        return v

    @validator('outcome_classification')
    def validate_outcome_classification(cls, v: Optional[str]) -> Optional[str]:
        """結果分類のバリデーション"""
        if v is None:
            return v
        allowed_values = ['success', 'failure', 'neutral', 'pending']
        if v not in allowed_values:
            raise ValueError(f'outcome_classification must be one of {allowed_values}')
        return v

    @validator('date_to')
    def validate_date_range(cls, v: Optional[datetime], values: dict) -> Optional[datetime]:
        """日付範囲のバリデーション"""
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if v < values['date_from']:
                raise ValueError('date_to must be later than date_from')
        return v


class ArchiveCreateRequestModel(BaseModel):
    """アーカイブ作成リクエストモデル"""
    stock_code: str = Field(..., min_length=4, max_length=10, description="銘柄コード")
    stock_name: str = Field(..., min_length=1, max_length=100, description="銘柄名")
    logic_type: str = Field(..., description="検出ロジック")
    scan_id: str = Field(..., description="スキャンID")
    price_at_detection: float = Field(..., gt=0, description="検出時価格")
    volume_at_detection: int = Field(..., ge=0, description="検出時出来高")
    market_cap_at_detection: Optional[float] = Field(None, ge=0, description="検出時時価総額")
    technical_signals_snapshot: Optional[Dict[str, Any]] = Field(None, description="検出時テクニカル指標")
    logic_specific_data: Optional[Dict[str, Any]] = Field(None, description="ロジック固有データ")
    manual_score: Optional[ManualScoreValue] = Field(None, description="手動スコア")
    manual_score_reason: Optional[str] = Field(None, description="手動スコア理由")
    lessons_learned: Optional[str] = Field(None, max_length=2000, description="学習事項・改善点")
    follow_up_notes: Optional[str] = Field(None, max_length=1000, description="フォローアップメモ")

    @validator('logic_type')
    def validate_logic_type(cls, v: str) -> str:
        """ロジックタイプのバリデーション"""
        allowed_types = ['logic_a', 'logic_b']
        if v not in allowed_types:
            raise ValueError(f'logic_type must be one of {allowed_types}')
        return v


class ArchiveUpdateRequestModel(BaseModel):
    """アーカイブ更新リクエストモデル"""
    performance_after_1d: Optional[float] = Field(None, description="1日後パフォーマンス(%)")
    performance_after_1w: Optional[float] = Field(None, description="1週間後パフォーマンス(%)")
    performance_after_1m: Optional[float] = Field(None, description="1ヶ月後パフォーマンス(%)")
    max_gain: Optional[float] = Field(None, description="最大利益(%)")
    max_loss: Optional[float] = Field(None, description="最大損失(%)")
    outcome_classification: Optional[str] = Field(None, description="結果分類")
    manual_score: Optional[ManualScoreValue] = Field(None, description="手動スコア")
    manual_score_reason: Optional[str] = Field(None, description="手動スコア理由")
    trade_execution: Optional[Dict[str, Any]] = Field(None, description="売買実行情報")
    lessons_learned: Optional[str] = Field(None, max_length=2000, description="学習事項・改善点")
    follow_up_notes: Optional[str] = Field(None, max_length=1000, description="フォローアップメモ")
    archive_status: Optional[str] = Field(None, description="アーカイブステータス")

    @validator('outcome_classification')
    def validate_outcome_classification(cls, v: Optional[str]) -> Optional[str]:
        """結果分類のバリデーション"""
        if v is None:
            return v
        allowed_values = ['success', 'failure', 'neutral', 'pending']
        if v not in allowed_values:
            raise ValueError(f'outcome_classification must be one of {allowed_values}')
        return v

    @validator('archive_status')
    def validate_archive_status(cls, v: Optional[str]) -> Optional[str]:
        """アーカイブステータスのバリデーション"""
        if v is None:
            return v
        allowed_statuses = ['active', 'archived', 'deleted']
        if v not in allowed_statuses:
            raise ValueError(f'archive_status must be one of {allowed_statuses}')
        return v


class ArchiveSearchResponseModel(BaseModel):
    """アーカイブ検索レスポンスモデル"""
    success: bool = Field(..., description="成功フラグ")
    archives: List[ArchiveStockModel] = Field(..., description="アーカイブ一覧")
    total: int = Field(..., ge=0, description="総件数")
    page: int = Field(..., ge=1, description="現在のページ")
    limit: int = Field(..., ge=1, description="1ページあたりの件数")
    has_next: bool = Field(..., description="次ページ有無")


class ArchivePerformanceStatsModel(BaseModel):
    """アーカイブパフォーマンス統計モデル"""
    total_archived: int = Field(..., ge=0, description="総アーカイブ件数")
    logic_a_count: int = Field(..., ge=0, description="ロジックA検出件数")
    logic_b_count: int = Field(..., ge=0, description="ロジックB検出件数")
    success_rate: float = Field(..., ge=0, le=100, description="成功率(%)")
    average_1d_performance: Optional[float] = Field(None, description="平均1日後パフォーマンス(%)")
    average_1w_performance: Optional[float] = Field(None, description="平均1週間後パフォーマンス(%)")
    average_1m_performance: Optional[float] = Field(None, description="平均1ヶ月後パフォーマンス(%)")
    best_performing_stock: Optional[Dict[str, Any]] = Field(None, description="最高パフォーマンス銘柄")
    worst_performing_stock: Optional[Dict[str, Any]] = Field(None, description="最低パフォーマンス銘柄")
    manual_score_distribution: Dict[str, int] = Field(..., description="手動スコア分布")


class ArchiveCSVExportRequestModel(BaseModel):
    """アーカイブCSV出力リクエストモデル"""
    search_params: ArchiveSearchRequestModel = Field(..., description="検索パラメータ")
    include_fields: List[str] = Field(default_factory=list, description="出力フィールド指定")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S", description="日付フォーマット")
    decimal_places: int = Field(default=2, ge=0, le=10, description="小数点以下桁数")

    @validator('include_fields')
    def validate_include_fields(cls, v: List[str]) -> List[str]:
        """出力フィールドのバリデーション"""
        allowed_fields = [
            'stock_code', 'stock_name', 'logic_type', 'detection_date',
            'price_at_detection', 'volume_at_detection', 'market_cap_at_detection',
            'performance_after_1d', 'performance_after_1w', 'performance_after_1m',
            'max_gain', 'max_loss', 'outcome_classification', 'manual_score',
            'manual_score_reason', 'lessons_learned', 'created_at'
        ]
        if v:  # 指定がある場合のみバリデーション
            invalid_fields = set(v) - set(allowed_fields)
            if invalid_fields:
                raise ValueError(f'Invalid fields: {invalid_fields}. Allowed fields: {allowed_fields}')
        return v