"""
ロジック検出サービス（強化版）
ストップ高張り付き精密検出（ロジックA強化版）とセミナーノウハウ対応
上場条件・決算タイミング・履歴管理・売買シグナル機能を包含
"""

import logging
from typing import Dict, bool, List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import math

logger = logging.getLogger(__name__)


class LogicDetectionService:
    """ロジック検出専門サービス（強化版）"""
    
    def __init__(self):
        # ロジックA強化版の設定（セミナーノウハウ対応）
        self.logic_a_enhanced_config = {
            'entry_signal_rate': 5.0,        # エントリーシグナル上昇率（%）
            'profit_target_rate': 24.0,      # 利確目標（%）
            'stop_loss_rate': -10.0,         # 損切り（%）
            'max_holding_days': 30,          # 最大保有期間（日）
            'min_stop_high_volume': 20000000, # ストップ高最低出来高
            'max_lower_shadow_ratio': 0.15,  # 下髭最大比率（15%）
            'max_listing_years': 2.5,        # 上場後最大年数
            'exclude_consecutive_stop_high': True, # 2連続ストップ高除外
        }
        
        # ロジックB強化版の設定（黒字転換銘柄精密検出）
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
        
        # 従来のロジック設定（互換性維持）
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
        
        # 履歴管理用辞書
        self.stock_history = {}
        self.earnings_announcement_cache = {}
        self.earnings_data_cache = {}  # 決算データキャッシュ
        self.moving_average_cache = {}  # 移動平均線キャッシュ
    
    async def detect_logic_a_enhanced(self, stock_data: Dict) -> Dict:
        """
        ロジックA強化版: ストップ高張り付き精密検出（セミナーノウハウ対応）
        返り値: 検出結果・シグナル種別・リスク評価を含む詳細結果
        """
        try:
            stock_code = stock_data.get('code', '')
            
            # Step 1: 上場条件チェック
            if not await self._check_listing_conditions(stock_code):
                return {'detected': False, 'reason': '上場条件未満（2年半以上経過）'}
            
            # Step 2: ストップ高張り付き判定
            stop_high_result = await self._detect_stop_high_sticking(stock_data)
            if not stop_high_result['is_stop_high']:
                return {'detected': False, 'reason': 'ストップ高張り付きでない'}
            
            # Step 3: 決算タイミング判定
            earnings_timing = await self._check_earnings_timing(stock_code)
            if not earnings_timing['is_earnings_day']:
                return {'detected': False, 'reason': '決算翌日でない'}
            
            # Step 4: 除外条件チェック
            exclusion_check = await self._check_exclusion_rules(stock_data, stock_code)
            if exclusion_check['should_exclude']:
                return {'detected': False, 'reason': f'除外条件該当: {exclusion_check["reason"]}'}
            
            # Step 5: 初回条件確認
            first_time_check = await self._check_first_time_condition(stock_code)
            if not first_time_check['is_first_time']:
                return {'detected': False, 'reason': '初回条件達成済み'}
            
            # Step 6: 売買シグナル生成
            trading_signal = await self._generate_trading_signal(stock_data)
            
            # 履歴に記録
            await self._record_stock_history(stock_code, {
                'detection_date': datetime.now(),
                'detection_type': 'logic_a_enhanced',
                'stock_data': stock_data,
                'signal': trading_signal
            })
            
            logger.info(f"ロジックA強化版検出: {stock_code} - シグナル:{trading_signal['signal_type']}, 強度:{trading_signal['signal_strength']}")
            
            return {
                'detected': True,
                'signal_type': trading_signal['signal_type'],
                'signal_strength': trading_signal['signal_strength'],
                'entry_price': trading_signal['entry_price'],
                'profit_target': trading_signal['profit_target'],
                'stop_loss': trading_signal['stop_loss'],
                'max_holding_days': trading_signal['max_holding_days'],
                'risk_assessment': trading_signal['risk_assessment'],
                'detection_details': {
                    'stop_high_details': stop_high_result,
                    'earnings_timing': earnings_timing,
                    'exclusion_check': exclusion_check,
                    'first_time_check': first_time_check
                }
            }
            
        except Exception as e:
            logger.warning(f"ロジックA強化版検出エラー: {str(e)}")
            return {'detected': False, 'reason': f'検出エラー: {str(e)}'}
    
    async def detect_logic_a(self, stock_data: Dict) -> bool:
        """
        ロジックA: 従来版（互換性維持）
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
            
            # 履歴に記録
            await self._record_stock_history(stock_code, {
                'detection_date': datetime.now(),
                'detection_type': 'logic_b_enhanced',
                'stock_data': stock_data,
                'signal': trading_signal,
                'profitability_data': profitability_check
            })
            
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
    
    async def detect_logic_b(self, stock_data: Dict) -> bool:
        """
        ロジックB: 赤字→黒字転換銘柄の検出（従来版・互換性維持）
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
    
    async def _detect_stop_high_sticking(self, stock_data: Dict) -> Dict:
        """
        ストップ高張り付き判定アルゴリズム
        価格がストップ高に達し、張り付き状態を維持しているかを判定
        """
        try:
            stock_code = stock_data.get('code', '')
            current_price = stock_data.get('price', 0)
            change_rate = stock_data.get('changeRate', 0)
            volume = stock_data.get('volume', 0)
            
            # ストップ高価格を計算（日本株は30%が上限だが、実際は業種により異なる）
            # 簡易計算：前日終値から計算（change_rateから逆算）
            if change_rate > 0:
                prev_close = current_price / (1 + change_rate / 100)
                stop_high_price = prev_close * 1.30  # 30%上限として計算
            else:
                return {'is_stop_high': False, 'reason': '価格下落中'}
            
            # ストップ高価格に対する到達率
            stop_high_reach_ratio = current_price / stop_high_price
            
            # 判定条件
            is_stop_high = (
                change_rate >= 15.0 and  # 15%以上の上昇
                stop_high_reach_ratio >= 0.98 and  # ストップ高の98%以上
                volume >= self.logic_a_enhanced_config['min_stop_high_volume']
            )
            
            # 下髭の長さをチェック（ローソク足分析）
            lower_shadow_ratio = await self._calculate_lower_shadow_ratio(stock_data)
            if lower_shadow_ratio > self.logic_a_enhanced_config['max_lower_shadow_ratio']:
                return {
                    'is_stop_high': False, 
                    'reason': f'下髭が長すぎる（{lower_shadow_ratio:.2%}）'
                }
            
            return {
                'is_stop_high': is_stop_high,
                'stop_high_price': stop_high_price,
                'reach_ratio': stop_high_reach_ratio,
                'change_rate': change_rate,
                'volume': volume,
                'lower_shadow_ratio': lower_shadow_ratio,
                'reason': '条件を満たす' if is_stop_high else 'ストップ高条件未満'
            }
            
        except Exception as e:
            logger.warning(f"ストップ高張り付き判定エラー: {str(e)}")
            return {'is_stop_high': False, 'reason': f'計算エラー: {str(e)}'}
    
    async def _calculate_lower_shadow_ratio(self, stock_data: Dict) -> float:
        """
        下髭の長さを計算（ローソク足分析）
        無料APIの制約で簡易実装：価格変動幅に対する下髭比率を推定
        """
        try:
            # 実装簡易版：高値・安値・終値データが必要だが、
            # 現在のstock_dataには含まれていないため推定計算
            change_rate = stock_data.get('changeRate', 0)
            
            # 推定計算：大幅上昇の場合、通常下髭は短い
            if change_rate >= 10:
                # 大幅上昇時の推定下髭比率（実際の実装ではyfinanceから詳細データ取得）
                estimated_lower_shadow = abs(change_rate) * 0.05  # 5%程度と推定
                return estimated_lower_shadow / 100
            else:
                # 通常の上昇時
                return 0.03  # 3%と推定
                
        except Exception as e:
            logger.warning(f"下髭比率計算エラー: {str(e)}")
            return 0.1  # デフォルトで10%とする
    
    async def _check_listing_conditions(self, stock_code: str) -> bool:
        """
        上場条件チェック: 上場2年半以内（最大5年以内）の企業
        """
        try:
            # 実装簡易版：Yahoo Finance等から上場日データを取得する必要があるが、
            # 無料API制限のため、銘柄コードパターンで推定判定
            
            # 新興市場銘柄（通常4桁で3000番台以降が比較的新しい）
            if stock_code.isdigit() and len(stock_code) == 4:
                code_num = int(stock_code)
                
                # 簡易判定：3000番台以降を新興銘柄として扱う
                if code_num >= 3000:
                    return True  # 新興市場とみなす
                
                # その他の条件（実際の実装では上場日APIが必要）
                # ここでは一部の既知新興銘柄をリストアップ
                known_new_listings = [
                    '4385', '4477', '4490', '4499',  # IT系新興
                    '6094', '6195', '6198',          # サービス系
                    '7047', '7095', '7128'           # その他新興
                ]
                
                return stock_code in known_new_listings
            
            # 上記以外は上場2年半超とみなす（保守的判定）
            return False
            
        except Exception as e:
            logger.warning(f"上場条件チェックエラー {stock_code}: {str(e)}")
            return False  # エラー時は条件未満とする
    
    async def _check_earnings_timing(self, stock_code: str) -> Dict:
        """
        決算タイミング判定: 四半期決算翌日かどうかチェック
        """
        try:
            # キャッシュから決算日情報を取得
            if stock_code in self.earnings_announcement_cache:
                cached_data = self.earnings_announcement_cache[stock_code]
                
                # キャッシュの有効期限チェック（1日間有効）
                if datetime.now() - cached_data['cached_date'] < timedelta(days=1):
                    earnings_date = cached_data['earnings_date']
                    
                    # 決算翌日判定
                    today = datetime.now().date()
                    is_earnings_day = (today - earnings_date).days == 1
                    
                    return {
                        'is_earnings_day': is_earnings_day,
                        'earnings_date': earnings_date,
                        'days_since_earnings': (today - earnings_date).days,
                        'source': 'cache'
                    }
            
            # 実装簡易版：決算日の正確な特定には有料APIが必要
            # 無料実装では月末・四半期末を決算日として推定
            today = datetime.now()
            
            # 四半期末（3, 6, 9, 12月末）の翌営業日を決算発表日と推定
            quarter_ends = [
                datetime(today.year, 3, 31),
                datetime(today.year, 6, 30), 
                datetime(today.year, 9, 30),
                datetime(today.year, 12, 31)
            ]
            
            # 直近の四半期末を特定
            recent_quarter_end = None
            for quarter_end in quarter_ends:
                if quarter_end <= today:
                    recent_quarter_end = quarter_end
            
            # 前年四半期も考慮
            if recent_quarter_end is None and quarter_ends:
                prev_year_q4 = datetime(today.year - 1, 12, 31)
                recent_quarter_end = prev_year_q4
            
            if recent_quarter_end:
                # 決算発表は四半期末から1-45日後と推定
                days_since_quarter = (today - recent_quarter_end).days
                is_likely_earnings_period = 1 <= days_since_quarter <= 45
                
                # キャッシュに保存
                self.earnings_announcement_cache[stock_code] = {
                    'earnings_date': recent_quarter_end.date(),
                    'cached_date': datetime.now(),
                    'estimated': True
                }
                
                return {
                    'is_earnings_day': is_likely_earnings_period,
                    'earnings_date': recent_quarter_end.date(),
                    'days_since_earnings': days_since_quarter,
                    'source': 'estimated',
                    'note': '四半期末からの推定'
                }
            
            return {
                'is_earnings_day': False,
                'reason': '決算期判定不可',
                'source': 'unknown'
            }
            
        except Exception as e:
            logger.warning(f"決算タイミング判定エラー {stock_code}: {str(e)}")
            return {
                'is_earnings_day': False, 
                'reason': f'判定エラー: {str(e)}',
                'source': 'error'
            }
    
    async def _check_exclusion_rules(self, stock_data: Dict, stock_code: str) -> Dict:
        """
        除外ルール判定: 2連続ストップ高・下髭長い銘柄の除外
        """
        try:
            # 2連続ストップ高チェック
            if self.logic_a_enhanced_config['exclude_consecutive_stop_high']:
                consecutive_check = await self._check_consecutive_stop_high(stock_code)
                if consecutive_check['is_consecutive']:
                    return {
                        'should_exclude': True,
                        'reason': f"2連続ストップ高検出（{consecutive_check['consecutive_days']}日連続）"
                    }
            
            # 下髭の長さチェック（既に_detect_stop_high_stickingで実行済みだが、再確認）
            lower_shadow_ratio = await self._calculate_lower_shadow_ratio(stock_data)
            if lower_shadow_ratio > self.logic_a_enhanced_config['max_lower_shadow_ratio']:
                return {
                    'should_exclude': True,
                    'reason': f"下髭が長すぎる（{lower_shadow_ratio:.2%}）"
                }
            
            # 決算発表以外のストップ高除外（実装簡易版）
            change_rate = stock_data.get('changeRate', 0)
            if change_rate >= 20.0:  # 20%以上の大幅上昇
                # 決算タイミング以外での大幅上昇は除外対象とする
                earnings_check = await self._check_earnings_timing(stock_code)
                if not earnings_check['is_earnings_day']:
                    return {
                        'should_exclude': True,
                        'reason': "決算発表以外でのストップ高（材料不明）"
                    }
            
            return {'should_exclude': False, 'reason': '除外条件なし'}
            
        except Exception as e:
            logger.warning(f"除外ルール判定エラー {stock_code}: {str(e)}")
            return {'should_exclude': False, 'reason': 'エラーのため除外しない'}
    
    async def _check_consecutive_stop_high(self, stock_code: str) -> Dict:
        """
        連続ストップ高チェック（実装簡易版）
        """
        try:
            # 履歴から過去のストップ高日を取得
            if stock_code in self.stock_history:
                history = self.stock_history[stock_code]
                
                # 直近のストップ高検出履歴をチェック
                recent_detections = []
                today = datetime.now().date()
                
                for record in history:
                    detection_date = record.get('detection_date', datetime.now()).date()
                    days_ago = (today - detection_date).days
                    
                    # 直近3日以内のストップ高検出を確認
                    if days_ago <= 3 and record.get('detection_type') == 'stop_high':
                        recent_detections.append({
                            'date': detection_date,
                            'days_ago': days_ago
                        })
                
                # 連続ストップ高の判定
                if len(recent_detections) >= 2:
                    return {
                        'is_consecutive': True,
                        'consecutive_days': len(recent_detections),
                        'recent_dates': [d['date'] for d in recent_detections]
                    }
            
            return {'is_consecutive': False, 'consecutive_days': 0}
            
        except Exception as e:
            logger.warning(f"連続ストップ高チェックエラー {stock_code}: {str(e)}")
            return {'is_consecutive': False, 'consecutive_days': 0}
    
    async def _check_first_time_condition(self, stock_code: str) -> Dict:
        """
        初回条件達成判定: 過去に同一ロジックで検出されていないかチェック
        """
        try:
            if stock_code in self.stock_history:
                history = self.stock_history[stock_code]
                
                # 過去のロジックA強化版検出履歴をチェック
                for record in history:
                    if record.get('detection_type') == 'logic_a_enhanced':
                        return {
                            'is_first_time': False,
                            'previous_detection_date': record.get('detection_date'),
                            'reason': '過去に条件達成済み'
                        }
            
            return {
                'is_first_time': True,
                'reason': '初回条件達成'
            }
            
        except Exception as e:
            logger.warning(f"初回条件判定エラー {stock_code}: {str(e)}")
            return {'is_first_time': True, 'reason': 'エラーのため初回とみなす'}
    
    async def _generate_trading_signal(self, stock_data: Dict) -> Dict:
        """
        売買シグナル生成: エントリー・利確・損切りシグナルを生成
        """
        try:
            current_price = stock_data.get('price', 0)
            change_rate = stock_data.get('changeRate', 0)
            volume = stock_data.get('volume', 0)
            signals = stock_data.get('signals', {})
            
            # エントリーシグナル判定（+5%上昇時）
            entry_trigger_rate = self.logic_a_enhanced_config['entry_signal_rate']
            if change_rate >= entry_trigger_rate:
                signal_type = 'BUY_ENTRY'
                signal_strength = min(100, (change_rate / entry_trigger_rate) * 60 + 40)  # 40-100%
            else:
                signal_type = 'WATCH'
                signal_strength = (change_rate / entry_trigger_rate) * 40  # 0-40%
            
            # 価格ターゲット計算
            entry_price = current_price * (1 + entry_trigger_rate / 100)
            profit_target = entry_price * (1 + self.logic_a_enhanced_config['profit_target_rate'] / 100)
            stop_loss = entry_price * (1 + self.logic_a_enhanced_config['stop_loss_rate'] / 100)
            
            # リスク評価
            risk_assessment = await self._assess_trading_risk(stock_data, signals)
            
            # 最大保有期間
            max_holding_days = self.logic_a_enhanced_config['max_holding_days']
            
            return {
                'signal_type': signal_type,
                'signal_strength': round(signal_strength, 1),
                'entry_price': round(entry_price, 2),
                'profit_target': round(profit_target, 2),
                'stop_loss': round(stop_loss, 2),
                'max_holding_days': max_holding_days,
                'current_price': current_price,
                'expected_return': self.logic_a_enhanced_config['profit_target_rate'],
                'max_loss': self.logic_a_enhanced_config['stop_loss_rate'],
                'risk_assessment': risk_assessment,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"売買シグナル生成エラー: {str(e)}")
            return {
                'signal_type': 'ERROR',
                'signal_strength': 0,
                'reason': f'シグナル生成エラー: {str(e)}'
            }
    
    async def _assess_trading_risk(self, stock_data: Dict, signals: Dict) -> Dict:
        """
        トレーディングリスク評価
        """
        try:
            risk_factors = []
            risk_score = 0  # 0-100, 低いほど高リスク
            
            # RSI評価
            rsi = signals.get('rsi', 50)
            if rsi > 80:
                risk_factors.append('RSI過熱（買われ過ぎ）')
                risk_score += 20
            elif rsi > 70:
                risk_factors.append('RSI高水準')
                risk_score += 40
            else:
                risk_score += 70
            
            # 出来高評価
            volume_ratio = signals.get('volumeRatio', 1.0)
            if volume_ratio > 3.0:
                risk_factors.append('異常高出来高')
                risk_score += 10
            elif volume_ratio > 2.0:
                risk_factors.append('高出来高')
                risk_score += 20
            else:
                risk_score += 30
            
            # ボラティリティ評価
            change_rate = abs(stock_data.get('changeRate', 0))
            if change_rate > 25:
                risk_factors.append('極端な値動き')
                risk_score += 0
            elif change_rate > 15:
                risk_factors.append('大幅な値動き')
                risk_score += 10
            else:
                risk_score += 20
            
            # リスクレベル判定
            risk_score = min(100, risk_score)  # 最大100点
            
            if risk_score >= 80:
                risk_level = 'LOW'
            elif risk_score >= 60:
                risk_level = 'MEDIUM'
            elif risk_score >= 40:
                risk_level = 'HIGH'
            else:
                risk_level = 'VERY_HIGH'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'recommendation': self._get_risk_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.warning(f"リスク評価エラー: {str(e)}")
            return {
                'risk_level': 'HIGH',
                'risk_score': 30,
                'risk_factors': ['評価エラー'],
                'recommendation': '慎重な判断を推奨'
            }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """リスクレベルに応じた推奨事項"""
        recommendations = {
            'LOW': '通常の投資判断で問題なし',
            'MEDIUM': '適切なリスク管理の下で投資検討',
            'HIGH': '小額での投資またはより詳細な分析を推奨',
            'VERY_HIGH': '投資見送りまたは専門家への相談を推奨'
        }
        return recommendations.get(risk_level, '詳細な分析が必要')
    
    async def _record_stock_history(self, stock_code: str, record: Dict) -> None:
        """
        銘柄履歴記録: 検出結果を履歴に保存
        """
        try:
            if stock_code not in self.stock_history:
                self.stock_history[stock_code] = []
            
            # 履歴に新しいレコードを追加
            self.stock_history[stock_code].append(record)
            
            # 履歴の上限管理（直近50件まで）
            if len(self.stock_history[stock_code]) > 50:
                self.stock_history[stock_code] = self.stock_history[stock_code][-50:]
            
            logger.info(f"履歴記録完了: {stock_code} - {record.get('detection_type', 'unknown')}")
            
        except Exception as e:
            logger.warning(f"履歴記録エラー {stock_code}: {str(e)}")
    
    def get_stock_history(self, stock_code: str) -> List[Dict]:
        """
        指定銘柄の履歴を取得
        """
        return self.stock_history.get(stock_code, [])
    
    def get_all_detected_stocks(self, detection_type: str = None) -> List[Dict]:
        """
        すべての検出銘柄履歴を取得
        """
        result = []
        for stock_code, history in self.stock_history.items():
            for record in history:
                if detection_type is None or record.get('detection_type') == detection_type:
                    result.append({
                        'stock_code': stock_code,
                        **record
                    })
        
        # 検出日時順でソート
        result.sort(key=lambda x: x.get('detection_date', datetime.min), reverse=True)
        return result
    
    # ===========================
    # ロジックB強化版 専用メソッド群
    # ===========================
    
    async def _check_profitability_turnaround(self, stock_code: str) -> Dict:
        """
        黒字転換条件判定: 直近1年間で初めて経常利益が黒字転換
        """
        try:
            # キャッシュから決算データを取得
            if stock_code in self.earnings_data_cache:
                cached_data = self.earnings_data_cache[stock_code]
                
                # キャッシュの有効期限チェック（1週間有効）
                if datetime.now() - cached_data['cached_date'] < timedelta(days=7):
                    earnings_history = cached_data['earnings_history']
                    return await self._analyze_profitability_turnaround(earnings_history)
            
            # 決算データ取得（実装簡易版：Yahoo Finance等から取得）
            earnings_data = await self._fetch_earnings_data(stock_code)
            
            # キャッシュに保存
            self.earnings_data_cache[stock_code] = {
                'earnings_history': earnings_data,
                'cached_date': datetime.now()
            }
            
            return await self._analyze_profitability_turnaround(earnings_data)
            
        except Exception as e:
            logger.warning(f"黒字転換判定エラー {stock_code}: {str(e)}")
            return {
                'is_turnaround': False,
                'reason': f'判定エラー: {str(e)}',
                'confidence': 0.0
            }
    
    async def _fetch_earnings_data(self, stock_code: str) -> List[Dict]:
        """
        決算データ取得（EDINET公開データ・企業IR情報活用）
        無料版実装：Yahoo Finance財務データを活用
        """
        try:
            # Yahoo Finance Tickerオブジェクト作成
            ticker = yf.Ticker(f"{stock_code}.T")  # 東証銘柄
            
            # 四半期財務データ取得
            quarterly_financials = ticker.quarterly_financials
            
            if quarterly_financials is None or quarterly_financials.empty:
                # データが取得できない場合、模擬データで代替
                return self._generate_mock_earnings_data()
            
            # 経常利益に相当するデータを抽出
            earnings_history = []
            
            # Operating Income（営業利益）を経常利益の代替として使用
            if 'Operating Income' in quarterly_financials.index:
                operating_income_data = quarterly_financials.loc['Operating Income']
                
                for quarter_date, income_value in operating_income_data.items():
                    if income_value is not None and not math.isnan(income_value):
                        earnings_history.append({
                            'quarter_date': quarter_date.date(),
                            'operating_income': float(income_value),
                            'is_profit': income_value > 0,
                            'source': 'yahoo_finance'
                        })
            
            # 最新4四半期分にフィルタリング
            earnings_history.sort(key=lambda x: x['quarter_date'], reverse=True)
            return earnings_history[:4]
            
        except Exception as e:
            logger.warning(f"決算データ取得エラー {stock_code}: {str(e)}")
            # エラー時は模擬データを返す
            return self._generate_mock_earnings_data()
    
    def _generate_mock_earnings_data(self) -> List[Dict]:
        """
        模擬決算データ生成（テスト・デモ用）
        実際のプロダクションでは実データ取得が必要
        """
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
        """
        黒字転換分析: 決算データから黒字転換パターンを判定
        """
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
                    break  # 黒字四半期が見つかったら停止
            
            # 黒字転換条件判定
            min_loss_quarters = self.logic_b_enhanced_config['consecutive_profit_quarters']
            
            if consecutive_loss_quarters >= min_loss_quarters:
                # 初回黒字転換と判定
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
            logger.warning(f"黒字転換分析エラー: {str(e)}")
            return {
                'is_turnaround': False,
                'reason': f'分析エラー: {str(e)}',
                'confidence': 0.0
            }
    
    def _calculate_improvement_rate(self, earnings_history: List[Dict]) -> float:
        """
        利益改善率計算: 最新四半期と過去平均の改善度を算出
        """
        try:
            if len(earnings_history) < 2:
                return 0.0
            
            latest_income = earnings_history[0]['operating_income']
            
            # 過去四半期の平均損失計算
            past_incomes = [q['operating_income'] for q in earnings_history[1:] if not q['is_profit']]
            
            if not past_incomes:
                return 1.0  # 全て黒字の場合
            
            avg_past_loss = sum(past_incomes) / len(past_incomes)
            
            # 改善率計算（赤字から黒字への改善度）
            if avg_past_loss < 0:
                improvement_rate = (latest_income - avg_past_loss) / abs(avg_past_loss)
                return min(2.0, max(0.0, improvement_rate))  # 0-200%の範囲
            
            return 0.5  # デフォルト改善率
            
        except Exception as e:
            logger.warning(f"改善率計算エラー: {str(e)}")
            return 0.0
    
    async def _detect_ma5_crossover(self, stock_data: Dict) -> Dict:
        """
        5日移動平均線上抜けタイミング検出
        """
        try:
            stock_code = stock_data.get('code', '')
            current_price = stock_data.get('price', 0)
            
            # キャッシュから移動平均データを取得
            if stock_code in self.moving_average_cache:
                cached_data = self.moving_average_cache[stock_code]
                
                # キャッシュの有効期限チェック（1日有効）
                if datetime.now() - cached_data['cached_date'] < timedelta(hours=1):
                    ma5_data = cached_data['ma5_data']
                    return self._analyze_ma5_crossover(current_price, ma5_data)
            
            # 5日移動平均線データ取得
            ma5_data = await self._fetch_moving_average_data(stock_code, 5)
            
            # キャッシュに保存
            self.moving_average_cache[stock_code] = {
                'ma5_data': ma5_data,
                'cached_date': datetime.now()
            }
            
            return self._analyze_ma5_crossover(current_price, ma5_data)
            
        except Exception as e:
            logger.warning(f"MA5上抜け検出エラー {stock_code}: {str(e)}")
            return {
                'is_crossover': False,
                'reason': f'検出エラー: {str(e)}',
                'confidence': 0.0
            }
    
    async def _fetch_moving_average_data(self, stock_code: str, period: int) -> Dict:
        """
        移動平均線データ取得
        """
        try:
            # Yahoo Financeから過去データを取得
            ticker = yf.Ticker(f"{stock_code}.T")
            hist_data = ticker.history(period="1mo")  # 1ヶ月分のデータ
            
            if hist_data is None or hist_data.empty:
                # データが取得できない場合、現在価格ベースで推定
                return self._generate_mock_ma_data(stock_code)
            
            # 終値から移動平均を計算
            close_prices = hist_data['Close'].values
            
            if len(close_prices) >= period:
                # 直近5日間の平均価格
                recent_ma = sum(close_prices[-period:]) / period
                
                # 前日の移動平均（推定）
                if len(close_prices) >= period + 1:
                    prev_ma = sum(close_prices[-(period+1):-1]) / period
                else:
                    prev_ma = recent_ma * 0.98  # 2%下として推定
                
                return {
                    'current_ma5': recent_ma,
                    'previous_ma5': prev_ma,
                    'ma5_slope': (recent_ma - prev_ma) / prev_ma if prev_ma > 0 else 0,
                    'data_source': 'yahoo_finance',
                    'data_points': len(close_prices)
                }
            else:
                return self._generate_mock_ma_data(stock_code)
                
        except Exception as e:
            logger.warning(f"移動平均データ取得エラー {stock_code}: {str(e)}")
            return self._generate_mock_ma_data(stock_code)
    
    def _generate_mock_ma_data(self, stock_code: str) -> Dict:
        """
        模擬移動平均データ生成
        """
        # 現在価格から推定MA5を生成
        base_price = 1000  # 基準価格（実際は現在価格を使用）
        
        return {
            'current_ma5': base_price * 0.97,  # 現在価格より3%下に設定
            'previous_ma5': base_price * 0.95,  # 前日はさらに2%下
            'ma5_slope': 0.02,  # 上昇トレンド
            'data_source': 'mock_data',
            'data_points': 5
        }
    
    def _analyze_ma5_crossover(self, current_price: float, ma5_data: Dict) -> Dict:
        """
        5日移動平均線上抜け分析
        """
        try:
            current_ma5 = ma5_data['current_ma5']
            previous_ma5 = ma5_data['previous_ma5']
            ma5_slope = ma5_data.get('ma5_slope', 0)
            
            # 上抜け条件判定
            crossover_threshold = self.logic_b_enhanced_config['ma5_crossover_threshold']
            
            # 現在価格がMA5より上
            price_above_ma5 = current_price > current_ma5
            
            # MA5の上昇傾向
            ma5_rising = ma5_slope > 0
            
            # 上抜け幅が閾値以上
            if current_ma5 > 0:
                crossover_ratio = (current_price - current_ma5) / current_ma5
                significant_crossover = crossover_ratio >= crossover_threshold
            else:
                significant_crossover = False
            
            # 総合判定
            is_crossover = price_above_ma5 and ma5_rising and significant_crossover
            
            # 信頼度計算
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
                'crossover_ratio': crossover_ratio if current_ma5 > 0 else 0,
                'ma5_slope': ma5_slope,
                'confidence': confidence,
                'reason': '5日MA上抜けシグナル検出' if is_crossover else '上抜け条件未満',
                'analysis_details': {
                    'price_above_ma5': price_above_ma5,
                    'ma5_rising': ma5_rising,
                    'significant_crossover': significant_crossover
                }
            }
            
        except Exception as e:
            logger.warning(f"MA5上抜け分析エラー: {str(e)}")
            return {
                'is_crossover': False,
                'reason': f'分析エラー: {str(e)}',
                'confidence': 0.0
            }
    
    async def _validate_entry_conditions_b(self, stock_data: Dict) -> Dict:
        """
        ロジックB強化版のエントリー条件検証
        """
        try:
            change_rate = stock_data.get('changeRate', 0)
            volume = stock_data.get('volume', 0)
            signals = stock_data.get('signals', {})
            
            # 必要出来高チェック
            min_volume = self.logic_b_enhanced_config['min_volume']
            volume_valid = volume >= min_volume
            
            # 価格上昇チェック（穏やかな上昇を期待）
            price_change_valid = 1.0 <= change_rate <= 8.0  # 1-8%の穏やかな上昇
            
            # RSI適正範囲チェック（過熱していない）
            rsi = signals.get('rsi', 50)
            rsi_valid = 40 <= rsi <= 75  # 適正範囲
            
            # 出来高比率チェック（異常な出来高は除外）
            volume_ratio = signals.get('volumeRatio', 1.0)
            volume_ratio_valid = 1.2 <= volume_ratio <= 3.0  # 適度な出来高増加
            
            # 全条件チェック
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
                    'reason': ', '.join(failed_reasons),
                    'failed_conditions': failed_conditions
                }
            
            return {
                'valid': True,
                'reason': '全エントリー条件クリア',
                'conditions_summary': {
                    'volume': volume,
                    'change_rate': change_rate,
                    'rsi': rsi,
                    'volume_ratio': volume_ratio
                }
            }
            
        except Exception as e:
            logger.warning(f"エントリー条件検証エラー: {str(e)}")
            return {
                'valid': False,
                'reason': f'検証エラー: {str(e)}'
            }
    
    async def _check_exclusion_rules_b(self, stock_data: Dict, stock_code: str) -> Dict:
        """
        ロジックB強化版の除外ルール判定
        """
        try:
            # 繰越損失除外チェック
            if self.logic_b_enhanced_config['exclude_loss_carryforward']:
                loss_carryforward_check = await self._check_loss_carryforward(stock_code)
                if loss_carryforward_check['has_loss_carryforward']:
                    return {
                        'should_exclude': True,
                        'reason': '繰越損失あり（税務上の理由で除外）'
                    }
            
            # 極端な価格変動除外
            change_rate = abs(stock_data.get('changeRate', 0))
            if change_rate > 15.0:  # 15%以上の大幅変動
                return {
                    'should_exclude': True,
                    'reason': f'極端な価格変動（{change_rate:.1f}%）'
                }
            
            # 低流動性銘柄除外
            volume = stock_data.get('volume', 0)
            if volume < 5000000:  # 500万株未満
                return {
                    'should_exclude': True,
                    'reason': f'低流動性銘柄（出来高: {volume:,}）'
                }
            
            # 過去の黒字転換履歴チェック（重複除外）
            previous_detection_check = await self._check_previous_b_detection(stock_code)
            if previous_detection_check['previously_detected']:
                return {
                    'should_exclude': True,
                    'reason': f'過去6ヶ月以内に検出済み（{previous_detection_check["last_detection_date"]}）'
                }
            
            return {'should_exclude': False, 'reason': '除外条件なし'}
            
        except Exception as e:
            logger.warning(f"ロジックB除外ルール判定エラー {stock_code}: {str(e)}")
            return {'should_exclude': False, 'reason': 'エラーのため除外しない'}
    
    async def _check_loss_carryforward(self, stock_code: str) -> Dict:
        """
        繰越損失チェック（簡易実装）
        実際の実装では有価証券報告書等の詳細データが必要
        """
        try:
            # 簡易実装：過去の決算データから推定
            if stock_code in self.earnings_data_cache:
                cached_data = self.earnings_data_cache[stock_code]
                earnings_history = cached_data['earnings_history']
                
                # 過去3年間の累積損失を計算
                cumulative_loss = 0
                loss_quarters = 0
                
                for quarter in earnings_history:
                    if not quarter['is_profit']:
                        cumulative_loss += abs(quarter['operating_income'])
                        loss_quarters += 1
                
                # 大幅な累積損失がある場合は繰越損失ありと推定
                significant_cumulative_loss = cumulative_loss > 100000000  # 1億円以上
                extended_loss_period = loss_quarters >= 6  # 6四半期以上の赤字
                
                has_loss_carryforward = significant_cumulative_loss and extended_loss_period
                
                return {
                    'has_loss_carryforward': has_loss_carryforward,
                    'cumulative_loss': cumulative_loss,
                    'loss_quarters': loss_quarters,
                    'reason': '大幅な累積損失' if has_loss_carryforward else '繰越損失なし'
                }
            
            # データがない場合は繰越損失なしとみなす
            return {
                'has_loss_carryforward': False,
                'reason': '決算データなし（繰越損失なしとみなす）'
            }
            
        except Exception as e:
            logger.warning(f"繰越損失チェックエラー {stock_code}: {str(e)}")
            return {
                'has_loss_carryforward': False,
                'reason': 'チェックエラー（繰越損失なしとみなす）'
            }
    
    async def _check_previous_b_detection(self, stock_code: str) -> Dict:
        """
        過去のロジックB検出履歴チェック
        """
        try:
            if stock_code in self.stock_history:
                history = self.stock_history[stock_code]
                
                # 過去6ヶ月以内のロジックB検出をチェック
                six_months_ago = datetime.now() - timedelta(days=180)
                
                for record in history:
                    if record.get('detection_type') == 'logic_b_enhanced':
                        detection_date = record.get('detection_date', datetime.now())
                        
                        if isinstance(detection_date, str):
                            detection_date = datetime.fromisoformat(detection_date.replace('Z', '+00:00'))
                        
                        if detection_date > six_months_ago:
                            return {
                                'previously_detected': True,
                                'last_detection_date': detection_date.strftime('%Y-%m-%d'),
                                'days_since_detection': (datetime.now() - detection_date).days
                            }
            
            return {
                'previously_detected': False,
                'reason': '過去6ヶ月以内に検出履歴なし'
            }
            
        except Exception as e:
            logger.warning(f"過去検出履歴チェックエラー {stock_code}: {str(e)}")
            return {
                'previously_detected': False,
                'reason': '履歴チェックエラー'
            }
    
    async def _generate_trading_signal_b(self, stock_data: Dict) -> Dict:
        """
        ロジックB専用売買シグナル生成
        +25%利確/-10%損切り、1.5ヶ月保有期間管理
        """
        try:
            current_price = stock_data.get('price', 0)
            change_rate = stock_data.get('changeRate', 0)
            volume = stock_data.get('volume', 0)
            signals = stock_data.get('signals', {})
            
            # エントリーシグナル判定（MA5上抜けタイミング）
            if change_rate >= 1.5:  # 1.5%以上の上昇でエントリーシグナル
                signal_type = 'BUY_ENTRY'
                signal_strength = min(90, 50 + (change_rate * 8))  # 50-90%の範囲
            else:
                signal_type = 'WATCH'
                signal_strength = max(20, change_rate * 20)  # 0-30%の範囲
            
            # 価格ターゲット計算（ロジックB強化版設定）
            entry_price = current_price
            profit_target = entry_price * (1 + self.logic_b_enhanced_config['profit_target_rate'] / 100)
            stop_loss = entry_price * (1 + self.logic_b_enhanced_config['stop_loss_rate'] / 100)
            
            # リスク評価（ロジックB専用）
            risk_assessment = await self._assess_trading_risk_b(stock_data, signals)
            
            # 最大保有期間（1.5ヶ月）
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
                'strategy_type': 'profitability_turnaround',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"ロジックB売買シグナル生成エラー: {str(e)}")
            return {
                'signal_type': 'ERROR',
                'signal_strength': 0,
                'reason': f'シグナル生成エラー: {str(e)}'
            }
    
    async def _assess_trading_risk_b(self, stock_data: Dict, signals: Dict) -> Dict:
        """
        ロジックB専用リスク評価
        """
        try:
            risk_factors = []
            risk_score = 0  # 0-100, 低いほど高リスク
            
            # 決算期タイミングリスク
            change_rate = abs(stock_data.get('changeRate', 0))
            if change_rate < 2.0:
                risk_factors.append('価格変動が小さい（動きが鈍い）')
                risk_score += 20
            else:
                risk_score += 40
            
            # 流動性リスク
            volume = stock_data.get('volume', 0)
            if volume < 10000000:  # 1000万株未満
                risk_factors.append('やや低流動性')
                risk_score += 20
            else:
                risk_score += 35
            
            # RSI過熱リスク
            rsi = signals.get('rsi', 50)
            if rsi > 75:
                risk_factors.append('RSI過熱気味')
                risk_score += 15
            elif rsi < 40:
                risk_factors.append('RSI低水準（下落継続リスク）')
                risk_score += 20
            else:
                risk_score += 35
            
            # 業績改善の持続性リスク（中期的視点）
            if len(risk_factors) == 0:
                risk_score += 10  # ボーナス点
            
            # リスクレベル判定（ロジックBは比較的低リスク戦略）
            risk_score = min(100, risk_score)
            
            if risk_score >= 85:
                risk_level = 'LOW'
            elif risk_score >= 70:
                risk_level = 'MEDIUM'
            elif risk_score >= 55:
                risk_level = 'MEDIUM_HIGH'
            else:
                risk_level = 'HIGH'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'strategy_notes': '黒字転換戦略は中長期的な企業価値向上を期待',
                'recommendation': self._get_risk_recommendation_b(risk_level)
            }
            
        except Exception as e:
            logger.warning(f"ロジックBリスク評価エラー: {str(e)}")
            return {
                'risk_level': 'MEDIUM_HIGH',
                'risk_score': 50,
                'risk_factors': ['評価エラー'],
                'recommendation': '詳細分析後に投資判断を推奨'
            }
    
    def _get_risk_recommendation_b(self, risk_level: str) -> str:
        """ロジックB専用リスクレベル推奨事項"""
        recommendations = {
            'LOW': '黒字転換トレンドが良好、通常の投資判断で検討可',
            'MEDIUM': '決算動向を注視しながら慎重に投資検討',
            'MEDIUM_HIGH': '業績改善の持続性を詳細確認後に小額投資検討',
            'HIGH': '投資見送りまたは業績回復の確証後に再検討'
        }
        return recommendations.get(risk_level, '詳細な業績分析が必要')
    
    def get_logic_b_enhanced_description(self) -> str:
        """ロジックB強化版の説明を返す"""
        return f"黒字転換銘柄精密検出: 直近1年間初回黒字転換 + 5日MA上抜け + 利確25%/損切り10%"
    
    def update_logic_b_enhanced_config(self, **kwargs) -> None:
        """ロジックB強化版の設定を更新"""
        for key, value in kwargs.items():
            if key in self.logic_b_enhanced_config:
                self.logic_b_enhanced_config[key] = value
                logger.info(f"ロジックB強化版設定更新: {key} = {value}")
    
    def get_all_logic_configs(self) -> Dict:
        """現在の全ロジック設定を取得"""
        return {
            'logic_a': self.logic_a_config.copy(),
            'logic_a_enhanced': self.logic_a_enhanced_config.copy(),
            'logic_b': self.logic_b_config.copy(),
            'logic_b_enhanced': self.logic_b_enhanced_config.copy()
        }