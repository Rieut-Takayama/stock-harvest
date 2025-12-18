"""
Charts Validators - チャート機能バリデーター
リクエストデータの検証とサニタイゼーション
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging

from ..models.charts_models import (
    ChartDataRequestModel,
    TimeframeEnum,
    PeriodEnum,
    TechnicalIndicatorEnum
)

logger = logging.getLogger(__name__)


class ChartsValidator:
    """チャート機能用バリデータークラス"""

    # 有効な銘柄コードの正規表現
    STOCK_CODE_PATTERN = re.compile(r'^[0-9]{4}$')
    
    # 東証銘柄コード範囲（実際の上場企業範囲）
    VALID_STOCK_CODE_RANGES = [
        (1000, 9999),  # 東証全体の範囲
    ]
    
    # 無効な銘柄コード（テスト用途など）
    INVALID_STOCK_CODES = {
        "0000", "9999", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888"
    }

    @classmethod
    def validate_stock_code(cls, stock_code: str) -> Tuple[bool, str]:
        """
        銘柄コードの包括的検証
        
        Args:
            stock_code: 検証対象の銘柄コード
            
        Returns:
            Tuple[bool, str]: (有効性, エラーメッセージ)
        """
        if not stock_code:
            return False, "銘柄コードが指定されていません"
        
        # 文字列型チェック
        if not isinstance(stock_code, str):
            return False, "銘柄コードは文字列で指定してください"
        
        # 空白除去
        stock_code = stock_code.strip()
        
        # 基本形式チェック
        if not cls.STOCK_CODE_PATTERN.match(stock_code):
            return False, "銘柄コードは4桁の数字で入力してください (例: 7203)"
        
        # 数値範囲チェック
        code_int = int(stock_code)
        valid_range = any(
            start <= code_int <= end 
            for start, end in cls.VALID_STOCK_CODE_RANGES
        )
        
        if not valid_range:
            return False, f"銘柄コード {stock_code} は有効な範囲外です"
        
        # 無効コードチェック
        if stock_code in cls.INVALID_STOCK_CODES:
            return False, f"銘柄コード {stock_code} は無効です"
        
        return True, ""

    @classmethod
    def validate_timeframe(cls, timeframe: str) -> Tuple[bool, str, Optional[TimeframeEnum]]:
        """
        タイムフレームバリデーション
        
        Args:
            timeframe: タイムフレーム文字列
            
        Returns:
            Tuple[bool, str, Optional[TimeframeEnum]]: (有効性, エラーメッセージ, 変換後値)
        """
        if not timeframe:
            return True, "", TimeframeEnum.ONE_DAY  # デフォルト値
        
        try:
            timeframe_enum = TimeframeEnum(timeframe)
            return True, "", timeframe_enum
        except ValueError:
            valid_values = [e.value for e in TimeframeEnum]
            return False, f"無効なタイムフレームです。有効な値: {', '.join(valid_values)}", None

    @classmethod
    def validate_period(cls, period: str) -> Tuple[bool, str, Optional[PeriodEnum]]:
        """
        期間バリデーション
        
        Args:
            period: 期間文字列
            
        Returns:
            Tuple[bool, str, Optional[PeriodEnum]]: (有効性, エラーメッセージ, 変換後値)
        """
        if not period:
            return True, "", PeriodEnum.THIRTY_DAYS  # デフォルト値
        
        try:
            period_enum = PeriodEnum(period)
            return True, "", period_enum
        except ValueError:
            valid_values = [e.value for e in PeriodEnum]
            return False, f"無効な期間です。有効な値: {', '.join(valid_values)}", None

    @classmethod
    def validate_indicators(cls, indicators_str: Optional[str]) -> Tuple[bool, str, List[TechnicalIndicatorEnum]]:
        """
        テクニカル指標バリデーション
        
        Args:
            indicators_str: カンマ区切りの指標文字列
            
        Returns:
            Tuple[bool, str, List[TechnicalIndicatorEnum]]: (有効性, エラーメッセージ, 変換後リスト)
        """
        if not indicators_str:
            return True, "", []  # 空リスト
        
        try:
            # カンマで分割してトリム
            indicator_list = [ind.strip().lower() for ind in indicators_str.split(",") if ind.strip()]
            
            # 重複除去
            indicator_list = list(set(indicator_list))
            
            # 各指標の有効性チェック
            validated_indicators = []
            for indicator in indicator_list:
                try:
                    indicator_enum = TechnicalIndicatorEnum(indicator)
                    validated_indicators.append(indicator_enum)
                except ValueError:
                    valid_values = [e.value for e in TechnicalIndicatorEnum]
                    return False, f"無効なテクニカル指標 '{indicator}'。有効な値: {', '.join(valid_values)}", []
            
            return True, "", validated_indicators
            
        except Exception as e:
            return False, f"テクニカル指標の解析エラー: {str(e)}", []

    @classmethod
    def validate_chart_request(cls, request_data: Dict[str, Any]) -> Tuple[bool, str, Optional[ChartDataRequestModel]]:
        """
        チャートリクエスト全体の検証
        
        Args:
            request_data: リクエストデータ辞書
            
        Returns:
            Tuple[bool, str, Optional[ChartDataRequestModel]]: (有効性, エラーメッセージ, 検証済みモデル)
        """
        try:
            # 必須フィールド検証
            stock_code = request_data.get('stock_code', '').strip()
            if not stock_code:
                return False, "銘柄コードは必須です", None
            
            # 銘柄コード検証
            is_valid_code, code_error = cls.validate_stock_code(stock_code)
            if not is_valid_code:
                return False, code_error, None
            
            # タイムフレーム検証
            timeframe = request_data.get('timeframe', '1d')
            is_valid_timeframe, timeframe_error, timeframe_enum = cls.validate_timeframe(timeframe)
            if not is_valid_timeframe:
                return False, timeframe_error, None
            
            # 期間検証
            period = request_data.get('period', '30d')
            is_valid_period, period_error, period_enum = cls.validate_period(period)
            if not is_valid_period:
                return False, period_error, None
            
            # テクニカル指標検証
            indicators = request_data.get('indicators')
            is_valid_indicators, indicators_error, indicators_list = cls.validate_indicators(indicators)
            if not is_valid_indicators:
                return False, indicators_error, None
            
            # Pydanticモデル作成
            chart_request = ChartDataRequestModel(
                stock_code=stock_code,
                timeframe=timeframe_enum,
                period=period_enum,
                indicators=indicators_list or []
            )
            
            return True, "", chart_request
            
        except Exception as e:
            logger.error(f"チャートリクエスト検証エラー: {str(e)}")
            return False, f"リクエストの検証に失敗しました: {str(e)}", None

    @classmethod
    def sanitize_float(cls, value: Any, field_name: str, min_value: float = 0.0) -> float:
        """
        浮動小数点数のサニタイゼーション
        
        Args:
            value: サニタイゼーション対象
            field_name: フィールド名
            min_value: 最小値
            
        Returns:
            サニタイゼーション済み値
        """
        try:
            float_value = float(value)
            
            # NaN/無限大チェック
            if not isinstance(float_value, (int, float)) or str(float_value).lower() in ['nan', 'inf', '-inf']:
                logger.warning(f"Invalid float value for {field_name}: {value}")
                return min_value
            
            # 最小値チェック
            if float_value < min_value:
                return min_value
            
            return float_value
            
        except (ValueError, TypeError):
            logger.warning(f"Cannot convert to float for {field_name}: {value}")
            return min_value

    @classmethod
    def sanitize_int(cls, value: Any, field_name: str, min_value: int = 0) -> int:
        """
        整数のサニタイゼーション
        
        Args:
            value: サニタイゼーション対象
            field_name: フィールド名
            min_value: 最小値
            
        Returns:
            サニタイゼーション済み値
        """
        try:
            int_value = int(float(value))
            
            # 最小値チェック
            if int_value < min_value:
                return min_value
            
            return int_value
            
        except (ValueError, TypeError):
            logger.warning(f"Cannot convert to int for {field_name}: {value}")
            return min_value

    @classmethod
    def validate_timeframe_period_combination(cls, timeframe: str, period: str) -> Tuple[bool, str]:
        """
        タイムフレームと期間の組み合わせ検証
        
        Args:
            timeframe: タイムフレーム
            period: 期間
            
        Returns:
            Tuple[bool, str]: (有効性, エラーメッセージ)
        """
        # 論理的に無効な組み合わせをチェック
        invalid_combinations = [
            # 月足で5日間は無意味
            ("1m", "5d"),
            ("3m", "5d"),
            ("3m", "30d"),
        ]
        
        combination = (timeframe, period)
        if combination in invalid_combinations:
            return False, f"タイムフレーム '{timeframe}' と期間 '{period}' の組み合わせは無効です"
        
        return True, ""

    @classmethod
    def get_validation_summary(cls) -> Dict[str, Any]:
        """
        バリデーションルールの概要を取得
        
        Returns:
            バリデーションルール概要
        """
        return {
            "stock_code": {
                "format": "4桁の数字",
                "example": "7203",
                "invalid_examples": list(cls.INVALID_STOCK_CODES)
            },
            "timeframe": {
                "valid_values": [e.value for e in TimeframeEnum],
                "default": "1d"
            },
            "period": {
                "valid_values": [e.value for e in PeriodEnum],
                "default": "30d"
            },
            "indicators": {
                "valid_values": [e.value for e in TechnicalIndicatorEnum],
                "format": "カンマ区切り文字列",
                "example": "sma,rsi,macd"
            }
        }