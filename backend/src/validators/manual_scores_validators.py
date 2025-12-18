"""
手動スコア評価バリデーター
Stock Harvest AI - 入力データ検証とエラーハンドリング
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from ..lib.logger import logger
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ScoreValidationError(Exception):
    """スコア評価バリデーションエラー"""
    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None):
        self.message = message
        self.field = field
        self.code = code or "VALIDATION_ERROR"
        super().__init__(message)


class ManualScoresValidator:
    """手動スコア評価バリデーター"""
    
    # 銘柄コードパターン（日本の株式）
    STOCK_CODE_PATTERN = re.compile(r'^[0-9]{4}$')
    
    # 許可されたロジックタイプ
    ALLOWED_LOGIC_TYPES = {'logic_a', 'logic_b'}
    
    # 手動スコアの値
    ALLOWED_MANUAL_SCORES = {'S', 'A+', 'A', 'B', 'C'}
    
    # 確信度レベル
    ALLOWED_CONFIDENCE_LEVELS = {'high', 'medium', 'low'}
    
    # ステータス値
    ALLOWED_STATUSES = {'active', 'archived', 'superseded'}
    
    @classmethod
    def validate_stock_code(cls, stock_code: str) -> str:
        """銘柄コードのバリデーション"""
        if not stock_code:
            raise ScoreValidationError("銘柄コードは必須です", "stock_code", "REQUIRED")
        
        stock_code = stock_code.strip()
        
        if not cls.STOCK_CODE_PATTERN.match(stock_code):
            raise ScoreValidationError(
                "銘柄コードは4桁の数字である必要があります", 
                "stock_code", 
                "INVALID_FORMAT"
            )
        
        return stock_code
    
    @classmethod
    def validate_stock_name(cls, stock_name: str) -> str:
        """銘柄名のバリデーション"""
        if not stock_name:
            raise ScoreValidationError("銘柄名は必須です", "stock_name", "REQUIRED")
        
        stock_name = stock_name.strip()
        
        if len(stock_name) < 1:
            raise ScoreValidationError(
                "銘柄名は1文字以上である必要があります", 
                "stock_name", 
                "TOO_SHORT"
            )
        
        if len(stock_name) > 100:
            raise ScoreValidationError(
                "銘柄名は100文字以内である必要があります", 
                "stock_name", 
                "TOO_LONG"
            )
        
        return stock_name
    
    @classmethod
    def validate_manual_score(cls, score: ManualScoreValue) -> ManualScoreValue:
        """手動スコアのバリデーション"""
        if not score:
            raise ScoreValidationError("手動スコアは必須です", "score", "REQUIRED")
        
        if score not in cls.ALLOWED_MANUAL_SCORES:
            raise ScoreValidationError(
                f"手動スコアは {', '.join(cls.ALLOWED_MANUAL_SCORES)} のいずれかである必要があります",
                "score",
                "INVALID_VALUE"
            )
        
        return score
    
    @classmethod
    def validate_logic_type(cls, logic_type: str) -> str:
        """ロジックタイプのバリデーション"""
        if not logic_type:
            raise ScoreValidationError("ロジックタイプは必須です", "logic_type", "REQUIRED")
        
        logic_type = logic_type.strip().lower()
        
        if logic_type not in cls.ALLOWED_LOGIC_TYPES:
            raise ScoreValidationError(
                f"ロジックタイプは {', '.join(cls.ALLOWED_LOGIC_TYPES)} のいずれかである必要があります",
                "logic_type",
                "INVALID_VALUE"
            )
        
        return logic_type
    
    @classmethod
    def validate_evaluation_reason(cls, reason: str) -> str:
        """評価理由のバリデーション"""
        if not reason:
            raise ScoreValidationError("評価理由は必須です", "evaluation_reason", "REQUIRED")
        
        reason = reason.strip()
        
        if len(reason) < 1:
            raise ScoreValidationError(
                "評価理由は1文字以上である必要があります", 
                "evaluation_reason", 
                "TOO_SHORT"
            )
        
        if len(reason) > 1000:
            raise ScoreValidationError(
                "評価理由は1000文字以内である必要があります", 
                "evaluation_reason", 
                "TOO_LONG"
            )
        
        return reason
    
    @classmethod
    def validate_confidence_level(cls, level: Optional[str]) -> Optional[str]:
        """確信度のバリデーション"""
        if level is None:
            return None
        
        level = level.strip().lower()
        
        if level not in cls.ALLOWED_CONFIDENCE_LEVELS:
            raise ScoreValidationError(
                f"確信度は {', '.join(cls.ALLOWED_CONFIDENCE_LEVELS)} のいずれかである必要があります",
                "confidence_level",
                "INVALID_VALUE"
            )
        
        return level
    
    @classmethod
    def validate_status(cls, status: Optional[str]) -> Optional[str]:
        """ステータスのバリデーション"""
        if status is None:
            return None
        
        status = status.strip().lower()
        
        if status not in cls.ALLOWED_STATUSES:
            raise ScoreValidationError(
                f"ステータスは {', '.join(cls.ALLOWED_STATUSES)} のいずれかである必要があります",
                "status",
                "INVALID_VALUE"
            )
        
        return status
    
    @classmethod
    def validate_price(cls, price: Optional[float], field_name: str = "price") -> Optional[float]:
        """価格のバリデーション"""
        if price is None:
            return None
        
        if not isinstance(price, (int, float)):
            raise ScoreValidationError(
                f"{field_name}は数値である必要があります", 
                field_name, 
                "INVALID_TYPE"
            )
        
        if price < 0:
            raise ScoreValidationError(
                f"{field_name}は0以上である必要があります", 
                field_name, 
                "INVALID_RANGE"
            )
        
        if price > 1000000:  # 100万円を超える株価は異常値として判定
            raise ScoreValidationError(
                f"{field_name}が異常に高い値です", 
                field_name, 
                "ABNORMAL_VALUE"
            )
        
        return float(price)
    
    @classmethod
    def validate_tags(cls, tags: Optional[List[str]]) -> Optional[List[str]]:
        """タグのバリデーション"""
        if tags is None:
            return None
        
        if not isinstance(tags, list):
            raise ScoreValidationError(
                "タグは文字列のリストである必要があります",
                "tags",
                "INVALID_TYPE"
            )
        
        validated_tags = []
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                raise ScoreValidationError(
                    f"タグ[{i}]は文字列である必要があります",
                    f"tags[{i}]",
                    "INVALID_TYPE"
                )
            
            tag = tag.strip()
            if len(tag) == 0:
                continue  # 空のタグはスキップ
            
            if len(tag) > 50:
                raise ScoreValidationError(
                    f"タグ[{i}]は50文字以内である必要があります",
                    f"tags[{i}]",
                    "TOO_LONG"
                )
            
            validated_tags.append(tag)
        
        # 重複削除
        validated_tags = list(set(validated_tags))
        
        if len(validated_tags) > 10:
            raise ScoreValidationError(
                "タグは10個以内である必要があります",
                "tags",
                "TOO_MANY"
            )
        
        return validated_tags if validated_tags else None
    
    @classmethod
    def validate_date_range(cls, date_from: Optional[datetime], date_to: Optional[datetime]) -> tuple[Optional[datetime], Optional[datetime]]:
        """日付範囲のバリデーション"""
        if date_from is None and date_to is None:
            return None, None
        
        # 未来日付のチェック
        now = datetime.now()
        
        if date_from and date_from > now:
            raise ScoreValidationError(
                "開始日は現在日時以前である必要があります",
                "date_from",
                "FUTURE_DATE"
            )
        
        if date_to and date_to > now:
            raise ScoreValidationError(
                "終了日は現在日時以前である必要があります",
                "date_to",
                "FUTURE_DATE"
            )
        
        # 日付の順序チェック
        if date_from and date_to and date_from > date_to:
            raise ScoreValidationError(
                "開始日は終了日以前である必要があります",
                "date_range",
                "INVALID_RANGE"
            )
        
        # 検索範囲の制限（3年以内）
        if date_from:
            max_past_date = now.replace(year=now.year - 3)
            if date_from < max_past_date:
                logger.warning(f"検索開始日が3年以上前に設定されています: {date_from}")
        
        return date_from, date_to
    
    @classmethod
    def validate_pagination(cls, page: int, limit: int) -> tuple[int, int]:
        """ページネーションのバリデーション"""
        if not isinstance(page, int) or page < 1:
            raise ScoreValidationError(
                "ページ番号は1以上の整数である必要があります",
                "page",
                "INVALID_VALUE"
            )
        
        if not isinstance(limit, int) or limit < 1:
            raise ScoreValidationError(
                "制限件数は1以上の整数である必要があります",
                "limit",
                "INVALID_VALUE"
            )
        
        if limit > 100:
            raise ScoreValidationError(
                "制限件数は100件以下である必要があります",
                "limit",
                "TOO_LARGE"
            )
        
        return page, limit
    
    @classmethod
    def validate_follow_up_date(cls, follow_up_date: Optional[datetime], follow_up_required: bool) -> Optional[datetime]:
        """フォローアップ日のバリデーション"""
        if follow_up_date is None:
            if follow_up_required:
                logger.warning("フォローアップが必要ですが、フォローアップ日が設定されていません")
            return None
        
        # フォローアップ日は未来日である必要がある
        now = datetime.now()
        if follow_up_date <= now:
            raise ScoreValidationError(
                "フォローアップ日は現在日時より後である必要があります",
                "follow_up_date",
                "MUST_BE_FUTURE"
            )
        
        # 最大1年後まで
        max_future_date = now.replace(year=now.year + 1)
        if follow_up_date > max_future_date:
            raise ScoreValidationError(
                "フォローアップ日は1年以内である必要があります",
                "follow_up_date",
                "TOO_FAR_FUTURE"
            )
        
        return follow_up_date
    
    @classmethod
    def validate_evaluation_request(cls, eval_data: Dict[str, Any]) -> Dict[str, Any]:
        """評価作成リクエストの包括的バリデーション"""
        try:
            validated_data = {}
            
            # 必須フィールド
            validated_data['stock_code'] = cls.validate_stock_code(eval_data.get('stock_code'))
            validated_data['stock_name'] = cls.validate_stock_name(eval_data.get('stock_name'))
            validated_data['score'] = cls.validate_manual_score(eval_data.get('score'))
            validated_data['logic_type'] = cls.validate_logic_type(eval_data.get('logic_type'))
            validated_data['evaluation_reason'] = cls.validate_evaluation_reason(eval_data.get('evaluation_reason'))
            
            # オプションフィールド
            if scan_result_id := eval_data.get('scan_result_id'):
                validated_data['scan_result_id'] = scan_result_id.strip()
            
            if confidence_level := eval_data.get('confidence_level'):
                validated_data['confidence_level'] = cls.validate_confidence_level(confidence_level)
            
            if price_at_evaluation := eval_data.get('price_at_evaluation'):
                validated_data['price_at_evaluation'] = cls.validate_price(price_at_evaluation, "price_at_evaluation")
            
            if ai_score_before := eval_data.get('ai_score_before'):
                validated_data['ai_score_before'] = cls.validate_manual_score(ai_score_before)
            
            # フォローアップ関連
            follow_up_required = eval_data.get('follow_up_required', False)
            validated_data['follow_up_required'] = bool(follow_up_required)
            
            if follow_up_date := eval_data.get('follow_up_date'):
                validated_data['follow_up_date'] = cls.validate_follow_up_date(follow_up_date, follow_up_required)
            
            # その他フラグ
            validated_data['is_learning_case'] = bool(eval_data.get('is_learning_case', False))
            
            # タグ
            if tags := eval_data.get('tags'):
                validated_data['tags'] = cls.validate_tags(tags)
            
            return validated_data
            
        except ScoreValidationError:
            raise
        except Exception as e:
            logger.error(f"評価リクエストバリデーション中に予期しないエラー: {e}")
            raise ScoreValidationError(
                "評価リクエストのバリデーション中にエラーが発生しました",
                "validation",
                "UNEXPECTED_ERROR"
            )
    
    @classmethod
    def validate_update_request(cls, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """スコア更新リクエストの包括的バリデーション"""
        try:
            validated_data = {}
            
            # 変更理由は必須
            if not update_data.get('change_reason'):
                raise ScoreValidationError("変更理由は必須です", "change_reason", "REQUIRED")
            
            change_reason = update_data['change_reason'].strip()
            if len(change_reason) < 1:
                raise ScoreValidationError("変更理由は1文字以上である必要があります", "change_reason", "TOO_SHORT")
            if len(change_reason) > 500:
                raise ScoreValidationError("変更理由は500文字以内である必要があります", "change_reason", "TOO_LONG")
            
            validated_data['change_reason'] = change_reason
            
            # 更新可能フィールド
            if score := update_data.get('score'):
                validated_data['score'] = cls.validate_manual_score(score)
            
            if evaluation_reason := update_data.get('evaluation_reason'):
                validated_data['evaluation_reason'] = cls.validate_evaluation_reason(evaluation_reason)
            
            if confidence_level := update_data.get('confidence_level'):
                validated_data['confidence_level'] = cls.validate_confidence_level(confidence_level)
            
            if price_at_evaluation := update_data.get('price_at_evaluation'):
                validated_data['price_at_evaluation'] = cls.validate_price(price_at_evaluation, "price_at_evaluation")
            
            if ai_score_after := update_data.get('ai_score_after'):
                validated_data['ai_score_after'] = cls.validate_manual_score(ai_score_after)
            
            if status := update_data.get('status'):
                validated_data['status'] = cls.validate_status(status)
            
            # フォローアップ関連
            if 'follow_up_required' in update_data:
                follow_up_required = bool(update_data['follow_up_required'])
                validated_data['follow_up_required'] = follow_up_required
                
                if follow_up_date := update_data.get('follow_up_date'):
                    validated_data['follow_up_date'] = cls.validate_follow_up_date(follow_up_date, follow_up_required)
            
            # その他フラグ
            if 'is_learning_case' in update_data:
                validated_data['is_learning_case'] = bool(update_data['is_learning_case'])
            
            # タグ
            if tags := update_data.get('tags'):
                validated_data['tags'] = cls.validate_tags(tags)
            
            # パフォーマンス検証結果（JSONデータはそのまま保存）
            if performance_validation := update_data.get('performance_validation'):
                validated_data['performance_validation'] = performance_validation
            
            return validated_data
            
        except ScoreValidationError:
            raise
        except Exception as e:
            logger.error(f"更新リクエストバリデーション中に予期しないエラー: {e}")
            raise ScoreValidationError(
                "更新リクエストのバリデーション中にエラーが発生しました",
                "validation",
                "UNEXPECTED_ERROR"
            )
    
    @classmethod
    def validate_search_request(cls, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """検索リクエストの包括的バリデーション"""
        try:
            validated_data = {}
            
            # オプション検索条件
            if stock_code := search_data.get('stock_code'):
                validated_data['stock_code'] = cls.validate_stock_code(stock_code)
            
            if logic_type := search_data.get('logic_type'):
                validated_data['logic_type'] = cls.validate_logic_type(logic_type)
            
            if score := search_data.get('score'):
                validated_data['score'] = cls.validate_manual_score(score)
            
            if confidence_level := search_data.get('confidence_level'):
                validated_data['confidence_level'] = cls.validate_confidence_level(confidence_level)
            
            if status := search_data.get('status'):
                validated_data['status'] = cls.validate_status(status)
            
            # 日付範囲
            date_from = search_data.get('date_from')
            date_to = search_data.get('date_to')
            if date_from or date_to:
                validated_from, validated_to = cls.validate_date_range(date_from, date_to)
                if validated_from:
                    validated_data['date_from'] = validated_from
                if validated_to:
                    validated_data['date_to'] = validated_to
            
            # フラグ検索
            if 'is_learning_case' in search_data:
                validated_data['is_learning_case'] = bool(search_data['is_learning_case'])
            
            if 'follow_up_required' in search_data:
                validated_data['follow_up_required'] = bool(search_data['follow_up_required'])
            
            # タグ検索
            if tags := search_data.get('tags'):
                validated_data['tags'] = cls.validate_tags(tags)
            
            # ページネーション
            page = search_data.get('page', 1)
            limit = search_data.get('limit', 20)
            validated_data['page'], validated_data['limit'] = cls.validate_pagination(page, limit)
            
            return validated_data
            
        except ScoreValidationError:
            raise
        except Exception as e:
            logger.error(f"検索リクエストバリデーション中に予期しないエラー: {e}")
            raise ScoreValidationError(
                "検索リクエストのバリデーション中にエラーが発生しました",
                "validation",
                "UNEXPECTED_ERROR"
            )