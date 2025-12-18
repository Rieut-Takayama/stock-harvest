"""
銘柄アーカイブバリデーター
Stock Harvest AI - 入力データ検証とエラーハンドリング
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from ..lib.logger import logger
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ArchiveValidationError(Exception):
    """アーカイブバリデーションエラー"""
    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


class ArchiveValidator:
    """銘柄アーカイブバリデーター"""
    
    # 銘柄コードパターン（日本の株式）
    STOCK_CODE_PATTERN = re.compile(r'^[0-9]{4}$')
    
    # 許可されたロジックタイプ
    ALLOWED_LOGIC_TYPES = {'logic_a', 'logic_b'}
    
    # 許可された結果分類
    ALLOWED_OUTCOME_CLASSIFICATIONS = {'success', 'failure', 'neutral', 'pending'}
    
    # 許可されたアーカイブステータス
    ALLOWED_ARCHIVE_STATUSES = {'active', 'archived', 'deleted'}
    
    # 手動スコアの値
    ALLOWED_MANUAL_SCORES = {'S', 'A+', 'A', 'B', 'C'}
    
    @classmethod
    def validate_stock_code(cls, stock_code: str) -> str:
        """銘柄コードのバリデーション"""
        if not stock_code:
            raise ArchiveValidationError("銘柄コードは必須です", "stock_code", "REQUIRED")
        
        stock_code = stock_code.strip()
        
        if not cls.STOCK_CODE_PATTERN.match(stock_code):
            raise ArchiveValidationError(
                "銘柄コードは4桁の数字である必要があります", 
                "stock_code", 
                "INVALID_FORMAT"
            )
        
        return stock_code
    
    @classmethod
    def validate_stock_name(cls, stock_name: str) -> str:
        """銘柄名のバリデーション"""
        if not stock_name:
            raise ArchiveValidationError("銘柄名は必須です", "stock_name", "REQUIRED")
        
        stock_name = stock_name.strip()
        
        if len(stock_name) < 1:
            raise ArchiveValidationError(
                "銘柄名は1文字以上である必要があります", 
                "stock_name", 
                "TOO_SHORT"
            )
        
        if len(stock_name) > 100:
            raise ArchiveValidationError(
                "銘柄名は100文字以内である必要があります", 
                "stock_name", 
                "TOO_LONG"
            )
        
        return stock_name
    
    @classmethod
    def validate_logic_type(cls, logic_type: str) -> str:
        """ロジックタイプのバリデーション"""
        if not logic_type:
            raise ArchiveValidationError("ロジックタイプは必須です", "logic_type", "REQUIRED")
        
        logic_type = logic_type.strip().lower()
        
        if logic_type not in cls.ALLOWED_LOGIC_TYPES:
            raise ArchiveValidationError(
                f"ロジックタイプは {', '.join(cls.ALLOWED_LOGIC_TYPES)} のいずれかである必要があります",
                "logic_type",
                "INVALID_VALUE"
            )
        
        return logic_type
    
    @classmethod
    def validate_price(cls, price: float, field_name: str = "price") -> float:
        """価格のバリデーション"""
        if price is None:
            raise ArchiveValidationError(f"{field_name}は必須です", field_name, "REQUIRED")
        
        if not isinstance(price, (int, float)):
            raise ArchiveValidationError(
                f"{field_name}は数値である必要があります", 
                field_name, 
                "INVALID_TYPE"
            )
        
        if price <= 0:
            raise ArchiveValidationError(
                f"{field_name}は0より大きい値である必要があります", 
                field_name, 
                "INVALID_RANGE"
            )
        
        if price > 1000000:  # 100万円を超える株価は異常値として判定
            raise ArchiveValidationError(
                f"{field_name}が異常に高い値です", 
                field_name, 
                "ABNORMAL_VALUE"
            )
        
        return float(price)
    
    @classmethod
    def validate_volume(cls, volume: int, field_name: str = "volume") -> int:
        """出来高のバリデーション"""
        if volume is None:
            raise ArchiveValidationError(f"{field_name}は必須です", field_name, "REQUIRED")
        
        if not isinstance(volume, (int, float)):
            raise ArchiveValidationError(
                f"{field_name}は整数である必要があります", 
                field_name, 
                "INVALID_TYPE"
            )
        
        volume = int(volume)
        
        if volume < 0:
            raise ArchiveValidationError(
                f"{field_name}は0以上である必要があります", 
                field_name, 
                "INVALID_RANGE"
            )
        
        return volume
    
    @classmethod
    def validate_percentage(cls, percentage: Optional[float], field_name: str) -> Optional[float]:
        """パーセンテージのバリデーション"""
        if percentage is None:
            return None
        
        if not isinstance(percentage, (int, float)):
            raise ArchiveValidationError(
                f"{field_name}は数値である必要があります", 
                field_name, 
                "INVALID_TYPE"
            )
        
        # -100%から+1000%の範囲をチェック（極端な値を制限）
        if percentage < -100 or percentage > 1000:
            raise ArchiveValidationError(
                f"{field_name}は-100%から1000%の範囲内である必要があります", 
                field_name, 
                "INVALID_RANGE"
            )
        
        return float(percentage)
    
    @classmethod
    def validate_outcome_classification(cls, classification: Optional[str]) -> Optional[str]:
        """結果分類のバリデーション"""
        if classification is None:
            return None
        
        classification = classification.strip().lower()
        
        if classification not in cls.ALLOWED_OUTCOME_CLASSIFICATIONS:
            raise ArchiveValidationError(
                f"結果分類は {', '.join(cls.ALLOWED_OUTCOME_CLASSIFICATIONS)} のいずれかである必要があります",
                "outcome_classification",
                "INVALID_VALUE"
            )
        
        return classification
    
    @classmethod
    def validate_manual_score(cls, score: Optional[ManualScoreValue]) -> Optional[ManualScoreValue]:
        """手動スコアのバリデーション"""
        if score is None:
            return None
        
        if score not in cls.ALLOWED_MANUAL_SCORES:
            raise ArchiveValidationError(
                f"手動スコアは {', '.join(cls.ALLOWED_MANUAL_SCORES)} のいずれかである必要があります",
                "manual_score",
                "INVALID_VALUE"
            )
        
        return score
    
    @classmethod
    def validate_archive_status(cls, status: Optional[str]) -> Optional[str]:
        """アーカイブステータスのバリデーション"""
        if status is None:
            return None
        
        status = status.strip().lower()
        
        if status not in cls.ALLOWED_ARCHIVE_STATUSES:
            raise ArchiveValidationError(
                f"アーカイブステータスは {', '.join(cls.ALLOWED_ARCHIVE_STATUSES)} のいずれかである必要があります",
                "archive_status",
                "INVALID_VALUE"
            )
        
        return status
    
    @classmethod
    def validate_text_field(cls, text: Optional[str], field_name: str, max_length: int, required: bool = False) -> Optional[str]:
        """テキストフィールドのバリデーション"""
        if text is None:
            if required:
                raise ArchiveValidationError(f"{field_name}は必須です", field_name, "REQUIRED")
            return None
        
        text = text.strip()
        
        if not text and required:
            raise ArchiveValidationError(f"{field_name}は必須です", field_name, "REQUIRED")
        
        if len(text) > max_length:
            raise ArchiveValidationError(
                f"{field_name}は{max_length}文字以内である必要があります", 
                field_name, 
                "TOO_LONG"
            )
        
        return text if text else None
    
    @classmethod
    def validate_date_range(cls, date_from: Optional[datetime], date_to: Optional[datetime]) -> tuple[Optional[datetime], Optional[datetime]]:
        """日付範囲のバリデーション"""
        if date_from is None and date_to is None:
            return None, None
        
        # 未来日付のチェック
        now = datetime.now()
        
        if date_from and date_from > now:
            raise ArchiveValidationError(
                "開始日は現在日時以前である必要があります",
                "date_from",
                "FUTURE_DATE"
            )
        
        if date_to and date_to > now:
            raise ArchiveValidationError(
                "終了日は現在日時以前である必要があります",
                "date_to",
                "FUTURE_DATE"
            )
        
        # 日付の順序チェック
        if date_from and date_to and date_from > date_to:
            raise ArchiveValidationError(
                "開始日は終了日以前である必要があります",
                "date_range",
                "INVALID_RANGE"
            )
        
        # 検索範囲の制限（5年以内）
        if date_from:
            max_past_date = now.replace(year=now.year - 5)
            if date_from < max_past_date:
                logger.warning(f"検索開始日が5年以上前に設定されています: {date_from}")
        
        return date_from, date_to
    
    @classmethod
    def validate_pagination(cls, page: int, limit: int) -> tuple[int, int]:
        """ページネーションのバリデーション"""
        if not isinstance(page, int) or page < 1:
            raise ArchiveValidationError(
                "ページ番号は1以上の整数である必要があります",
                "page",
                "INVALID_VALUE"
            )
        
        if not isinstance(limit, int) or limit < 1:
            raise ArchiveValidationError(
                "制限件数は1以上の整数である必要があります",
                "limit",
                "INVALID_VALUE"
            )
        
        if limit > 100:
            raise ArchiveValidationError(
                "制限件数は100件以下である必要があります",
                "limit",
                "TOO_LARGE"
            )
        
        return page, limit
    
    @classmethod
    def validate_search_request(cls, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """検索リクエストの包括的バリデーション"""
        try:
            validated_data = {}
            
            # 銘柄コード
            if stock_code := search_data.get('stock_code'):
                validated_data['stock_code'] = cls.validate_stock_code(stock_code)
            
            # ロジックタイプ
            if logic_type := search_data.get('logic_type'):
                validated_data['logic_type'] = cls.validate_logic_type(logic_type)
            
            # 日付範囲
            date_from = search_data.get('date_from')
            date_to = search_data.get('date_to')
            if date_from or date_to:
                validated_from, validated_to = cls.validate_date_range(date_from, date_to)
                if validated_from:
                    validated_data['date_from'] = validated_from
                if validated_to:
                    validated_data['date_to'] = validated_to
            
            # 結果分類
            if outcome_classification := search_data.get('outcome_classification'):
                validated_data['outcome_classification'] = cls.validate_outcome_classification(outcome_classification)
            
            # 手動スコア
            if manual_score := search_data.get('manual_score'):
                validated_data['manual_score'] = cls.validate_manual_score(manual_score)
            
            # ページネーション
            page = search_data.get('page', 1)
            limit = search_data.get('limit', 20)
            validated_data['page'], validated_data['limit'] = cls.validate_pagination(page, limit)
            
            return validated_data
            
        except ArchiveValidationError:
            raise
        except Exception as e:
            logger.error(f"検索リクエストバリデーション中に予期しないエラー: {e}")
            raise ArchiveValidationError(
                "検索リクエストのバリデーション中にエラーが発生しました",
                "validation",
                "UNEXPECTED_ERROR"
            )
    
    @classmethod
    def validate_create_request(cls, create_data: Dict[str, Any]) -> Dict[str, Any]:
        """アーカイブ作成リクエストの包括的バリデーション"""
        try:
            validated_data = {}
            
            # 必須フィールド
            validated_data['stock_code'] = cls.validate_stock_code(create_data.get('stock_code'))
            validated_data['stock_name'] = cls.validate_stock_name(create_data.get('stock_name'))
            validated_data['logic_type'] = cls.validate_logic_type(create_data.get('logic_type'))
            
            # スキャンIDは必須（他のバリデーションでは扱わない）
            scan_id = create_data.get('scan_id')
            if not scan_id or not isinstance(scan_id, str):
                raise ArchiveValidationError("スキャンIDは必須です", "scan_id", "REQUIRED")
            validated_data['scan_id'] = scan_id.strip()
            
            # 価格・出来高
            validated_data['price_at_detection'] = cls.validate_price(
                create_data.get('price_at_detection'), 
                "price_at_detection"
            )
            validated_data['volume_at_detection'] = cls.validate_volume(
                create_data.get('volume_at_detection'), 
                "volume_at_detection"
            )
            
            # オプションフィールド
            if market_cap := create_data.get('market_cap_at_detection'):
                validated_data['market_cap_at_detection'] = cls.validate_price(market_cap, "market_cap_at_detection")
            
            if manual_score := create_data.get('manual_score'):
                validated_data['manual_score'] = cls.validate_manual_score(manual_score)
            
            if manual_score_reason := create_data.get('manual_score_reason'):
                validated_data['manual_score_reason'] = cls.validate_text_field(
                    manual_score_reason, "manual_score_reason", 500
                )
            
            if lessons_learned := create_data.get('lessons_learned'):
                validated_data['lessons_learned'] = cls.validate_text_field(
                    lessons_learned, "lessons_learned", 2000
                )
            
            if follow_up_notes := create_data.get('follow_up_notes'):
                validated_data['follow_up_notes'] = cls.validate_text_field(
                    follow_up_notes, "follow_up_notes", 1000
                )
            
            # JSONフィールドはそのまま保存（詳細なバリデーションは省略）
            for json_field in ['technical_signals_snapshot', 'logic_specific_data']:
                if value := create_data.get(json_field):
                    validated_data[json_field] = value
            
            return validated_data
            
        except ArchiveValidationError:
            raise
        except Exception as e:
            logger.error(f"アーカイブ作成リクエストバリデーション中に予期しないエラー: {e}")
            raise ArchiveValidationError(
                "アーカイブ作成リクエストのバリデーション中にエラーが発生しました",
                "validation",
                "UNEXPECTED_ERROR"
            )