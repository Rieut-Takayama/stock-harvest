"""
決定的テストヘルパー
テスト結果の予測可能性を保証し、外部API依存を軽減
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import patch, AsyncMock, MagicMock
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DeterministicTestHelper:
    """
    決定的なテスト結果を提供するヘルパークラス
    外部API依存を軽減し、テスト結果の予測可能性を保証
    """
    
    def __init__(self):
        self.test_mode_enabled = False
        self.mock_patches = []
        
    def enable_test_mode(self):
        """テストモードを有効化"""
        os.environ['TESTING_MODE'] = 'true'
        self.test_mode_enabled = True
        logger.info("🧪 決定的テストモードを有効化")
    
    def disable_test_mode(self):
        """テストモードを無効化"""
        os.environ.pop('TESTING_MODE', None)
        self.test_mode_enabled = False
        logger.info("🔧 テストモードを無効化")
    
    def create_yfinance_mock_patch(self, deterministic_data: Dict[str, Any]):
        """
        yfinanceをモックしてAPIエラーを防ぐパッチを作成
        注意: 実データでの動作保証を維持するため、テストでのみ使用
        """
        def mock_ticker_class(symbol):
            mock_ticker = MagicMock()
            
            # 決定的なhistoryメソッドを作成
            def history(period="1d", interval="1d"):
                if symbol in deterministic_data:
                    data = deterministic_data[symbol]
                    
                    # pandas DataFrameとして返す
                    df_data = {
                        'Open': [data['open']],
                        'High': [data['high']],
                        'Low': [data['low']], 
                        'Close': [data['close']],
                        'Volume': [data['volume']]
                    }
                    
                    from datetime import datetime
                    import pandas as pd
                    df = pd.DataFrame(df_data, index=[datetime.now()])
                    return df
                else:
                    # 空のDataFrameを返す（エラーケース）
                    return pd.DataFrame()
            
            mock_ticker.history = history
            mock_ticker.info = {
                'longName': deterministic_data.get(symbol, {}).get('name', 'Test Stock'),
                'sector': 'Test Sector',
                'industry': 'Test Industry',
                'marketCap': 1000000000
            }
            
            return mock_ticker
        
        return patch('yfinance.Ticker', side_effect=mock_ticker_class)
    
    def get_deterministic_test_data_set(self) -> Dict[str, Dict[str, Any]]:
        """
        決定的なテストデータセットを提供
        全テストで一貫した結果を保証
        """
        return {
            '7203.T': {  # トヨタ自動車
                'name': 'トヨタ自動車',
                'open': 2800.0,
                'high': 2900.0,
                'low': 2780.0,
                'close': 2850.0,
                'volume': 15234000,
                'change': 45.0,
                'changeRate': 1.6
            },
            '6758.T': {  # ソニーグループ
                'name': 'ソニーグループ', 
                'open': 13200.0,
                'high': 13280.0,
                'low': 13100.0,
                'close': 13150.0,
                'volume': 8456000,
                'change': -120.0,
                'changeRate': -0.9
            },
            '9984.T': {  # ソフトバンクグループ
                'name': 'ソフトバンクグループ',
                'open': 5200.0,
                'high': 5320.0,
                'low': 5180.0,
                'close': 5280.0,
                'volume': 12890000,
                'change': 85.0,
                'changeRate': 1.6
            },
            '4689.T': {  # Zホールディングス
                'name': 'Zホールディングス',
                'open': 415.0,
                'high': 430.0,
                'low': 410.0,
                'close': 425.0,
                'volume': 19567000,
                'change': 12.0,
                'changeRate': 2.9
            },
            'test_unknown.T': {  # 未知の銘柄テスト用
                'name': 'テスト銘柄',
                'open': 1000.0,
                'high': 1050.0,
                'low': 980.0,
                'close': 1025.0,
                'volume': 5000000,
                'change': 25.0,
                'changeRate': 2.5
            }
        }
    
    def create_api_failure_simulation_patch(self, failure_rate: float = 1.0):
        """
        外部API障害をシミュレートするパッチ
        テスト環境での外部API依存を軽減
        """
        def mock_ticker_with_failure(symbol):
            mock_ticker = MagicMock()
            
            def history_with_failure(*args, **kwargs):
                import random
                if random.random() < failure_rate:
                    # API失敗をシミュレート
                    raise Exception("Simulated API failure")
                else:
                    # 成功時は空のDataFrameを返す
                    return pd.DataFrame()
            
            mock_ticker.history = history_with_failure
            return mock_ticker
        
        return patch('yfinance.Ticker', side_effect=mock_ticker_with_failure)
    
    def verify_fallback_behavior(self, service_method, expected_fallback_data):
        """
        フォールバック動作の検証
        外部API失敗時に適切にフォールバックデータが使用されることを確認
        """
        # API失敗をシミュレート
        with self.create_api_failure_simulation_patch(failure_rate=1.0):
            result = asyncio.run(service_method())
            
            # フォールバックデータが使用されていることを確認
            for key, expected_value in expected_fallback_data.items():
                assert key in result, f"Expected key '{key}' not found in result"
                if isinstance(expected_value, (int, float)):
                    assert abs(result[key] - expected_value) < 0.01, \
                        f"Expected {key}={expected_value}, got {result[key]}"
                else:
                    assert result[key] == expected_value, \
                        f"Expected {key}='{expected_value}', got '{result[key]}'"
    
    def create_network_timeout_simulation(self):
        """
        ネットワークタイムアウトをシミュレート
        """
        def timeout_simulation(*args, **kwargs):
            import time
            time.sleep(10)  # タイムアウトをシミュレート
            raise TimeoutError("Network timeout simulation")
        
        return patch('yfinance.Ticker', side_effect=timeout_simulation)
    
    def assert_deterministic_results(self, actual_results: List[Dict], expected_patterns: Dict):
        """
        決定的な結果パターンをアサート
        テスト結果が予測可能であることを確認
        """
        for result in actual_results:
            stock_code = result.get('code', '')
            
            if stock_code in expected_patterns:
                expected = expected_patterns[stock_code]
                
                # 価格データの確認
                assert 'price' in result, "Price should be present"
                assert isinstance(result['price'], (int, float)), "Price should be numeric"
                
                # 変動率の確認
                assert 'changeRate' in result, "Change rate should be present"
                assert isinstance(result['changeRate'], (int, float)), "Change rate should be numeric"
                
                # 決定的な値の確認（許容誤差あり）
                if 'expected_price_range' in expected:
                    min_price, max_price = expected['expected_price_range']
                    assert min_price <= result['price'] <= max_price, \
                        f"Price {result['price']} not in expected range [{min_price}, {max_price}]"
    
    def cleanup(self):
        """テストヘルパーのクリーンアップ"""
        # 全モックパッチを停止
        for patch_obj in self.mock_patches:
            try:
                patch_obj.stop()
            except:
                pass
        self.mock_patches.clear()
        
        # テストモードを無効化
        self.disable_test_mode()
        
        logger.info("🧹 決定的テストヘルパーをクリーンアップ")


# シングルトンインスタンス
deterministic_test_helper = DeterministicTestHelper()