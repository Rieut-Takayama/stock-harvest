"""
テストデータ提供サービス
外部API依存を軽減し、決定的なテスト結果を提供するための固定データ管理
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

class TestDataProvider:
    """
    テスト用の固定データを提供するサービス
    外部API不可時の安全なフォールバック機能と決定的なテスト結果を保証
    """
    
    def __init__(self):
        self.is_test_mode = os.getenv('TESTING_MODE', 'false').lower() == 'true'
        self.fallback_enabled = True
        self._cache = {}
        
    def get_fixed_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """
        決定的な株価データを提供
        テスト環境で予測可能な結果を保証
        """
        
        # 固定の株価データ（実際の企業データに基づく）
        fixed_data = {
            '7203': {  # トヨタ自動車
                'code': '7203',
                'name': 'トヨタ自動車',
                'price': 2850.0,
                'change': 45.0,
                'changeRate': 1.6,
                'volume': 15234000,
                'marketCap': 37500000000000,
                'sector': 'Consumer Cyclical',
                'industry': 'Auto Manufacturers',
                'ohlc_data': self._generate_deterministic_ohlc('7203', 2850.0, 30)
            },
            '6758': {  # ソニーグループ
                'code': '6758',
                'name': 'ソニーグループ',
                'price': 13150.0,
                'change': -120.0,
                'changeRate': -0.9,
                'volume': 8456000,
                'marketCap': 16200000000000,
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'ohlc_data': self._generate_deterministic_ohlc('6758', 13150.0, 30)
            },
            '9984': {  # ソフトバンクグループ
                'code': '9984',
                'name': 'ソフトバンクグループ',
                'price': 5280.0,
                'change': 85.0,
                'changeRate': 1.6,
                'volume': 12890000,
                'marketCap': 11500000000000,
                'sector': 'Technology',
                'industry': 'Telecom Services',
                'ohlc_data': self._generate_deterministic_ohlc('9984', 5280.0, 30)
            },
            '4689': {  # Zホールディングス
                'code': '4689',
                'name': 'Zホールディングス',
                'price': 425.0,
                'change': 12.0,
                'changeRate': 2.9,
                'volume': 19567000,
                'marketCap': 3100000000000,
                'sector': 'Technology',
                'industry': 'Internet Content & Information',
                'ohlc_data': self._generate_deterministic_ohlc('4689', 425.0, 30)
            },
            '8306': {  # 三菱UFJ
                'code': '8306',
                'name': '三菱UFJフィナンシャル・グループ',
                'price': 1195.0,
                'change': -8.0,
                'changeRate': -0.7,
                'volume': 25478000,
                'marketCap': 15800000000000,
                'sector': 'Financial Services',
                'industry': 'Banks - Regional',
                'ohlc_data': self._generate_deterministic_ohlc('8306', 1195.0, 30)
            },
            '6861': {  # キーエンス
                'code': '6861',
                'name': 'キーエンス',
                'price': 47200.0,
                'change': 650.0,
                'changeRate': 1.4,
                'volume': 445000,
                'marketCap': 9200000000000,
                'sector': 'Technology',
                'industry': 'Scientific & Technical Instruments',
                'ohlc_data': self._generate_deterministic_ohlc('6861', 47200.0, 30)
            },
            '9433': {  # KDDI
                'code': '9433',
                'name': 'KDDI',
                'price': 3845.0,
                'change': 25.0,
                'changeRate': 0.7,
                'volume': 3567000,
                'marketCap': 8900000000000,
                'sector': 'Communication Services',
                'industry': 'Telecom Services',
                'ohlc_data': self._generate_deterministic_ohlc('9433', 3845.0, 30)
            },
            '4063': {  # 信越化学工業
                'code': '4063',
                'name': '信越化学工業',
                'price': 24750.0,
                'change': 180.0,
                'changeRate': 0.7,
                'volume': 876000,
                'marketCap': 10100000000000,
                'sector': 'Basic Materials',
                'industry': 'Chemicals',
                'ohlc_data': self._generate_deterministic_ohlc('4063', 24750.0, 30)
            },
            '6954': {  # ファナック
                'code': '6954',
                'name': 'ファナック',
                'price': 54800.0,
                'change': -450.0,
                'changeRate': -0.8,
                'volume': 234000,
                'marketCap': 10500000000000,
                'sector': 'Industrials',
                'industry': 'Specialty Industrial Machinery',
                'ohlc_data': self._generate_deterministic_ohlc('6954', 54800.0, 30)
            },
            '8058': {  # 三菱商事
                'code': '8058',
                'name': '三菱商事',
                'price': 4525.0,
                'change': 75.0,
                'changeRate': 1.7,
                'volume': 7890000,
                'marketCap': 6700000000000,
                'sector': 'Industrials',
                'industry': 'Conglomerates',
                'ohlc_data': self._generate_deterministic_ohlc('8058', 4525.0, 30)
            }
        }
        
        # 指定された銘柄の固定データを返す
        if stock_code in fixed_data:
            data = fixed_data[stock_code].copy()
            data['signals'] = self.get_deterministic_technical_signals(stock_code)
            return data
        
        # 未知の銘柄の場合はNoneを返す（存在しない銘柄として扱う）
        logger.info(f"📊 未知の銘柄コード: {stock_code} - 存在しない銘柄として扱います")
        return None
    
    def get_deterministic_technical_signals(self, stock_code: str) -> Dict[str, Any]:
        """
        決定的なテクニカル指標を提供
        銘柄コードベースで一意の値を生成し、テスト結果の予測可能性を保証
        """
        
        # 銘柄コードから決定的な値を生成
        code_hash = hash(stock_code) % 10000
        
        # 固定シード値を使用して決定的な指標値を生成
        signals = {
            'rsi': 30.0 + (code_hash % 40),  # 30-70の範囲
            'macd': -1.0 + (code_hash % 200) / 100,  # -1.0 to 1.0
            'bollingerPosition': -1.0 + (code_hash % 200) / 100,  # -1.0 to 1.0
            'volumeRatio': 0.5 + (code_hash % 150) / 100,  # 0.5 to 2.0
            'trendDirection': ['up', 'down', 'sideways'][code_hash % 3],
            'sma20': None,  # チャート用データで計算
            'sma50': None   # チャート用データで計算
        }
        
        return signals
    
    def _generate_deterministic_ohlc(self, stock_code: str, current_price: float, days: int) -> List[Dict[str, Any]]:
        """
        決定的なOHLCデータを生成
        銘柄コードとパラメータから一意のデータを生成
        """
        code_hash = hash(stock_code)
        ohlc_data = []
        
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # 決定的な価格変動を生成
            day_hash = hash(f"{stock_code}_{i}") % 1000
            price_variation = (day_hash % 10) - 5  # -5% to +5%
            
            # その日の価格を計算
            day_price = current_price * (1 + price_variation / 100)
            
            # OHLC値を計算（決定的に、株価の整合性を保持）
            intraday_variation = (day_hash % 6) / 100  # 0-6%の日中変動
            
            # 始値と終値を先に決める
            open_price = day_price + (day_hash % 20 - 10) * (current_price * 0.01)
            close_price = day_price
            
            # 高値は始値・終値の最大値以上
            max_oc = max(open_price, close_price)
            high = max_oc * (1 + intraday_variation)
            
            # 安値は始値・終値の最小値以下
            min_oc = min(open_price, close_price)
            low = min_oc * (1 - intraday_variation)
            
            # 出来高も決定的に生成
            volume = 1000000 + (day_hash % 50) * 100000
            
            ohlc_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "timestamp": int(date.timestamp() * 1000),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
        
        return ohlc_data
    
    def _generate_deterministic_default_data(self, stock_code: str) -> Dict[str, Any]:
        """
        未知の銘柄用の決定的なデフォルトデータ
        """
        code_hash = hash(stock_code) % 10000
        
        base_price = 1000 + (code_hash % 5000)  # 1000-6000の範囲
        change = -50 + (code_hash % 100)  # -50 to +50
        
        return {
            'code': stock_code,
            'name': f'テスト銘柄{stock_code}',
            'price': float(base_price),
            'change': float(change),
            'changeRate': round((change / base_price) * 100, 2),
            'volume': 1000000 + (code_hash % 10000000),
            'marketCap': base_price * 1000000,
            'sector': 'Unknown',
            'industry': 'Unknown',
            'signals': self.get_deterministic_technical_signals(stock_code),
            'ohlc_data': self._generate_deterministic_ohlc(stock_code, float(base_price), 30)
        }
    
    def get_logic_detection_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        ロジック検出テスト用の決定的データセット
        テストの予測可能性を保証
        """
        return {
            'logic_a_candidates': [
                # ストップ高張り付き候補（変動率5%以上、大出来高）
                {
                    'code': '9999', 'name': 'テスト株A',
                    'price': 1500.0, 'change': 75.0, 'changeRate': 5.3,
                    'volume': 15000000, 'signals': {'rsi': 70, 'trendDirection': 'up'}
                },
                {
                    'code': '9998', 'name': 'テスト株B',
                    'price': 800.0, 'change': 48.0, 'changeRate': 6.4,
                    'volume': 12000000, 'signals': {'rsi': 75, 'trendDirection': 'up'}
                }
            ],
            'logic_b_candidates': [
                # 底値反転候補（RSI 60以上、変動率2%以上）
                {
                    'code': '9997', 'name': 'テスト株C',
                    'price': 2200.0, 'change': 55.0, 'changeRate': 2.6,
                    'volume': 8000000, 'signals': {'rsi': 65, 'trendDirection': 'up'}
                },
                {
                    'code': '9996', 'name': 'テスト株D',
                    'price': 3400.0, 'change': 105.0, 'changeRate': 3.2,
                    'volume': 6500000, 'signals': {'rsi': 62, 'trendDirection': 'up'}
                }
            ]
        }
    
    def is_api_available_simulation(self, failure_rate: float = 0.0) -> bool:
        """
        API可用性のシミュレーション
        テスト環境での外部API障害をシミュレート
        """
        if self.is_test_mode:
            # テストモードでは決定的な可用性を返す
            return failure_rate == 0.0
        
        import random
        return random.random() > failure_rate
    
    def create_mock_api_response(self, symbol: str, period: str) -> pd.DataFrame:
        """
        yfinance APIの応答を模擬するDataFrameを作成
        実際のAPIレスポンス構造と互換性を保持
        """
        stock_code = symbol.replace('.T', '')
        fixed_data = self.get_fixed_stock_data(stock_code)
        
        if fixed_data is None:
            # 存在しない銘柄の場合は空のDataFrameを返す
            return pd.DataFrame()
        
        # pandas DataFrameとして返す（yfinance互換）
        ohlc_data = fixed_data['ohlc_data']
        
        df_data = {
            'Open': [item['open'] for item in ohlc_data],
            'High': [item['high'] for item in ohlc_data],
            'Low': [item['low'] for item in ohlc_data],
            'Close': [item['close'] for item in ohlc_data],
            'Volume': [item['volume'] for item in ohlc_data]
        }
        
        # 日付インデックスを作成
        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in ohlc_data]
        
        df = pd.DataFrame(df_data, index=dates)
        return df
    
    def get_test_environment_info(self) -> Dict[str, Any]:
        """
        テスト環境の情報を返す
        """
        return {
            'is_test_mode': self.is_test_mode,
            'fallback_enabled': self.fallback_enabled,
            'deterministic_data': True,
            'external_api_dependency': False,
            'cache_size': len(self._cache),
            'supported_stocks': ['7203', '6758', '9984', '4689', '8306', '6861', '9433', '4063', '6954', '8058']
        }


# シングルトンインスタンス
test_data_provider = TestDataProvider()