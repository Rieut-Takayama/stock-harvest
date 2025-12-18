"""
売買支援APIバリデーター統合テスト
@9統合テスト成功請負人が実行・成功させるテスト

実データバリデーションに焦点を当てた統合テスト
"""

import pytest
import asyncio
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime

from tests.utils.MilestoneTracker import MilestoneTracker

# システム配下のインポート
import sys
import os

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from src.validators.trading_validators import (
    EntryOptimizationValidator,
    IfdocoGuideValidator,
    TradingHistoryValidator,
    SignalHistoryValidator,
    validate_stock_code,
    validate_price,
    validate_investment_amount,
    validate_risk_tolerance,
    validate_timeframe,
    validate_pagination,
    validate_date_range
)


class TradingValidatorsIntegrationTest:
    """売買支援APIバリデーター統合テスト"""

    async def test_entry_optimization_validator_comprehensive(self):
        """エントリーポイント最適化バリデーター包括テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("エントリーポイント最適化バリデーター包括テスト")
        
        try:
            # 正常ケーステスト
            valid_data = {
                'stock_code': '7203',
                'current_price': 1000.0,
                'logic_type': 'logic_a',
                'investment_amount': 100000.0,
                'risk_tolerance': 'medium',
                'timeframe': '1m',
                'market_conditions': {'trend': 'bullish'}
            }
            
            result = EntryOptimizationValidator.validate_request(valid_data)
            assert result['stock_code'] == '7203'
            assert result['current_price'] == Decimal('1000.0')
            assert result['logic_type'] == 'logic_a'
            assert result['risk_tolerance'] == 'medium'
            assert result['timeframe'] == '1m'
            tracker.mark("正常ケース検証成功")
            
            # 異常ケーステスト群
            invalid_cases = [
                # 銘柄コード異常
                {'stock_code': '123', 'current_price': 1000.0},  # 3桁
                {'stock_code': '12345', 'current_price': 1000.0},  # 5桁  
                {'stock_code': 'ABCD', 'current_price': 1000.0},  # アルファベット
                {'stock_code': '', 'current_price': 1000.0},      # 空文字
                
                # 価格異常
                {'stock_code': '7203', 'current_price': 0},       # ゼロ
                {'stock_code': '7203', 'current_price': -100},    # マイナス
                {'stock_code': '7203', 'current_price': 'invalid'}, # 文字列
                
                # リスク許容度異常
                {'stock_code': '7203', 'current_price': 1000.0, 'risk_tolerance': 'invalid'},
                
                # 投資期間異常
                {'stock_code': '7203', 'current_price': 1000.0, 'timeframe': 'invalid'}
            ]
            
            invalid_count = 0
            for invalid_data in invalid_cases:
                try:
                    EntryOptimizationValidator.validate_request(invalid_data)
                    # バリデーションエラーが発生しなかった場合は問題
                    raise AssertionError(f"バリデーションエラーが期待されたが成功した: {invalid_data}")
                except ValueError:
                    # 期待通りバリデーションエラーが発生
                    invalid_count += 1
                except Exception as e:
                    # 想定外のエラー
                    raise AssertionError(f"想定外のエラー: {e}, データ: {invalid_data}")
            
            assert invalid_count == len(invalid_cases)
            tracker.mark(f"異常ケース検証成功 ({invalid_count}件)")
            
            # 境界値テスト
            boundary_cases = [
                # 最小価格
                {'stock_code': '7203', 'current_price': 1.0},
                # 最大価格
                {'stock_code': '7203', 'current_price': 999999.0},
                # 最小投資金額  
                {'stock_code': '7203', 'current_price': 100.0, 'investment_amount': 1000.0},
                # 最大投資金額
                {'stock_code': '7203', 'current_price': 100.0, 'investment_amount': 100000000.0}
            ]
            
            for boundary_data in boundary_cases:
                result = EntryOptimizationValidator.validate_request(boundary_data)
                assert result is not None
            
            tracker.mark("境界値テスト成功")
            
            tracker.summary()
            print("✅ エントリーポイント最適化バリデーター包括テスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ エントリーポイント最適化バリデーターテストエラー: {e}")
            raise

    async def test_ifdoco_guide_validator_comprehensive(self):
        """IFDOCO注文ガイドバリデーター包括テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("IFDOCO注文ガイドバリデーター包括テスト")
        
        try:
            # 正常ケーステスト
            valid_data = {
                'stock_code': '8306',
                'entry_price': 800.0,
                'investment_amount': 160000.0,
                'logic_type': 'logic_b',
                'risk_level': 'conservative',
                'holding_period': '3m'
            }
            
            result = IfdocoGuideValidator.validate_request(valid_data)
            assert result['stock_code'] == '8306'
            assert result['entry_price'] == Decimal('800.0')
            assert result['investment_amount'] == Decimal('160000.0')
            assert result['risk_level'] == 'conservative'
            assert result['holding_period'] == '3m'
            tracker.mark("正常ケース検証成功")
            
            # リスクレベル全パターンテスト
            risk_levels = ['conservative', 'medium', 'aggressive']
            for risk_level in risk_levels:
                test_data = {
                    'stock_code': '9984',
                    'entry_price': 6000.0,
                    'investment_amount': 300000.0,
                    'risk_level': risk_level
                }
                result = IfdocoGuideValidator.validate_request(test_data)
                assert result['risk_level'] == risk_level
            
            tracker.mark("リスクレベル全パターン検証成功")
            
            # 保有期間全パターンテスト
            holding_periods = ['1w', '1m', '3m', '6m']
            for period in holding_periods:
                test_data = {
                    'stock_code': '7203',
                    'entry_price': 1000.0,
                    'investment_amount': 100000.0,
                    'holding_period': period
                }
                result = IfdocoGuideValidator.validate_request(test_data)
                assert result['holding_period'] == period
            
            tracker.mark("保有期間全パターン検証成功")
            
            # 異常ケーステスト
            invalid_cases = [
                # 必須フィールド不足
                {'entry_price': 1000.0, 'investment_amount': 100000.0},  # stock_code不足
                {'stock_code': '7203', 'investment_amount': 100000.0},   # entry_price不足
                {'stock_code': '7203', 'entry_price': 1000.0},           # investment_amount不足
                
                # 無効なリスクレベル
                {'stock_code': '7203', 'entry_price': 1000.0, 'investment_amount': 100000.0, 'risk_level': 'invalid'},
                
                # 無効な保有期間
                {'stock_code': '7203', 'entry_price': 1000.0, 'investment_amount': 100000.0, 'holding_period': 'invalid'}
            ]
            
            invalid_count = 0
            for invalid_data in invalid_cases:
                try:
                    IfdocoGuideValidator.validate_request(invalid_data)
                    raise AssertionError(f"バリデーションエラーが期待されたが成功した: {invalid_data}")
                except ValueError:
                    invalid_count += 1
                except Exception as e:
                    raise AssertionError(f"想定外のエラー: {e}, データ: {invalid_data}")
            
            assert invalid_count == len(invalid_cases)
            tracker.mark(f"異常ケース検証成功 ({invalid_count}件)")
            
            tracker.summary()
            print("✅ IFDOCO注文ガイドバリデーター包括テスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ IFDOCO注文ガイドバリデーターテストエラー: {e}")
            raise

    async def test_trading_history_validator_comprehensive(self):
        """売買履歴バリデーター包括テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("売買履歴バリデーター包括テスト")
        
        try:
            # 正常ケーステスト（フルフィルタ）
            valid_data = {
                'stock_code': '7203',
                'logic_type': 'logic_a',
                'trade_type': 'BUY',
                'status': 'closed',
                'date_from': '2024-01-01T00:00:00',
                'date_to': '2024-12-31T23:59:59',
                'min_profit_loss': -10000.0,
                'max_profit_loss': 50000.0,
                'page': 1,
                'limit': 20
            }
            
            result = TradingHistoryValidator.validate_filter(valid_data)
            assert result['stock_code'] == '7203'
            assert result['logic_type'] == 'logic_a'
            assert result['trade_type'] == 'BUY'
            assert result['status'] == 'closed'
            assert result['page'] == 1
            assert result['limit'] == 20
            tracker.mark("フルフィルタ検証成功")
            
            # 最小フィルタ（ページネーションのみ）
            minimal_data = {'page': 2, 'limit': 10}
            result_minimal = TradingHistoryValidator.validate_filter(minimal_data)
            assert result_minimal['page'] == 2
            assert result_minimal['limit'] == 10
            tracker.mark("最小フィルタ検証成功")
            
            # 取引種別全パターンテスト
            trade_types = ['BUY', 'SELL']
            for trade_type in trade_types:
                test_data = {'trade_type': trade_type, 'page': 1, 'limit': 10}
                result = TradingHistoryValidator.validate_filter(test_data)
                assert result['trade_type'] == trade_type
            
            tracker.mark("取引種別全パターン検証成功")
            
            # ステータス全パターンテスト
            statuses = ['open', 'closed', 'cancelled']
            for status in statuses:
                test_data = {'status': status, 'page': 1, 'limit': 10}
                result = TradingHistoryValidator.validate_filter(test_data)
                assert result['status'] == status
            
            tracker.mark("ステータス全パターン検証成功")
            
            # ページネーション境界値テスト
            pagination_cases = [
                {'page': 1, 'limit': 1},      # 最小値
                {'page': 1, 'limit': 100},    # 最大値
                {'page': 999, 'limit': 50}    # 大きなページ番号
            ]
            
            for pagination_data in pagination_cases:
                result = TradingHistoryValidator.validate_filter(pagination_data)
                assert result['page'] == pagination_data['page']
                assert result['limit'] == pagination_data['limit']
            
            tracker.mark("ページネーション境界値検証成功")
            
            # 異常ケーステスト
            invalid_cases = [
                # 無効な取引種別
                {'trade_type': 'INVALID', 'page': 1, 'limit': 10},
                
                # 無効なステータス  
                {'status': 'invalid', 'page': 1, 'limit': 10},
                
                # 無効なページネーション
                {'page': 0, 'limit': 10},      # ページ番号ゼロ
                {'page': 1, 'limit': 0},       # 件数ゼロ
                {'page': 1, 'limit': 101},     # 件数上限超過
                
                # 無効な日付形式
                {'date_from': 'invalid-date', 'page': 1, 'limit': 10},
                
                # 日付範囲逆転
                {'date_from': '2024-12-31', 'date_to': '2024-01-01', 'page': 1, 'limit': 10}
            ]
            
            invalid_count = 0
            for invalid_data in invalid_cases:
                try:
                    TradingHistoryValidator.validate_filter(invalid_data)
                    raise AssertionError(f"バリデーションエラーが期待されたが成功した: {invalid_data}")
                except ValueError:
                    invalid_count += 1
                except Exception as e:
                    raise AssertionError(f"想定外のエラー: {e}, データ: {invalid_data}")
            
            assert invalid_count == len(invalid_cases)
            tracker.mark(f"異常ケース検証成功 ({invalid_count}件)")
            
            tracker.summary()
            print("✅ 売買履歴バリデーター包括テスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ 売買履歴バリデーターテストエラー: {e}")
            raise

    async def test_signal_history_validator_comprehensive(self):
        """シグナル履歴バリデーター包括テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("シグナル履歴バリデーター包括テスト")
        
        try:
            # 正常ケーステスト
            valid_data = {
                'stock_code': '9984',
                'signal_type': 'BUY',
                'status': 'executed',
                'confidence_min': 0.8,
                'date_from': '2024-01-01T00:00:00',
                'date_to': '2024-12-31T23:59:59',
                'page': 1,
                'limit': 15
            }
            
            result = SignalHistoryValidator.validate_filter(valid_data)
            assert result['stock_code'] == '9984'
            assert result['signal_type'] == 'BUY'
            assert result['status'] == 'executed'
            assert result['confidence_min'] == Decimal('0.8')
            assert result['page'] == 1
            assert result['limit'] == 15
            tracker.mark("正常ケース検証成功")
            
            # 信頼度境界値テスト
            confidence_cases = [
                {'confidence_min': 0.0, 'page': 1, 'limit': 10},    # 最小値
                {'confidence_min': 1.0, 'page': 1, 'limit': 10},    # 最大値
                {'confidence_min': 0.5, 'page': 1, 'limit': 10},    # 中間値
                {'confidence_min': 0.99, 'page': 1, 'limit': 10}    # 高信頼度
            ]
            
            for confidence_data in confidence_cases:
                result = SignalHistoryValidator.validate_filter(confidence_data)
                assert result['confidence_min'] == Decimal(str(confidence_data['confidence_min']))
            
            tracker.mark("信頼度境界値検証成功")
            
            # オプションフィールドなしテスト
            minimal_data = {'page': 1, 'limit': 20}
            result_minimal = SignalHistoryValidator.validate_filter(minimal_data)
            assert 'stock_code' not in result_minimal or result_minimal['stock_code'] is None
            assert 'signal_type' not in result_minimal or result_minimal['signal_type'] is None
            assert result_minimal['page'] == 1
            assert result_minimal['limit'] == 20
            tracker.mark("オプションフィールドなし検証成功")
            
            # 異常ケーステスト
            invalid_cases = [
                # 無効な信頼度
                {'confidence_min': -0.1, 'page': 1, 'limit': 10},   # 負の値
                {'confidence_min': 1.1, 'page': 1, 'limit': 10},    # 1を超える値
                {'confidence_min': 'invalid', 'page': 1, 'limit': 10}, # 文字列
                
                # 無効なページネーション（TradingHistoryValidatorと同様）
                {'page': 0, 'limit': 10},
                {'page': 1, 'limit': 0},
                {'page': 1, 'limit': 101}
            ]
            
            invalid_count = 0
            for invalid_data in invalid_cases:
                try:
                    SignalHistoryValidator.validate_filter(invalid_data)
                    raise AssertionError(f"バリデーションエラーが期待されたが成功した: {invalid_data}")
                except ValueError:
                    invalid_count += 1
                except Exception as e:
                    raise AssertionError(f"想定外のエラー: {e}, データ: {invalid_data}")
            
            assert invalid_count == len(invalid_cases)
            tracker.mark(f"異常ケース検証成功 ({invalid_count}件)")
            
            tracker.summary()
            print("✅ シグナル履歴バリデーター包括テスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ シグナル履歴バリデーターテストエラー: {e}")
            raise

    async def test_individual_validator_functions(self):
        """個別バリデーター関数包括テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("個別バリデーター関数包括テスト")
        
        try:
            # validate_stock_code テスト
            valid_codes = ['7203', '8306', '9984', '1111']
            for code in valid_codes:
                result = validate_stock_code(code)
                assert result == code
            
            invalid_codes = ['123', '12345', 'ABCD', '', None, '720A']
            for code in invalid_codes:
                try:
                    validate_stock_code(code)
                    raise AssertionError(f"無効な銘柄コードでエラーが発生しませんでした: {code}")
                except ValueError:
                    pass  # 期待通り
            
            tracker.mark("validate_stock_code テスト成功")
            
            # validate_price テスト
            valid_prices = [1.0, 100, 1000.5, Decimal('999999')]
            for price in valid_prices:
                result = validate_price(price)
                assert isinstance(result, Decimal)
                assert result > 0
            
            invalid_prices = [0, -100, 'invalid', None]
            for price in invalid_prices:
                try:
                    validate_price(price)
                    raise AssertionError(f"無効な価格でエラーが発生しませんでした: {price}")
                except ValueError:
                    pass  # 期待通り
            
            tracker.mark("validate_price テスト成功")
            
            # validate_investment_amount テスト
            valid_amounts = [1000, 50000, 1000000, Decimal('100000000')]
            for amount in valid_amounts:
                result = validate_investment_amount(amount)
                assert isinstance(result, Decimal)
                assert result >= 1000
            
            invalid_amounts = [999, 100000001, 0, -1000, 'invalid']
            for amount in invalid_amounts:
                try:
                    validate_investment_amount(amount)
                    raise AssertionError(f"無効な投資金額でエラーが発生しませんでした: {amount}")
                except ValueError:
                    pass  # 期待通り
            
            tracker.mark("validate_investment_amount テスト成功")
            
            # validate_risk_tolerance テスト
            valid_tolerances = ['low', 'medium', 'high']
            for tolerance in valid_tolerances:
                result = validate_risk_tolerance(tolerance)
                assert result == tolerance
            
            invalid_tolerances = ['invalid', '', None, 'LOW', 'MEDIUM']
            for tolerance in invalid_tolerances:
                try:
                    validate_risk_tolerance(tolerance)
                    raise AssertionError(f"無効なリスク許容度でエラーが発生しませんでした: {tolerance}")
                except ValueError:
                    pass  # 期待通り
            
            tracker.mark("validate_risk_tolerance テスト成功")
            
            # validate_timeframe テスト
            valid_timeframes = ['1w', '1m', '3m', '6m', '1y']
            for timeframe in valid_timeframes:
                result = validate_timeframe(timeframe)
                assert result == timeframe
            
            invalid_timeframes = ['invalid', '2m', '1d', '', None]
            for timeframe in invalid_timeframes:
                try:
                    validate_timeframe(timeframe)
                    raise AssertionError(f"無効な投資期間でエラーが発生しませんでした: {timeframe}")
                except ValueError:
                    pass  # 期待通り
            
            tracker.mark("validate_timeframe テスト成功")
            
            # validate_pagination テスト
            valid_paginations = [(1, 1), (1, 20), (100, 100), (999, 50)]
            for page, limit in valid_paginations:
                result_page, result_limit = validate_pagination(page, limit)
                assert result_page == page
                assert result_limit == limit
            
            invalid_paginations = [(0, 10), (1, 0), (1, 101), (-1, 20)]
            for page, limit in invalid_paginations:
                try:
                    validate_pagination(page, limit)
                    raise AssertionError(f"無効なページネーションでエラーが発生しませんでした: page={page}, limit={limit}")
                except ValueError:
                    pass  # 期待通り
            
            tracker.mark("validate_pagination テスト成功")
            
            # validate_date_range テスト
            from datetime import datetime, timedelta
            
            now = datetime.now()
            past = now - timedelta(days=30)
            future = now + timedelta(days=30)
            
            valid_ranges = [
                (past, now),      # 過去→現在
                (past, future),   # 過去→未来
                (None, now),      # None→現在
                (past, None),     # 過去→None
                (None, None)      # None→None
            ]
            
            for date_from, date_to in valid_ranges:
                result_from, result_to = validate_date_range(date_from, date_to)
                # エラーが発生しなければOK
            
            # 無効な日付範囲（終了日が開始日より前）
            try:
                validate_date_range(future, past)
                raise AssertionError("無効な日付範囲でエラーが発生しませんでした")
            except ValueError:
                pass  # 期待通り
            
            tracker.mark("validate_date_range テスト成功")
            
            tracker.summary()
            print("✅ 個別バリデーター関数包括テスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ 個別バリデーター関数テストエラー: {e}")
            raise


# @9統合テスト成功請負人が実行するバリデーター統合テスト関数
async def test_trading_validators_integration():
    """
    @9統合テスト成功請負人が実行する売買支援APIバリデーター統合テスト
    
    このテストは以下のバリデーターを完全に検証します:
    1. EntryOptimizationValidator
    2. IfdocoGuideValidator
    3. TradingHistoryValidator
    4. SignalHistoryValidator
    5. 個別バリデーター関数群
    
    正常ケース、異常ケース、境界値ケースを網羅的にテストします。
    """
    print("🔍 売買支援APIバリデーター統合テスト開始")
    print("=" * 60)
    
    validator_test = TradingValidatorsIntegrationTest()
    
    try:
        # 各バリデーター包括テスト
        await validator_test.test_entry_optimization_validator_comprehensive()
        print()
        
        await validator_test.test_ifdoco_guide_validator_comprehensive()
        print()
        
        await validator_test.test_trading_history_validator_comprehensive()
        print()
        
        await validator_test.test_signal_history_validator_comprehensive()
        print()
        
        await validator_test.test_individual_validator_functions()
        print()
        
        print("=" * 60)
        print("🎉 売買支援APIバリデーター統合テスト全件成功！")
        print("✅ エントリーポイント最適化バリデーター: PASS")
        print("✅ IFDOCO注文ガイドバリデーター: PASS")
        print("✅ 売買履歴バリデーター: PASS")
        print("✅ シグナル履歴バリデーター: PASS")
        print("✅ 個別バリデーター関数群: PASS")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ バリデーター統合テストエラー: {e}")
        raise


if __name__ == "__main__":
    """
    @9統合テスト成功請負人用のバリデーターテスト実行エントリーポイント
    
    実行方法:
    cd backend
    python -m pytest tests/integration/trading/trading_validators_test.py::test_trading_validators_integration -v
    
    または:
    python tests/integration/trading/trading_validators_test.py
    """
    asyncio.run(test_trading_validators_integration())