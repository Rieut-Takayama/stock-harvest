"""
手動スコア評価モデル
Stock Harvest AI - S,A+,A,B,C評価の保存・管理
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ManualScoreModel(BaseModel):
    """手動スコア評価モデル"""
    id: str = Field(..., description="スコアID")
    stock_code: str = Field(..., min_length=4, max_length=10, description="銘柄コード")
    stock_name: str = Field(..., min_length=1, max_length=100, description="銘柄名")
    score: ManualScoreValue = Field(..., description="手動スコア")
    logic_type: str = Field(..., description="対象ロジック")
    scan_result_id: Optional[str] = Field(None, description="関連スキャン結果ID")
    evaluation_reason: str = Field(..., min_length=1, description="評価理由")
    evaluated_by: str = Field(..., description="評価者")
    evaluated_at: datetime = Field(..., description="評価日時")
    confidence_level: Optional[str] = Field(None, description="確信度")
    price_at_evaluation: Optional[float] = Field(None, ge=0, description="評価時価格")
    market_context: Optional[Dict[str, Any]] = Field(None, description="評価時の市場状況")
    ai_score_before: Optional[ManualScoreValue] = Field(None, description="AI計算スコア（評価前）")
    ai_score_after: Optional[ManualScoreValue] = Field(None, description="AI計算スコア（評価後）")
    score_change_history: Optional[Dict[str, Any]] = Field(None, description="スコア変更履歴")
    follow_up_required: bool = Field(default=False, description="フォローアップ要否")
    follow_up_date: Optional[datetime] = Field(None, description="フォローアップ予定日")
    performance_validation: Optional[Dict[str, Any]] = Field(None, description="パフォーマンス検証結果")
    tags: Optional[List[str]] = Field(None, description="タグ")
    is_learning_case: bool = Field(default=False, description="学習事例フラグ")
    status: str = Field(default="active", description="ステータス")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    @validator('logic_type')
    def validate_logic_type(cls, v: str) -> str:
        """ロジックタイプのバリデーション"""
        allowed_types = ['logic_a', 'logic_b']
        if v not in allowed_types:
            raise ValueError(f'logic_type must be one of {allowed_types}')
        return v

    @validator('confidence_level')
    def validate_confidence_level(cls, v: Optional[str]) -> Optional[str]:
        """確信度のバリデーション"""
        if v is None:
            return v
        allowed_levels = ['high', 'medium', 'low']
        if v not in allowed_levels:
            raise ValueError(f'confidence_level must be one of {allowed_levels}')
        return v

    @validator('status')
    def validate_status(cls, v: str) -> str:
        """ステータスのバリデーション"""
        allowed_statuses = ['active', 'archived', 'superseded']
        if v not in allowed_statuses:
            raise ValueError(f'status must be one of {allowed_statuses}')
        return v


class ScoreEvaluationRequestModel(BaseModel):
    """スコア評価作成リクエストモデル"""
    stock_code: str = Field(..., min_length=4, max_length=10, description="銘柄コード")
    stock_name: str = Field(..., min_length=1, max_length=100, description="銘柄名")
    score: ManualScoreValue = Field(..., description="手動スコア")
    logic_type: str = Field(..., description="対象ロジック")
    scan_result_id: Optional[str] = Field(None, description="関連スキャン結果ID")
    evaluation_reason: str = Field(..., min_length=1, max_length=1000, description="評価理由")
    confidence_level: Optional[str] = Field(None, description="確信度")
    price_at_evaluation: Optional[float] = Field(None, ge=0, description="評価時価格")
    ai_score_before: Optional[ManualScoreValue] = Field(None, description="AI計算スコア（評価前）")
    follow_up_required: bool = Field(default=False, description="フォローアップ要否")
    follow_up_date: Optional[datetime] = Field(None, description="フォローアップ予定日")
    tags: Optional[List[str]] = Field(None, description="タグ")
    is_learning_case: bool = Field(default=False, description="学習事例フラグ")

    @validator('logic_type')
    def validate_logic_type(cls, v: str) -> str:
        """ロジックタイプのバリデーション"""
        allowed_types = ['logic_a', 'logic_b']
        if v not in allowed_types:
            raise ValueError(f'logic_type must be one of {allowed_types}')
        return v

    @validator('confidence_level')
    def validate_confidence_level(cls, v: Optional[str]) -> Optional[str]:
        """確信度のバリデーション"""
        if v is None:
            return v
        allowed_levels = ['high', 'medium', 'low']
        if v not in allowed_levels:
            raise ValueError(f'confidence_level must be one of {allowed_levels}')
        return v

    @validator('follow_up_date')
    def validate_follow_up_date(cls, v: Optional[datetime], values: dict) -> Optional[datetime]:
        """フォローアップ日の妥当性チェック"""
        if v is not None and 'follow_up_required' in values:
            # フォローアップ必要時のみ日付チェック
            if values.get('follow_up_required') and v <= datetime.now():
                raise ValueError('follow_up_date must be in the future when follow_up_required is True')
        return v


class ScoreUpdateRequestModel(BaseModel):
    """スコア更新リクエストモデル"""
    score: Optional[ManualScoreValue] = Field(None, description="手動スコア")
    evaluation_reason: Optional[str] = Field(None, min_length=1, max_length=1000, description="評価理由")
    confidence_level: Optional[str] = Field(None, description="確信度")
    price_at_evaluation: Optional[float] = Field(None, ge=0, description="評価時価格")
    ai_score_after: Optional[ManualScoreValue] = Field(None, description="AI計算スコア（評価後）")
    follow_up_required: Optional[bool] = Field(None, description="フォローアップ要否")
    follow_up_date: Optional[datetime] = Field(None, description="フォローアップ予定日")
    performance_validation: Optional[Dict[str, Any]] = Field(None, description="パフォーマンス検証結果")
    tags: Optional[List[str]] = Field(None, description="タグ")
    is_learning_case: Optional[bool] = Field(None, description="学習事例フラグ")
    status: Optional[str] = Field(None, description="ステータス")
    change_reason: str = Field(..., min_length=1, max_length=500, description="変更理由")

    @validator('confidence_level')
    def validate_confidence_level(cls, v: Optional[str]) -> Optional[str]:
        """確信度のバリデーション"""
        if v is None:
            return v
        allowed_levels = ['high', 'medium', 'low']
        if v not in allowed_levels:
            raise ValueError(f'confidence_level must be one of {allowed_levels}')
        return v

    @validator('status')
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """ステータスのバリデーション"""
        if v is None:
            return v
        allowed_statuses = ['active', 'archived', 'superseded']
        if v not in allowed_statuses:
            raise ValueError(f'status must be one of {allowed_statuses}')
        return v


class ScoreSearchRequestModel(BaseModel):
    """スコア検索リクエストモデル"""
    stock_code: Optional[str] = Field(None, min_length=4, max_length=10, description="銘柄コード")
    logic_type: Optional[str] = Field(None, description="対象ロジック")
    score: Optional[ManualScoreValue] = Field(None, description="手動スコア")
    confidence_level: Optional[str] = Field(None, description="確信度")
    date_from: Optional[datetime] = Field(None, description="評価日開始")
    date_to: Optional[datetime] = Field(None, description="評価日終了")
    is_learning_case: Optional[bool] = Field(None, description="学習事例フラグ")
    follow_up_required: Optional[bool] = Field(None, description="フォローアップ要否")
    status: Optional[str] = Field(None, description="ステータス")
    tags: Optional[List[str]] = Field(None, description="タグ")
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

    @validator('confidence_level')
    def validate_confidence_level(cls, v: Optional[str]) -> Optional[str]:
        """確信度のバリデーション"""
        if v is None:
            return v
        allowed_levels = ['high', 'medium', 'low']
        if v not in allowed_levels:
            raise ValueError(f'confidence_level must be one of {allowed_levels}')
        return v

    @validator('status')
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """ステータスのバリデーション"""
        if v is None:
            return v
        allowed_statuses = ['active', 'archived', 'superseded']
        if v not in allowed_statuses:
            raise ValueError(f'status must be one of {allowed_statuses}')
        return v

    @validator('date_to')
    def validate_date_range(cls, v: Optional[datetime], values: dict) -> Optional[datetime]:
        """日付範囲のバリデーション"""
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if v < values['date_from']:
                raise ValueError('date_to must be later than date_from')
        return v


class ScoreHistoryModel(BaseModel):
    """スコア変更履歴モデル"""
    id: str = Field(..., description="履歴ID")
    original_score_id: str = Field(..., description="元のスコアID")
    stock_code: str = Field(..., description="銘柄コード")
    stock_name: str = Field(..., description="銘柄名")
    old_score: Optional[ManualScoreValue] = Field(None, description="変更前スコア")
    new_score: ManualScoreValue = Field(..., description="変更後スコア")
    change_reason: str = Field(..., description="変更理由")
    changed_by: str = Field(..., description="変更者")
    changed_at: datetime = Field(..., description="変更日時")
    logic_type: str = Field(..., description="対象ロジック")
    scan_result_id: Optional[str] = Field(None, description="関連スキャン結果ID")


class ScoreSearchResponseModel(BaseModel):
    """スコア検索レスポンスモデル"""
    success: bool = Field(..., description="成功フラグ")
    scores: List[ManualScoreModel] = Field(..., description="スコア一覧")
    total: int = Field(..., ge=0, description="総件数")
    page: int = Field(..., ge=1, description="現在のページ")
    limit: int = Field(..., ge=1, description="1ページあたりの件数")
    has_next: bool = Field(..., description="次ページ有無")


class ScoreStatsModel(BaseModel):
    """スコア統計モデル"""
    total_evaluations: int = Field(..., ge=0, description="総評価件数")
    score_distribution: Dict[str, int] = Field(..., description="スコア分布")
    confidence_distribution: Dict[str, int] = Field(..., description="確信度分布")
    logic_type_distribution: Dict[str, int] = Field(..., description="ロジック別分布")
    learning_cases_count: int = Field(..., ge=0, description="学習事例件数")
    follow_up_pending_count: int = Field(..., ge=0, description="フォローアップ待ち件数")
    recent_evaluations: List[ManualScoreModel] = Field(..., description="最近の評価")


class AIScoreCalculationStatusModel(BaseModel):
    """AI スコア計算状態モデル"""
    is_calculating: bool = Field(..., description="計算中フラグ")
    stock_code: Optional[str] = Field(None, description="対象銘柄コード")
    started_at: Optional[datetime] = Field(None, description="開始日時")
    estimated_completion: Optional[datetime] = Field(None, description="完了予定日時")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100, description="進捗率")
    current_step: Optional[str] = Field(None, description="現在のステップ")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")