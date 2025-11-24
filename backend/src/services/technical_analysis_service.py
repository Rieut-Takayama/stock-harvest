"""
テクニカル分析サービス
Yahoo Finance APIを使用した高度なテクニカル指標計算

機能:
- RSI, MACD, ボリンジャーバンド等の基本指標
- トレンド分析（移動平均線、方向性）
- サポート・レジスタンス分析
- 出来高分析
- ボラティリティ分析
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """テクニカル分析専門サービス"""
    
    def __init__(self):
        # テクニカル分析設定
        self.config = {
            # RSI設定
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            
            # MACD設定  
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # ボリンジャーバンド設定
            'bb_period': 20,
            'bb_std': 2,
            
            # 移動平均設定
            'ma_short': 20,
            'ma_medium': 50,
            'ma_long': 200,
            
            # 出来高設定
            'volume_ma_period': 20,
            
            # データ取得設定
            'data_period': '3mo',  # 3ヶ月分のデータ
            'data_interval': '1d',  # 日足データ
        }
        
        # キャッシュ管理
        self.price_data_cache = {}
        self.cache_expiry = {}
    
    async def analyze_stock_technical(self, stock_code: str) -> Dict:
        """
        指定銘柄の包括的テクニカル分析実行
        """
        try:
            # 価格データ取得
            price_data = await self._get_price_data(stock_code)
            if price_data is None or len(price_data) < 50:
                return self._create_error_result('十分な価格データが取得できません')
            
            # 各種テクニカル指標計算
            analysis_results = {}
            
            # 1. RSI分析
            analysis_results['rsi'] = await self._calculate_rsi(price_data)
            
            # 2. MACD分析
            analysis_results['macd'] = await self._calculate_macd(price_data)
            
            # 3. ボリンジャーバンド分析
            analysis_results['bollinger'] = await self._calculate_bollinger_bands(price_data)
            
            # 4. 移動平均線分析
            analysis_results['moving_averages'] = await self._calculate_moving_averages(price_data)
            
            # 5. トレンド分析
            analysis_results['trend'] = await self._analyze_trend(price_data)
            
            # 6. サポート・レジスタンス分析
            analysis_results['support_resistance'] = await self._analyze_support_resistance(price_data)
            
            # 7. 出来高分析
            analysis_results['volume'] = await self._analyze_volume(price_data)
            
            # 8. ボラティリティ分析
            analysis_results['volatility'] = await self._analyze_volatility(price_data)
            
            # 9. 価格パターン分析
            analysis_results['patterns'] = await self._analyze_price_patterns(price_data)
            
            # 10. 総合スコア計算
            analysis_results['overall'] = await self._calculate_overall_score(analysis_results)
            
            # 最新の価格情報を追加
            latest_data = price_data.iloc[-1]
            analysis_results['current_price'] = {
                'price': float(latest_data['Close']),
                'volume': int(latest_data['Volume']),
                'date': latest_data.name.strftime('%Y-%m-%d'),
                'change': float(latest_data['Close'] - latest_data['Open']),
                'change_rate': float((latest_data['Close'] - latest_data['Open']) / latest_data['Open'] * 100)
            }
            
            logger.info(f"テクニカル分析完了: {stock_code} - 総合スコア:{analysis_results['overall']['score']:.1f}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"テクニカル分析エラー {stock_code}: {str(e)}")
            return self._create_error_result(f'分析エラー: {str(e)}')
    
    async def _get_price_data(self, stock_code: str) -> Optional[pd.DataFrame]:
        """価格データ取得（キャッシュ機能付き）"""
        try:
            # キャッシュチェック
            current_time = datetime.now()
            if (stock_code in self.price_data_cache and 
                stock_code in self.cache_expiry and
                current_time < self.cache_expiry[stock_code]):
                logger.debug(f"キャッシュから価格データ取得: {stock_code}")
                return self.price_data_cache[stock_code]
            
            # Yahoo Financeから取得
            # 日本株の場合は.Tサフィックスを追加
            symbol = f"{stock_code}.T" if stock_code.isdigit() else stock_code
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                period=self.config['data_period'],
                interval=self.config['data_interval']
            )
            
            if data.empty:
                logger.warning(f"価格データが取得できません: {stock_code}")
                return None
            
            # 必要な指標を事前計算
            data = await self._preprocess_price_data(data)
            
            # キャッシュに保存（5分間有効）
            self.price_data_cache[stock_code] = data
            self.cache_expiry[stock_code] = current_time + timedelta(minutes=5)
            
            logger.debug(f"価格データ取得完了: {stock_code} - {len(data)}件")
            return data
            
        except Exception as e:
            logger.warning(f"価格データ取得エラー {stock_code}: {str(e)}")
            return None
    
    async def _preprocess_price_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """価格データの前処理"""
        try:
            # 基本的な価格計算
            data['HL2'] = (data['High'] + data['Low']) / 2
            data['HLC3'] = (data['High'] + data['Low'] + data['Close']) / 3
            data['OHLC4'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
            
            # True Range計算
            data['TR'] = np.maximum(
                data['High'] - data['Low'],
                np.maximum(
                    abs(data['High'] - data['Close'].shift(1)),
                    abs(data['Low'] - data['Close'].shift(1))
                )
            )
            
            # 価格変動率
            data['Returns'] = data['Close'].pct_change()
            
            return data
            
        except Exception as e:
            logger.warning(f"価格データ前処理エラー: {str(e)}")
            return data
    
    async def _calculate_rsi(self, data: pd.DataFrame) -> Dict:
        """RSI計算"""
        try:
            period = self.config['rsi_period']
            
            # 価格差分計算
            delta = data['Close'].diff()
            
            # 上昇・下降分離
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # 移動平均計算
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # RSI計算
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50
            
            # シグナル判定
            signal = 'NEUTRAL'
            if current_rsi > self.config['rsi_overbought']:
                signal = 'OVERBOUGHT'
            elif current_rsi < self.config['rsi_oversold']:
                signal = 'OVERSOLD'
            
            # 強度計算
            if current_rsi > 70:
                strength = 100 - current_rsi  # 買われ過ぎほど低スコア
            elif current_rsi < 30:
                strength = current_rsi + 40    # 売られ過ぎは回復期待
            else:
                strength = 70                  # 正常範囲
            
            return {
                'current': current_rsi,
                'signal': signal,
                'strength': strength,
                'overbought_level': self.config['rsi_overbought'],
                'oversold_level': self.config['rsi_oversold'],
                'interpretation': self._interpret_rsi(current_rsi)
            }
            
        except Exception as e:
            logger.warning(f"RSI計算エラー: {str(e)}")
            return {'current': 50, 'signal': 'ERROR', 'error': str(e)}
    
    async def _calculate_macd(self, data: pd.DataFrame) -> Dict:
        """MACD計算"""
        try:
            fast_period = self.config['macd_fast']
            slow_period = self.config['macd_slow']
            signal_period = self.config['macd_signal']
            
            # 指数移動平均計算
            ema_fast = data['Close'].ewm(span=fast_period).mean()
            ema_slow = data['Close'].ewm(span=slow_period).mean()
            
            # MACD線計算
            macd_line = ema_fast - ema_slow
            
            # シグナル線計算
            signal_line = macd_line.ewm(span=signal_period).mean()
            
            # ヒストグラム計算
            histogram = macd_line - signal_line
            
            # 現在値
            current_macd = float(macd_line.iloc[-1]) if not macd_line.empty else 0
            current_signal = float(signal_line.iloc[-1]) if not signal_line.empty else 0
            current_histogram = float(histogram.iloc[-1]) if not histogram.empty else 0
            
            # シグナル判定
            signal = 'NEUTRAL'
            if current_macd > current_signal and current_histogram > 0:
                signal = 'BUY'
            elif current_macd < current_signal and current_histogram < 0:
                signal = 'SELL'
            
            # 強度計算
            strength = 50 + (current_histogram * 10)  # ヒストグラムベース
            strength = max(0, min(100, strength))
            
            return {
                'macd': current_macd,
                'signal_line': current_signal,
                'histogram': current_histogram,
                'signal': signal,
                'strength': strength,
                'interpretation': self._interpret_macd(current_macd, current_signal, current_histogram)
            }
            
        except Exception as e:
            logger.warning(f"MACD計算エラー: {str(e)}")
            return {'macd': 0, 'signal': 'ERROR', 'error': str(e)}
    
    async def _calculate_bollinger_bands(self, data: pd.DataFrame) -> Dict:
        """ボリンジャーバンド計算"""
        try:
            period = self.config['bb_period']
            std_dev = self.config['bb_std']
            
            # 移動平均
            ma = data['Close'].rolling(window=period).mean()
            
            # 標準偏差
            std = data['Close'].rolling(window=period).std()
            
            # ボリンジャーバンド
            upper = ma + (std * std_dev)
            lower = ma - (std * std_dev)
            
            # 現在値
            current_price = float(data['Close'].iloc[-1])
            current_upper = float(upper.iloc[-1]) if not upper.empty else current_price
            current_lower = float(lower.iloc[-1]) if not lower.empty else current_price
            current_ma = float(ma.iloc[-1]) if not ma.empty else current_price
            
            # バンド内位置計算（-1から1の範囲）
            band_width = current_upper - current_lower
            if band_width > 0:
                position = (current_price - current_lower) / band_width * 2 - 1
            else:
                position = 0
            
            # シグナル判定
            signal = 'NEUTRAL'
            if position > 0.8:
                signal = 'OVERBOUGHT'
            elif position < -0.8:
                signal = 'OVERSOLD'
            elif position > 0.2:
                signal = 'UPPER_TREND'
            elif position < -0.2:
                signal = 'LOWER_TREND'
            
            # 強度計算
            if position > 0:
                strength = 50 + (position * 25)
            else:
                strength = 50 + (position * 25)
            
            return {
                'upper': current_upper,
                'middle': current_ma,
                'lower': current_lower,
                'position': position,
                'width': band_width,
                'signal': signal,
                'strength': strength,
                'interpretation': self._interpret_bollinger(position)
            }
            
        except Exception as e:
            logger.warning(f"ボリンジャーバンド計算エラー: {str(e)}")
            return {'signal': 'ERROR', 'error': str(e)}
    
    async def _calculate_moving_averages(self, data: pd.DataFrame) -> Dict:
        """移動平均線計算"""
        try:
            # 各期間の移動平均
            ma_short = data['Close'].rolling(window=self.config['ma_short']).mean()
            ma_medium = data['Close'].rolling(window=self.config['ma_medium']).mean()
            ma_long = data['Close'].rolling(window=self.config['ma_long']).mean()
            
            # 現在値
            current_price = float(data['Close'].iloc[-1])
            current_short = float(ma_short.iloc[-1]) if not ma_short.empty else current_price
            current_medium = float(ma_medium.iloc[-1]) if not ma_medium.empty else current_price
            current_long = float(ma_long.iloc[-1]) if not ma_long.empty else current_price
            
            # トレンド判定
            trend = 'NEUTRAL'
            strength = 50
            
            if current_short > current_medium > current_long:
                trend = 'STRONG_UP'
                strength = 85
            elif current_short > current_medium:
                trend = 'UP'
                strength = 70
            elif current_short < current_medium < current_long:
                trend = 'STRONG_DOWN'
                strength = 15
            elif current_short < current_medium:
                trend = 'DOWN'
                strength = 30
            
            # 価格と移動平均の位置関係
            price_position = self._calculate_price_position(
                current_price, current_short, current_medium, current_long
            )
            
            return {
                'ma20': current_short,
                'ma50': current_medium,
                'ma200': current_long,
                'trend': trend,
                'strength': strength,
                'price_position': price_position,
                'interpretation': self._interpret_moving_averages(trend, price_position)
            }
            
        except Exception as e:
            logger.warning(f"移動平均計算エラー: {str(e)}")
            return {'trend': 'ERROR', 'error': str(e)}
    
    async def _analyze_trend(self, data: pd.DataFrame) -> Dict:
        """トレンド分析"""
        try:
            # 複数期間でのトレンド分析
            periods = [5, 10, 20]
            trend_scores = []
            
            for period in periods:
                if len(data) >= period:
                    # 線形回帰でトレンド方向を判定
                    y = data['Close'].tail(period).values
                    x = np.arange(len(y))
                    
                    if len(y) > 1:
                        slope = np.polyfit(x, y, 1)[0]
                        trend_scores.append(slope)
            
            # 平均トレンド強度
            avg_slope = np.mean(trend_scores) if trend_scores else 0
            
            # トレンド判定
            if avg_slope > 0.5:
                direction = 'STRONG_UP'
                strength = min(100, 70 + abs(avg_slope) * 10)
            elif avg_slope > 0.1:
                direction = 'UP'
                strength = min(80, 60 + abs(avg_slope) * 20)
            elif avg_slope < -0.5:
                direction = 'STRONG_DOWN'
                strength = max(0, 30 - abs(avg_slope) * 10)
            elif avg_slope < -0.1:
                direction = 'DOWN'
                strength = max(20, 40 - abs(avg_slope) * 20)
            else:
                direction = 'SIDEWAYS'
                strength = 50
            
            # トレンドの持続性分析
            consistency = self._analyze_trend_consistency(data)
            
            return {
                'direction': direction,
                'strength': strength,
                'slope': avg_slope,
                'consistency': consistency,
                'interpretation': self._interpret_trend(direction, strength)
            }
            
        except Exception as e:
            logger.warning(f"トレンド分析エラー: {str(e)}")
            return {'direction': 'ERROR', 'error': str(e)}
    
    async def _analyze_support_resistance(self, data: pd.DataFrame) -> Dict:
        """サポート・レジスタンス分析"""
        try:
            if len(data) < 20:
                return {'error': 'データ不足'}
            
            # ピークとボトムを検出
            highs = data['High'].rolling(window=5, center=True).max()
            lows = data['Low'].rolling(window=5, center=True).min()
            
            # 現在価格
            current_price = float(data['Close'].iloc[-1])
            
            # 最近の高値・安値（20日以内）
            recent_data = data.tail(20)
            resistance_levels = []
            support_levels = []
            
            for i in range(2, len(recent_data) - 2):
                # 高値レジスタンス候補
                if (recent_data['High'].iloc[i] >= recent_data['High'].iloc[i-1] and
                    recent_data['High'].iloc[i] >= recent_data['High'].iloc[i-2] and
                    recent_data['High'].iloc[i] >= recent_data['High'].iloc[i+1] and
                    recent_data['High'].iloc[i] >= recent_data['High'].iloc[i+2]):
                    resistance_levels.append(float(recent_data['High'].iloc[i]))
                
                # 安値サポート候補
                if (recent_data['Low'].iloc[i] <= recent_data['Low'].iloc[i-1] and
                    recent_data['Low'].iloc[i] <= recent_data['Low'].iloc[i-2] and
                    recent_data['Low'].iloc[i] <= recent_data['Low'].iloc[i+1] and
                    recent_data['Low'].iloc[i] <= recent_data['Low'].iloc[i+2]):
                    support_levels.append(float(recent_data['Low'].iloc[i]))
            
            # 最も近いサポート・レジスタンス
            resistance_levels = [r for r in resistance_levels if r > current_price]
            support_levels = [s for s in support_levels if s < current_price]
            
            nearest_resistance = min(resistance_levels) if resistance_levels else None
            nearest_support = max(support_levels) if support_levels else None
            
            # 価格位置分析
            position_analysis = self._analyze_price_position(
                current_price, nearest_support, nearest_resistance
            )
            
            return {
                'nearest_resistance': nearest_resistance,
                'nearest_support': nearest_support,
                'resistance_levels': resistance_levels[:3],  # 上位3つ
                'support_levels': support_levels[-3:],       # 下位3つ
                'position_analysis': position_analysis,
                'interpretation': self._interpret_support_resistance(position_analysis)
            }
            
        except Exception as e:
            logger.warning(f"サポート・レジスタンス分析エラー: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """出来高分析"""
        try:
            # 出来高移動平均
            volume_ma = data['Volume'].rolling(window=self.config['volume_ma_period']).mean()
            
            current_volume = int(data['Volume'].iloc[-1])
            avg_volume = float(volume_ma.iloc[-1]) if not volume_ma.empty else current_volume
            
            # 出来高比率
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # 出来高トレンド
            volume_trend = self._analyze_volume_trend(data['Volume'])
            
            # OBV (On Balance Volume) 計算
            obv = self._calculate_obv(data)
            
            # シグナル判定
            signal = 'NORMAL'
            strength = 50
            
            if volume_ratio > 3.0:
                signal = 'VERY_HIGH'
                strength = 90
            elif volume_ratio > 2.0:
                signal = 'HIGH'
                strength = 80
            elif volume_ratio > 1.5:
                signal = 'ABOVE_AVERAGE'
                strength = 70
            elif volume_ratio < 0.5:
                signal = 'LOW'
                strength = 30
            
            return {
                'current': current_volume,
                'average': avg_volume,
                'ratio': volume_ratio,
                'trend': volume_trend,
                'obv': obv,
                'signal': signal,
                'strength': strength,
                'interpretation': self._interpret_volume(signal, volume_ratio)
            }
            
        except Exception as e:
            logger.warning(f"出来高分析エラー: {str(e)}")
            return {'signal': 'ERROR', 'error': str(e)}
    
    async def _analyze_volatility(self, data: pd.DataFrame) -> Dict:
        """ボラティリティ分析"""
        try:
            # ATR (Average True Range) 計算
            atr_period = 14
            atr = data['TR'].rolling(window=atr_period).mean()
            current_atr = float(atr.iloc[-1]) if not atr.empty else 0
            
            # 価格に対するATR比率
            current_price = float(data['Close'].iloc[-1])
            atr_percentage = (current_atr / current_price * 100) if current_price > 0 else 0
            
            # 日次リターンのボラティリティ
            returns_volatility = float(data['Returns'].std() * 100) if 'Returns' in data.columns else 0
            
            # ボラティリティレベル判定
            if atr_percentage > 5:
                level = 'VERY_HIGH'
                strength = 20
            elif atr_percentage > 3:
                level = 'HIGH'
                strength = 40
            elif atr_percentage > 2:
                level = 'MEDIUM'
                strength = 60
            elif atr_percentage > 1:
                level = 'LOW'
                strength = 80
            else:
                level = 'VERY_LOW'
                strength = 90
            
            return {
                'atr': current_atr,
                'atr_percentage': atr_percentage,
                'returns_volatility': returns_volatility,
                'level': level,
                'strength': strength,
                'interpretation': self._interpret_volatility(level, atr_percentage)
            }
            
        except Exception as e:
            logger.warning(f"ボラティリティ分析エラー: {str(e)}")
            return {'level': 'ERROR', 'error': str(e)}
    
    async def _analyze_price_patterns(self, data: pd.DataFrame) -> Dict:
        """価格パターン分析"""
        try:
            patterns = []
            
            # 基本的なローソク足パターン検出
            if len(data) >= 3:
                latest = data.iloc[-1]
                prev1 = data.iloc[-2]
                prev2 = data.iloc[-3]
                
                # ドージパターン
                if abs(latest['Open'] - latest['Close']) < (latest['High'] - latest['Low']) * 0.1:
                    patterns.append('DOJI')
                
                # ハンマー・逆ハンマー
                body = abs(latest['Close'] - latest['Open'])
                upper_shadow = latest['High'] - max(latest['Open'], latest['Close'])
                lower_shadow = min(latest['Open'], latest['Close']) - latest['Low']
                
                if body > 0:
                    if lower_shadow > body * 2 and upper_shadow < body * 0.5:
                        patterns.append('HAMMER')
                    elif upper_shadow > body * 2 and lower_shadow < body * 0.5:
                        patterns.append('INVERTED_HAMMER')
                
                # 連続パターン
                if (latest['Close'] > prev1['Close'] > prev2['Close']):
                    patterns.append('THREE_UP')
                elif (latest['Close'] < prev1['Close'] < prev2['Close']):
                    patterns.append('THREE_DOWN')
            
            # パターンの強度計算
            pattern_strength = len(patterns) * 20 if patterns else 50
            
            return {
                'patterns': patterns,
                'strength': min(100, pattern_strength),
                'interpretation': self._interpret_patterns(patterns)
            }
            
        except Exception as e:
            logger.warning(f"価格パターン分析エラー: {str(e)}")
            return {'patterns': [], 'error': str(e)}
    
    async def _calculate_overall_score(self, analysis_results: Dict) -> Dict:
        """総合スコア計算"""
        try:
            # 各指標の重み
            weights = {
                'rsi': 0.2,
                'macd': 0.2,
                'bollinger': 0.15,
                'moving_averages': 0.15,
                'trend': 0.15,
                'volume': 0.1,
                'volatility': 0.05
            }
            
            # 各スコア取得
            scores = {}
            for indicator, weight in weights.items():
                if indicator in analysis_results and 'strength' in analysis_results[indicator]:
                    scores[indicator] = analysis_results[indicator]['strength'] * weight
                else:
                    scores[indicator] = 50 * weight  # デフォルト値
            
            # 総合スコア
            overall_score = sum(scores.values())
            
            # 信頼度計算
            available_indicators = len([k for k in weights.keys() if k in analysis_results])
            confidence = available_indicators / len(weights)
            
            # 総合判定
            if overall_score >= 80:
                judgment = 'VERY_BULLISH'
            elif overall_score >= 65:
                judgment = 'BULLISH'
            elif overall_score >= 50:
                judgment = 'NEUTRAL'
            elif overall_score >= 35:
                judgment = 'BEARISH'
            else:
                judgment = 'VERY_BEARISH'
            
            return {
                'score': overall_score,
                'judgment': judgment,
                'confidence': confidence,
                'component_scores': scores,
                'interpretation': self._interpret_overall_score(judgment, overall_score)
            }
            
        except Exception as e:
            logger.warning(f"総合スコア計算エラー: {str(e)}")
            return {'score': 50, 'judgment': 'ERROR', 'error': str(e)}
    
    # ヘルパーメソッド群
    
    def _create_error_result(self, message: str) -> Dict:
        """エラー結果作成"""
        return {
            'error': message,
            'overall': {'score': 50, 'judgment': 'ERROR'}
        }
    
    def _interpret_rsi(self, rsi: float) -> str:
        """RSI解釈"""
        if rsi > 80:
            return '極度の買われ過ぎ状態'
        elif rsi > 70:
            return '買われ過ぎ状態'
        elif rsi > 50:
            return '上昇圧力あり'
        elif rsi > 30:
            return '下降圧力あり'
        elif rsi > 20:
            return '売られ過ぎ状態'
        else:
            return '極度の売られ過ぎ状態'
    
    def _interpret_macd(self, macd: float, signal: float, histogram: float) -> str:
        """MACD解釈"""
        if macd > signal and histogram > 0:
            return '強い上昇トレンド継続中'
        elif macd > signal and histogram < 0:
            return '上昇トレンドだが勢い減速'
        elif macd < signal and histogram > 0:
            return '下降トレンドだが底打ち兆候'
        else:
            return '下降トレンド継続中'
    
    def _interpret_bollinger(self, position: float) -> str:
        """ボリンジャーバンド解釈"""
        if position > 0.8:
            return 'アッパーバンド付近（買われ過ぎ）'
        elif position > 0.2:
            return 'ミドルライン上方（上昇傾向）'
        elif position > -0.2:
            return 'ミドルライン付近（レンジ相場）'
        elif position > -0.8:
            return 'ミドルライン下方（下降傾向）'
        else:
            return 'ローワーバンド付近（売られ過ぎ）'
    
    def _interpret_moving_averages(self, trend: str, position: dict) -> str:
        """移動平均解釈"""
        trend_descriptions = {
            'STRONG_UP': '強い上昇トレンド（黄金配列）',
            'UP': '上昇トレンド',
            'NEUTRAL': '横ばいトレンド',
            'DOWN': '下降トレンド',
            'STRONG_DOWN': '強い下降トレンド（デッドクロス）'
        }
        return trend_descriptions.get(trend, 'トレンド不明')
    
    def _interpret_trend(self, direction: str, strength: float) -> str:
        """トレンド解釈"""
        direction_map = {
            'STRONG_UP': '非常に強い上昇トレンド',
            'UP': '上昇トレンド',
            'SIDEWAYS': '横ばい・レンジ相場',
            'DOWN': '下降トレンド',
            'STRONG_DOWN': '非常に強い下降トレンド'
        }
        return f"{direction_map.get(direction, '不明')}（強度: {strength:.0f}）"
    
    def _interpret_support_resistance(self, position: dict) -> str:
        """サポート・レジスタンス解釈"""
        # 簡易実装
        return 'サポート・レジスタンス分析結果'
    
    def _interpret_volume(self, signal: str, ratio: float) -> str:
        """出来高解釈"""
        descriptions = {
            'VERY_HIGH': f'異常高出来高（{ratio:.1f}倍）- 注目度極大',
            'HIGH': f'高出来高（{ratio:.1f}倍）- 強い関心',
            'ABOVE_AVERAGE': f'やや高出来高（{ratio:.1f}倍）',
            'NORMAL': '通常出来高',
            'LOW': f'低出来高（{ratio:.1f}倍）- 関心薄'
        }
        return descriptions.get(signal, '出来高分析結果')
    
    def _interpret_volatility(self, level: str, percentage: float) -> str:
        """ボラティリティ解釈"""
        descriptions = {
            'VERY_HIGH': f'極高ボラティリティ（{percentage:.1f}%）',
            'HIGH': f'高ボラティリティ（{percentage:.1f}%）',
            'MEDIUM': f'中ボラティリティ（{percentage:.1f}%）',
            'LOW': f'低ボラティリティ（{percentage:.1f}%）',
            'VERY_LOW': f'極低ボラティリティ（{percentage:.1f}%）'
        }
        return descriptions.get(level, 'ボラティリティ分析結果')
    
    def _interpret_patterns(self, patterns: List[str]) -> str:
        """パターン解釈"""
        if not patterns:
            return '特徴的なパターンなし'
        
        pattern_descriptions = {
            'DOJI': '迷いのドージ（方向感なし）',
            'HAMMER': 'ハンマー（底値圏で買いシグナル）',
            'INVERTED_HAMMER': '逆ハンマー（天井圏で売りシグナル）',
            'THREE_UP': '3連続上昇',
            'THREE_DOWN': '3連続下降'
        }
        
        descriptions = [pattern_descriptions.get(p, p) for p in patterns]
        return '、'.join(descriptions)
    
    def _interpret_overall_score(self, judgment: str, score: float) -> str:
        """総合スコア解釈"""
        descriptions = {
            'VERY_BULLISH': f'非常に強気（{score:.0f}点）',
            'BULLISH': f'強気（{score:.0f}点）',
            'NEUTRAL': f'中立（{score:.0f}点）',
            'BEARISH': f'弱気（{score:.0f}点）',
            'VERY_BEARISH': f'非常に弱気（{score:.0f}点）'
        }
        return descriptions.get(judgment, f'判定不可（{score:.0f}点）')
    
    def _calculate_price_position(self, price: float, ma20: float, ma50: float, ma200: float) -> Dict:
        """価格位置計算"""
        return {
            'vs_ma20': (price - ma20) / ma20 * 100 if ma20 > 0 else 0,
            'vs_ma50': (price - ma50) / ma50 * 100 if ma50 > 0 else 0,
            'vs_ma200': (price - ma200) / ma200 * 100 if ma200 > 0 else 0,
        }
    
    def _analyze_trend_consistency(self, data: pd.DataFrame) -> float:
        """トレンドの一致度分析"""
        try:
            # 直近の価格変動の一致度を計算
            returns = data['Returns'].tail(10).dropna()
            if len(returns) < 5:
                return 50
            
            positive_count = (returns > 0).sum()
            consistency = (positive_count / len(returns)) * 100
            
            return consistency
            
        except Exception:
            return 50
    
    def _analyze_price_position(self, current: float, support: Optional[float], resistance: Optional[float]) -> Dict:
        """価格位置分析"""
        try:
            analysis = {
                'position': 'MIDDLE',
                'distance_to_resistance': None,
                'distance_to_support': None,
                'range_position': 0.5  # 0-1の範囲
            }
            
            if support is not None and resistance is not None:
                range_size = resistance - support
                if range_size > 0:
                    analysis['range_position'] = (current - support) / range_size
                    
                    if analysis['range_position'] > 0.8:
                        analysis['position'] = 'NEAR_RESISTANCE'
                    elif analysis['range_position'] < 0.2:
                        analysis['position'] = 'NEAR_SUPPORT'
            
            if resistance is not None:
                analysis['distance_to_resistance'] = (resistance - current) / current * 100
            
            if support is not None:
                analysis['distance_to_support'] = (current - support) / current * 100
            
            return analysis
            
        except Exception:
            return {'position': 'UNKNOWN'}
    
    def _analyze_volume_trend(self, volume_series: pd.Series) -> str:
        """出来高トレンド分析"""
        try:
            if len(volume_series) < 5:
                return 'INSUFFICIENT_DATA'
            
            recent_avg = volume_series.tail(5).mean()
            previous_avg = volume_series.tail(10).head(5).mean()
            
            if recent_avg > previous_avg * 1.2:
                return 'INCREASING'
            elif recent_avg < previous_avg * 0.8:
                return 'DECREASING'
            else:
                return 'STABLE'
                
        except Exception:
            return 'UNKNOWN'
    
    def _calculate_obv(self, data: pd.DataFrame) -> float:
        """OBV (On Balance Volume) 計算"""
        try:
            obv = 0
            prev_close = None
            
            for _, row in data.iterrows():
                if prev_close is not None:
                    if row['Close'] > prev_close:
                        obv += row['Volume']
                    elif row['Close'] < prev_close:
                        obv -= row['Volume']
                
                prev_close = row['Close']
            
            return float(obv)
            
        except Exception:
            return 0