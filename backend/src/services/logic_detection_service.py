"""
ロジック検出サービス
ストップ高張り付き（ロジックA）と赤字→黒字転換（ロジックB）の検出を専門に扱う
カスタムロジック追加や検出条件の調整も可能
"""

import logging
from typing import Dict, bool

logger = logging.getLogger(__name__)


class LogicDetectionService:
    """ロジック検出専門サービス"""
    
    def __init__(self):
        # ロジック検出の閾値設定
        self.logic_a_config = {
            'min_change_rate': 5.0,      # 最低上昇率（%）
            'min_volume': 10000000,      # 最低出来高
            'rsi_threshold': 70          # RSI閾値
        }
        
        self.logic_b_config = {
            'min_rsi': 60,              # RSI下限
            'min_change_rate': 2.0,     # 最低上昇率（%）
            'min_volume': 5000000,      # 最低出来高
            'rsi_recovery_threshold': 30 # RSI回復の基準値
        }
    
    async def detect_logic_a(self, stock_data: Dict) -> bool:
        """
        ロジックA: ストップ高張り付き銘柄の検出
        実装: 大幅な上昇（5%以上）+ 高出来高をストップ高張り付きとみなす
        """
        try:
            change_rate = stock_data.get('changeRate', 0)
            volume = stock_data.get('volume', 0)
            signals = stock_data.get('signals', {})
            rsi = signals.get('rsi', 50)
            
            # 基本条件: 大幅上昇 + 高出来高
            basic_condition = (
                change_rate >= self.logic_a_config['min_change_rate'] and
                volume > self.logic_a_config['min_volume']
            )
            
            # 補強条件: RSIが高い（買われ過ぎ状態）
            rsi_condition = rsi >= self.logic_a_config['rsi_threshold']
            
            # トレンド条件: 上昇トレンド
            trend_condition = signals.get('trendDirection') == 'up'
            
            # 出来高比率条件: 平均より高い出来高
            volume_ratio_condition = signals.get('volumeRatio', 1.0) > 1.5
            
            # 最低限の条件 + 補強条件の組み合わせで判定
            result = basic_condition and (rsi_condition or trend_condition or volume_ratio_condition)
            
            if result:
                logger.info(f"ロジックA検出: {stock_data.get('code')} - 変化率:{change_rate:.2f}%, 出来高:{volume:,}, RSI:{rsi:.1f}")
            
            return result
            
        except Exception as e:
            logger.warning(f"ロジックA検出エラー: {str(e)}")
            return False
    
    async def detect_logic_b(self, stock_data: Dict) -> bool:
        """
        ロジックB: 赤字→黒字転換銘柄の検出
        実装: RSIが30以下から60以上に上昇した銘柄（底値からの反転）
        """
        try:
            signals = stock_data.get('signals', {})
            rsi = signals.get('rsi', 50)
            change_rate = stock_data.get('changeRate', 0)
            volume = stock_data.get('volume', 0)
            
            # 基本条件: RSI回復 + 適度な上昇 + 出来高確保
            rsi_recovery_condition = rsi >= self.logic_b_config['min_rsi']
            price_recovery_condition = change_rate > self.logic_b_config['min_change_rate']
            volume_condition = volume > self.logic_b_config['min_volume']
            
            # 補強条件: トレンド転換
            trend_condition = signals.get('trendDirection') in ['up', 'sideways']
            
            # MACD転換シグナル（正値転換）
            macd_condition = signals.get('macd', 0) > 0
            
            # ボリンジャーバンド位置（底値圏からの脱出）
            bollinger_condition = signals.get('bollingerPosition', 0) > -0.5
            
            # 基本条件をすべて満たし、補強条件のいずれかを満たす
            basic_met = rsi_recovery_condition and price_recovery_condition and volume_condition
            reinforced = trend_condition or macd_condition or bollinger_condition
            
            result = basic_met and reinforced
            
            if result:
                logger.info(f"ロジックB検出: {stock_data.get('code')} - RSI:{rsi:.1f}, 変化率:{change_rate:.2f}%, 出来高:{volume:,}")
            
            return result
            
        except Exception as e:
            logger.warning(f"ロジックB検出エラー: {str(e)}")
            return False
    
    def get_logic_a_description(self) -> str:
        """ロジックAの説明を返す"""
        return f"ストップ高張り付き検出: 上昇率{self.logic_a_config['min_change_rate']}%以上 + 出来高{self.logic_a_config['min_volume']:,}以上"
    
    def get_logic_b_description(self) -> str:
        """ロジックBの説明を返す"""
        return f"赤字→黒字転換検出: RSI{self.logic_b_config['min_rsi']}以上 + 上昇率{self.logic_b_config['min_change_rate']}%以上"
    
    def update_logic_a_config(self, **kwargs) -> None:
        """ロジックAの設定を更新"""
        for key, value in kwargs.items():
            if key in self.logic_a_config:
                self.logic_a_config[key] = value
                logger.info(f"ロジックA設定更新: {key} = {value}")
    
    def update_logic_b_config(self, **kwargs) -> None:
        """ロジックBの設定を更新"""
        for key, value in kwargs.items():
            if key in self.logic_b_config:
                self.logic_b_config[key] = value
                logger.info(f"ロジックB設定更新: {key} = {value}")
    
    def get_logic_configs(self) -> Dict:
        """現在のロジック設定を取得"""
        return {
            'logic_a': self.logic_a_config.copy(),
            'logic_b': self.logic_b_config.copy()
        }
    
    async def detect_custom_logic(self, stock_data: Dict, logic_name: str, conditions: Dict) -> bool:
        """
        カスタムロジックの検出（将来拡張用）
        """
        try:
            # カスタムロジックの実装例
            if logic_name == "volume_surge":
                volume_ratio = stock_data.get('signals', {}).get('volumeRatio', 1.0)
                threshold = conditions.get('volume_threshold', 3.0)
                return volume_ratio > threshold
            
            elif logic_name == "rsi_divergence":
                rsi = stock_data.get('signals', {}).get('rsi', 50)
                change_rate = stock_data.get('changeRate', 0)
                return rsi < 30 and change_rate > 0  # RSI低いが価格上昇
            
            # 追加ロジックはここに実装
            return False
            
        except Exception as e:
            logger.warning(f"カスタムロジック検出エラー {logic_name}: {str(e)}")
            return False
    
    def validate_stock_data(self, stock_data: Dict) -> bool:
        """株価データの妥当性検証"""
        required_fields = ['code', 'name', 'price', 'changeRate', 'volume']
        
        try:
            # 必須フィールドの存在確認
            for field in required_fields:
                if field not in stock_data:
                    logger.warning(f"必須フィールド不足: {field}")
                    return False
            
            # データ型と範囲の検証
            price = stock_data.get('price', 0)
            volume = stock_data.get('volume', 0)
            
            if price <= 0:
                logger.warning(f"不正な株価: {price}")
                return False
            
            if volume < 0:
                logger.warning(f"不正な出来高: {volume}")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"データ検証エラー: {str(e)}")
            return False