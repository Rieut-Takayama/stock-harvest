#!/usr/bin/env python3
"""
ロジックB強化版（黒字転換銘柄精密検出）のスタンドアロンテスト
データベース接続なしで動作確認
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math
import yfinance as yf

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogicDetectionServiceStandalone:
    """ロジック検出サービス（スタンドアロン版）"""
    
    def __init__(self):
        # ロジックB強化版の設定
        self.logic_b_enhanced_config = {
            'ma5_crossover_threshold': 0.02,  # 5日移動平均線上抜け検出閾値（2%）
            'profit_target_rate': 25.0,       # 利確目標（+25%）
            'stop_loss_rate': -10.0,          # 損切りライン（-10%）
            'max_holding_days': 45,           # 最大保有期間（1.5ヶ月）
            'min_volume': 15000000,           # 最低出来高（強化版では高め）
            'earnings_improvement_threshold': 0.10,  # 利益改善率10%以上
            'consecutive_profit_quarters': 2,  # 連続黒字四半期数
            'exclude_loss_carryforward': True, # 繰越損失除外フラグ
        }
        
        # 履歴管理用辞書
        self.stock_history = {}
        self.earnings_data_cache = {}
        self.moving_average_cache = {}
    
    async def detect_logic_b_enhanced(self, stock_data: Dict) -> Dict:
        """
        ロジックB強化版: 黒字転換銘柄精密検出
        直近1年間で初めて経常利益黒字転換 + 5日移動平均線上抜けタイミング
        """
        try:
            stock_code = stock_data.get('code', '')
            
            # Step 1: 黒字転換条件チェック
            profitability_check = await self._check_profitability_turnaround(stock_code)
            if not profitability_check['is_turnaround']:
                return {'detected': False, 'reason': profitability_check['reason']}
            
            # Step 2: 5日移動平均線上抜けチェック
            ma5_crossover = await self._detect_ma5_crossover(stock_data)
            if not ma5_crossover['is_crossover']:
                return {'detected': False, 'reason': 'MA5上抜けシグナルなし'}
            
            # Step 3: エントリー条件の詳細判定
            entry_conditions = await self._validate_entry_conditions_b(stock_data)
            if not entry_conditions['valid']:
                return {'detected': False, 'reason': f'エントリー条件未満: {entry_conditions["reason"]}'}
            
            # Step 4: 除外条件チェック
            exclusion_check = await self._check_exclusion_rules_b(stock_data, stock_code)
            if exclusion_check['should_exclude']:
                return {'detected': False, 'reason': f'除外条件該当: {exclusion_check["reason"]}'}
            
            # Step 5: 売買シグナル生成（ロジックB専用）
            trading_signal = await self._generate_trading_signal_b(stock_data)
            
            logger.info(f"ロジックB強化版検出: {stock_code} - 黒字転換シグナル:{trading_signal['signal_type']}, 強度:{trading_signal['signal_strength']}")
            
            return {
                'detected': True,
                'signal_type': trading_signal['signal_type'],
                'signal_strength': trading_signal['signal_strength'],
                'entry_price': trading_signal['entry_price'],
                'profit_target': trading_signal['profit_target'],
                'stop_loss': trading_signal['stop_loss'],
                'max_holding_days': trading_signal['max_holding_days'],
                'risk_assessment': trading_signal['risk_assessment'],
                'expected_return': trading_signal['expected_return'],
                'max_loss': trading_signal['max_loss'],
                'strategy_type': trading_signal.get('strategy_type', 'profitability_turnaround'),
                'detection_details': {
                    'profitability_turnaround': profitability_check,
                    'ma5_crossover': ma5_crossover,
                    'entry_conditions': entry_conditions,
                    'exclusion_check': exclusion_check
                }
            }
            
        except Exception as e:
            logger.warning(f"ロジックB強化版検出エラー: {str(e)}")
            return {'detected': False, 'reason': f'検出エラー: {str(e)}'}
    
    async def _check_profitability_turnaround(self, stock_code: str) -> Dict:
        """黒字転換条件判定（模擬データ使用）"""
        try:
            # テスト用に模擬的な黒字転換パターンを生成
            mock_data = self._generate_mock_earnings_data()
            return await self._analyze_profitability_turnaround(mock_data)
            
        except Exception as e:
            logger.warning(f"黒字転換判定エラー {stock_code}: {str(e)}")
            return {
                'is_turnaround': False,
                'reason': f'判定エラー: {str(e)}',
                'confidence': 0.0
            }
    
    def _generate_mock_earnings_data(self) -> List[Dict]:
        """模擬決算データ生成（テスト用）"""
        base_date = datetime.now().replace(day=1)
        mock_data = []
        
        # 4四半期分の模擬データ
        for i in range(4):
            quarter_date = (base_date - timedelta(days=90 * i)).date()
            
            # 最新四半期は黒字、それ以前は赤字として模擬
            if i == 0:  # 最新四半期
                income = 50000000  # 5000万円の黒字
                is_profit = True
            else:  # 過去の四半期
                income = -30000000 * (i + 1)  # 赤字が拡大していた
                is_profit = False
            
            mock_data.append({
                'quarter_date': quarter_date,
                'operating_income': income,
                'is_profit': is_profit,
                'source': 'mock_data'
            })
        
        return mock_data
    
    async def _analyze_profitability_turnaround(self, earnings_history: List[Dict]) -> Dict:
        """黒字転換分析"""
        try:
            if len(earnings_history) < 2:
                return {
                    'is_turnaround': False,
                    'reason': '決算データ不足（2四半期分以上必要）',
                    'confidence': 0.0
                }
            
            # 最新四半期の状況
            latest_quarter = earnings_history[0]
            is_latest_profit = latest_quarter['is_profit']
            
            if not is_latest_profit:
                return {
                    'is_turnaround': False,
                    'reason': '最新四半期が黒字ではない',
                    'confidence': 0.0
                }
            
            # 過去の赤字期間をカウント
            consecutive_loss_quarters = 0
            for quarter in earnings_history[1:]:
                if not quarter['is_profit']:
                    consecutive_loss_quarters += 1
                else:
                    break
            
            # 黒字転換条件判定
            min_loss_quarters = self.logic_b_enhanced_config['consecutive_profit_quarters']
            
            if consecutive_loss_quarters >= min_loss_quarters:
                improvement_rate = self._calculate_improvement_rate(earnings_history)
                confidence = min(0.95, 0.6 + (consecutive_loss_quarters * 0.1) + (improvement_rate * 0.25))
                
                return {
                    'is_turnaround': True,
                    'reason': f'{consecutive_loss_quarters}四半期連続赤字からの黒字転換',
                    'confidence': confidence,
                    'consecutive_loss_quarters': consecutive_loss_quarters,
                    'improvement_rate': improvement_rate,
                    'latest_income': latest_quarter['operating_income'],
                    'analysis_date': datetime.now().isoformat()
                }
            else:
                return {
                    'is_turnaround': False,
                    'reason': f'赤字期間が短い（{consecutive_loss_quarters}四半期）',
                    'confidence': 0.3
                }
            
        except Exception as e:
            return {
                'is_turnaround': False,
                'reason': f'分析エラー: {str(e)}',
                'confidence': 0.0
            }
    
    def _calculate_improvement_rate(self, earnings_history: List[Dict]) -> float:
        """利益改善率計算"""
        try:
            if len(earnings_history) < 2:
                return 0.0
            
            latest_income = earnings_history[0]['operating_income']
            past_incomes = [q['operating_income'] for q in earnings_history[1:] if not q['is_profit']]
            
            if not past_incomes:
                return 1.0
            
            avg_past_loss = sum(past_incomes) / len(past_incomes)
            
            if avg_past_loss < 0:
                improvement_rate = (latest_income - avg_past_loss) / abs(avg_past_loss)
                return min(2.0, max(0.0, improvement_rate))
            
            return 0.5
            
        except Exception as e:
            logger.warning(f"改善率計算エラー: {str(e)}")
            return 0.0
    
    async def _detect_ma5_crossover(self, stock_data: Dict) -> Dict:
        """5日移動平均線上抜けタイミング検出（模擬実装）"""
        try:
            current_price = stock_data.get('price', 0)
            
            # 模擬MA5データを生成
            ma5_data = self._generate_mock_ma_data(current_price)
            return self._analyze_ma5_crossover(current_price, ma5_data)
            
        except Exception as e:
            logger.warning(f"MA5上抜け検出エラー: {str(e)}")
            return {
                'is_crossover': False,
                'reason': f'検出エラー: {str(e)}',
                'confidence': 0.0
            }
    
    def _generate_mock_ma_data(self, current_price: float) -> Dict:
        """模擬移動平均データ生成"""
        return {
            'current_ma5': current_price * 0.97,  # 現在価格より3%下に設定
            'previous_ma5': current_price * 0.95,  # 前日はさらに2%下
            'ma5_slope': 0.02,  # 上昇トレンド
            'data_source': 'mock_data',
            'data_points': 5
        }
    
    def _analyze_ma5_crossover(self, current_price: float, ma5_data: Dict) -> Dict:
        """5日移動平均線上抜け分析"""
        try:
            current_ma5 = ma5_data['current_ma5']
            ma5_slope = ma5_data.get('ma5_slope', 0)
            
            crossover_threshold = self.logic_b_enhanced_config['ma5_crossover_threshold']
            
            price_above_ma5 = current_price > current_ma5
            ma5_rising = ma5_slope > 0
            
            if current_ma5 > 0:
                crossover_ratio = (current_price - current_ma5) / current_ma5
                significant_crossover = crossover_ratio >= crossover_threshold
            else:
                crossover_ratio = 0
                significant_crossover = False
            
            is_crossover = price_above_ma5 and ma5_rising and significant_crossover
            
            confidence = 0.0
            if price_above_ma5:
                confidence += 0.4
            if ma5_rising:
                confidence += 0.3
            if significant_crossover:
                confidence += 0.3
            
            return {
                'is_crossover': is_crossover,
                'current_price': current_price,
                'ma5_value': current_ma5,
                'crossover_ratio': crossover_ratio,
                'ma5_slope': ma5_slope,
                'confidence': confidence,
                'reason': '5日MA上抜けシグナル検出' if is_crossover else '上抜け条件未満'
            }
            
        except Exception as e:
            return {
                'is_crossover': False,
                'reason': f'分析エラー: {str(e)}',
                'confidence': 0.0
            }
    
    async def _validate_entry_conditions_b(self, stock_data: Dict) -> Dict:
        """エントリー条件検証"""
        try:
            change_rate = stock_data.get('changeRate', 0)
            volume = stock_data.get('volume', 0)
            signals = stock_data.get('signals', {})
            
            min_volume = self.logic_b_enhanced_config['min_volume']
            volume_valid = volume >= min_volume
            price_change_valid = 1.0 <= change_rate <= 8.0
            
            rsi = signals.get('rsi', 50)
            rsi_valid = 40 <= rsi <= 75
            
            volume_ratio = signals.get('volumeRatio', 1.0)
            volume_ratio_valid = 1.2 <= volume_ratio <= 3.0
            
            all_conditions = [
                ('volume', volume_valid, f'出来高: {volume:,} (最低: {min_volume:,})'),
                ('price_change', price_change_valid, f'価格変化: {change_rate:.1f}% (適正: 1-8%)'),
                ('rsi', rsi_valid, f'RSI: {rsi:.1f} (適正: 40-75)'),
                ('volume_ratio', volume_ratio_valid, f'出来高比率: {volume_ratio:.1f} (適正: 1.2-3.0)')
            ]
            
            failed_conditions = [cond for cond in all_conditions if not cond[1]]
            
            if failed_conditions:
                failed_reasons = [f"{cond[0]}: {cond[2]}" for cond in failed_conditions]
                return {
                    'valid': False,
                    'reason': ', '.join(failed_reasons)
                }
            
            return {
                'valid': True,
                'reason': '全エントリー条件クリア'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'検証エラー: {str(e)}'
            }
    
    async def _check_exclusion_rules_b(self, stock_data: Dict, stock_code: str) -> Dict:
        """除外ルール判定"""
        try:
            change_rate = abs(stock_data.get('changeRate', 0))
            if change_rate > 15.0:
                return {
                    'should_exclude': True,
                    'reason': f'極端な価格変動（{change_rate:.1f}%）'
                }
            
            volume = stock_data.get('volume', 0)
            if volume < 5000000:
                return {
                    'should_exclude': True,
                    'reason': f'低流動性銘柄（出来高: {volume:,}）'
                }
            
            return {'should_exclude': False, 'reason': '除外条件なし'}
            
        except Exception as e:
            return {'should_exclude': False, 'reason': 'エラーのため除外しない'}
    
    async def _generate_trading_signal_b(self, stock_data: Dict) -> Dict:
        """売買シグナル生成"""
        try:
            current_price = stock_data.get('price', 0)
            change_rate = stock_data.get('changeRate', 0)
            signals = stock_data.get('signals', {})
            
            if change_rate >= 1.5:
                signal_type = 'BUY_ENTRY'
                signal_strength = min(90, 50 + (change_rate * 8))
            else:
                signal_type = 'WATCH'
                signal_strength = max(20, change_rate * 20)
            
            entry_price = current_price
            profit_target = entry_price * (1 + self.logic_b_enhanced_config['profit_target_rate'] / 100)
            stop_loss = entry_price * (1 + self.logic_b_enhanced_config['stop_loss_rate'] / 100)
            
            risk_assessment = await self._assess_trading_risk_b(stock_data, signals)
            max_holding_days = self.logic_b_enhanced_config['max_holding_days']
            
            return {
                'signal_type': signal_type,
                'signal_strength': round(signal_strength, 1),
                'entry_price': round(entry_price, 2),
                'profit_target': round(profit_target, 2),
                'stop_loss': round(stop_loss, 2),
                'max_holding_days': max_holding_days,
                'current_price': current_price,
                'expected_return': self.logic_b_enhanced_config['profit_target_rate'],
                'max_loss': self.logic_b_enhanced_config['stop_loss_rate'],
                'risk_assessment': risk_assessment,
                'strategy_type': 'profitability_turnaround'
            }
            
        except Exception as e:
            return {
                'signal_type': 'ERROR',
                'signal_strength': 0,
                'reason': f'シグナル生成エラー: {str(e)}'
            }
    
    async def _assess_trading_risk_b(self, stock_data: Dict, signals: Dict) -> Dict:
        """リスク評価"""
        try:
            risk_factors = []
            risk_score = 70  # ベーススコア
            
            change_rate = abs(stock_data.get('changeRate', 0))
            if change_rate < 2.0:
                risk_factors.append('価格変動が小さい')
                risk_score -= 10
            
            volume = stock_data.get('volume', 0)
            if volume < 10000000:
                risk_factors.append('やや低流動性')
                risk_score -= 15
            
            rsi = signals.get('rsi', 50)
            if rsi > 75:
                risk_factors.append('RSI過熱気味')
                risk_score -= 10
            elif rsi < 40:
                risk_factors.append('RSI低水準')
                risk_score -= 10
            
            if risk_score >= 85:
                risk_level = 'LOW'
            elif risk_score >= 70:
                risk_level = 'MEDIUM'
            elif risk_score >= 55:
                risk_level = 'MEDIUM_HIGH'
            else:
                risk_level = 'HIGH'
            
            recommendations = {
                'LOW': '黒字転換トレンドが良好、通常の投資判断で検討可',
                'MEDIUM': '決算動向を注視しながら慎重に投資検討',
                'MEDIUM_HIGH': '業績改善の持続性を詳細確認後に小額投資検討',
                'HIGH': '投資見送りまたは業績回復の確証後に再検討'
            }
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'strategy_notes': '黒字転換戦略は中長期的な企業価値向上を期待',
                'recommendation': recommendations.get(risk_level, '詳細な業績分析が必要')
            }
            
        except Exception as e:
            return {
                'risk_level': 'MEDIUM_HIGH',
                'risk_score': 50,
                'risk_factors': ['評価エラー'],
                'recommendation': '詳細分析後に投資判断を推奨'
            }
    
    def get_logic_b_enhanced_description(self) -> str:
        """説明を返す"""
        return f"黒字転換銘柄精密検出: 直近1年間初回黒字転換 + 5日MA上抜け + 利確25%/損切り10%"


async def test_logic_b_enhanced():
    """ロジックB強化版の動作テスト"""
    print("🔍 ロジックB強化版（黒字転換銘柄精密検出）テスト開始\n")
    
    # ロジック検出サービスを初期化
    logic_service = LogicDetectionServiceStandalone()
    
    # テスト用の株価データ
    test_stock_data = {
        'code': '3456',
        'name': 'パルコデジタル',
        'price': 1250.0,
        'changeRate': 3.2,
        'volume': 18500000,
        'signals': {
            'rsi': 65.3,
            'macd': 0.05,
            'bollingerPosition': -0.2,
            'trendDirection': 'up',
            'volumeRatio': 2.1,
            'ma5': 1215.0,
            'ma25': 1180.0
        }
    }
    
    print("📊 テスト対象銘柄:")
    print(f"   銘柄コード: {test_stock_data['code']}")
    print(f"   銘柄名: {test_stock_data['name']}")
    print(f"   現在価格: {test_stock_data['price']:,.0f}円")
    print(f"   変化率: {test_stock_data['changeRate']:+.1f}%")
    print(f"   出来高: {test_stock_data['volume']:,}株")
    print(f"   RSI: {test_stock_data['signals']['rsi']:.1f}")
    print()
    
    # ロジックB強化版テスト
    print("🎯 ロジックB強化版検出テスト...")
    result = await logic_service.detect_logic_b_enhanced(test_stock_data)
    
    print("📈 検出結果:")
    print(f"   検出成功: {'✅' if result['detected'] else '❌'}")
    
    if result['detected']:
        print(f"   シグナルタイプ: {result['signal_type']}")
        print(f"   シグナル強度: {result['signal_strength']}%")
        print(f"   エントリー価格: {result['entry_price']:,.0f}円")
        print(f"   利確目標: {result['profit_target']:,.0f}円 (+{result['expected_return']}%)")
        print(f"   損切り: {result['stop_loss']:,.0f}円 ({result['max_loss']}%)")
        print(f"   最大保有期間: {result['max_holding_days']}日")
        print(f"   リスクレベル: {result['risk_assessment']['risk_level']}")
        print(f"   推奨事項: {result['risk_assessment']['recommendation']}")
        
        print("\n🔍 詳細分析結果:")
        if 'detection_details' in result:
            details = result['detection_details']
            
            # 黒字転換分析
            if 'profitability_turnaround' in details:
                prof_data = details['profitability_turnaround']
                print(f"   黒字転換: {'✅' if prof_data.get('is_turnaround', False) else '❌'} ({prof_data.get('confidence', 0):.1%}信頼度)")
                if prof_data.get('is_turnaround'):
                    print(f"     - {prof_data.get('reason', 'N/A')}")
                    print(f"     - 連続赤字四半期: {prof_data.get('consecutive_loss_quarters', 0)}期")
                    print(f"     - 改善率: {prof_data.get('improvement_rate', 0):.1%}")
            
            # MA5上抜け分析
            if 'ma5_crossover' in details:
                ma_data = details['ma5_crossover']
                print(f"   MA5上抜け: {'✅' if ma_data.get('is_crossover', False) else '❌'} ({ma_data.get('confidence', 0):.1%}信頼度)")
                if ma_data.get('is_crossover'):
                    print(f"     - 現在価格: {ma_data.get('current_price', 0):,.0f}円")
                    print(f"     - MA5価格: {ma_data.get('ma5_value', 0):,.0f}円")
                    print(f"     - 上抜け率: {ma_data.get('crossover_ratio', 0):+.1%}")
            
            # エントリー条件
            if 'entry_conditions' in details:
                entry_data = details['entry_conditions']
                print(f"   エントリー条件: {'✅' if entry_data.get('valid', False) else '❌'}")
                if not entry_data.get('valid'):
                    print(f"     - 未満理由: {entry_data.get('reason', 'N/A')}")
    else:
        print(f"   未検出理由: {result.get('reason', 'N/A')}")
    
    print()
    
    # 設定情報の表示
    print("⚙️ ロジックB強化版設定:")
    config = logic_service.logic_b_enhanced_config
    print(f"   MA5上抜け閾値: {config['ma5_crossover_threshold']:.1%}")
    print(f"   利確目標: +{config['profit_target_rate']}%")
    print(f"   損切りライン: {config['stop_loss_rate']}%")
    print(f"   最大保有期間: {config['max_holding_days']}日")
    print(f"   最低出来高: {config['min_volume']:,}株")
    print(f"   連続黒字期間: {config['consecutive_profit_quarters']}四半期")
    
    print("\n📝 説明:")
    print(f"   {logic_service.get_logic_b_enhanced_description()}")
    
    print("\n✅ ロジックB強化版テスト完了")


async def main():
    """メイン実行関数"""
    try:
        await test_logic_b_enhanced()
        print("\n🎉 すべてのテストが完了しました！")
        
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("  ロジックB強化版（黒字転換銘柄精密検出）テスト")
    print("=" * 60)
    
    asyncio.run(main())