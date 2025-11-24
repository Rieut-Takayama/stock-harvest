"""
株価データ取得サービス
Yahoo Finance APIを使用した株価データの取得・管理

機能:
- リアルタイム株価データ取得
- 履歴データ取得（日足、時間足、分足）
- マルチタイムフレームデータ管理
- データキャッシング
- エラーハンドリング
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class StockDataService:
    """株価データ取得専門サービス"""
    
    def __init__(self):
        # データ取得設定
        self.config = {
            # タイムアウト設定
            'request_timeout': 30,
            'retry_count': 3,
            'retry_delay': 1,
            
            # キャッシュ設定
            'cache_duration': {
                '1m': timedelta(minutes=1),
                '5m': timedelta(minutes=5),
                '15m': timedelta(minutes=15),
                '1h': timedelta(hours=1),
                '1d': timedelta(hours=6),
                'info': timedelta(hours=24),
            },
            
            # データ期間設定
            'max_periods': {
                '1m': '1d',      # 1分足は1日分
                '5m': '5d',      # 5分足は5日分
                '15m': '1mo',    # 15分足は1ヶ月分
                '1h': '3mo',     # 1時間足は3ヶ月分
                '1d': '2y',      # 日足は2年分
            },
            
            # レート制限設定
            'rate_limit_delay': 0.1,  # API呼び出し間隔（秒）
            'max_concurrent': 5,      # 最大同時実行数
        }
        
        # キャッシュ管理
        self.price_cache = {}
        self.cache_timestamps = {}
        self.info_cache = {}
        
        # レート制限管理
        self.last_request_time = {}
        self.request_semaphore = asyncio.Semaphore(self.config['max_concurrent'])
        
        # スレッドプール（同期処理用）
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def get_current_price(self, stock_code: str) -> Dict:
        """
        現在の株価データ取得（リアルタイム）
        """
        try:
            # キャッシュチェック（1分間有効）
            cache_key = f"{stock_code}_current"
            if await self._is_cache_valid(cache_key, '1m'):
                logger.debug(f"キャッシュから現在価格取得: {stock_code}")
                return self.price_cache[cache_key]
            
            # Yahoo Financeから取得
            data = await self._fetch_current_data(stock_code)
            if data:
                # キャッシュに保存
                await self._save_to_cache(cache_key, data, '1m')
                return data
            else:
                return self._create_error_response('データ取得失敗')
                
        except Exception as e:
            logger.error(f"現在価格取得エラー {stock_code}: {str(e)}")
            return self._create_error_response(f'取得エラー: {str(e)}')
    
    async def get_historical_data(
        self, 
        stock_code: str, 
        period: str = '1mo', 
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        履歴データ取得
        """
        try:
            # キャッシュキー生成
            cache_key = f"{stock_code}_{period}_{interval}"
            
            # キャッシュチェック
            cache_duration = self.config['cache_duration'].get(interval, timedelta(hours=1))
            if await self._is_cache_valid(cache_key, cache_duration):
                logger.debug(f"キャッシュから履歴データ取得: {cache_key}")
                return self.price_cache[cache_key]
            
            # データ取得
            data = await self._fetch_historical_data(stock_code, period, interval)
            if data is not None and not data.empty:
                # キャッシュに保存
                await self._save_to_cache(cache_key, data, cache_duration)
                return data
            else:
                logger.warning(f"履歴データが空です: {stock_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"履歴データ取得エラー {stock_code}: {str(e)}")
            return pd.DataFrame()
    
    async def get_multiple_stocks_data(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        複数銘柄の同時データ取得
        """
        try:
            # 並行処理でデータ取得
            tasks = []
            for stock_code in stock_codes:
                task = self._get_stock_data_with_semaphore(stock_code)
                tasks.append(task)
            
            # 結果収集
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 結果整理
            stock_data = {}
            for i, result in enumerate(results):
                stock_code = stock_codes[i]
                if isinstance(result, Exception):
                    logger.warning(f"データ取得エラー {stock_code}: {str(result)}")
                    stock_data[stock_code] = self._create_error_response(str(result))
                else:
                    stock_data[stock_code] = result
            
            return stock_data
            
        except Exception as e:
            logger.error(f"複数銘柄データ取得エラー: {str(e)}")
            return {}
    
    async def get_market_summary(self) -> Dict:
        """
        市場全体のサマリー取得
        """
        try:
            # 主要指数のデータ取得
            indices = {
                'nikkei': '^N225',      # 日経平均
                'topix': '^TOPX',       # TOPIX
                'jasdaq': '^JASDAQ',    # JASDAQ
                'mothers': '^MOTHERS',  # マザーズ（存在する場合）
            }
            
            summary = {}
            
            for name, symbol in indices.items():
                try:
                    data = await self.get_current_price(symbol)
                    if 'error' not in data:
                        summary[name] = {
                            'price': data.get('price', 0),
                            'change': data.get('change', 0),
                            'change_rate': data.get('change_rate', 0),
                            'volume': data.get('volume', 0)
                        }
                except Exception as e:
                    logger.warning(f"指数データ取得エラー {name}: {str(e)}")
                    summary[name] = {'error': str(e)}
            
            # 市場統計情報
            summary['market_stats'] = await self._calculate_market_stats()
            summary['updated_at'] = datetime.now().isoformat()
            
            return summary
            
        except Exception as e:
            logger.error(f"市場サマリー取得エラー: {str(e)}")
            return {'error': str(e)}
    
    async def get_stock_info(self, stock_code: str) -> Dict:
        """
        銘柄基本情報取得
        """
        try:
            # キャッシュチェック（24時間有効）
            cache_key = f"{stock_code}_info"
            if await self._is_cache_valid(cache_key, 'info'):
                return self.info_cache[cache_key]
            
            # Yahoo Financeから取得
            info = await self._fetch_stock_info(stock_code)
            
            if info:
                # キャッシュに保存
                await self._save_info_to_cache(cache_key, info)
                return info
            else:
                return {'error': '企業情報取得失敗'}
                
        except Exception as e:
            logger.error(f"銘柄情報取得エラー {stock_code}: {str(e)}")
            return {'error': str(e)}
    
    async def validate_stock_code(self, stock_code: str) -> bool:
        """
        銘柄コード妥当性検証
        """
        try:
            # 基本的なフォーマットチェック
            if not stock_code or len(stock_code) < 3:
                return False
            
            # 簡易データ取得テスト
            symbol = f"{stock_code}.T" if stock_code.isdigit() else stock_code
            
            async with self.request_semaphore:
                await self._rate_limit_check(stock_code)
                
                # スレッドプールで同期処理実行
                loop = asyncio.get_event_loop()
                ticker = yf.Ticker(symbol)
                info = await loop.run_in_executor(self.executor, ticker.info)
                
                return bool(info and 'symbol' in info)
                
        except Exception as e:
            logger.debug(f"銘柄コード検証エラー {stock_code}: {str(e)}")
            return False
    
    async def get_earnings_calendar(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        決算カレンダー取得（簡易版）
        """
        try:
            earnings_data = {}
            
            for stock_code in stock_codes:
                try:
                    info = await self.get_stock_info(stock_code)
                    if 'error' not in info:
                        # 決算関連情報抽出
                        earnings_data[stock_code] = {
                            'fiscal_year_end': info.get('lastFiscalYearEnd'),
                            'next_earnings_date': info.get('nextEarningsDate'),
                            'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
                            'revenue_quarterly_growth': info.get('revenueQuarterlyGrowth'),
                        }
                    else:
                        earnings_data[stock_code] = {'error': 'データ取得不可'}
                        
                except Exception as e:
                    logger.warning(f"決算情報取得エラー {stock_code}: {str(e)}")
                    earnings_data[stock_code] = {'error': str(e)}
            
            return earnings_data
            
        except Exception as e:
            logger.error(f"決算カレンダー取得エラー: {str(e)}")
            return {}
    
    # プライベートメソッド
    
    async def _fetch_current_data(self, stock_code: str) -> Optional[Dict]:
        """現在データ取得（内部処理）"""
        try:
            symbol = f"{stock_code}.T" if stock_code.isdigit() else stock_code
            
            async with self.request_semaphore:
                await self._rate_limit_check(stock_code)
                
                # スレッドプールで同期処理実行
                loop = asyncio.get_event_loop()
                ticker = yf.Ticker(symbol)
                
                # 最新の価格データ取得
                hist = await loop.run_in_executor(
                    self.executor, 
                    lambda: ticker.history(period='2d', interval='1d')
                )
                
                if hist.empty:
                    return None
                
                # 最新データ抽出
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                
                # 変化計算
                current_price = float(latest['Close'])
                prev_close = float(prev['Close'])
                change = current_price - prev_close
                change_rate = (change / prev_close * 100) if prev_close > 0 else 0
                
                return {
                    'code': stock_code,
                    'price': current_price,
                    'change': change,
                    'change_rate': change_rate,
                    'volume': int(latest['Volume']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'open': float(latest['Open']),
                    'timestamp': datetime.now().isoformat(),
                }
                
        except Exception as e:
            logger.warning(f"現在データ取得失敗 {stock_code}: {str(e)}")
            return None
    
    async def _fetch_historical_data(
        self, 
        stock_code: str, 
        period: str, 
        interval: str
    ) -> Optional[pd.DataFrame]:
        """履歴データ取得（内部処理）"""
        try:
            symbol = f"{stock_code}.T" if stock_code.isdigit() else stock_code
            
            async with self.request_semaphore:
                await self._rate_limit_check(stock_code)
                
                # スレッドプールで同期処理実行
                loop = asyncio.get_event_loop()
                ticker = yf.Ticker(symbol)
                
                data = await loop.run_in_executor(
                    self.executor,
                    lambda: ticker.history(period=period, interval=interval)
                )
                
                if data.empty:
                    return None
                
                # データ前処理
                data = await self._preprocess_historical_data(data)
                
                return data
                
        except Exception as e:
            logger.warning(f"履歴データ取得失敗 {stock_code}: {str(e)}")
            return None
    
    async def _fetch_stock_info(self, stock_code: str) -> Optional[Dict]:
        """銘柄情報取得（内部処理）"""
        try:
            symbol = f"{stock_code}.T" if stock_code.isdigit() else stock_code
            
            async with self.request_semaphore:
                await self._rate_limit_check(stock_code)
                
                # スレッドプールで同期処理実行
                loop = asyncio.get_event_loop()
                ticker = yf.Ticker(symbol)
                
                info = await loop.run_in_executor(self.executor, ticker.info)
                
                if not info:
                    return None
                
                # 必要な情報を抽出・整理
                processed_info = {
                    'symbol': info.get('symbol', stock_code),
                    'name': info.get('longName', info.get('shortName', '')),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'market_cap': info.get('marketCap', 0),
                    'employees': info.get('fullTimeEmployees', 0),
                    'website': info.get('website', ''),
                    'business_summary': info.get('businessSummary', ''),
                    'country': info.get('country', 'Japan'),
                    'exchange': info.get('exchange', ''),
                    'currency': info.get('currency', 'JPY'),
                    
                    # 財務情報
                    'total_revenue': info.get('totalRevenue', 0),
                    'gross_profits': info.get('grossProfits', 0),
                    'total_debt': info.get('totalDebt', 0),
                    'total_cash': info.get('totalCash', 0),
                    'book_value': info.get('bookValue', 0),
                    
                    # 株価関連
                    'shares_outstanding': info.get('sharesOutstanding', 0),
                    'float_shares': info.get('floatShares', 0),
                    'price_to_book': info.get('priceToBook', 0),
                    'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                    'forward_pe': info.get('forwardPE', 0),
                    'trailing_pe': info.get('trailingPE', 0),
                    
                    # 配当情報
                    'dividend_rate': info.get('dividendRate', 0),
                    'dividend_yield': info.get('dividendYield', 0),
                    'ex_dividend_date': info.get('exDividendDate', ''),
                    
                    # 決算情報
                    'last_fiscal_year_end': info.get('lastFiscalYearEnd', ''),
                    'next_earnings_date': info.get('nextEarningsDate', ''),
                    'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 0),
                    'revenue_quarterly_growth': info.get('revenueQuarterlyGrowth', 0),
                    
                    # 分析者評価
                    'recommendation_key': info.get('recommendationKey', ''),
                    'recommendation_mean': info.get('recommendationMean', 0),
                    'number_of_analyst_opinions': info.get('numberOfAnalystOpinions', 0),
                    'target_high_price': info.get('targetHighPrice', 0),
                    'target_low_price': info.get('targetLowPrice', 0),
                    'target_mean_price': info.get('targetMeanPrice', 0),
                }
                
                return processed_info
                
        except Exception as e:
            logger.warning(f"銘柄情報取得失敗 {stock_code}: {str(e)}")
            return None
    
    async def _get_stock_data_with_semaphore(self, stock_code: str) -> Dict:
        """セマフォ付きデータ取得"""
        try:
            return await self.get_current_price(stock_code)
        except Exception as e:
            return self._create_error_response(str(e))
    
    async def _preprocess_historical_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """履歴データ前処理"""
        try:
            # NaN値の処理
            data = data.fillna(method='forward').fillna(method='backward')
            
            # 追加計算フィールド
            data['Returns'] = data['Close'].pct_change()
            data['HL2'] = (data['High'] + data['Low']) / 2
            data['HLC3'] = (data['High'] + data['Low'] + data['Close']) / 3
            data['OHLC4'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
            
            # True Range計算
            data['TR'] = pd.concat([
                data['High'] - data['Low'],
                abs(data['High'] - data['Close'].shift(1)),
                abs(data['Low'] - data['Close'].shift(1))
            ], axis=1).max(axis=1)
            
            # 出来高平均
            data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
            data['Volume_Ratio'] = data['Volume'] / data['Volume_MA']
            
            return data
            
        except Exception as e:
            logger.warning(f"履歴データ前処理エラー: {str(e)}")
            return data
    
    async def _calculate_market_stats(self) -> Dict:
        """市場統計計算"""
        try:
            # 簡易的な市場統計（実装拡張可能）
            return {
                'active_stocks': 0,  # アクティブ銘柄数（実装予定）
                'advancing_stocks': 0,  # 上昇銘柄数
                'declining_stocks': 0,  # 下落銘柄数
                'unchanged_stocks': 0,  # 変わらず銘柄数
                'total_volume': 0,  # 全体出来高
                'market_trend': 'NEUTRAL',  # 市場トレンド
                'volatility_index': 50,  # ボラティリティ指標
            }
            
        except Exception as e:
            logger.warning(f"市場統計計算エラー: {str(e)}")
            return {'error': str(e)}
    
    async def _rate_limit_check(self, stock_code: str) -> None:
        """レート制限チェック"""
        try:
            current_time = time.time()
            last_time = self.last_request_time.get(stock_code, 0)
            
            elapsed = current_time - last_time
            required_delay = self.config['rate_limit_delay']
            
            if elapsed < required_delay:
                sleep_time = required_delay - elapsed
                await asyncio.sleep(sleep_time)
            
            self.last_request_time[stock_code] = time.time()
            
        except Exception as e:
            logger.debug(f"レート制限チェックエラー: {str(e)}")
    
    async def _is_cache_valid(self, cache_key: str, duration_key: str) -> bool:
        """キャッシュ有効性判定"""
        try:
            if cache_key not in self.price_cache:
                return False
            
            if cache_key not in self.cache_timestamps:
                return False
            
            # 有効期限の決定
            if isinstance(duration_key, str):
                duration = self.config['cache_duration'].get(duration_key, timedelta(hours=1))
            else:
                duration = duration_key
            
            cached_time = self.cache_timestamps[cache_key]
            return datetime.now() - cached_time < duration
            
        except Exception as e:
            logger.debug(f"キャッシュ有効性判定エラー: {str(e)}")
            return False
    
    async def _save_to_cache(self, cache_key: str, data, duration) -> None:
        """キャッシュ保存"""
        try:
            self.price_cache[cache_key] = data
            self.cache_timestamps[cache_key] = datetime.now()
            
            # キャッシュサイズ管理
            if len(self.price_cache) > 1000:
                await self._cleanup_cache()
                
        except Exception as e:
            logger.debug(f"キャッシュ保存エラー: {str(e)}")
    
    async def _save_info_to_cache(self, cache_key: str, info: Dict) -> None:
        """情報キャッシュ保存"""
        try:
            self.info_cache[cache_key] = info
            self.cache_timestamps[cache_key] = datetime.now()
            
        except Exception as e:
            logger.debug(f"情報キャッシュ保存エラー: {str(e)}")
    
    async def _cleanup_cache(self) -> None:
        """キャッシュクリーンアップ"""
        try:
            # 古いキャッシュエントリを削除
            current_time = datetime.now()
            keys_to_remove = []
            
            for key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > timedelta(hours=24):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self.price_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
                self.info_cache.pop(key, None)
            
            logger.debug(f"キャッシュクリーンアップ完了: {len(keys_to_remove)}件削除")
            
        except Exception as e:
            logger.warning(f"キャッシュクリーンアップエラー: {str(e)}")
    
    def _create_error_response(self, message: str) -> Dict:
        """エラーレスポンス作成"""
        return {
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_cache_stats(self) -> Dict:
        """キャッシュ統計取得"""
        try:
            return {
                'price_cache_size': len(self.price_cache),
                'info_cache_size': len(self.info_cache),
                'total_cache_entries': len(self.cache_timestamps),
                'oldest_entry': min(self.cache_timestamps.values()) if self.cache_timestamps else None,
                'newest_entry': max(self.cache_timestamps.values()) if self.cache_timestamps else None,
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def clear_cache(self) -> bool:
        """キャッシュクリア"""
        try:
            self.price_cache.clear()
            self.info_cache.clear()
            self.cache_timestamps.clear()
            logger.info("全キャッシュをクリアしました")
            return True
        except Exception as e:
            logger.error(f"キャッシュクリアエラー: {str(e)}")
            return False