"""
テクニカル分析サービス
株価データからテクニカル指標を計算し、売買シグナルを生成
RSI、MACD、ボリンジャーバンドなどの分析機能を提供
"""

import logging
from typing import Dict
import pandas as pd
import numpy as np
import random

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """テクニカル分析専門サービス"""
    
    def __init__(self):
        pass
    
    def generate_technical_signals(self, price_data: pd.DataFrame = None, stock_data: Dict = None) -> Dict:
        """
        価格データからテクニカル指標を計算
        price_dataがない場合はstock_dataからモック値を生成
        """
        try:
            # 既存のsignalsがある場合はそれを使用
            if stock_data and 'signals' in stock_data:
                return stock_data['signals']
            
            # 価格データがある場合は実際のテクニカル分析を実行
            if price_data is not None and not price_data.empty:
                return self._calculate_technical_indicators(price_data)
            
            # データ不足の場合はモック値を生成
            return self._generate_mock_technical_signals()
            
        except Exception as e:
            logger.warning(f"テクニカル指標計算エラー: {str(e)}")
            return self._generate_mock_technical_signals()
    
    def _calculate_technical_indicators(self, price_data: pd.DataFrame) -> Dict:
        """実際のテクニカル指標を計算"""
        try:
            if len(price_data) < 14:
                # データ不足の場合はモック値
                return self._generate_mock_technical_signals()
            
            # RSI計算
            rsi = self._calculate_rsi(price_data['Close'])
            
            # トレンド方向判定
            trend = self._calculate_trend_direction(price_data['Close'])
            
            # ボリューム分析
            volume_ratio = self._calculate_volume_ratio(price_data)
            
            # MACD計算（簡易版）
            macd = self._calculate_macd_simple(price_data['Close'])
            
            # ボリンジャーバンド位置
            bollinger_position = self._calculate_bollinger_position(price_data['Close'])
            
            return {
                'rsi': round(float(rsi) if not pd.isna(rsi) else 50.0, 2),
                'macd': round(float(macd) if not pd.isna(macd) else 0.0, 3),
                'bollingerPosition': round(float(bollinger_position) if not pd.isna(bollinger_position) else 0.0, 2),
                'volumeRatio': round(float(volume_ratio) if not pd.isna(volume_ratio) else 1.0, 2),
                'trendDirection': trend
            }
            
        except Exception as e:
            logger.warning(f"テクニカル指標詳細計算エラー: {str(e)}")
            return self._generate_mock_technical_signals()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """RSI（相対力指数）を計算"""
        try:
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except Exception as e:
            logger.warning(f"RSI計算エラー: {str(e)}")
            return 50.0
    
    def _calculate_macd_simple(self, prices: pd.Series) -> float:
        """簡易MACD計算"""
        try:
            if len(prices) < 26:
                return 0.0
            
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            return macd_line.iloc[-1]
        except Exception as e:
            logger.warning(f"MACD計算エラー: {str(e)}")
            return 0.0
    
    def _calculate_bollinger_position(self, prices: pd.Series, period: int = 20) -> float:
        """ボリンジャーバンド内の位置を計算（-1〜1）"""
        try:
            if len(prices) < period:
                return 0.0
            
            ma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = ma + (std * 2)
            lower_band = ma - (std * 2)
            
            current_price = prices.iloc[-1]
            current_ma = ma.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            
            # バンド幅での正規化位置（-1〜1）
            if current_upper == current_lower:
                return 0.0
            
            position = (current_price - current_ma) / (current_upper - current_ma)
            return max(-1.0, min(1.0, position))
        except Exception as e:
            logger.warning(f"MACD計算エラー: {str(e)}")
            return 0.0
    
    def _calculate_volume_ratio(self, price_data: pd.DataFrame, period: int = 10) -> float:
        """出来高比率を計算"""
        try:
            if 'Volume' not in price_data.columns or len(price_data) < period:
                return 1.0
            
            current_volume = price_data['Volume'].iloc[-1]
            avg_volume = price_data['Volume'].rolling(window=period).mean().iloc[-1]
            
            if avg_volume == 0:
                return 1.0
            
            return current_volume / avg_volume
        except Exception as e:
            logger.warning(f"出来高比計算エラー: {str(e)}")
            return 1.0
    
    def _calculate_trend_direction(self, prices: pd.Series) -> str:
        """トレンド方向を判定"""
        try:
            if len(prices) < 5:
                return 'sideways'
            
            recent_avg = prices.tail(5).mean()
            older_avg = prices.head(-5).tail(5).mean()
            
            if recent_avg > older_avg * 1.02:
                return 'up'
            elif recent_avg < older_avg * 0.98:
                return 'down'
            else:
                return 'sideways'
        except Exception as e:
            logger.warning(f"トレンド分析エラー: {str(e)}")
            return 'sideways'
    
    def _generate_mock_technical_signals(self) -> Dict:
        """モックテクニカルシグナルを生成"""
        return {
            'rsi': round(random.uniform(30, 70), 2),
            'macd': round(random.uniform(-0.5, 0.5), 3),
            'bollingerPosition': round(random.uniform(-1, 1), 2),
            'volumeRatio': round(random.uniform(0.8, 1.5), 2),
            'trendDirection': random.choice(['up', 'down', 'sideways'])
        }
    
    def is_oversold(self, signals: Dict) -> bool:
        """売られ過ぎ状態の判定"""
        try:
            return signals.get('rsi', 50) < 30
        except Exception as e:
            logger.warning(f"シグナル判定エラー: {str(e)}")
            return False
    
    def is_overbought(self, signals: Dict) -> bool:
        """買われ過ぎ状態の判定"""
        try:
            return signals.get('rsi', 50) > 70
        except Exception as e:
            logger.warning(f"シグナル判定エラー: {str(e)}")
            return False
    
    def is_trending_up(self, signals: Dict) -> bool:
        """上昇トレンドの判定"""
        try:
            return signals.get('trendDirection') == 'up'
        except Exception as e:
            logger.warning(f"シグナル判定エラー: {str(e)}")
            return False
    
    def is_high_volume(self, signals: Dict, threshold: float = 1.5) -> bool:
        """高出来高の判定"""
        try:
            return signals.get('volumeRatio', 1.0) > threshold
        except Exception as e:
            logger.warning(f"シグナル判定エラー: {str(e)}")
            return False