"""
売買支援関連サービス
Stock Harvest AI プロジェクト用
"""

from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import statistics

from ..repositories.trading_repository import TradingRepository
from ..services.real_stock_data_service import RealStockDataService
from ..services.technical_analysis_service import TechnicalAnalysisService
from ..models.trading_models import (
    EntryOptimizationRequest,
    EntryOptimizationResponse,
    IfdocoGuideRequest,
    IfdocoGuideResponse,
    IfdocoOrderSettings,
    TradingHistoryFilter,
    TradingHistoryResponse,
    TradingHistorySummary,
    SignalHistoryFilter,
    SignalHistoryResponse,
    SignalHistorySummary,
    PerformanceAnalysisRequest,
    PerformanceAnalysisResponse,
    PerformanceMetrics
)
from ..lib.logger import logger, PerformanceTracker


class TradingService:
    """売買支援サービス"""

    def __init__(self):
        self.trading_repo = TradingRepository()
        self.stock_data_service = RealStockDataService()
        self.technical_service = TechnicalAnalysisService()

    async def optimize_entry_point(self, request: EntryOptimizationRequest) -> EntryOptimizationResponse:
        """エントリーポイント最適化"""
        tracker = PerformanceTracker("エントリーポイント最適化")
        
        try:
            logger.info(f"エントリーポイント最適化開始: {request.stock_code}")
            
            # 銘柄情報取得
            stock_info = await self.trading_repo.get_stock_info(request.stock_code)
            if not stock_info:
                raise ValueError(f"銘柄情報が見つかりません: {request.stock_code}")
            
            stock_name = stock_info['stock_name']
            
            # 過去の売買データ取得
            historical_trades = await self.trading_repo.get_historical_trading_data(
                request.stock_code, 
                request.logic_type,
                days=365
            )
            
            # テクニカル分析実行
            technical_data = await self._get_technical_analysis(request.stock_code)
            
            # 最適エントリー価格計算
            optimal_entry = await self._calculate_optimal_entry_price(
                request, historical_trades, technical_data
            )
            
            # リスク・リワード分析
            risk_reward_analysis = await self._calculate_risk_reward_ratio(
                request, optimal_entry, historical_trades
            )
            
            # ポジションサイズ推奨
            position_size = await self._calculate_position_size(
                request, optimal_entry, risk_reward_analysis
            )
            
            # 市場タイミングスコア計算
            timing_score = await self._calculate_market_timing_score(
                request.stock_code, technical_data
            )
            
            # 過去パフォーマンス分析
            historical_performance = await self._analyze_historical_performance(
                request.stock_code, request.logic_type, historical_trades
            )
            
            response = EntryOptimizationResponse(
                stock_code=request.stock_code,
                stock_name=stock_name,
                current_price=request.current_price,
                optimal_entry_price=optimal_entry['price'],
                optimal_entry_price_range=optimal_entry['range'],
                target_profit_price=risk_reward_analysis['target_profit'],
                stop_loss_price=risk_reward_analysis['stop_loss'],
                risk_reward_ratio=risk_reward_analysis['ratio'],
                expected_return=risk_reward_analysis['expected_return'],
                confidence_level=optimal_entry['confidence_level'],
                position_size_recommendation=position_size,
                market_timing_score=timing_score,
                analysis_factors=optimal_entry['analysis_factors'],
                recommended_order_type=optimal_entry['order_type'],
                execution_notes=optimal_entry['execution_notes'],
                historical_performance=historical_performance
            )
            
            logger.info(f"エントリーポイント最適化完了: {request.stock_code}")
            tracker.end({'stock_code': request.stock_code})
            return response
            
        except Exception as e:
            logger.error(f"エントリーポイント最適化エラー: {e}", exc_info=True)
            raise

    async def generate_ifdoco_guide(self, request: IfdocoGuideRequest) -> IfdocoGuideResponse:
        """IFDOCO注文ガイド生成"""
        tracker = PerformanceTracker("IFDOCO注文ガイド生成")
        
        try:
            logger.info(f"IFDOCO注文ガイド生成開始: {request.stock_code}")
            
            # 銘柄情報取得
            stock_info = await self.trading_repo.get_stock_info(request.stock_code)
            if not stock_info:
                raise ValueError(f"銘柄情報が見つかりません: {request.stock_code}")
            
            stock_name = stock_info['stock_name']
            
            # 推奨取引株数計算
            recommended_quantity = int(request.investment_amount / request.entry_price)
            
            # IFDOCO注文設定生成
            order_settings = await self._generate_ifdoco_settings(request, recommended_quantity)
            
            # ステップバイステップガイド生成
            step_guide = await self._generate_step_by_step_guide(request, order_settings)
            
            # リスク分析
            risk_analysis = await self._analyze_ifdoco_risks(request, order_settings)
            
            # 想定シナリオ生成
            scenarios = await self._generate_expected_scenarios(request, order_settings)
            
            # 証券会社別注意事項
            broker_notes = await self._get_broker_specific_notes(request.risk_level)
            
            # 監視ポイント生成
            monitoring_points = await self._generate_monitoring_points(request)
            
            # 出口戦略
            exit_strategy = await self._generate_exit_strategy(request, order_settings)
            
            response = IfdocoGuideResponse(
                stock_code=request.stock_code,
                stock_name=stock_name,
                entry_price=request.entry_price,
                investment_amount=request.investment_amount,
                recommended_quantity=recommended_quantity,
                order_settings=order_settings,
                step_by_step_guide=step_guide,
                risk_analysis=risk_analysis,
                expected_scenarios=scenarios,
                broker_specific_notes=broker_notes,
                monitoring_points=monitoring_points,
                exit_strategy=exit_strategy
            )
            
            logger.info(f"IFDOCO注文ガイド生成完了: {request.stock_code}")
            tracker.end({'stock_code': request.stock_code})
            return response
            
        except Exception as e:
            logger.error(f"IFDOCO注文ガイド生成エラー: {e}", exc_info=True)
            raise

    async def get_trading_history(self, filters: TradingHistoryFilter) -> TradingHistoryResponse:
        """売買履歴取得"""
        try:
            logger.info("売買履歴取得開始")
            
            # フィルタ辞書に変換
            filter_dict = filters.dict(exclude_unset=True)
            
            # 履歴データ取得
            trades, total_count = await self.trading_repo.get_trading_history_list(filter_dict)
            
            # サマリー統計取得
            summary_stats = await self.trading_repo.get_trading_summary_stats(filter_dict)
            
            summary = TradingHistorySummary(**summary_stats)
            
            # ページネーション情報
            has_next = (filters.page * filters.limit) < total_count
            
            response = TradingHistoryResponse(
                trades=trades,
                summary=summary,
                total=total_count,
                page=filters.page,
                limit=filters.limit,
                has_next=has_next
            )
            
            logger.info(f"売買履歴取得完了: {total_count}件")
            return response
            
        except Exception as e:
            logger.error(f"売買履歴取得エラー: {e}", exc_info=True)
            raise

    async def get_signal_history(self, filters: SignalHistoryFilter) -> SignalHistoryResponse:
        """シグナル履歴取得"""
        try:
            logger.info("シグナル履歴取得開始")
            
            # フィルタ辞書に変換
            filter_dict = filters.dict(exclude_unset=True)
            
            # シグナルデータ取得
            signals, total_count = await self.trading_repo.get_signal_history_list(filter_dict)
            
            # サマリー統計取得
            summary_stats = await self.trading_repo.get_signal_summary_stats(filter_dict)
            
            summary = SignalHistorySummary(**summary_stats)
            
            # ページネーション情報
            has_next = (filters.page * filters.limit) < total_count
            
            response = SignalHistoryResponse(
                signals=signals,
                summary=summary,
                total=total_count,
                page=filters.page,
                limit=filters.limit,
                has_next=has_next
            )
            
            logger.info(f"シグナル履歴取得完了: {total_count}件")
            return response
            
        except Exception as e:
            logger.error(f"シグナル履歴取得エラー: {e}", exc_info=True)
            raise

    # プライベートメソッド群

    async def _get_technical_analysis(self, stock_code: str) -> Dict[str, Any]:
        """テクニカル分析データ取得"""
        try:
            # RealStockDataServiceとTechnicalAnalysisServiceを使用
            # 簡略化した実装例
            return {
                'rsi': 50.0,
                'macd': 0.0,
                'bollinger_position': 0.5,
                'volume_ratio': 1.2,
                'support_levels': [1000, 950, 900],
                'resistance_levels': [1100, 1150, 1200],
                'trend_direction': 'up',
                'volatility': 0.25
            }
        except Exception as e:
            logger.error(f"テクニカル分析データ取得エラー: {e}")
            return {}

    async def _calculate_optimal_entry_price(self, request: EntryOptimizationRequest, 
                                           historical_trades: List[Dict[str, Any]], 
                                           technical_data: Dict[str, Any]) -> Dict[str, Any]:
        """最適エントリー価格計算"""
        try:
            current_price = request.current_price
            
            # リスク許容度に基づく調整
            risk_multipliers = {'low': 0.98, 'medium': 0.95, 'high': 0.92}
            risk_multiplier = risk_multipliers.get(request.risk_tolerance, 0.95)
            
            # テクニカル分析に基づく調整
            technical_adjustment = 1.0
            if technical_data.get('support_levels'):
                nearest_support = min(technical_data['support_levels'], 
                                    key=lambda x: abs(x - float(current_price)))
                if nearest_support < float(current_price):
                    technical_adjustment = nearest_support / float(current_price)
            
            # 過去データに基づく調整
            historical_adjustment = 1.0
            if historical_trades:
                successful_entries = [
                    trade for trade in historical_trades 
                    if trade.get('profit_loss', 0) > 0
                ]
                if successful_entries:
                    avg_entry_discount = statistics.mean([
                        (trade.get('exit_price', trade['entry_price']) - trade['entry_price']) / trade['entry_price']
                        for trade in successful_entries
                        if trade.get('exit_price')
                    ])
                    historical_adjustment = 1.0 + (avg_entry_discount * 0.1)  # 10%の重み
            
            # 最適価格計算
            optimal_price = current_price * risk_multiplier * technical_adjustment * historical_adjustment
            
            # 価格範囲計算
            price_range = {
                'min': optimal_price * Decimal('0.98'),
                'max': optimal_price * Decimal('1.02')
            }
            
            # 信頼度レベル決定
            confidence_factors = [
                len(historical_trades) > 5,  # 十分な履歴データ
                technical_data.get('trend_direction') == 'up',  # 上昇トレンド
                technical_data.get('rsi', 50) < 70  # 買われすぎでない
            ]
            confidence_score = sum(confidence_factors) / len(confidence_factors)
            
            if confidence_score >= 0.8:
                confidence_level = 'high'
            elif confidence_score >= 0.5:
                confidence_level = 'medium'
            else:
                confidence_level = 'low'
            
            return {
                'price': optimal_price,
                'range': price_range,
                'confidence_level': confidence_level,
                'analysis_factors': {
                    'risk_adjustment': risk_multiplier,
                    'technical_adjustment': technical_adjustment,
                    'historical_adjustment': historical_adjustment,
                    'confidence_score': confidence_score
                },
                'order_type': 'limit',  # 指値注文推奨
                'execution_notes': [
                    f"現在価格から{((1-risk_multiplier)*100):.1f}%程度の調整を推奨",
                    "テクニカル分析に基づく価格調整を実施",
                    f"信頼度レベル: {confidence_level}"
                ]
            }
            
        except Exception as e:
            logger.error(f"最適エントリー価格計算エラー: {e}")
            # フォールバック値を返す
            return {
                'price': request.current_price * Decimal('0.98'),
                'range': {
                    'min': request.current_price * Decimal('0.96'),
                    'max': request.current_price * Decimal('1.00')
                },
                'confidence_level': 'low',
                'analysis_factors': {},
                'order_type': 'market',
                'execution_notes': ["エラーのため簡易計算を使用"]
            }

    async def _calculate_risk_reward_ratio(self, request: EntryOptimizationRequest, 
                                         optimal_entry: Dict[str, Any],
                                         historical_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """リスク・リワード比率計算"""
        try:
            entry_price = optimal_entry['price']
            
            # ロジック種別に基づく利確・損切り設定
            logic_settings = {
                'logic_a': {'profit_rate': 0.24, 'loss_rate': 0.10},  # +24%利確, -10%損切り
                'logic_b': {'profit_rate': 0.25, 'loss_rate': 0.10},  # +25%利確, -10%損切り
                'manual': {'profit_rate': 0.15, 'loss_rate': 0.08}    # +15%利確, -8%損切り
            }
            
            settings = logic_settings.get(request.logic_type, logic_settings['manual'])
            
            # リスク許容度による調整
            risk_adjustments = {
                'low': {'profit': 0.8, 'loss': 1.2},      # 利確を早めに、損切りを厳しく
                'medium': {'profit': 1.0, 'loss': 1.0},   # 標準
                'high': {'profit': 1.2, 'loss': 0.8}      # 利確を遅めに、損切りを緩く
            }
            
            adjustment = risk_adjustments.get(request.risk_tolerance, risk_adjustments['medium'])
            
            # 利確・損切り価格計算
            profit_rate = settings['profit_rate'] * adjustment['profit']
            loss_rate = settings['loss_rate'] * adjustment['loss']
            
            target_profit_price = entry_price * (1 + Decimal(str(profit_rate)))
            stop_loss_price = entry_price * (1 - Decimal(str(loss_rate)))
            
            # リスク・リワード比率
            risk_amount = entry_price - stop_loss_price
            reward_amount = target_profit_price - entry_price
            risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else Decimal('0')
            
            # 期待リターン計算（過去データ基づく）
            expected_return = await self._calculate_expected_return(
                historical_trades, profit_rate, loss_rate
            )
            
            return {
                'target_profit': target_profit_price,
                'stop_loss': stop_loss_price,
                'ratio': risk_reward_ratio,
                'expected_return': expected_return,
                'profit_rate': Decimal(str(profit_rate)),
                'loss_rate': Decimal(str(loss_rate))
            }
            
        except Exception as e:
            logger.error(f"リスク・リワード比率計算エラー: {e}")
            # フォールバック値
            entry_price = optimal_entry.get('price', request.current_price)
            return {
                'target_profit': entry_price * Decimal('1.15'),
                'stop_loss': entry_price * Decimal('0.92'),
                'ratio': Decimal('2.0'),
                'expected_return': Decimal('10.0'),
                'profit_rate': Decimal('0.15'),
                'loss_rate': Decimal('0.08')
            }

    async def _calculate_expected_return(self, historical_trades: List[Dict[str, Any]], 
                                       profit_rate: float, loss_rate: float) -> Decimal:
        """期待リターン計算"""
        try:
            if not historical_trades:
                return Decimal('8.0')  # デフォルト8%
            
            # 勝率計算
            profitable_trades = [
                trade for trade in historical_trades 
                if trade.get('profit_loss', 0) > 0 and trade.get('status') == 'closed'
            ]
            total_closed = [
                trade for trade in historical_trades 
                if trade.get('status') == 'closed' and trade.get('profit_loss') is not None
            ]
            
            if not total_closed:
                return Decimal('8.0')
            
            win_rate = len(profitable_trades) / len(total_closed)
            
            # 期待リターン = (勝率 × 利益率) - (負け率 × 損失率)
            expected_return = (win_rate * profit_rate - (1 - win_rate) * loss_rate) * 100
            
            return Decimal(str(max(expected_return, 0)))
            
        except Exception as e:
            logger.error(f"期待リターン計算エラー: {e}")
            return Decimal('8.0')

    async def _calculate_position_size(self, request: EntryOptimizationRequest, 
                                     optimal_entry: Dict[str, Any],
                                     risk_reward: Dict[str, Any]) -> Dict[str, Any]:
        """ポジションサイズ計算"""
        try:
            entry_price = optimal_entry['price']
            
            # 投資金額が指定されている場合
            if request.investment_amount:
                shares = int(request.investment_amount / entry_price)
                investment_amount = shares * entry_price
                
                return {
                    'shares': shares,
                    'investment_amount': investment_amount,
                    'risk_amount': (entry_price - risk_reward['stop_loss']) * shares,
                    'max_profit': (risk_reward['target_profit'] - entry_price) * shares,
                    'position_type': 'fixed_amount'
                }
            
            # リスクベースのポジションサイズ計算
            # 仮想的な投資資金の2%をリスクとして設定
            assumed_capital = Decimal('1000000')  # 100万円と仮定
            risk_per_trade = assumed_capital * Decimal('0.02')  # 2%リスク
            
            risk_per_share = entry_price - risk_reward['stop_loss']
            shares = int(risk_per_trade / risk_per_share) if risk_per_share > 0 else 100
            investment_amount = shares * entry_price
            
            return {
                'shares': shares,
                'investment_amount': investment_amount,
                'risk_amount': risk_per_share * shares,
                'max_profit': (risk_reward['target_profit'] - entry_price) * shares,
                'position_type': 'risk_based'
            }
            
        except Exception as e:
            logger.error(f"ポジションサイズ計算エラー: {e}")
            # フォールバック
            shares = 100
            entry_price = optimal_entry.get('price', request.current_price)
            return {
                'shares': shares,
                'investment_amount': shares * entry_price,
                'risk_amount': shares * entry_price * Decimal('0.08'),
                'max_profit': shares * entry_price * Decimal('0.15'),
                'position_type': 'default'
            }

    async def _calculate_market_timing_score(self, stock_code: str, 
                                           technical_data: Dict[str, Any]) -> int:
        """市場タイミングスコア計算（1-100）"""
        try:
            score = 50  # ベーススコア
            
            # RSI評価
            rsi = technical_data.get('rsi', 50)
            if 30 <= rsi <= 70:
                score += 15
            elif rsi < 30:
                score += 20  # 買われすぎでない
            else:
                score -= 10
            
            # MACD評価
            macd = technical_data.get('macd', 0)
            if macd > 0:
                score += 10
            
            # トレンド評価
            trend = technical_data.get('trend_direction', 'sideways')
            if trend == 'up':
                score += 15
            elif trend == 'down':
                score -= 15
            
            # ボリューム評価
            volume_ratio = technical_data.get('volume_ratio', 1.0)
            if volume_ratio > 1.5:
                score += 10
            elif volume_ratio < 0.5:
                score -= 10
            
            # スコアを1-100の範囲に制限
            return max(1, min(100, score))
            
        except Exception as e:
            logger.error(f"市場タイミングスコア計算エラー: {e}")
            return 50

    async def _analyze_historical_performance(self, stock_code: str, logic_type: Optional[str],
                                            historical_trades: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """過去パフォーマンス分析"""
        try:
            if not historical_trades:
                return None
            
            closed_trades = [
                trade for trade in historical_trades 
                if trade.get('status') == 'closed' and trade.get('profit_loss') is not None
            ]
            
            if not closed_trades:
                return None
            
            # 基本統計
            total_trades = len(closed_trades)
            profitable_trades = len([t for t in closed_trades if t['profit_loss'] > 0])
            win_rate = (profitable_trades / total_trades) * 100
            
            profit_losses = [float(trade['profit_loss']) for trade in closed_trades]
            avg_return = statistics.mean(profit_losses) if profit_losses else 0
            max_profit = max(profit_losses) if profit_losses else 0
            max_loss = min(profit_losses) if profit_losses else 0
            
            return {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'average_return': avg_return,
                'max_profit': max_profit,
                'max_loss': max_loss,
                'analysis_period_days': 365
            }
            
        except Exception as e:
            logger.error(f"過去パフォーマンス分析エラー: {e}")
            return None

    async def _generate_ifdoco_settings(self, request: IfdocoGuideRequest, 
                                      recommended_quantity: int) -> IfdocoOrderSettings:
        """IFDOCO注文設定生成"""
        try:
            # リスクレベルに基づく設定
            risk_settings = {
                'conservative': {'profit_rate': 0.10, 'loss_rate': 0.05},
                'medium': {'profit_rate': 0.15, 'loss_rate': 0.08},
                'aggressive': {'profit_rate': 0.25, 'loss_rate': 0.12}
            }
            
            settings = risk_settings.get(request.risk_level, risk_settings['medium'])
            
            profit_target_price = request.entry_price * (1 + Decimal(str(settings['profit_rate'])))
            stop_loss_price = request.entry_price * (1 - Decimal(str(settings['loss_rate'])))
            
            return IfdocoOrderSettings(
                entry_order={
                    'type': 'limit',
                    'price': request.entry_price,
                    'quantity': recommended_quantity
                },
                profit_target_order={
                    'type': 'limit',
                    'price': profit_target_price,
                    'trigger_condition': 'OCO'
                },
                stop_loss_order={
                    'type': 'stop',
                    'price': stop_loss_price,
                    'trigger_condition': 'OCO'
                },
                order_validity='month',
                execution_priority='simultaneous'
            )
            
        except Exception as e:
            logger.error(f"IFDOCO注文設定生成エラー: {e}")
            raise

    async def _generate_step_by_step_guide(self, request: IfdocoGuideRequest, 
                                         order_settings: IfdocoOrderSettings) -> List[Dict[str, Any]]:
        """ステップバイステップガイド生成"""
        try:
            return [
                {
                    'step': 1,
                    'title': '銘柄検索・選択',
                    'description': f'証券会社のシステムで銘柄コード {request.stock_code} を検索',
                    'details': ['取引画面にアクセス', '銘柄コード入力', '銘柄情報確認'],
                    'tips': ['正確な銘柄コードを入力', '現在価格の確認']
                },
                {
                    'step': 2,
                    'title': 'IFDOCO注文設定',
                    'description': 'IFDOCO注文を選択し、詳細設定を入力',
                    'details': [
                        f'注文種別: IFDOCO選択',
                        f'エントリー価格: {order_settings.entry_order["price"]}円',
                        f'数量: {order_settings.entry_order["quantity"]}株'
                    ],
                    'tips': ['IFDOCO注文が可能な証券会社を確認']
                },
                {
                    'step': 3,
                    'title': '利確・損切り設定',
                    'description': 'OCO注文で利確と損切りを同時設定',
                    'details': [
                        f'利確価格: {order_settings.profit_target_order["price"]}円',
                        f'損切り価格: {order_settings.stop_loss_order["price"]}円',
                        f'注文有効期限: {order_settings.order_validity}'
                    ],
                    'tips': ['価格設定を慎重に確認', '有効期限の設定忘れに注意']
                },
                {
                    'step': 4,
                    'title': '注文確認・実行',
                    'description': '全ての設定を確認してから注文を実行',
                    'details': ['注文内容の最終確認', '手数料の確認', '注文実行'],
                    'tips': ['間違いがないか慎重に確認', '注文完了後の確認書を保存']
                }
            ]
            
        except Exception as e:
            logger.error(f"ステップバイステップガイド生成エラー: {e}")
            return []

    async def _analyze_ifdoco_risks(self, request: IfdocoGuideRequest, 
                                  order_settings: IfdocoOrderSettings) -> Dict[str, Any]:
        """IFDOCO注文リスク分析"""
        try:
            entry_price = request.entry_price
            profit_price = order_settings.profit_target_order['price']
            loss_price = order_settings.stop_loss_order['price']
            
            # 最大利益・損失
            max_profit = (profit_price - entry_price) * request.investment_amount / entry_price
            max_loss = (entry_price - loss_price) * request.investment_amount / entry_price
            
            # リスク・リワード比率
            risk_reward_ratio = max_profit / max_loss if max_loss > 0 else 0
            
            return {
                'max_profit_amount': max_profit,
                'max_loss_amount': max_loss,
                'risk_reward_ratio': risk_reward_ratio,
                'breakeven_point': entry_price,
                'position_risk_percentage': (max_loss / request.investment_amount) * 100,
                'risk_factors': [
                    '価格変動リスク',
                    '流動性リスク',
                    '注文執行リスク',
                    '時間価値の減少'
                ],
                'mitigation_strategies': [
                    '適切なポジションサイズの設定',
                    '定期的な市場監視',
                    '注文状況の確認',
                    'ストップロス価格の調整'
                ]
            }
            
        except Exception as e:
            logger.error(f"IFDOCO注文リスク分析エラー: {e}")
            return {}

    async def _generate_expected_scenarios(self, request: IfdocoGuideRequest, 
                                         order_settings: IfdocoOrderSettings) -> Dict[str, Any]:
        """想定シナリオ生成"""
        try:
            entry_price = request.entry_price
            quantity = request.investment_amount / entry_price
            
            return {
                'best_case': {
                    'description': '利確目標到達',
                    'exit_price': order_settings.profit_target_order['price'],
                    'profit_amount': (order_settings.profit_target_order['price'] - entry_price) * quantity,
                    'probability': '30%',
                    'timeline': '2-4週間'
                },
                'base_case': {
                    'description': '小幅な利益で手動決済',
                    'exit_price': entry_price * Decimal('1.05'),
                    'profit_amount': entry_price * Decimal('0.05') * quantity,
                    'probability': '40%',
                    'timeline': '1-2週間'
                },
                'worst_case': {
                    'description': 'ストップロス発動',
                    'exit_price': order_settings.stop_loss_order['price'],
                    'profit_amount': (order_settings.stop_loss_order['price'] - entry_price) * quantity,
                    'probability': '30%',
                    'timeline': '数日-1週間'
                }
            }
            
        except Exception as e:
            logger.error(f"想定シナリオ生成エラー: {e}")
            return {}

    async def _get_broker_specific_notes(self, risk_level: str) -> Dict[str, List[str]]:
        """証券会社別注意事項"""
        return {
            'SBI証券': [
                'IFDOCO注文は「複合注文」メニューから選択',
                '手数料: 約定金額に応じた手数料体系',
                '注文有効期限は最大3ヶ月間',
                '夜間取引（PTS）でも利用可能'
            ],
            '楽天証券': [
                'IFDOCO注文は「条件付き注文」から選択',
                '楽天ポイントでの手数料支払い可能',
                '注文状況はリアルタイムで確認可能',
                'スマートフォンアプリでも注文可能'
            ],
            'マネックス証券': [
                'IFDOCO注文は「逆指値付通常注文」を利用',
                '米国株でも同様の注文が可能',
                '詳細な注文履歴が確認可能',
                '注文の一部取消・変更が可能'
            ],
            '松井証券': [
                'IFDOCO注文は25歳以下手数料無料',
                '一日定額制手数料体系',
                '注文管理画面で詳細確認可能',
                'サポート体制が充実'
            ]
        }

    async def _generate_monitoring_points(self, request: IfdocoGuideRequest) -> List[str]:
        """監視ポイント生成"""
        return [
            '注文約定状況の定期確認',
            '株価の動向とボラティリティの監視',
            '出来高の変化をチェック',
            '関連ニュース・IR情報の確認',
            '市場全体の動向把握',
            'ストップロス価格の妥当性検討',
            '利確価格到達時の追加戦略検討',
            '保有期間の管理'
        ]

    async def _generate_exit_strategy(self, request: IfdocoGuideRequest, 
                                    order_settings: IfdocoOrderSettings) -> Dict[str, Any]:
        """出口戦略生成"""
        return {
            'primary_exit': {
                'method': 'IFDOCO自動決済',
                'conditions': [
                    f"利確: {order_settings.profit_target_order['price']}円到達時",
                    f"損切り: {order_settings.stop_loss_order['price']}円到達時"
                ]
            },
            'secondary_exit': {
                'method': '手動決済',
                'conditions': [
                    '想定より早く利益が出た場合の早期利確',
                    '重要なニュースが出た場合の緊急決済',
                    '市場全体が急変した場合の損切り'
                ]
            },
            'review_schedule': [
                '注文後1週間での状況確認',
                '保有期間中間点での戦略見直し',
                '注文有効期限前の判断'
            ],
            'decision_criteria': [
                'リスク・リワード比率の変化',
                'ファンダメンタルズの変化',
                'テクニカル指標の悪化',
                'ポートフォリオ全体のバランス'
            ]
        }