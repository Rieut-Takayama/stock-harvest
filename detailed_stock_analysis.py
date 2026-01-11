#!/usr/bin/env python3
"""
日本株式市場の詳細調査 - より網羅的な分析
2023年10-12月期間、Synspective、四半期決算影響の詳細調査
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

# より多くの2018年以降上場銘柄を含む網羅的なリスト
GROWTH_MARKET_STOCKS = [
    # 2018年以降上場の成長銘柄
    "4477.T",   # BASE (2019年10月上場)
    "4490.T",   # ビザスク (2020年3月上場) 
    "5253.T",   # カバー (2019年12月上場)
    "4881.T",   # ファンペップ (2019年6月上場)
    "4883.T",   # モダリス (2020年12月上場)
    "4884.T",   # クリングルファーマ (2020年12月上場)
    "4012.T",   # アクシージア
    "4013.T",   # ナガオカ
    "7383.T",   # ネットプロテクションズ (2018年12月上場)
    "7378.T",   # ヘルスケア&メディカル投資法人
    "7049.T",   # 識学 (2019年4月上場)
    "7045.T",   # フィット (2018年7月上場)
    "7044.T",   # ピアラ (2018年12月上場)
    "4475.T",   # HENNGE (2019年10月上場)
    "4486.T",   # ユナイテッド&コレクティブ
    "4488.T",   # AI inside (2020年3月上場)
    "4492.T",   # ゼネテック (2018年12月上場)
    "4493.T",   # サイバーセキュリティクラウド (2020年3月上場)
    "4498.T",   # サイバートラスト
    "3696.T",   # セレス (2019年3月東証一部指定替え)
    "3941.T",   # レンジャーシステムズ
    "3937.T",   # Ubicomホールディングス
    "3962.T",   # チームスピリット (2018年8月上場)
    "3989.T",   # シェアリングテクノロジー
    "4014.T",   # カラダノート
    "4015.T",   # アララ
    "4595.T",   # ミズホメディー
    "4597.T",   # ソレイジア・ファーマ
    "4598.T",   # Delta-Fly Pharma
    "4599.T",   # ステムリム
    "6552.T",   # GameWith (2017年12月上場) 
    "6555.T",   # MS&Consulting (2018年12月上場)
    "6556.T",   # ウェルビー (2018年12月上場)
    "6094.T",   # フリークアウト・ホールディングス
    "9434.T",   # ソフトバンク (2018年12月上場)
    "290A.T",   # Synspective (2024年12月上場)
]

# より多くの決算時期に注目すべき銘柄
EARNINGS_FOCUS_STOCKS = [
    "4385.T",   # メルカリ
    "4477.T",   # BASE
    "4490.T",   # ビザスク
    "5253.T",   # カバー
    "7049.T",   # 識学
    "4475.T",   # HENNGE
    "4488.T",   # AI inside
    "4493.T",   # サイバーセキュリティクラウド
    "3962.T",   # チームスピリット
    "9434.T",   # ソフトバンク
    "6552.T",   # GameWith
    "6555.T",   # MS&Consulting
    "6556.T",   # ウェルビー
]

class DetailedStockAnalyzer:
    def __init__(self):
        self.target_period_start = "2023-10-01"
        self.target_period_end = "2023-12-31"
        self.ipo_cutoff_date = "2018-10-01"
        
    def get_stock_data_with_retry(self, symbol: str, start_date: str, end_date: str, max_retries: int = 3) -> Optional[pd.DataFrame]:
        """リトライ機能付き株価データ取得"""
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date, auto_adjust=True, back_adjust=True)
                
                if data.empty:
                    print(f"データが空です: {symbol}")
                    return None
                    
                # 必要な列が存在するかチェック
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in data.columns for col in required_columns):
                    print(f"必要な列が不足: {symbol}")
                    return None
                    
                data['Symbol'] = symbol
                data['Date'] = data.index
                data.reset_index(drop=True, inplace=True)
                
                return data
                
            except Exception as e:
                print(f"試行 {attempt + 1}/{max_retries} エラー: {symbol} - {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # リトライ前に待機
                else:
                    print(f"最終的に失敗: {symbol}")
                    return None
        
        return None
    
    def calculate_stop_high_price(self, prev_close: float) -> float:
        """東証のストップ高制限価格を計算"""
        if prev_close < 100:
            return prev_close + 30
        elif prev_close < 200:
            return prev_close + 50
        elif prev_close < 500:
            return prev_close + 80
        elif prev_close < 700:
            return prev_close + 100
        elif prev_close < 1000:
            return prev_close + 150
        elif prev_close < 1500:
            return prev_close + 300
        elif prev_close < 2000:
            return prev_close + 400
        elif prev_close < 3000:
            return prev_close + 500
        elif prev_close < 5000:
            return prev_close + 700
        elif prev_close < 7000:
            return prev_close + 1000
        elif prev_close < 10000:
            return prev_close + 1500
        else:
            # 一般的な上限（約30%制限）
            return prev_close * 1.30
    
    def is_stop_high_stuck(self, row: Dict, prev_close: float) -> Tuple[bool, Dict]:
        """ストップ高張り付き判定の厳密版"""
        open_price = row['Open']
        high_price = row['High']
        low_price = row['Low']
        close_price = row['Close']
        volume = row['Volume']
        
        # ストップ高価格計算
        stop_high_price = self.calculate_stop_high_price(prev_close)
        
        # ストップ高張り付き条件
        # 1. 終値がストップ高価格の99%以上
        is_close_to_stop_high = close_price >= stop_high_price * 0.99
        
        # 2. 高値がストップ高価格の99%以上
        is_high_at_stop_high = high_price >= stop_high_price * 0.99
        
        # 3. 安値が終値の1%未満（99%以上で推移）
        low_close_ratio = (close_price - low_price) / close_price
        is_stuck_at_high = low_close_ratio < 0.01
        
        # 4. 出来高が一定以上（流動性確認）
        has_volume = volume > 1000
        
        # 全条件をクリア
        is_stop_high_stuck = (is_close_to_stop_high and 
                             is_high_at_stop_high and 
                             is_stuck_at_high and 
                             has_volume)
        
        details = {
            'stop_high_price': stop_high_price,
            'close_to_stop_high': is_close_to_stop_high,
            'high_at_stop_high': is_high_at_stop_high,
            'stuck_at_high': is_stuck_at_high,
            'has_volume': has_volume,
            'low_close_ratio': low_close_ratio,
            'price_change_rate': (close_price - prev_close) / prev_close,
            'volume': volume
        }
        
        return is_stop_high_stuck, details
    
    def get_company_listing_info(self, symbol: str) -> Dict:
        """企業の上場情報を取得"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 長期間のデータから上場日を推定
            hist = ticker.history(period="max")
            listing_date = hist.index[0].strftime("%Y-%m-%d") if not hist.empty else "不明"
            
            return {
                'symbol': symbol,
                'listing_date': listing_date,
                'company_name': info.get('longName', info.get('shortName', '不明')),
                'sector': info.get('sector', '不明'),
                'industry': info.get('industry', '不明'),
                'market_cap': info.get('marketCap', 0)
            }
            
        except Exception as e:
            print(f"企業情報取得エラー: {symbol} - {str(e)}")
            return {
                'symbol': symbol,
                'listing_date': '不明',
                'company_name': '不明',
                'sector': '不明', 
                'industry': '不明',
                'market_cap': 0
            }
    
    def analyze_survey1_detailed(self) -> List[Dict]:
        """調査1の詳細版: 厳密条件ストップ高銘柄"""
        print("=== 調査1詳細: 2023年10-12月の厳密条件ストップ高銘柄 ===")
        
        all_results = []
        processed_stocks = []
        
        for symbol in GROWTH_MARKET_STOCKS:
            print(f"\n分析中: {symbol}")
            
            # 企業情報取得
            company_info = self.get_company_listing_info(symbol)
            processed_stocks.append(company_info)
            
            # 上場日チェック（2018年10月以降）
            listing_date = company_info['listing_date']
            if listing_date != '不明' and listing_date < self.ipo_cutoff_date:
                print(f"  スキップ（上場5年超）: {symbol} - 上場日: {listing_date}")
                continue
            
            print(f"  企業名: {company_info['company_name']}")
            print(f"  上場日: {listing_date}")
            print(f"  セクター: {company_info['sector']}")
            
            # 株価データ取得（期間を少し拡張）
            extended_start = "2023-09-15"  # 前日比計算のため少し前から取得
            data = self.get_stock_data_with_retry(symbol, extended_start, self.target_period_end)
            
            if data is None:
                print(f"  データ取得失敗: {symbol}")
                continue
            
            print(f"  取得データ期間: {len(data)}日")
            
            # 対象期間のデータにフィルタ
            target_data = data[data['Date'] >= self.target_period_start].copy()
            
            if target_data.empty:
                print(f"  対象期間のデータなし: {symbol}")
                continue
            
            # ストップ高張り付き判定
            stop_high_days = []
            
            for idx, row in target_data.iterrows():
                # 前日データを取得
                if idx > 0:
                    prev_idx = idx - 1
                    prev_row = data.iloc[prev_idx]
                    prev_close = prev_row['Close']
                    
                    is_stuck, details = self.is_stop_high_stuck(row, prev_close)
                    
                    if is_stuck:
                        result = {
                            'symbol': symbol,
                            'company_name': company_info['company_name'],
                            'listing_date': listing_date,
                            'sector': company_info['sector'],
                            'date': row['Date'],
                            'open': row['Open'],
                            'high': row['High'],
                            'low': row['Low'],
                            'close': row['Close'],
                            'volume': row['Volume'],
                            'prev_close': prev_close,
                            **details
                        }
                        
                        stop_high_days.append(result)
                        all_results.append(result)
                        
                        print(f"  ✓ ストップ高張り付き: {row['Date']} - 上昇率: {details['price_change_rate']:.2%}")
                        print(f"    安値/終値比率: {details['low_close_ratio']:.3f}")
                        print(f"    出来高: {details['volume']:,}")
            
            if not stop_high_days:
                print(f"  該当日なし: {symbol}")
            
            # APIレート制限対策
            time.sleep(1.0)
        
        return all_results, processed_stocks
    
    def analyze_synspective_detailed(self) -> Dict:
        """調査2詳細: Synspectiveの詳細分析"""
        print("\n=== 調査2詳細: Synspective (290A) の詳細分析 ===")
        
        symbol = "290A.T"
        
        # 上場日以降の全データを取得
        start_date = "2024-12-19"
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"分析期間: {start_date} ～ {end_date}")
        
        # 企業情報取得
        company_info = self.get_company_listing_info(symbol)
        print(f"企業名: {company_info['company_name']}")
        print(f"セクター: {company_info['sector']}")
        
        # 株価データ取得
        data = self.get_stock_data_with_retry(symbol, start_date, end_date)
        
        if data is None:
            return {"error": f"Synspective ({symbol}) のデータを取得できませんでした"}
        
        print(f"取得データ: {len(data)}日間")
        
        # 日次分析
        daily_analysis = []
        stop_high_count = 0
        
        for idx, row in data.iterrows():
            if idx > 0:  # 前日データが必要
                prev_close = data.iloc[idx-1]['Close']
                is_stuck, details = self.is_stop_high_stuck(row, prev_close)
                
                daily_data = {
                    'date': row['Date'],
                    'open': row['Open'],
                    'high': row['High'],
                    'low': row['Low'],
                    'close': row['Close'],
                    'volume': row['Volume'],
                    'change_rate': details['price_change_rate'],
                    'low_close_ratio': details['low_close_ratio'],
                    'is_stop_high_stuck': is_stuck
                }
                
                daily_analysis.append(daily_data)
                
                if is_stuck:
                    stop_high_count += 1
                    print(f"  ストップ高張り付き: {row['Date']} - 上昇率: {details['price_change_rate']:.2%}")
        
        return {
            "symbol": symbol,
            "company_info": company_info,
            "analysis_period": f"{start_date} ～ {end_date}",
            "total_trading_days": len(data),
            "stop_high_stuck_days": stop_high_count,
            "daily_analysis": daily_analysis,
            "summary": {
                "initial_price": data.iloc[0]['Close'] if not data.empty else None,
                "latest_price": data.iloc[-1]['Close'] if not data.empty else None,
                "total_return": ((data.iloc[-1]['Close'] - data.iloc[0]['Close']) / data.iloc[0]['Close']) if len(data) > 0 else 0,
                "max_price": data['High'].max() if not data.empty else None,
                "min_price": data['Low'].min() if not data.empty else None,
                "avg_volume": data['Volume'].mean() if not data.empty else None
            }
        }
    
    def run_detailed_analysis(self):
        """詳細調査を実行"""
        print("📊 詳細株式市場調査を開始します...")
        start_time = time.time()
        
        # 調査1の詳細実行
        print("\n" + "="*60)
        survey1_results, processed_stocks = self.analyze_survey1_detailed()
        
        # 調査2の詳細実行  
        print("\n" + "="*60)
        survey2_results = self.analyze_synspective_detailed()
        
        end_time = time.time()
        print(f"\n⏱️ 分析完了時間: {end_time - start_time:.1f}秒")
        
        return {
            "survey1": {
                "results": survey1_results,
                "processed_stocks": processed_stocks,
                "total_candidates": len(processed_stocks),
                "qualifying_stocks": len(survey1_results)
            },
            "survey2": survey2_results,
            "metadata": {
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_period": f"{self.target_period_start} ～ {self.target_period_end}",
                "ipo_cutoff": self.ipo_cutoff_date
            }
        }

def print_detailed_results(results: Dict):
    """詳細結果を整理して表示"""
    print("\n" + "="*80)
    print("📋 調査結果サマリー")
    print("="*80)
    
    # 調査1結果
    print(f"\n【調査1: 2023年10-12月の厳密条件ストップ高銘柄】")
    print(f"対象銘柄数: {results['survey1']['total_candidates']}")
    print(f"条件適合銘柄数: {results['survey1']['qualifying_stocks']}")
    
    if results['survey1']['results']:
        print(f"\n📊 条件適合銘柄一覧:")
        print("-" * 120)
        print(f"{'銘柄コード':<10} {'企業名':<25} {'日付':<12} {'上昇率':<8} {'安値/終値':<10} {'出来高':<12} {'上場日':<12}")
        print("-" * 120)
        
        for result in results['survey1']['results']:
            print(f"{result['symbol']:<10} "
                  f"{result['company_name'][:23]:<25} "
                  f"{result['date'].strftime('%Y-%m-%d'):<12} "
                  f"{result['price_change_rate']:.1%}:<8 "
                  f"{result['low_close_ratio']:.3f}:<10 "
                  f"{result['volume']:,}:<12 "
                  f"{result['listing_date']:<12}")
    else:
        print("❌ 該当銘柄なし")
        print("理由: 2023年10-12月期間において、以下の全ての条件を満たす銘柄は見つかりませんでした")
        print("  - ストップ高張り付き（終値がストップ高価格の99%以上）")
        print("  - 安値が終値の1%未満（ほぼ終日高値維持）") 
        print("  - 上場5年未満（2018年10月以降上場）")
        print("  - 十分な出来高（1,000株以上）")
    
    # 調査2結果
    print(f"\n【調査2: Synspective (290A) 分析結果】")
    if "error" in results['survey2']:
        print(f"❌ エラー: {results['survey2']['error']}")
    else:
        synsp = results['survey2']
        print(f"企業名: {synsp['company_info']['company_name']}")
        print(f"分析期間: {synsp['analysis_period']}")
        print(f"取引日数: {synsp['total_trading_days']}")
        print(f"ストップ高張り付き日数: {synsp['stop_high_stuck_days']}")
        
        if synsp['summary']:
            print(f"\n📈 価格推移:")
            print(f"  初値: {synsp['summary']['initial_price']:.0f}円")
            print(f"  最新価格: {synsp['summary']['latest_price']:.0f}円") 
            print(f"  通算リターン: {synsp['summary']['total_return']:.1%}")
            print(f"  最高値: {synsp['summary']['max_price']:.0f}円")
            print(f"  最安値: {synsp['summary']['min_price']:.0f}円")
            print(f"  平均出来高: {synsp['summary']['avg_volume']:,.0f}株")
    
    print(f"\n⏰ 分析実施日時: {results['metadata']['analysis_date']}")

if __name__ == "__main__":
    analyzer = DetailedStockAnalyzer()
    results = analyzer.run_detailed_analysis()
    print_detailed_results(results)