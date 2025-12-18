"""
売買支援関連バリデータ
Stock Harvest AI プロジェクト用
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from decimal import Decimal
from datetime import datetime
import re


def validate_stock_code(stock_code: str) -> str:
    """銘柄コードのバリデーション"""
    if not stock_code:
        raise ValueError("銘柄コードが指定されていません")
    
    if not isinstance(stock_code, str):
        raise ValueError("銘柄コードは文字列である必要があります")
    
    # 4桁の数字であることを確認
    if not re.match(r'^[0-9]{4}$', stock_code):
        raise ValueError("銘柄コードは4桁の数字である必要があります（例: 7203）")
    
    return stock_code


def validate_price(price: Any, field_name: str = "価格") -> Decimal:
    """価格のバリデーション"""
    if price is None:
        raise ValueError(f"{field_name}が指定されていません")
    
    try:
        price_decimal = Decimal(str(price))
    except (TypeError, ValueError):
        raise ValueError(f"{field_name}は数値である必要があります")
    
    if price_decimal <= 0:
        raise ValueError(f"{field_name}は0より大きい値である必要があります")
    
    # 日本株の価格範囲チェック（1円 ～ 100万円）
    if price_decimal < Decimal('1') or price_decimal > Decimal('1000000'):
        raise ValueError(f"{field_name}は1円から100万円の範囲内である必要があります")
    
    return price_decimal


def validate_investment_amount(amount: Any) -> Decimal:
    """投資金額のバリデーション"""
    if amount is None:
        raise ValueError("投資金額が指定されていません")
    
    try:
        amount_decimal = Decimal(str(amount))
    except (TypeError, ValueError):
        raise ValueError("投資金額は数値である必要があります")
    
    if amount_decimal <= 0:
        raise ValueError("投資金額は0より大きい値である必要があります")
    
    # 最小投資金額: 1,000円、最大投資金額: 1億円
    if amount_decimal < Decimal('1000'):
        raise ValueError("投資金額は1,000円以上である必要があります")
    
    if amount_decimal > Decimal('100000000'):
        raise ValueError("投資金額は1億円以下である必要があります")
    
    return amount_decimal


def validate_risk_tolerance(risk_tolerance: str) -> str:
    """リスク許容度のバリデーション"""
    valid_levels = ['low', 'medium', 'high']
    
    if not risk_tolerance:
        raise ValueError("リスク許容度が指定されていません")
    
    if risk_tolerance not in valid_levels:
        raise ValueError(f"リスク許容度は {', '.join(valid_levels)} のいずれかである必要があります")
    
    return risk_tolerance


def validate_timeframe(timeframe: str) -> str:
    """投資期間のバリデーション"""
    valid_timeframes = ['1w', '1m', '3m', '6m', '1y']
    
    if not timeframe:
        raise ValueError("投資期間が指定されていません")
    
    if timeframe not in valid_timeframes:
        raise ValueError(f"投資期間は {', '.join(valid_timeframes)} のいずれかである必要があります")
    
    return timeframe


def validate_logic_type(logic_type: Optional[str]) -> Optional[str]:
    """ロジック種別のバリデーション"""
    if logic_type is None:
        return "manual"
    
    valid_types = ['logic_a', 'logic_b', 'manual']
    
    if logic_type not in valid_types:
        raise ValueError(f"ロジック種別は {', '.join(valid_types)} のいずれかである必要があります")
    
    return logic_type


def validate_order_method(order_method: str) -> str:
    """注文方法のバリデーション"""
    valid_methods = ['market', 'limit', 'stop', 'ifdoco']
    
    if not order_method:
        raise ValueError("注文方法が指定されていません")
    
    if order_method not in valid_methods:
        raise ValueError(f"注文方法は {', '.join(valid_methods)} のいずれかである必要があります")
    
    return order_method


def validate_trade_type(trade_type: str) -> str:
    """取引種別のバリデーション"""
    valid_types = ['BUY', 'SELL']
    
    if not trade_type:
        raise ValueError("取引種別が指定されていません")
    
    if trade_type not in valid_types:
        raise ValueError(f"取引種別は {', '.join(valid_types)} のいずれかである必要があります")
    
    return trade_type


def validate_status(status: str) -> str:
    """ステータスのバリデーション"""
    valid_statuses = ['open', 'closed', 'cancelled', 'pending', 'executed', 'failed']
    
    if not status:
        raise ValueError("ステータスが指定されていません")
    
    if status not in valid_statuses:
        raise ValueError(f"ステータスは {', '.join(valid_statuses)} のいずれかである必要があります")
    
    return status


def validate_pagination(page: int, limit: int) -> tuple[int, int]:
    """ページネーションパラメータのバリデーション"""
    if page < 1:
        raise ValueError("ページ番号は1以上である必要があります")
    
    if limit < 1:
        raise ValueError("取得件数は1以上である必要があります")
    
    if limit > 100:
        raise ValueError("取得件数は100以下である必要があります")
    
    return page, limit


def validate_date_range(date_from: Optional[datetime], date_to: Optional[datetime]) -> tuple[Optional[datetime], Optional[datetime]]:
    """日付範囲のバリデーション"""
    if date_from and date_to:
        if date_from > date_to:
            raise ValueError("開始日は終了日より前である必要があります")
        
        # 最大検索期間: 3年
        max_days = 365 * 3
        if (date_to - date_from).days > max_days:
            raise ValueError(f"検索期間は{max_days}日以下である必要があります")
    
    return date_from, date_to


def validate_confidence_level(confidence: Optional[Decimal]) -> Optional[Decimal]:
    """信頼度のバリデーション"""
    if confidence is None:
        return None
    
    try:
        confidence_decimal = Decimal(str(confidence))
    except (TypeError, ValueError):
        raise ValueError("信頼度は数値である必要があります")
    
    if confidence_decimal < 0 or confidence_decimal > 1:
        raise ValueError("信頼度は0から1の範囲内である必要があります")
    
    return confidence_decimal


def validate_risk_reward_ratio(ratio: Optional[Decimal]) -> Optional[Decimal]:
    """リスクリワード比率のバリデーション"""
    if ratio is None:
        return None
    
    try:
        ratio_decimal = Decimal(str(ratio))
    except (TypeError, ValueError):
        raise ValueError("リスクリワード比率は数値である必要があります")
    
    if ratio_decimal <= 0:
        raise ValueError("リスクリワード比率は0より大きい値である必要があります")
    
    # 現実的な範囲: 0.1 ～ 10.0
    if ratio_decimal < Decimal('0.1') or ratio_decimal > Decimal('10.0'):
        raise ValueError("リスクリワード比率は0.1から10.0の範囲内である必要があります")
    
    return ratio_decimal


class EntryOptimizationValidator:
    """エントリーポイント最適化用バリデータ"""
    
    @staticmethod
    def validate_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """リクエストデータのバリデーション"""
        validated_data = {}
        
        # 必須フィールド
        validated_data['stock_code'] = validate_stock_code(data.get('stock_code'))
        validated_data['current_price'] = validate_price(data.get('current_price'), "現在価格")
        
        # オプションフィールド
        validated_data['logic_type'] = validate_logic_type(data.get('logic_type'))
        validated_data['risk_tolerance'] = validate_risk_tolerance(data.get('risk_tolerance', 'medium'))
        validated_data['timeframe'] = validate_timeframe(data.get('timeframe', '1m'))
        
        if 'investment_amount' in data and data['investment_amount'] is not None:
            validated_data['investment_amount'] = validate_investment_amount(data['investment_amount'])
        
        # 市場状況データの検証（簡易）
        if 'market_conditions' in data and data['market_conditions']:
            if not isinstance(data['market_conditions'], dict):
                raise ValueError("市場状況は辞書形式である必要があります")
            validated_data['market_conditions'] = data['market_conditions']
        
        return validated_data


class IfdocoGuideValidator:
    """IFDOCO注文ガイド用バリデータ"""
    
    @staticmethod
    def validate_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """リクエストデータのバリデーション"""
        validated_data = {}
        
        # 必須フィールド
        validated_data['stock_code'] = validate_stock_code(data.get('stock_code'))
        validated_data['entry_price'] = validate_price(data.get('entry_price'), "エントリー価格")
        validated_data['investment_amount'] = validate_investment_amount(data.get('investment_amount'))
        
        # オプションフィールド
        validated_data['logic_type'] = validate_logic_type(data.get('logic_type'))
        
        # リスクレベルの検証
        risk_level = data.get('risk_level', 'medium')
        valid_risk_levels = ['conservative', 'medium', 'aggressive']
        if risk_level not in valid_risk_levels:
            raise ValueError(f"リスクレベルは {', '.join(valid_risk_levels)} のいずれかである必要があります")
        validated_data['risk_level'] = risk_level
        
        # 保有期間の検証
        holding_period = data.get('holding_period', '1m')
        validated_data['holding_period'] = validate_timeframe(holding_period)
        
        return validated_data


class TradingHistoryValidator:
    """売買履歴用バリデータ"""
    
    @staticmethod
    def validate_filter(data: Dict[str, Any]) -> Dict[str, Any]:
        """フィルタパラメータのバリデーション"""
        validated_data = {}
        
        # オプションフィールド
        if 'stock_code' in data and data['stock_code']:
            validated_data['stock_code'] = validate_stock_code(data['stock_code'])
        
        if 'logic_type' in data and data['logic_type']:
            validated_data['logic_type'] = validate_logic_type(data['logic_type'])
        
        if 'trade_type' in data and data['trade_type']:
            validated_data['trade_type'] = validate_trade_type(data['trade_type'])
        
        if 'status' in data and data['status']:
            validated_data['status'] = validate_status(data['status'])
        
        # 日付範囲の検証
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        if date_from or date_to:
            # 文字列の場合はdatetimeに変換
            if isinstance(date_from, str):
                try:
                    date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("開始日の形式が正しくありません（ISO形式を使用してください）")
            
            if isinstance(date_to, str):
                try:
                    date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("終了日の形式が正しくありません（ISO形式を使用してください）")
            
            validated_data['date_from'], validated_data['date_to'] = validate_date_range(date_from, date_to)
        
        # 損益範囲の検証
        if 'min_profit_loss' in data and data['min_profit_loss'] is not None:
            try:
                validated_data['min_profit_loss'] = Decimal(str(data['min_profit_loss']))
            except (TypeError, ValueError):
                raise ValueError("最小損益は数値である必要があります")
        
        if 'max_profit_loss' in data and data['max_profit_loss'] is not None:
            try:
                validated_data['max_profit_loss'] = Decimal(str(data['max_profit_loss']))
            except (TypeError, ValueError):
                raise ValueError("最大損益は数値である必要があります")
        
        # ページネーション
        page = int(data.get('page', 1))
        limit = int(data.get('limit', 20))
        validated_data['page'], validated_data['limit'] = validate_pagination(page, limit)
        
        return validated_data


class SignalHistoryValidator:
    """シグナル履歴用バリデータ"""
    
    @staticmethod
    def validate_filter(data: Dict[str, Any]) -> Dict[str, Any]:
        """フィルタパラメータのバリデーション"""
        validated_data = {}
        
        # オプションフィールド
        if 'stock_code' in data and data['stock_code']:
            validated_data['stock_code'] = validate_stock_code(data['stock_code'])
        
        if 'signal_type' in data and data['signal_type']:
            # シグナル種別の簡易検証
            validated_data['signal_type'] = data['signal_type']
        
        if 'status' in data and data['status']:
            validated_data['status'] = validate_status(data['status'])
        
        if 'confidence_min' in data and data['confidence_min'] is not None:
            validated_data['confidence_min'] = validate_confidence_level(data['confidence_min'])
        
        # 日付範囲の検証（TradingHistoryValidatorと同様）
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        if date_from or date_to:
            if isinstance(date_from, str):
                try:
                    date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("開始日の形式が正しくありません（ISO形式を使用してください）")
            
            if isinstance(date_to, str):
                try:
                    date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("終了日の形式が正しくありません（ISO形式を使用してください）")
            
            validated_data['date_from'], validated_data['date_to'] = validate_date_range(date_from, date_to)
        
        # ページネーション
        page = int(data.get('page', 1))
        limit = int(data.get('limit', 20))
        validated_data['page'], validated_data['limit'] = validate_pagination(page, limit)
        
        return validated_data