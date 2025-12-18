"""
Charts Repository - チャートデータリポジトリ層
外部データソース（yfinance）との連携とキャッシュ管理
"""

import logging
import os
import json
import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib

from ..lib.logger import logger, PerformanceTracker
from ..services.test_data_provider import test_data_provider

class ChartsRepository:
    """チャートデータ取得リポジトリ"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.is_test_mode = os.getenv('TESTING_MODE', 'false').lower() == 'true'
        self.cache_enabled = True
        self.cache = {}  # 簡易メモリキャッシュ
        self.cache_ttl = 300  # 5分
    
    async def fetch_stock_data(
        self,
        stock_code: str,
        period: str,
        symbol: Optional[str] = None
    ) -> Tuple[bool, pd.DataFrame, str]:
        """
        株価データの取得
        
        Args:
            stock_code: 銘柄コード
            period: 取得期間
            symbol: yfinanceシンボル（省略時は自動生成）
            
        Returns:
            Tuple[bool, pd.DataFrame, str]: (成功フラグ, データ, エラーメッセージ)
        """
        perf_tracker = PerformanceTracker(f"stock_data_fetch_{stock_code}", logger)
        
        try:
            if symbol is None:
                symbol = f"{stock_code}.T"
            
            logger.info(f"📊 株価データ取得開始", {
                "stock_code": stock_code,
                "symbol": symbol,
                "period": period,
                "test_mode": self.is_test_mode
            })
            
            # キャッシュチェック
            if self.cache_enabled:
                cached_data = await self._get_cached_data(symbol, period)
                if cached_data is not None:
                    logger.debug("キャッシュからデータを取得")
                    perf_tracker.end({"cache_hit": True})
                    return True, cached_data, ""
            
            # テストモード時の処理
            if self.is_test_mode:
                return await self._fetch_test_data(symbol, period, perf_tracker)
            
            # 本番モード時の処理
            return await self._fetch_production_data(symbol, period, perf_tracker)
            
        except Exception as e:
            error_msg = f"株価データ取得エラー: {str(e)}"
            logger.error(error_msg, {
                "stock_code": stock_code,
                "symbol": symbol,
                "period": period,
                "error": str(e)
            })
            perf_tracker.end({"error": True})
            return False, pd.DataFrame(), error_msg
    
    async def _fetch_test_data(
        self,
        symbol: str,
        period: str,
        perf_tracker: PerformanceTracker
    ) -> Tuple[bool, pd.DataFrame, str]:
        """テストモード用データ取得"""
        logger.info("🧪 テストモード: 固定データを使用")
        
        # 存在確認（symbolから銘柄コードを抽出）
        stock_code = symbol.replace('.T', '')
        stock_data = test_data_provider.get_fixed_stock_data(stock_code)
        if stock_data is None:
            logger.warning(f"テストモード: 存在しない銘柄 - {symbol} (code: {stock_code})")
            perf_tracker.end({"test_mode": True, "stock_exists": False})
            return False, pd.DataFrame(), "指定された銘柄が見つかりません"
        
        # モックデータ生成
        mock_data = test_data_provider.create_mock_api_response(symbol, period)
        
        # キャッシュ保存
        if self.cache_enabled:
            await self._save_to_cache(symbol, period, mock_data)
        
        perf_tracker.end({
            "test_mode": True,
            "stock_exists": True,
            "data_points": len(mock_data)
        })
        
        return True, mock_data, ""
    
    async def _fetch_production_data(
        self,
        symbol: str,
        period: str,
        perf_tracker: PerformanceTracker
    ) -> Tuple[bool, pd.DataFrame, str]:
        """本番モード用データ取得"""
        logger.info("🌐 本番モード: yfinanceからデータ取得")
        
        loop = asyncio.get_event_loop()
        
        def fetch_yfinance_data() -> Tuple[bool, pd.DataFrame, str]:
            try:
                # API可用性シミュレーション
                if not test_data_provider.is_api_available_simulation():
                    raise Exception("API unavailable simulation")
                
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                
                if data.empty:
                    logger.warning(f"yfinanceで空データ - 存在しない銘柄: {symbol}")
                    return False, pd.DataFrame(), "指定された銘柄が見つかりません"
                
                logger.info(f"yfinanceデータ取得成功", {
                    "symbol": symbol,
                    "data_points": len(data),
                    "date_range": f"{data.index[0]} to {data.index[-1]}"
                })
                
                return True, data, ""
                
            except Exception as e:
                logger.warning(f"yfinance取得失敗: {symbol} - {str(e)}")
                
                # フォールバック判定
                if "unavailable simulation" in str(e):
                    logger.info(f"API接続問題によりフォールバック使用: {symbol}")
                    fallback_data = test_data_provider.create_mock_api_response(symbol, period)
                    return True, fallback_data, "フォールバックデータを使用"
                else:
                    return False, pd.DataFrame(), f"データ取得エラー: {str(e)}"
        
        success, data, error_msg = await loop.run_in_executor(self.executor, fetch_yfinance_data)
        
        # 成功時はキャッシュ保存
        if success and self.cache_enabled and not data.empty:
            await self._save_to_cache(symbol, period, data)
        
        perf_tracker.end({
            "production_mode": True,
            "success": success,
            "data_points": len(data) if success else 0,
            "fallback_used": "フォールバック" in error_msg
        })
        
        return success, data, error_msg
    
    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        銘柄情報の取得
        
        Args:
            symbol: yfinanceシンボル
            
        Returns:
            銘柄情報辞書
        """
        try:
            logger.debug(f"銘柄情報取得開始: {symbol}")
            
            # テストモード時
            if self.is_test_mode:
                stock_code = symbol.replace('.T', '')
                stock_data = test_data_provider.get_fixed_stock_data(stock_code)
                if stock_data:
                    return {
                        "name": stock_data["name"],
                        "sector": stock_data.get("sector", "テクノロジー"),
                        "industry": stock_data.get("industry", "自動車"),
                        "marketCap": stock_data.get("market_cap", 1000000000)
                    }
                return {"name": "Unknown", "sector": "Unknown", "industry": "Unknown", "marketCap": 0}
            
            # 本番モード時
            loop = asyncio.get_event_loop()
            
            def fetch_info():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    return {
                        "name": info.get("longName", info.get("shortName", "Unknown")),
                        "sector": info.get("sector", "Unknown"),
                        "industry": info.get("industry", "Unknown"),
                        "marketCap": info.get("marketCap", 0)
                    }
                except Exception as e:
                    logger.warning(f"銘柄情報取得エラー: {str(e)}")
                    return {"name": "Unknown", "sector": "Unknown", "industry": "Unknown", "marketCap": 0}
            
            return await loop.run_in_executor(self.executor, fetch_info)
            
        except Exception as e:
            logger.error(f"銘柄情報取得処理エラー: {str(e)}")
            return {"name": "Unknown", "sector": "Unknown", "industry": "Unknown", "marketCap": 0}
    
    async def validate_stock_exists(self, stock_code: str) -> Tuple[bool, str]:
        """
        銘柄の存在確認
        
        Args:
            stock_code: 銘柄コード
            
        Returns:
            Tuple[bool, str]: (存在フラグ, エラーメッセージ)
        """
        try:
            symbol = f"{stock_code}.T"
            
            # テストモード時
            if self.is_test_mode:
                stock_data = test_data_provider.get_fixed_stock_data(stock_code)
                if stock_data:
                    return True, ""
                return False, "指定された銘柄が見つかりません（テストモード）"
            
            # 本番モード時は軽量なデータ取得で確認
            success, data, error_msg = await self.fetch_stock_data(stock_code, "5d", symbol)
            
            if success and not data.empty:
                return True, ""
            else:
                return False, error_msg or "指定された銘柄が見つかりません"
                
        except Exception as e:
            error_msg = f"銘柄存在確認エラー: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    async def _get_cached_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """キャッシュからデータを取得"""
        try:
            cache_key = self._generate_cache_key(symbol, period)
            
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                cached_time = cache_entry['timestamp']
                
                # TTL確認
                if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                    return cache_entry['data']
                else:
                    # 期限切れキャッシュ削除
                    del self.cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.warning(f"キャッシュ読み取りエラー: {str(e)}")
            return None
    
    async def _save_to_cache(self, symbol: str, period: str, data: pd.DataFrame) -> None:
        """データをキャッシュに保存"""
        try:
            cache_key = self._generate_cache_key(symbol, period)
            
            self.cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            # キャッシュサイズ管理（最大100エントリー）
            if len(self.cache) > 100:
                # 最も古いエントリーを削除
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]['timestamp']
                )
                del self.cache[oldest_key]
            
        except Exception as e:
            logger.warning(f"キャッシュ保存エラー: {str(e)}")
    
    def _generate_cache_key(self, symbol: str, period: str) -> str:
        """キャッシュキー生成"""
        raw_key = f"{symbol}_{period}"
        return hashlib.md5(raw_key.encode()).hexdigest()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        リポジトリ層ヘルスチェック
        
        Returns:
            ヘルスチェック結果
        """
        try:
            # テスト銘柄でのデータ取得確認
            test_symbol = "7203.T"
            success, data, error_msg = await self.fetch_stock_data("7203", "5d", test_symbol)
            
            health_info = {
                "repository_status": "healthy" if success else "degraded",
                "test_symbol": test_symbol,
                "test_data_points": len(data) if success else 0,
                "test_mode": self.is_test_mode,
                "cache_enabled": self.cache_enabled,
                "cache_entries": len(self.cache),
                "last_check": datetime.now().isoformat()
            }
            
            if not success:
                health_info["error"] = error_msg
            
            return health_info
            
        except Exception as e:
            logger.error(f"リポジトリヘルスチェック失敗: {str(e)}")
            return {
                "repository_status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def clear_cache(self) -> int:
        """
        キャッシュクリア
        
        Returns:
            クリアされたエントリー数
        """
        cleared_count = len(self.cache)
        self.cache.clear()
        logger.info(f"キャッシュクリア完了: {cleared_count}エントリー削除")
        return cleared_count