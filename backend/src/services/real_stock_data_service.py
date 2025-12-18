"""
リアルタイム株価データ取得サービス
Yahoo Finance APIを使用
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RealStockDataService:
    """
    Yahoo Finance APIを使用したリアルタイム株価データ取得
    """
    
    def __init__(self):
        self.session = None
    
    def get_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        個別銘柄の基本情報を取得
        
        Args:
            ticker: 銘柄コード (例: "7203.T" for トヨタ)
        
        Returns:
            株価情報の辞書
        """
        try:
            # 日本株の場合は .T を付与
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="5d")
            
            if hist.empty:
                logger.warning(f"No data found for ticker: {ticker}")
                return None
            
            # 最新の価格データ
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            # 基本情報を構築
            stock_data = {
                "code": ticker.replace('.T', ''),
                "name": info.get('longName', info.get('shortName', 'Unknown')),
                "price": float(latest['Close']),
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "volume": int(latest['Volume']),
                "previous_close": float(previous['Close']),
                "change": float(latest['Close'] - previous['Close']),
                "change_rate": float((latest['Close'] - previous['Close']) / previous['Close'] * 100),
                "market_cap": info.get('marketCap'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "last_updated": datetime.now().isoformat()
            }
            
            # 追加メタデータ
            stock_data['metadata'] = {
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "avg_volume": info.get('averageVolume'),
                "pe_ratio": info.get('trailingPE'),
                "pb_ratio": info.get('priceToBook'),
                "dividend_yield": info.get('dividendYield')
            }
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error getting stock info for {ticker}: {str(e)}")
            return None
    
    def get_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        複数銘柄の情報を一括取得
        
        Args:
            tickers: 銘柄コードのリスト
        
        Returns:
            銘柄コードをキーとした株価情報の辞書
        """
        results = {}
        
        for ticker in tickers:
            stock_data = self.get_stock_info(ticker)
            if stock_data:
                results[ticker] = stock_data
        
        return results
    
    def check_stop_high(self, ticker: str, days_back: int = 5) -> Dict[str, Any]:
        """
        ストップ高状況をチェック
        
        Args:
            ticker: 銘柄コード
            days_back: 過去何日分チェックするか
        
        Returns:
            ストップ高情報
        """
        try:
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days_back}d")
            
            if hist.empty:
                return {"is_stop_high": False, "reason": "No data"}
            
            # 日本の制限値幅を簡易計算（実際はより複雑）
            latest = hist.iloc[-1]
            base_price = latest['Open']
            
            # 制限値幅の簡易計算（100円未満〜5000円以上で段階的に設定）
            if base_price < 100:
                limit_up = base_price * 1.3  # +30%
            elif base_price < 200:
                limit_up = base_price * 1.25  # +25%
            elif base_price < 500:
                limit_up = base_price * 1.2   # +20%
            elif base_price < 1000:
                limit_up = base_price * 1.15  # +15%
            elif base_price < 5000:
                limit_up = base_price * 1.1   # +10%
            else:
                limit_up = base_price * 1.05  # +5%
            
            # ストップ高判定（終値が制限値幅の95%以上）
            is_stop_high = latest['Close'] >= (limit_up * 0.95)
            
            # 連続ストップ高チェック
            consecutive_days = 0
            for i in range(len(hist)-1, -1, -1):
                day_data = hist.iloc[i]
                day_base = day_data['Open']
                
                if day_base < 100:
                    day_limit = day_base * 1.3
                elif day_base < 200:
                    day_limit = day_base * 1.25
                elif day_base < 500:
                    day_limit = day_base * 1.2
                elif day_base < 1000:
                    day_limit = day_base * 1.15
                elif day_base < 5000:
                    day_limit = day_base * 1.1
                else:
                    day_limit = day_base * 1.05
                
                if day_data['Close'] >= (day_limit * 0.95):
                    consecutive_days += 1
                else:
                    break
            
            return {
                "is_stop_high": is_stop_high,
                "consecutive_days": consecutive_days,
                "limit_up_price": round(limit_up, 0),
                "current_price": float(latest['Close']),
                "volume": int(latest['Volume']),
                "date": latest.name.strftime('%Y-%m-%d'),
                "percentage_to_limit": round((latest['Close'] / limit_up) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error checking stop high for {ticker}: {str(e)}")
            return {"is_stop_high": False, "error": str(e)}
    
    def get_historical_data(self, ticker: str, period: str = "1mo") -> pd.DataFrame:
        """
        過去データを取得
        
        Args:
            ticker: 銘柄コード
            period: 期間 ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        
        Returns:
            過去データのDataFrame
        """
        try:
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            return hist
            
        except Exception as e:
            logger.error(f"Error getting historical data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def calculate_moving_averages(self, ticker: str, periods: List[int] = [5, 25, 75]) -> Dict[str, float]:
        """
        移動平均線を計算
        
        Args:
            ticker: 銘柄コード
            periods: 移動平均の期間リスト
        
        Returns:
            各期間の移動平均値
        """
        try:
            hist = self.get_historical_data(ticker, "3mo")
            
            if hist.empty:
                return {}
            
            moving_averages = {}
            for period in periods:
                if len(hist) >= period:
                    ma_value = hist['Close'].rolling(window=period).mean().iloc[-1]
                    moving_averages[f"ma_{period}"] = float(ma_value)
            
            # 現在価格と移動平均線の関係
            current_price = float(hist['Close'].iloc[-1])
            for period in periods:
                ma_key = f"ma_{period}"
                if ma_key in moving_averages:
                    # 移動平均線上抜けの判定
                    above_ma = current_price > moving_averages[ma_key]
                    moving_averages[f"{ma_key}_above"] = above_ma
                    
                    # 乖離率の計算
                    deviation = ((current_price - moving_averages[ma_key]) / moving_averages[ma_key]) * 100
                    moving_averages[f"{ma_key}_deviation"] = round(deviation, 2)
            
            return moving_averages
            
        except Exception as e:
            logger.error(f"Error calculating moving averages for {ticker}: {str(e)}")
            return {}

# 使用例とテスト用関数
def test_real_stock_service():
    """
    リアルタイム株価サービスのテスト
    """
    service = RealStockDataService()
    
    # 主要銘柄のテスト
    test_tickers = ["7203", "6501", "9984"]  # トヨタ、日立、ソフトバンク
    
    logger.info("=== Individual Stock Test ===")
    for ticker in test_tickers:
        logger.info(f"Testing {ticker}...")
        stock_data = service.get_stock_info(ticker)
        if stock_data:
            logger.info(f"Name: {stock_data['name']}")
            logger.info(f"Price: {stock_data['price']:,.0f}円")
            logger.info(f"Change: {stock_data['change']:+,.0f}円 ({stock_data['change_rate']:+.2f}%)")
            logger.info(f"Volume: {stock_data['volume']:,}")
        else:
            logger.warning(f"Failed to get data for {ticker}")
    
    logger.info("=== Stop High Check Test ===")
    for ticker in test_tickers:
        stop_high_info = service.check_stop_high(ticker)
        logger.info(f"{ticker}: Stop High = {stop_high_info.get('is_stop_high', False)}")
        if stop_high_info.get('is_stop_high'):
            logger.info(f"  Consecutive days: {stop_high_info.get('consecutive_days', 0)}")
            logger.info(f"  Limit price: {stop_high_info.get('limit_up_price', 0):,.0f}円")
    
    logger.info("=== Moving Average Test ===")
    ma_data = service.calculate_moving_averages("7203")
    for key, value in ma_data.items():
        logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    test_real_stock_service()