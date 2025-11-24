"""
Stock Harvest AI 売買シグナル自動計算システム
統合シグナル計算エンジン - ロジックA・B統合版

機能:
- エントリータイミング自動判定
- 利確・損切り価格自動計算
- シグナル強度評価(0-100スコア)
- リスク・リワード比率算出
- アクション推奨生成(BUY/SELL/HOLD)
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import math

from .logic_detection_service import LogicDetectionService
from .technical_analysis_service import TechnicalAnalysisService
from .stock_data_service import StockDataService

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """シグナルタイプ定義"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WATCH = "WATCH"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


class RiskLevel(Enum):
    """リスクレベル定義"""
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class TradingSignalsService:
    """売買シグナル自動計算サービス"""
    
    def __init__(self):
        self.logic_service = LogicDetectionService()
        self.technical_service = TechnicalAnalysisService()
        self.stock_service = StockDataService()
        
        # シグナル計算設定
        self.signal_config = {
            # 基本設定
            'min_signal_strength': 60.0,          # 最低シグナル強度
            'strong_signal_threshold': 80.0,      # 強シグナル閾値
            'position_size_multiplier': 1.0,      # ポジションサイズ倍率
            
            # リスク管理設定
            'max_risk_per_trade': 0.02,           # トレード当たり最大リスク(2%)
            'min_risk_reward_ratio': 1.5,         # 最小リスク・リワード比率
            'max_portfolio_exposure': 0.10,       # 最大ポートフォリオ露出(10%)
            
            # エントリー・イグジット設定
            'entry_confirmation_minutes': 5,       # エントリー確認時間(分)
            'profit_target_method': 'adaptive',    # 利確方法: 'fixed'|'adaptive'
            'stop_loss_method': 'trailing',        # 損切り方法: 'fixed'|'trailing'
            'trailing_stop_percentage': 0.05,     # トレーリングストップ幅(5%)
            
            # マルチタイムフレーム設定
            'timeframes': ['1d', '1h', '15m'],     # 分析タイムフレーム
            'confirmation_timeframes': ['1d', '1h'], # 確認用タイムフレーム
            
            # フィルター設定
            'volume_filter_enabled': True,         # 出来高フィルター有効
            'trend_filter_enabled': True,          # トレンドフィルター有効
            'volatility_filter_enabled': True,     # ボラティリティフィルター有効
        }
        
        # アクティブシグナル管理
        self.active_signals = {}
        self.signal_history = []
        self.performance_metrics = {
            'total_signals': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'average_return': 0.0,
            'win_rate': 0.0,
            'max_drawdown': 0.0,
            'profit_factor': 1.0
        }
    
    async def calculate_integrated_signal(self, stock_data: Dict) -> Dict:
        """
        統合シグナル計算メイン関数
        ロジックA・Bの結果を統合し、最終的な売買シグナルを生成
        """
        try:
            stock_code = stock_data.get('code', '')
            
            # Step 1: 基本データ検証
            if not self._validate_stock_data(stock_data):
                return self._create_error_signal('データ検証失敗')
            
            # Step 2: 複数ロジック検出実行
            logic_results = await self._execute_all_logics(stock_data)
            
            # Step 3: テクニカル分析実行
            technical_analysis = await self._perform_technical_analysis(stock_data)
            
            # Step 4: マルチタイムフレーム分析
            timeframe_analysis = await self._analyze_multiple_timeframes(stock_code)
            
            # Step 5: シグナル統合計算
            integrated_signal = await self._integrate_signals(
                stock_data, logic_results, technical_analysis, timeframe_analysis
            )
            
            # Step 6: リスク・リワード分析
            risk_reward = await self._calculate_risk_reward(stock_data, integrated_signal)
            
            # Step 7: ポジションサイジング
            position_info = await self._calculate_position_size(stock_data, risk_reward)
            
            # Step 8: 最終シグナル生成
            final_signal = await self._generate_final_signal(
                stock_data, integrated_signal, risk_reward, position_info
            )
            
            # Step 9: アクティブシグナル管理
            await self._manage_active_signals(stock_code, final_signal)
            
            # Step 10: パフォーマンス記録
            await self._record_signal_performance(final_signal)
            
            logger.info(f"統合シグナル計算完了: {stock_code} - {final_signal['action']}, 強度:{final_signal['signal_strength']}")
            
            return final_signal
            
        except Exception as e:
            logger.error(f"統合シグナル計算エラー: {str(e)}")
            return self._create_error_signal(f'計算エラー: {str(e)}')
    
    async def _execute_all_logics(self, stock_data: Dict) -> Dict:
        """すべてのロジックを実行し結果を統合"""
        try:
            results = {}
            
            # ロジックA (従来版)
            logic_a_result = await self.logic_service.detect_logic_a(stock_data)
            results['logic_a'] = {
                'detected': logic_a_result,
                'confidence': 0.7 if logic_a_result else 0.0,
                'weight': 0.3
            }
            
            # ロジックA (強化版)
            logic_a_enhanced = await self.logic_service.detect_logic_a_enhanced(stock_data)
            results['logic_a_enhanced'] = {
                'detected': logic_a_enhanced.get('detected', False),
                'details': logic_a_enhanced,
                'confidence': logic_a_enhanced.get('signal_strength', 0) / 100 if logic_a_enhanced.get('detected') else 0.0,
                'weight': 0.4
            }
            
            # ロジックB
            logic_b_result = await self.logic_service.detect_logic_b(stock_data)
            results['logic_b'] = {
                'detected': logic_b_result,
                'confidence': 0.6 if logic_b_result else 0.0,
                'weight': 0.3
            }
            
            # 総合評価
            total_score = sum(
                r['confidence'] * r['weight'] 
                for r in results.values() if r['detected']
            )
            
            results['integrated_score'] = total_score
            results['any_detected'] = any(r['detected'] for r in results.values())
            
            return results
            
        except Exception as e:
            logger.warning(f"ロジック実行エラー: {str(e)}")
            return {'error': str(e)}
    
    async def _perform_technical_analysis(self, stock_data: Dict) -> Dict:
        """テクニカル分析実行"""
        try:
            # 基本テクニカル指標
            signals = stock_data.get('signals', {})
            
            analysis = {
                'momentum': await self._analyze_momentum(signals),
                'trend': await self._analyze_trend(signals),
                'volume': await self._analyze_volume(stock_data),
                'support_resistance': await self._analyze_support_resistance(stock_data),
                'volatility': await self._analyze_volatility(stock_data),
            }
            
            # 総合テクニカルスコア
            technical_scores = [a.get('score', 0) for a in analysis.values()]
            analysis['overall_score'] = sum(technical_scores) / len(technical_scores) if technical_scores else 0
            
            return analysis
            
        except Exception as e:
            logger.warning(f"テクニカル分析エラー: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_momentum(self, signals: Dict) -> Dict:
        """モメンタム分析"""
        try:
            rsi = signals.get('rsi', 50)
            macd = signals.get('macd', 0)
            roc = signals.get('roc', 0)  # Rate of Change
            
            # モメンタムスコア計算
            momentum_factors = []
            
            # RSI評価
            if 30 <= rsi <= 70:
                momentum_factors.append(0.7)  # 適正範囲
            elif rsi > 70:
                momentum_factors.append(0.9)  # 強い上昇モメンタム
            else:
                momentum_factors.append(0.3)  # 弱いモメンタム
            
            # MACD評価
            if macd > 0:
                momentum_factors.append(0.8)
            else:
                momentum_factors.append(0.4)
            
            # ROC評価
            if roc > 5:
                momentum_factors.append(0.9)
            elif roc > 0:
                momentum_factors.append(0.7)
            else:
                momentum_factors.append(0.3)
            
            score = sum(momentum_factors) / len(momentum_factors) * 100
            
            return {
                'score': score,
                'rsi': rsi,
                'macd': macd,
                'roc': roc,
                'interpretation': self._interpret_momentum(score)
            }
            
        except Exception as e:
            logger.warning(f"モメンタム分析エラー: {str(e)}")
            return {'score': 50, 'error': str(e)}
    
    async def _analyze_trend(self, signals: Dict) -> Dict:
        """トレンド分析"""
        try:
            trend_direction = signals.get('trendDirection', 'sideways')
            moving_average_20 = signals.get('ma20', 0)
            moving_average_50 = signals.get('ma50', 0)
            bollinger_position = signals.get('bollingerPosition', 0)
            
            # トレンドスコア計算
            trend_score = 50  # 中立
            
            if trend_direction == 'up':
                trend_score = 80
            elif trend_direction == 'down':
                trend_score = 20
            else:  # sideways
                trend_score = 50
            
            # 移動平均線クロス
            if moving_average_20 > moving_average_50:
                trend_score += 10
            else:
                trend_score -= 10
            
            # ボリンジャーバンド位置
            if bollinger_position > 0.5:
                trend_score += 5
            elif bollinger_position < -0.5:
                trend_score -= 5
            
            trend_score = max(0, min(100, trend_score))
            
            return {
                'score': trend_score,
                'direction': trend_direction,
                'ma_cross': 'bullish' if moving_average_20 > moving_average_50 else 'bearish',
                'bollinger_position': bollinger_position,
                'interpretation': self._interpret_trend(trend_score)
            }
            
        except Exception as e:
            logger.warning(f"トレンド分析エラー: {str(e)}")
            return {'score': 50, 'error': str(e)}
    
    async def _analyze_volume(self, stock_data: Dict) -> Dict:
        """出来高分析"""
        try:
            volume = stock_data.get('volume', 0)
            signals = stock_data.get('signals', {})
            volume_ratio = signals.get('volumeRatio', 1.0)
            
            # 出来高スコア計算
            if volume_ratio >= 3.0:
                volume_score = 95  # 異常高出来高
            elif volume_ratio >= 2.0:
                volume_score = 85  # 高出来高
            elif volume_ratio >= 1.5:
                volume_score = 75  # やや高出来高
            elif volume_ratio >= 1.0:
                volume_score = 60  # 平均的
            elif volume_ratio >= 0.5:
                volume_score = 40  # やや低出来高
            else:
                volume_score = 20  # 低出来高
            
            return {
                'score': volume_score,
                'volume': volume,
                'volume_ratio': volume_ratio,
                'interpretation': self._interpret_volume(volume_score, volume_ratio)
            }
            
        except Exception as e:
            logger.warning(f"出来高分析エラー: {str(e)}")
            return {'score': 50, 'error': str(e)}
    
    async def _analyze_support_resistance(self, stock_data: Dict) -> Dict:
        """サポート・レジスタンス分析"""
        try:
            price = stock_data.get('price', 0)
            change_rate = stock_data.get('changeRate', 0)
            signals = stock_data.get('signals', {})
            
            # 簡易サポート・レジスタンス計算
            # より詳細な実装には過去の価格データが必要
            
            score = 50  # 中立
            
            # 価格変動率からサポート・レジスタンス近接度を推定
            if abs(change_rate) < 1:
                score = 45  # 横ばい、サポート・レジスタンス付近
            elif change_rate > 5:
                score = 70  # レジスタンス突破
            elif change_rate < -5:
                score = 30  # サポート割れ
            
            return {
                'score': score,
                'price': price,
                'change_rate': change_rate,
                'interpretation': self._interpret_support_resistance(score)
            }
            
        except Exception as e:
            logger.warning(f"サポート・レジスタンス分析エラー: {str(e)}")
            return {'score': 50, 'error': str(e)}
    
    async def _analyze_volatility(self, stock_data: Dict) -> Dict:
        """ボラティリティ分析"""
        try:
            change_rate = abs(stock_data.get('changeRate', 0))
            signals = stock_data.get('signals', {})
            
            # ボラティリティスコア計算
            if change_rate >= 20:
                volatility_score = 95  # 極高ボラティリティ
            elif change_rate >= 10:
                volatility_score = 80  # 高ボラティリティ
            elif change_rate >= 5:
                volatility_score = 65  # 中ボラティリティ
            elif change_rate >= 2:
                volatility_score = 50  # 普通
            elif change_rate >= 1:
                volatility_score = 35  # 低ボラティリティ
            else:
                volatility_score = 20  # 極低ボラティリティ
            
            return {
                'score': volatility_score,
                'change_rate': change_rate,
                'level': self._get_volatility_level(volatility_score),
                'interpretation': self._interpret_volatility(volatility_score)
            }
            
        except Exception as e:
            logger.warning(f"ボラティリティ分析エラー: {str(e)}")
            return {'score': 50, 'error': str(e)}
    
    async def _analyze_multiple_timeframes(self, stock_code: str) -> Dict:
        """マルチタイムフレーム分析"""
        try:
            # 複数時間軸での分析（実装簡易版）
            # 実際の実装では各時間軸のデータを取得して分析
            
            timeframe_results = {}
            
            for timeframe in self.signal_config['timeframes']:
                # 各時間軸での簡易分析
                # 実際にはstock_data_serviceから各時間軸データを取得
                timeframe_results[timeframe] = {
                    'trend': 'up',  # 簡易実装
                    'strength': 70,
                    'volume_confirmed': True
                }
            
            # タイムフレーム一致度計算
            trend_consistency = self._calculate_trend_consistency(timeframe_results)
            
            return {
                'timeframe_results': timeframe_results,
                'trend_consistency': trend_consistency,
                'overall_direction': self._determine_overall_direction(timeframe_results)
            }
            
        except Exception as e:
            logger.warning(f"マルチタイムフレーム分析エラー: {str(e)}")
            return {'error': str(e)}
    
    async def _integrate_signals(
        self, 
        stock_data: Dict, 
        logic_results: Dict, 
        technical_analysis: Dict, 
        timeframe_analysis: Dict
    ) -> Dict:
        """シグナル統合処理"""
        try:
            # 各要素の重み付け
            weights = {
                'logic_score': 0.4,        # ロジック検出結果
                'technical_score': 0.3,    # テクニカル分析
                'timeframe_score': 0.2,    # マルチタイムフレーム
                'volume_score': 0.1        # 出来高確認
            }
            
            # 各スコア取得
            logic_score = logic_results.get('integrated_score', 0) * 100
            technical_score = technical_analysis.get('overall_score', 50)
            timeframe_score = timeframe_analysis.get('trend_consistency', 50)
            volume_score = technical_analysis.get('volume', {}).get('score', 50)
            
            # 統合スコア計算
            integrated_score = (
                logic_score * weights['logic_score'] +
                technical_score * weights['technical_score'] +
                timeframe_score * weights['timeframe_score'] +
                volume_score * weights['volume_score']
            )
            
            # シグナル強度正規化
            signal_strength = max(0, min(100, integrated_score))
            
            # アクション決定
            action = await self._determine_action(signal_strength, logic_results, technical_analysis)
            
            return {
                'signal_strength': round(signal_strength, 1),
                'action': action,
                'component_scores': {
                    'logic': logic_score,
                    'technical': technical_score,
                    'timeframe': timeframe_score,
                    'volume': volume_score
                },
                'weights': weights,
                'confidence': self._calculate_confidence(signal_strength, logic_results)
            }
            
        except Exception as e:
            logger.warning(f"シグナル統合エラー: {str(e)}")
            return {'signal_strength': 0, 'action': 'HOLD', 'error': str(e)}
    
    async def _determine_action(self, signal_strength: float, logic_results: Dict, technical_analysis: Dict) -> str:
        """アクション決定ロジック"""
        try:
            # 基本アクション判定
            if signal_strength >= self.signal_config['strong_signal_threshold']:
                base_action = SignalType.STRONG_BUY.value
            elif signal_strength >= self.signal_config['min_signal_strength']:
                base_action = SignalType.BUY.value
            elif signal_strength <= 20:
                base_action = SignalType.SELL.value
            elif signal_strength <= 40:
                base_action = SignalType.WATCH.value
            else:
                base_action = SignalType.HOLD.value
            
            # 追加条件でアクション調整
            
            # ロジック検出結果による強化
            if logic_results.get('logic_a_enhanced', {}).get('detected', False):
                if base_action == SignalType.BUY.value:
                    base_action = SignalType.STRONG_BUY.value
            
            # テクニカル分析による調整
            technical_score = technical_analysis.get('overall_score', 50)
            if technical_score < 30:
                # テクニカルが弱い場合はアクションを弱める
                if base_action == SignalType.STRONG_BUY.value:
                    base_action = SignalType.BUY.value
                elif base_action == SignalType.BUY.value:
                    base_action = SignalType.WATCH.value
            
            return base_action
            
        except Exception as e:
            logger.warning(f"アクション決定エラー: {str(e)}")
            return SignalType.HOLD.value
    
    async def _calculate_risk_reward(self, stock_data: Dict, integrated_signal: Dict) -> Dict:
        """リスク・リワード分析"""
        try:
            current_price = stock_data.get('price', 0)
            action = integrated_signal.get('action', 'HOLD')
            
            if action in [SignalType.BUY.value, SignalType.STRONG_BUY.value]:
                # 買いシグナルの場合のリスク・リワード計算
                
                # エントリー価格（現在価格+スプレッド想定）
                entry_price = current_price * 1.001  # 0.1%のスプレッド想定
                
                # 利確ターゲット（ロジック強化版の設定を使用）
                profit_target_rate = 0.24  # 24%
                profit_target = entry_price * (1 + profit_target_rate)
                
                # 損切り価格
                stop_loss_rate = 0.10  # 10%
                stop_loss = entry_price * (1 - stop_loss_rate)
                
                # リスク・リワード比率計算
                potential_profit = profit_target - entry_price
                potential_loss = entry_price - stop_loss
                risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
                
                return {
                    'entry_price': round(entry_price, 2),
                    'profit_target': round(profit_target, 2),
                    'stop_loss': round(stop_loss, 2),
                    'potential_profit': round(potential_profit, 2),
                    'potential_loss': round(potential_loss, 2),
                    'risk_reward_ratio': round(risk_reward_ratio, 2),
                    'profit_target_rate': profit_target_rate,
                    'stop_loss_rate': stop_loss_rate,
                    'meets_criteria': risk_reward_ratio >= self.signal_config['min_risk_reward_ratio']
                }
            
            else:
                # 売りまたはホールドの場合
                return {
                    'entry_price': current_price,
                    'action_reason': f'{action}シグナルのためリスク・リワード計算対象外',
                    'meets_criteria': True
                }
                
        except Exception as e:
            logger.warning(f"リスク・リワード計算エラー: {str(e)}")
            return {'error': str(e), 'meets_criteria': False}
    
    async def _calculate_position_size(self, stock_data: Dict, risk_reward: Dict) -> Dict:
        """ポジションサイズ計算"""
        try:
            # 簡易ポジションサイジング
            # 実際の実装では投資家の総資産、リスク許容度等を考慮
            
            max_risk_per_trade = self.signal_config['max_risk_per_trade']
            entry_price = risk_reward.get('entry_price', stock_data.get('price', 0))
            stop_loss = risk_reward.get('stop_loss', entry_price * 0.9)
            
            # リスク額計算
            risk_per_share = entry_price - stop_loss
            
            # 仮想ポートフォリオサイズ（1000万円）
            portfolio_size = 10000000
            max_risk_amount = portfolio_size * max_risk_per_trade
            
            # 推奨株数計算
            if risk_per_share > 0:
                recommended_shares = int(max_risk_amount / risk_per_share)
                position_value = recommended_shares * entry_price
                portfolio_exposure = position_value / portfolio_size
            else:
                recommended_shares = 0
                position_value = 0
                portfolio_exposure = 0
            
            return {
                'recommended_shares': recommended_shares,
                'position_value': round(position_value, 0),
                'portfolio_exposure': round(portfolio_exposure, 4),
                'max_risk_amount': round(max_risk_amount, 0),
                'risk_per_share': round(risk_per_share, 2),
                'meets_exposure_limit': portfolio_exposure <= self.signal_config['max_portfolio_exposure']
            }
            
        except Exception as e:
            logger.warning(f"ポジションサイズ計算エラー: {str(e)}")
            return {'error': str(e), 'recommended_shares': 0}
    
    async def _generate_final_signal(
        self, 
        stock_data: Dict, 
        integrated_signal: Dict, 
        risk_reward: Dict, 
        position_info: Dict
    ) -> Dict:
        """最終シグナル生成"""
        try:
            stock_code = stock_data.get('code', '')
            current_price = stock_data.get('price', 0)
            
            # 基本シグナル情報
            final_signal = {
                'stock_code': stock_code,
                'stock_name': stock_data.get('name', ''),
                'current_price': current_price,
                'timestamp': datetime.now().isoformat(),
                
                # シグナル情報
                'action': integrated_signal.get('action', 'HOLD'),
                'signal_strength': integrated_signal.get('signal_strength', 0),
                'confidence': integrated_signal.get('confidence', 0),
                
                # 価格情報
                'entry_price': risk_reward.get('entry_price', current_price),
                'profit_target': risk_reward.get('profit_target', 0),
                'stop_loss': risk_reward.get('stop_loss', 0),
                'risk_reward_ratio': risk_reward.get('risk_reward_ratio', 0),
                
                # ポジション情報
                'recommended_shares': position_info.get('recommended_shares', 0),
                'position_value': position_info.get('position_value', 0),
                'portfolio_exposure': position_info.get('portfolio_exposure', 0),
                
                # 詳細分析結果
                'component_scores': integrated_signal.get('component_scores', {}),
                'technical_analysis': {},
                'risk_assessment': await self._assess_signal_risk(stock_data, integrated_signal),
                
                # 実行可否判定
                'executable': await self._is_signal_executable(risk_reward, position_info),
                'execution_notes': await self._generate_execution_notes(stock_data, integrated_signal, risk_reward)
            }
            
            return final_signal
            
        except Exception as e:
            logger.error(f"最終シグナル生成エラー: {str(e)}")
            return self._create_error_signal(f'シグナル生成エラー: {str(e)}')
    
    async def _assess_signal_risk(self, stock_data: Dict, integrated_signal: Dict) -> Dict:
        """シグナルリスク評価"""
        try:
            risk_factors = []
            risk_score = 100  # 100点満点（高いほど低リスク）
            
            # シグナル強度によるリスク評価
            signal_strength = integrated_signal.get('signal_strength', 0)
            if signal_strength < 60:
                risk_factors.append('シグナル強度不足')
                risk_score -= 30
            
            # ボラティリティリスク
            change_rate = abs(stock_data.get('changeRate', 0))
            if change_rate > 20:
                risk_factors.append('高ボラティリティ')
                risk_score -= 25
            elif change_rate > 10:
                risk_factors.append('中ボラティリティ')
                risk_score -= 15
            
            # 出来高リスク
            signals = stock_data.get('signals', {})
            volume_ratio = signals.get('volumeRatio', 1.0)
            if volume_ratio < 0.5:
                risk_factors.append('出来高不足')
                risk_score -= 20
            
            # RSIリスク
            rsi = signals.get('rsi', 50)
            if rsi > 80:
                risk_factors.append('RSI過熱')
                risk_score -= 15
            elif rsi < 20:
                risk_factors.append('RSI売られ過ぎ')
                risk_score -= 10
            
            # リスクレベル判定
            risk_score = max(0, min(100, risk_score))
            risk_level = self._get_risk_level(risk_score)
            
            return {
                'risk_level': risk_level.value,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'recommendation': self._get_risk_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.warning(f"リスク評価エラー: {str(e)}")
            return {
                'risk_level': RiskLevel.HIGH.value,
                'risk_score': 30,
                'risk_factors': ['評価エラー'],
                'recommendation': '詳細な分析が必要'
            }
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """リスクスコアからリスクレベルを決定"""
        if risk_score >= 90:
            return RiskLevel.VERY_LOW
        elif risk_score >= 75:
            return RiskLevel.LOW
        elif risk_score >= 60:
            return RiskLevel.MEDIUM
        elif risk_score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _get_risk_recommendation(self, risk_level: RiskLevel) -> str:
        """リスクレベル別推奨事項"""
        recommendations = {
            RiskLevel.VERY_LOW: 'リスクが非常に低く、通常の投資判断で問題なし',
            RiskLevel.LOW: 'リスクが低く、適切な投資判断が可能',
            RiskLevel.MEDIUM: '中程度のリスク、適切なリスク管理の下で投資検討',
            RiskLevel.HIGH: '高リスク、小額での投資またはより詳細な分析を推奨',
            RiskLevel.VERY_HIGH: '非常に高リスク、投資見送りまたは専門家への相談を推奨'
        }
        return recommendations.get(risk_level, '詳細な分析が必要')
    
    async def _is_signal_executable(self, risk_reward: Dict, position_info: Dict) -> bool:
        """シグナル実行可否判定"""
        try:
            # リスク・リワード基準
            if not risk_reward.get('meets_criteria', False):
                return False
            
            # ポートフォリオ露出基準
            if not position_info.get('meets_exposure_limit', False):
                return False
            
            # 推奨株数が0以上
            if position_info.get('recommended_shares', 0) <= 0:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"実行可否判定エラー: {str(e)}")
            return False
    
    async def _generate_execution_notes(
        self, 
        stock_data: Dict, 
        integrated_signal: Dict, 
        risk_reward: Dict
    ) -> List[str]:
        """実行時注意事項生成"""
        try:
            notes = []
            
            action = integrated_signal.get('action', 'HOLD')
            signal_strength = integrated_signal.get('signal_strength', 0)
            
            # アクション別の注意事項
            if action == SignalType.STRONG_BUY.value:
                notes.append('強い買いシグナル検出。エントリータイミングを逃さないよう注意')
                notes.append('利確・損切りルールを厳守')
            elif action == SignalType.BUY.value:
                notes.append('買いシグナル検出。適切なタイミングでエントリー')
                notes.append('リスク管理を徹底')
            elif action == SignalType.WATCH.value:
                notes.append('監視継続。条件改善を待つ')
            
            # シグナル強度による注意事項
            if signal_strength < 70:
                notes.append('シグナル強度が中程度。追加確認を推奨')
            
            # リスク・リワード比率による注意事項
            rr_ratio = risk_reward.get('risk_reward_ratio', 0)
            if rr_ratio < 2.0:
                notes.append('リスク・リワード比率が低め。慎重な判断が必要')
            
            # ボラティリティによる注意事項
            change_rate = abs(stock_data.get('changeRate', 0))
            if change_rate > 15:
                notes.append('高ボラティリティ銘柄。急激な価格変動に注意')
            
            return notes
            
        except Exception as e:
            logger.warning(f"実行注意事項生成エラー: {str(e)}")
            return ['実行時は十分な注意が必要']
    
    async def get_active_signals(self, stock_code: str = None) -> List[Dict]:
        """アクティブシグナル取得"""
        try:
            if stock_code:
                return self.active_signals.get(stock_code, [])
            else:
                all_signals = []
                for signals in self.active_signals.values():
                    all_signals.extend(signals)
                return sorted(all_signals, key=lambda x: x['timestamp'], reverse=True)
                
        except Exception as e:
            logger.error(f"アクティブシグナル取得エラー: {str(e)}")
            return []
    
    async def get_signal_history(self, limit: int = 100) -> List[Dict]:
        """シグナル履歴取得"""
        try:
            return sorted(
                self.signal_history[-limit:], 
                key=lambda x: x['timestamp'], 
                reverse=True
            )
            
        except Exception as e:
            logger.error(f"シグナル履歴取得エラー: {str(e)}")
            return []
    
    async def get_performance_metrics(self) -> Dict:
        """パフォーマンス指標取得"""
        try:
            return self.performance_metrics.copy()
            
        except Exception as e:
            logger.error(f"パフォーマンス指標取得エラー: {str(e)}")
            return {}
    
    # ヘルパーメソッド
    
    def _validate_stock_data(self, stock_data: Dict) -> bool:
        """株価データ検証"""
        required_fields = ['code', 'name', 'price', 'changeRate', 'volume']
        return all(field in stock_data for field in required_fields)
    
    def _create_error_signal(self, error_message: str) -> Dict:
        """エラーシグナル生成"""
        return {
            'action': 'ERROR',
            'signal_strength': 0,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
    
    def _interpret_momentum(self, score: float) -> str:
        """モメンタムスコア解釈"""
        if score >= 80:
            return '非常に強いモメンタム'
        elif score >= 60:
            return '強いモメンタム'
        elif score >= 40:
            return '普通のモメンタム'
        else:
            return '弱いモメンタム'
    
    def _interpret_trend(self, score: float) -> str:
        """トレンドスコア解釈"""
        if score >= 80:
            return '強い上昇トレンド'
        elif score >= 60:
            return '上昇トレンド'
        elif score >= 40:
            return '横ばいトレンド'
        elif score >= 20:
            return '下降トレンド'
        else:
            return '強い下降トレンド'
    
    def _interpret_volume(self, score: float, volume_ratio: float) -> str:
        """出来高解釈"""
        if volume_ratio >= 3.0:
            return '異常高出来高（注意が必要）'
        elif volume_ratio >= 2.0:
            return '高出来高（好材料）'
        elif volume_ratio >= 1.5:
            return 'やや高出来高'
        else:
            return '平均的出来高'
    
    def _interpret_support_resistance(self, score: float) -> str:
        """サポート・レジスタンス解釈"""
        if score >= 70:
            return 'レジスタンス突破'
        elif score <= 30:
            return 'サポート割れ'
        else:
            return 'レンジ内'
    
    def _interpret_volatility(self, score: float) -> str:
        """ボラティリティ解釈"""
        if score >= 90:
            return '極高ボラティリティ'
        elif score >= 70:
            return '高ボラティリティ'
        elif score >= 50:
            return '中ボラティリティ'
        else:
            return '低ボラティリティ'
    
    def _get_volatility_level(self, score: float) -> str:
        """ボラティリティレベル"""
        if score >= 90:
            return 'EXTREME'
        elif score >= 70:
            return 'HIGH'
        elif score >= 50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_trend_consistency(self, timeframe_results: Dict) -> float:
        """トレンド一致度計算"""
        trends = [result.get('trend', 'sideways') for result in timeframe_results.values()]
        if not trends:
            return 50
        
        # 上昇トレンドの一致度
        up_count = trends.count('up')
        consistency = (up_count / len(trends)) * 100
        
        return consistency
    
    def _determine_overall_direction(self, timeframe_results: Dict) -> str:
        """全体トレンド方向決定"""
        trends = [result.get('trend', 'sideways') for result in timeframe_results.values()]
        if not trends:
            return 'sideways'
        
        up_count = trends.count('up')
        down_count = trends.count('down')
        
        if up_count > down_count:
            return 'up'
        elif down_count > up_count:
            return 'down'
        else:
            return 'sideways'
    
    def _calculate_confidence(self, signal_strength: float, logic_results: Dict) -> float:
        """信頼度計算"""
        base_confidence = signal_strength / 100
        
        # ロジック検出による信頼度向上
        if logic_results.get('any_detected', False):
            base_confidence += 0.2
        
        return min(1.0, base_confidence)
    
    async def _manage_active_signals(self, stock_code: str, signal: Dict) -> None:
        """アクティブシグナル管理"""
        try:
            if stock_code not in self.active_signals:
                self.active_signals[stock_code] = []
            
            # 新しいシグナルを追加
            self.active_signals[stock_code].append(signal)
            
            # 古いシグナルのクリーンアップ（24時間経過）
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.active_signals[stock_code] = [
                s for s in self.active_signals[stock_code]
                if datetime.fromisoformat(s['timestamp']) > cutoff_time
            ]
            
        except Exception as e:
            logger.warning(f"アクティブシグナル管理エラー: {str(e)}")
    
    async def _record_signal_performance(self, signal: Dict) -> None:
        """シグナルパフォーマンス記録"""
        try:
            # 履歴に追加
            self.signal_history.append(signal)
            
            # 履歴の上限管理
            if len(self.signal_history) > 1000:
                self.signal_history = self.signal_history[-1000:]
            
            # パフォーマンス指標更新
            self.performance_metrics['total_signals'] += 1
            
        except Exception as e:
            logger.warning(f"パフォーマンス記録エラー: {str(e)}")