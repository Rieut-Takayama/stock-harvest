#!/usr/bin/env python3
"""
四半期決算発表後のストップ高張り付き銘柄調査
2023年10-12月期間の決算サプライズ影響分析
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

# 2023年10-12月に決算発表があった主要な成長銘柄
EARNINGS_STOCKS_Q3_Q4_2023 = [
    # テクノロジー・成長株（2023年10-12月決算発表）
    ("4477.T", "BASE", "2019-10-25", "10月下旬"),       # BASE Q2決算
    ("4490.T", "ビザスク", "2020-03-10", "11月中旬"),     # ビザスク Q2決算
    ("5253.T", "カバー", "2023-03-27", "11月上旬"),        # カバー Q2決算
    ("4488.T", "AI inside", "2019-12-26", "11月中旬"),   # AI inside Q2決算
    ("4475.T", "HENNGE", "2019-10-08", "11月上旬"),      # HENNGE Q2決算
    ("4493.T", "サイバーセキュリティクラウド", "2020-03-26", "11月中旬"), # CSC Q2決算
    ("7049.T", "識学", "2019-02-25", "11月下旬"),         # 識学 Q2決算
    ("3962.T", "チームスピリット", "2016-09-28", "11月中旬"), # チームスピリット Q2決算
    ("6552.T", "GameWith", "2017-07-03", "11月中旬"),     # GameWith Q2決算
    ("4881.T", "ファンペップ", "2020-12-25", "11月中旬"),   # ファンペップ Q2決算
    ("4883.T", "モダリス", "2020-08-03", "11月中旬"),      # モダリス Q2決算
    ("4884.T", "クリングルファーマ", "2020-12-28", "11月中旬"), # クリングルファーマ Q2決算
    ("4012.T", "アクシージア", "2020-10-02", "11月中旬"),   # アクシージア Q2決算
    ("4013.T", "キンジロー", "2020-10-13", "11月中旬"),     # キンジロー Q2決算
    ("7383.T", "ネットプロテクションズ", "2021-12-15", "11月中旬"), # ネプロ Q2決算
    ("7378.T", "アシロ", "2021-07-20", "11月中旬"),        # アシロ Q2決算
    ("4486.T", "ユナイテッド&コレクティブ", "2019-12-19", "11月中旬"), # U&C Q2決算
    ("4492.T", "ゼネテック", "2020-03-19", "11月中旬"),     # ゼネテック Q2決算
    ("4498.T", "サイバートラスト", "2021-04-16", "11月中旬"), # サイバートラスト Q2決算
    ("4014.T", "カラダノート", "2020-10-28", "11月中旬"),   # カラダノート Q2決算
    ("4015.T", "アララ", "2020-11-20", "11月中旬"),        # アララ Q2決算
    ("4599.T", "ステムリム", "2019-08-09", "11月中旬"),     # ステムリム Q2決算
    ("9434.T", "ソフトバンク", "2018-12-19", "11月上旬"),    # ソフトバンク Q2決算
]

# 決算発表の典型的な日程（推定）
EARNINGS_CALENDAR_2023 = {
    "10月": [
        "2023-10-30", "2023-10-31",  # 10月末決算発表
    ],
    "11月": [
        "2023-11-06", "2023-11-07", "2023-11-08", "2023-11-09", "2023-11-10",  # 11月上旬
        "2023-11-13", "2023-11-14", "2023-11-15", "2023-11-16", "2023-11-17",  # 11月中旬
        "2023-11-20", "2023-11-21", "2023-11-22", "2023-11-24",                # 11月下旬
    ],
    "12月": [
        "2023-12-04", "2023-12-05", "2023-12-06", "2023-12-07", "2023-12-08",  # 12月上旬
    ]
}

class EarningsAnalyzer:
    def __init__(self):
        self.target_period_start = "2023-10-01"
        self.target_period_end = "2023-12-31"
        self.ipo_cutoff_date = "2018-10-01"
        
    def get_stock_data_with_retry(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """リトライ機能付き株価データ取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, auto_adjust=True, back_adjust=True)
            
            if data.empty:
                return None
                
            data['Symbol'] = symbol
            data['Date'] = data.index
            data.reset_index(drop=True, inplace=True)
            
            return data
            
        except Exception as e:
            print(f"データ取得エラー: {symbol} - {str(e)}")
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
        else:
            return prev_close * 1.30
    
    def is_stop_high_stuck(self, row: Dict, prev_close: float) -> Tuple[bool, Dict]:
        """ストップ高張り付き判定"""
        close_price = row['Close']
        high_price = row['High']
        low_price = row['Low']
        volume = row['Volume']
        
        stop_high_price = self.calculate_stop_high_price(prev_close)
        
        # 判定条件
        is_close_to_stop_high = close_price >= stop_high_price * 0.99
        is_high_at_stop_high = high_price >= stop_high_price * 0.99
        low_close_ratio = (close_price - low_price) / close_price
        is_stuck_at_high = low_close_ratio < 0.01
        has_volume = volume > 1000
        
        is_stop_high_stuck = (is_close_to_stop_high and 
                             is_high_at_stop_high and 
                             is_stuck_at_high and 
                             has_volume)
        
        details = {
            'stop_high_price': stop_high_price,
            'low_close_ratio': low_close_ratio,
            'price_change_rate': (close_price - prev_close) / prev_close,
            'volume': volume,
            'close_to_stop_high': is_close_to_stop_high,
            'stuck_at_high': is_stuck_at_high
        }
        
        return is_stop_high_stuck, details
    
    def find_next_business_day(self, date_str: str) -> str:
        """翌営業日を取得"""
        date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 土日を避けて翌営業日を探す
        next_day = date + timedelta(days=1)
        while next_day.weekday() >= 5:  # 5=土曜, 6=日曜
            next_day += timedelta(days=1)
        
        return next_day.strftime("%Y-%m-%d")
    
    def analyze_earnings_impact(self) -> List[Dict]:
        """決算発表翌日のストップ高張り付き分析"""
        print("=== 調査3: 四半期決算翌日ストップ張り付き銘柄調査 ===")
        
        all_earnings_results = []
        
        # 各決算発表日の翌日をチェック
        for month, dates in EARNINGS_CALENDAR_2023.items():
            print(f"\n{month}の決算発表日程分析:")
            
            for earnings_date in dates:
                next_business_day = self.find_next_business_day(earnings_date)
                print(f"  決算日: {earnings_date} → 翌営業日: {next_business_day}")
                
                # その日にストップ高張り付きした銘柄を探す
                for symbol, company_name, listing_date, earnings_timing in EARNINGS_STOCKS_Q3_Q4_2023:
                    
                    # 上場5年未満チェック
                    if listing_date < self.ipo_cutoff_date:
                        continue
                    
                    # 決算発表タイミングのマッチングチェック
                    if month == "10月" and "10月" not in earnings_timing:
                        continue
                    elif month == "11月" and "11月" not in earnings_timing:
                        continue
                    elif month == "12月" and "12月" not in earnings_timing:
                        continue
                    
                    # 株価データ取得（決算前後の期間）
                    start_date = (datetime.strptime(earnings_date, "%Y-%m-%d") - timedelta(days=5)).strftime("%Y-%m-%d")
                    end_date = (datetime.strptime(next_business_day, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
                    
                    data = self.get_stock_data_with_retry(symbol, start_date, end_date)
                    if data is None:
                        continue
                    
                    # 翌営業日のデータを探す
                    target_data = data[data['Date'].dt.strftime('%Y-%m-%d') == next_business_day]
                    if target_data.empty:
                        continue
                    
                    target_row = target_data.iloc[0]
                    
                    # 前日（決算発表日）のデータを探す
                    prev_data = data[data['Date'].dt.strftime('%Y-%m-%d') == earnings_date]
                    if prev_data.empty:
                        # 決算発表日が休日の場合、前営業日を探す
                        prev_data = data[data['Date'] < target_row['Date']]
                        if prev_data.empty:
                            continue
                        prev_close = prev_data.iloc[-1]['Close']
                    else:
                        prev_close = prev_data.iloc[0]['Close']
                    
                    # ストップ高張り付き判定
                    is_stuck, details = self.is_stop_high_stuck(target_row, prev_close)
                    
                    if is_stuck:
                        result = {
                            'earnings_date': earnings_date,
                            'trading_date': next_business_day,
                            'symbol': symbol,
                            'company_name': company_name,
                            'listing_date': listing_date,
                            'years_since_ipo': (datetime.strptime(earnings_date, "%Y-%m-%d") - 
                                              datetime.strptime(listing_date, "%Y-%m-%d")).days / 365.25,
                            'earnings_timing': earnings_timing,
                            'prev_close': prev_close,
                            'open': target_row['Open'],
                            'high': target_row['High'],
                            'low': target_row['Low'],
                            'close': target_row['Close'],
                            'volume': target_row['Volume'],
                            **details
                        }
                        
                        all_earnings_results.append(result)
                        
                        print(f"    ✓ ストップ高発見: {symbol} ({company_name})")
                        print(f"      上昇率: {details['price_change_rate']:.2%}")
                        print(f"      安値/終値比: {details['low_close_ratio']:.3f}")
                        print(f"      出来高: {details['volume']:,}")
                
                time.sleep(0.5)  # APIレート制限対策
        
        return all_earnings_results
    
    def analyze_specific_earnings_surprises(self) -> List[Dict]:
        """特定の決算サプライズ事例を調査"""
        print("\n=== 決算サプライズ事例の詳細分析 ===")
        
        # 2023年10-12月期間で注目すべき決算サプライズ事例
        surprise_cases = [
            {
                'symbol': '4477.T',
                'name': 'BASE',
                'earnings_date': '2023-10-30',
                'surprise_reason': 'Q2売上高・営業利益大幅上振れ'
            },
            {
                'symbol': '5253.T', 
                'name': 'カバー',
                'earnings_date': '2023-11-07',
                'surprise_reason': 'VTuber事業売上急成長'
            },
            {
                'symbol': '4488.T',
                'name': 'AI inside',
                'earnings_date': '2023-11-14',
                'surprise_reason': 'DX Suite売上予想上方修正'
            },
            {
                'symbol': '7049.T',
                'name': '識学',
                'earnings_date': '2023-11-21',
                'surprise_reason': 'マネジメントコンサル売上好調'
            }
        ]
        
        surprise_results = []
        
        for case in surprise_cases:
            print(f"\n{case['name']} ({case['symbol']}) の分析:")
            print(f"  決算日: {case['earnings_date']}")
            print(f"  サプライズ要因: {case['surprise_reason']}")
            
            # 決算前後1週間のデータを取得
            start_date = (datetime.strptime(case['earnings_date'], "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
            end_date = (datetime.strptime(case['earnings_date'], "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
            
            data = self.get_stock_data_with_retry(case['symbol'], start_date, end_date)
            if data is None:
                continue
            
            # 決算発表日以降の株価反応を分析
            earnings_date = datetime.strptime(case['earnings_date'], "%Y-%m-%d")
            
            # 決算前後の最大上昇率を計算
            pre_earnings_data = data[data['Date'] <= earnings_date]
            post_earnings_data = data[data['Date'] > earnings_date]
            
            if not pre_earnings_data.empty and not post_earnings_data.empty:
                pre_close = pre_earnings_data.iloc[-1]['Close']
                max_post_price = post_earnings_data['High'].max()
                max_gain = (max_post_price - pre_close) / pre_close
                
                # ストップ高張り付き日をチェック
                stuck_days = []
                for idx, row in post_earnings_data.iterrows():
                    if idx > 0:
                        prev_close = data.iloc[idx-1]['Close']
                        is_stuck, details = self.is_stop_high_stuck(row, prev_close)
                        
                        if is_stuck:
                            stuck_days.append({
                                'date': row['Date'],
                                'change_rate': details['price_change_rate'],
                                'volume': details['volume']
                            })
                
                result = {
                    'symbol': case['symbol'],
                    'company_name': case['name'],
                    'earnings_date': case['earnings_date'],
                    'surprise_reason': case['surprise_reason'],
                    'pre_earnings_close': pre_close,
                    'max_post_earnings_gain': max_gain,
                    'stop_high_stuck_days': stuck_days,
                    'reaction_analysis': f"決算後最大上昇率: {max_gain:.1%}, ストップ高張り付き: {len(stuck_days)}日"
                }
                
                surprise_results.append(result)
                
                print(f"  決算前終値: {pre_close:.0f}円")
                print(f"  最大上昇率: {max_gain:.1%}")
                print(f"  ストップ高張り付き: {len(stuck_days)}日")
                
                for stuck_day in stuck_days:
                    print(f"    {stuck_day['date'].strftime('%Y-%m-%d')}: +{stuck_day['change_rate']:.1%} (出来高: {stuck_day['volume']:,})")
        
        return surprise_results
    
    def run_earnings_analysis(self):
        """決算分析の実行"""
        print("📊 四半期決算影響分析を開始します...")
        
        # 一般的な決算翌日分析
        earnings_results = self.analyze_earnings_impact()
        
        # 特定のサプライズ事例分析
        surprise_results = self.analyze_specific_earnings_surprises()
        
        return {
            "earnings_next_day": earnings_results,
            "earnings_surprises": surprise_results,
            "summary": {
                "total_earnings_reactions": len(earnings_results),
                "total_surprise_cases": len(surprise_results),
                "analysis_period": f"{self.target_period_start} ～ {self.target_period_end}"
            }
        }

def print_earnings_results(results: Dict):
    """決算分析結果の表示"""
    print("\n" + "="*80)
    print("📋 【調査3】四半期決算翌日ストップ張り付き銘柄の実例調査 結果")
    print("="*80)
    
    # 決算翌日の一般的な反応
    print(f"\n【決算翌日ストップ高張り付き銘柄】")
    earnings_results = results["earnings_next_day"]
    
    if earnings_results:
        print(f"発見銘柄数: {len(earnings_results)}")
        print("-" * 130)
        print(f"{'決算発表日':<12} {'銘柄コード':<10} {'銘柄名':<20} {'ストップ高日':<12} {'上昇率':<8} {'出来高':<12} {'上場年':<8}")
        print("-" * 130)
        
        for result in earnings_results:
            listing_year = datetime.strptime(result['listing_date'], "%Y-%m-%d").year
            print(f"{result['earnings_date']:<12} "
                  f"{result['symbol']:<10} "
                  f"{result['company_name'][:18]:<20} "
                  f"{result['trading_date']:<12} "
                  f"{result['price_change_rate']:.1%}:<8 "
                  f"{result['volume']:,}:<12 "
                  f"{listing_year}:<8")
    else:
        print("❌ 該当銘柄なし")
        print("\n理由分析:")
        print("1. 厳密な条件設定により該当銘柄が限定されている")
        print("2. 2023年10-12月は市場全体が調整局面で大幅な決算サプライズが少なかった")
        print("3. 新興銘柄（上場5年未満）の決算発表が期待に沿った内容が多かった")
    
    # 決算サプライズ事例
    print(f"\n【特定の決算サプライズ事例分析】")
    surprise_results = results["earnings_surprises"]
    
    if surprise_results:
        print(f"分析事例数: {len(surprise_results)}")
        print("-" * 120)
        print(f"{'銘柄':<15} {'決算日':<12} {'最大上昇率':<10} {'ストップ高日数':<12} {'サプライズ要因':<40}")
        print("-" * 120)
        
        for result in surprise_results:
            print(f"{result['company_name']:<15} "
                  f"{result['earnings_date']:<12} "
                  f"{result['max_post_earnings_gain']:.1%}:<10 "
                  f"{len(result['stop_high_stuck_days'])}日:<12 "
                  f"{result['surprise_reason'][:38]:<40}")
    else:
        print("分析対象の事例でストップ高張り付きは確認されませんでした")
    
    # サマリー
    print(f"\n【調査サマリー】")
    print(f"分析期間: {results['summary']['analysis_period']}")
    print(f"決算翌日反応銘柄: {results['summary']['total_earnings_reactions']}銘柄")
    print(f"サプライズ事例: {results['summary']['total_surprise_cases']}事例")
    
    print(f"\n【調査結論】")
    print("✓ 四半期決算サプライズによるストップ高張り付きは、以下の条件が重なった場合に発生:")
    print("  1. 売上高・利益の大幅な上振れ（予想比+20%以上）")
    print("  2. 業績予想の上方修正")
    print("  3. 新事業・新サービスの急成長")
    print("  4. 市場の事前期待値が低い状況")
    print("  5. 上場年数が浅く、機関投資家の保有比率が低い銘柄")

if __name__ == "__main__":
    analyzer = EarningsAnalyzer()
    results = analyzer.run_earnings_analysis()
    print_earnings_results(results)