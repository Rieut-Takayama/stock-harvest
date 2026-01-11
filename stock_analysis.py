#!/usr/bin/env python3
"""
日本株式市場の厳密条件ストップ高銘柄調査
2023年10月-12月期間の詳細分析
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 東証上場銘柄の代表的なコードリスト（東証プライム・スタンダード・グロース）
JAPANESE_STOCK_CODES = [
    # テクノロジー・新興市場銘柄を中心に選定
    "4755.T",  # 楽天グループ
    "4563.T",  # アンジェス
    "3681.T",  # ブイキューブ
    "3984.T",  # ユーザーローカル
    "4385.T",  # メルカリ
    "4477.T",  # BASE
    "4490.T",  # ビザスク
    "4054.T",  # 日本情報クリエイト
    "3778.T",  # さくらインターネット
    "3656.T",  # KLab
    "3793.T",  # ドリコム
    "3815.T",  # メディア工房
    "3663.T",  # アートスパーク
    "3912.T",  # モバイルファクトリー
    "3923.T",  # ラクス
    "3966.T",  # ユーザベース
    "4588.T",  # オンコリスバイオファーマ
    "4592.T",  # サンバイオ
    "4594.T",  # ブライトパス・バイオ
    "4596.T",  # 窪田製薬ホールディングス
    "2148.T",  # アイティメディア
    "2160.T",  # GNIグループ
    "2326.T",  # デジタルアーツ
    "2345.T",  # クシム
    "2389.T",  # オプトホールディング
    "2438.T",  # アスカネット
    "6027.T",  # 弁護士ドットコム
    "6036.T",  # KeePer技研
    "6037.T",  # ファストリテイリング
    "6098.T",  # リクルートホールディングス
    # 2018年以降上場の新興銘柄も含める
    "4881.T",  # ファンペップ
    "4882.T",  # ペプチドリーム
    "4883.T",  # モダリス
    "4884.T",  # クリングルファーマ
    "4012.T",  # アクシージア
    "4013.T",  # ナガオカ
    "5253.T",  # カバー
    "6180.T",  # GMOメディア
    "6190.T",  # フェンリル
]

class StockAnalyzer:
    def __init__(self):
        self.target_period_start = "2023-10-01"
        self.target_period_end = "2023-12-31"
        self.ipo_cutoff_date = "2018-10-01"  # 上場5年未満の基準日
        
    def get_stock_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """株価データを取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, auto_adjust=True, back_adjust=True)
            
            if data.empty:
                print(f"データが取得できません: {symbol}")
                return None
                
            # データの整理
            data['Symbol'] = symbol
            data['Date'] = data.index
            data.reset_index(drop=True, inplace=True)
            
            return data
            
        except Exception as e:
            print(f"エラー: {symbol} - {str(e)}")
            return None
    
    def check_stop_high_conditions(self, data: pd.DataFrame) -> List[Dict]:
        """ストップ高条件をチェック"""
        results = []
        
        for idx, row in data.iterrows():
            date = row['Date']
            open_price = row['Open']
            high_price = row['High']
            low_price = row['Low']
            close_price = row['Close']
            volume = row['Volume']
            symbol = row['Symbol']
            
            # 前日終値を取得（ストップ高判定のため）
            if idx > 0:
                prev_close = data.iloc[idx-1]['Close']
                
                # 理論上のストップ高価格を計算（前日終値の1.3倍、または300円のうち小さい方）
                if prev_close <= 100:
                    stop_high_price = prev_close + 30
                elif prev_close <= 200:
                    stop_high_price = prev_close + 50
                elif prev_close <= 500:
                    stop_high_price = prev_close + 80
                elif prev_close <= 1000:
                    stop_high_price = prev_close + 150
                elif prev_close <= 1500:
                    stop_high_price = prev_close + 300
                else:
                    # 一般的な上限制限（30%上昇）
                    stop_high_price = prev_close * 1.30
                
                # ストップ高判定条件
                is_stop_high = abs(close_price - stop_high_price) / stop_high_price < 0.01  # 1%以内
                
                # 安値が終値の1%未満の条件
                low_close_ratio = (close_price - low_price) / close_price
                is_low_condition_met = low_close_ratio < 0.01
                
                # 両条件を満たす場合
                if is_stop_high and is_low_condition_met:
                    results.append({
                        'symbol': symbol,
                        'date': date,
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'close': close_price,
                        'volume': volume,
                        'prev_close': prev_close,
                        'stop_high_price': stop_high_price,
                        'low_close_ratio': low_close_ratio,
                        'price_change_rate': (close_price - prev_close) / prev_close
                    })
        
        return results
    
    def get_listing_date(self, symbol: str) -> Optional[str]:
        """上場日を取得（簡易版 - より古い期間から検索）"""
        try:
            ticker = yf.Ticker(symbol)
            # 過去10年分のデータを取得して最初の日を探す
            info_data = ticker.history(period="max", auto_adjust=True)
            
            if not info_data.empty:
                listing_date = info_data.index[0].strftime("%Y-%m-%d")
                return listing_date
            
        except Exception as e:
            print(f"上場日取得エラー: {symbol} - {str(e)}")
            
        return None
    
    def analyze_survey1(self) -> List[Dict]:
        """調査1: 2023年10-12月の厳密条件ストップ高銘柄"""
        print("=== 調査1: 2023年10-12月の厳密条件ストップ高銘柄 ===")
        
        all_results = []
        
        for symbol in JAPANESE_STOCK_CODES:
            print(f"分析中: {symbol}")
            
            # 上場日チェック
            listing_date = self.get_listing_date(symbol)
            if listing_date and listing_date < self.ipo_cutoff_date:
                print(f"  スキップ（上場5年超過）: {symbol} - 上場日: {listing_date}")
                continue
            
            # 株価データ取得
            data = self.get_stock_data(symbol, self.target_period_start, self.target_period_end)
            if data is None:
                continue
            
            # ストップ高条件チェック
            stop_high_results = self.check_stop_high_conditions(data)
            
            for result in stop_high_results:
                result['listing_date'] = listing_date
                all_results.append(result)
                print(f"  ✓ ストップ高発見: {symbol} - {result['date']} - 上昇率: {result['price_change_rate']:.2%}")
            
            # APIレート制限対策
            time.sleep(0.5)
        
        return all_results
    
    def analyze_synspective(self) -> Dict:
        """調査2: Synspective (290A) の分析"""
        print("=== 調査2: Synspective (290A) 分析 ===")
        
        symbol = "290A.T"  # Synspectiveのティッカーシンボル
        
        # 2024年12月19日以降のデータを取得
        start_date = "2024-12-19"
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = self.get_stock_data(symbol, start_date, end_date)
        
        if data is None:
            return {"error": "Synspectiveのデータを取得できませんでした"}
        
        stop_high_results = self.check_stop_high_conditions(data)
        
        return {
            "symbol": symbol,
            "listing_date": "2024-12-19",
            "analysis_period": f"{start_date} - {end_date}",
            "total_trading_days": len(data),
            "stop_high_days": stop_high_results,
            "stop_high_count": len(stop_high_results)
        }
    
    def run_full_analysis(self):
        """全調査を実行"""
        print("株式市場調査を開始します...")
        
        # 調査1の実行
        survey1_results = self.analyze_survey1()
        
        # 調査2の実行
        survey2_results = self.analyze_synspective()
        
        # 結果をまとめる
        return {
            "survey1": survey1_results,
            "survey2": survey2_results
        }

if __name__ == "__main__":
    analyzer = StockAnalyzer()
    results = analyzer.run_full_analysis()
    
    # 調査1の結果表示
    print("\n=== 調査1結果 ===")
    if results["survey1"]:
        for result in results["survey1"]:
            print(f"銘柄: {result['symbol']}, 日付: {result['date']}, "
                  f"上昇率: {result['price_change_rate']:.2%}, "
                  f"安値/終値比率: {result['low_close_ratio']:.3f}")
    else:
        print("該当銘柄なし")
    
    # 調査2の結果表示
    print("\n=== 調査2結果 ===")
    print(f"Synspective分析結果:")
    print(f"取引日数: {results['survey2'].get('total_trading_days', 'N/A')}")
    print(f"ストップ高回数: {results['survey2'].get('stop_high_count', 'N/A')}")