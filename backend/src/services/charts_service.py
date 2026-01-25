"""
Charts Service - チャートデータ取得サービス
リポジトリ層とバリデーター層を活用した堅牢なチャートデータ提供
"""

import logging
import os
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..lib.logger import logger, PerformanceTracker
from ..lib.test_data_provider import test_data_provider
from ..repositories.charts_repository import ChartsRepository
from ..validators.charts_validators import ChartsValidator
from ..models.charts_models import ChartDataModel, ChartDataRequestModel

class ChartsService:
    """チャートデータ取得サービス"""
    
    def __init__(self):
        self.charts_repository = ChartsRepository()
        self.charts_validator = ChartsValidator()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.is_test_mode = os.getenv('TESTING_MODE', 'false').lower() == 'true'
    
    async def get_chart_data(
        self,
        stock_code: str,
        timeframe: str = "1d",
        period: str = "30d",
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        チャートデータを取得（バリデーション・リポジトリ連携版）
        
        Args:
            stock_code: 銘柄コード (例: "7203")
            timeframe: タイムフレーム (1d, 1w, 1m, 3m)
            period: 期間 (30d, 90d, 1y, 2y)
            indicators: テクニカル指標リスト
            
        Returns:
            チャートデータ辞書
        """
        perf_tracker = PerformanceTracker(f"chart_data_service_{stock_code}", logger)
        
        try:
            # 入力値バリデーション
            request_data = {
                'stock_code': stock_code,
                'timeframe': timeframe,
                'period': period,
                'indicators': ','.join(indicators) if indicators else None
            }
            
            is_valid, validation_error, validated_request = self.charts_validator.validate_chart_request(request_data)
            if not is_valid:
                logger.warning(f"⚠️ バリデーションエラー: {validation_error}")
                return self._create_error_response(stock_code, validation_error)
            
            logger.info("📊 チャートデータ取得開始", {
                "stock_code": stock_code,
                "timeframe": timeframe,
                "period": period,
                "indicators_count": len(validated_request.indicators)
            })
            
            # タイムフレーム・期間の組み合わせ確認
            combination_valid, combination_error = self.charts_validator.validate_timeframe_period_combination(
                timeframe, period
            )
            if not combination_valid:
                return self._create_error_response(stock_code, combination_error)
            
            # データ取得（リポジトリ使用）
            symbol = f"{stock_code}.T"
            success, stock_data, error_msg = await self.charts_repository.fetch_stock_data(
                stock_code, period, symbol
            )
            
            if not success or stock_data.empty:
                logger.warning(f"⚠️ データ取得失敗 - 銘柄: {stock_code}")
                return self._create_error_response(stock_code, error_msg or "データが取得できませんでした")
            
            # OHLCデータを加工
            ohlc_data = self._process_ohlc_data(stock_data, timeframe)
            
            # テクニカル指標を計算
            technical_data = {}
            if validated_request.indicators:
                indicator_names = [ind.value for ind in validated_request.indicators]
                technical_data = await self._calculate_indicators(stock_data, indicator_names)
            
            # 銘柄情報を取得
            stock_info = await self.charts_repository.fetch_stock_info(symbol)
            
            # レスポンス構築
            response_data = {
                "success": True,
                "stockCode": stock_code,
                "symbol": symbol,
                "stockName": stock_info.get("name", f"銘柄{stock_code}"),
                "timeframe": timeframe,
                "period": period,
                "dataCount": len(ohlc_data),
                "lastUpdated": datetime.now().isoformat(),
                "ohlcData": ohlc_data,
                "technicalIndicators": technical_data,
                "currentPrice": {
                    "price": self.charts_validator.sanitize_float(
                        stock_data['Close'].iloc[-1] if not stock_data.empty else 0, 'price'
                    ),
                    "change": self._calculate_price_change(stock_data),
                    "changeRate": self._calculate_change_rate(stock_data),
                    "volume": self.charts_validator.sanitize_int(
                        stock_data['Volume'].iloc[-1] if not stock_data.empty else 0, 'volume'
                    )
                },
                "priceRange": {
                    "min": self.charts_validator.sanitize_float(
                        stock_data['Low'].min() if not stock_data.empty else 0, 'min_price'
                    ),
                    "max": self.charts_validator.sanitize_float(
                        stock_data['High'].max() if not stock_data.empty else 0, 'max_price'
                    ),
                    "period": period
                }
            }
            
            logger.info("✅ チャートデータ作成完了", {
                "stock_code": stock_code,
                "data_count": len(ohlc_data),
                "technical_indicators": list(technical_data.keys())
            })
            
            perf_tracker.end({
                "success": True,
                "data_points": len(ohlc_data),
                "indicators_calculated": len(technical_data)
            })
            
            return response_data
            
        except Exception as e:
            error_msg = f"チャートデータ取得エラー: {str(e)}"
            logger.error(error_msg, {
                "stock_code": stock_code,
                "timeframe": timeframe,
                "period": period,
                "error": str(e)
            })
            
            perf_tracker.end({"error": True})
            return self._create_error_response(stock_code, str(e))
    
    
    def _process_ohlc_data(self, data: pd.DataFrame, timeframe: str) -> List[Dict[str, Any]]:
        """OHLCデータを処理"""
        try:
            if data.empty:
                return []
            
            # タイムフレーム別リサンプリング
            if timeframe == "1w":
                data = data.resample('W').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
            elif timeframe == "1m":
                data = data.resample('M').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
            
            ohlc_list = []
            for index, row in data.iterrows():
                ohlc_list.append({
                    "date": index.strftime("%Y-%m-%d"),
                    "timestamp": int(index.timestamp() * 1000),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })
            
            return ohlc_list
            
        except Exception as e:
            logger.error(f"OHLCデータ処理エラー: {str(e)}")
            return []
    
    async def _calculate_indicators(self, data: pd.DataFrame, indicators: List[str]) -> Dict[str, Any]:
        """テクニカル指標を計算"""
        technical = {}
        
        try:
            if "sma" in indicators:
                technical["sma20"] = data['Close'].rolling(window=20).mean().fillna(0).tolist()
                technical["sma50"] = data['Close'].rolling(window=50).mean().fillna(0).tolist()
            
            if "rsi" in indicators:
                technical["rsi"] = self._calculate_rsi(data['Close']).tolist()
            
            if "macd" in indicators:
                macd_data = self._calculate_macd(data['Close'])
                technical["macd"] = macd_data
            
            if "bollinger" in indicators:
                bb_data = self._calculate_bollinger_bands(data['Close'])
                technical["bollingerBands"] = bb_data
                
        except Exception as e:
            logger.error(f"テクニカル指標計算エラー: {str(e)}")
        
        return technical
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_macd(self, prices: pd.Series) -> Dict[str, List[float]]:
        """MACD計算"""
        try:
            ema12 = prices.ewm(span=12).mean()
            ema26 = prices.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            histogram = macd - signal
            
            return {
                "macd": macd.fillna(0).tolist(),
                "signal": signal.fillna(0).tolist(),
                "histogram": histogram.fillna(0).tolist()
            }
        except Exception as e:
            logger.error(f"MACD計算エラー: {str(e)}")
            return {"macd": [], "signal": [], "histogram": []}
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict[str, List[float]]:
        """ボリンジャーバンド計算"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper = sma + (std * 2)
            lower = sma - (std * 2)
            
            return {
                "upper": upper.fillna(0).tolist(),
                "middle": sma.fillna(0).tolist(),
                "lower": lower.fillna(0).tolist()
            }
        except Exception as e:
            logger.error(f"ボリンジャーバンド計算エラー: {str(e)}")
            return {"upper": [], "middle": [], "lower": []}
    
    
    def _calculate_price_change(self, data: pd.DataFrame) -> float:
        """価格変動を計算"""
        if len(data) < 2:
            return 0.0
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[-2]
        return float(current_price - previous_price)
    
    def _calculate_change_rate(self, data: pd.DataFrame) -> float:
        """変動率を計算"""
        if len(data) < 2:
            return 0.0
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[-2]
        return float(((current_price - previous_price) / previous_price) * 100)
    
    def _create_error_response(self, stock_code: str, error_message: str) -> Dict[str, Any]:
        """エラーレスポンスを作成"""
        return {
            "success": False,
            "stockCode": stock_code,
            "symbol": f"{stock_code}.T",
            "stockName": f"銘柄{stock_code}",
            "timeframe": "1d",
            "period": "30d",
            "dataCount": 0,
            "lastUpdated": datetime.now().isoformat(),
            "ohlcData": [],
            "technicalIndicators": {},
            "currentPrice": {"price": 0, "change": 0, "changeRate": 0, "volume": 0},
            "priceRange": {"min": 0, "max": 0, "period": "30d"},
            "message": error_message
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """サービス層ヘルスチェック（リポジトリ連携）"""
        try:
            # リポジトリ層のヘルスチェックを実行
            repo_health = await self.charts_repository.health_check()
            
            # バリデータの基本機能確認
            test_validation = self.charts_validator.validate_stock_code("7203")
            validator_status = "healthy" if test_validation[0] else "error"
            
            return {
                "service_status": "healthy",
                "repository": repo_health,
                "validator": {
                    "status": validator_status,
                    "test_result": test_validation
                },
                "yfinance": "available" if not self.is_test_mode else "mock_mode",
                "test_mode": self.is_test_mode,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"サービスヘルスチェック失敗: {str(e)}")
            return {
                "service_status": "error", 
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }