"""
Vercel Functions用 実データ版 ロジックB強化版API
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 実データ用のサービスクラスを簡易実装
class SimpleEarningsAnalysisService:
    """
    Vercel Functions用の簡易決算分析サービス
    """
    
    @staticmethod
    def get_earnings_data(ticker: str):
        """
        簡易版決算分析（yfinance使用）
        """
        try:
            import yfinance as yf
            import pandas as pd
            
            # 日本株の場合は .T を付与
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            income_stmt = stock.income_stmt
            
            if income_stmt.empty:
                return None
            
            # 純利益の検索
            possible_net_income_names = [
                'Net Income',
                'Net Income Common Stockholders', 
                'Net Income From Continuing Operation Net Minority Interest'
            ]
            
            net_income_data = None
            for name in possible_net_income_names:
                if name in income_stmt.index:
                    net_income_data = income_stmt.loc[name]
                    break
            
            if net_income_data is None:
                return None
            
            # データを日付順にソート（新しい順）
            net_income_sorted = net_income_data.dropna().sort_index(ascending=False)
            
            if len(net_income_sorted) < 2:
                return None
            
            # 最新年度と前年度の比較
            latest_income = float(net_income_sorted.iloc[0])
            previous_income = float(net_income_sorted.iloc[1])
            
            # 黒字転換の判定
            is_black_ink_conversion = previous_income <= 0 and latest_income > 0
            
            # 成長率計算
            growth_rate = None
            if previous_income != 0:
                growth_rate = ((latest_income - previous_income) / abs(previous_income)) * 100
            
            # 利益変動の説明文生成
            latest_oku = latest_income / 100_000_000  # 億円換算
            previous_oku = previous_income / 100_000_000
            
            if previous_income <= 0 and latest_income > 0:
                profit_change = f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円(黒字転換)"
            elif previous_income > 0 and latest_income <= 0:
                profit_change = f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円(赤字転落)"
            elif previous_income > 0 and latest_income > 0:
                change_oku = latest_oku - previous_oku
                profit_change = f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({change_oku:+.0f}億円)"
            else:
                change_oku = latest_oku - previous_oku
                profit_change = f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({change_oku:+.0f}億円改善)" if change_oku > 0 else f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({abs(change_oku):.0f}億円悪化)"
            
            return {
                "code": ticker.replace('.T', ''),
                "name": info.get('longName', info.get('shortName', 'Unknown')),
                "latest_income": latest_income,
                "previous_income": previous_income,
                "is_black_ink_conversion": is_black_ink_conversion,
                "growth_rate": growth_rate,
                "profit_change": profit_change,
                "latest_year": net_income_sorted.index[0].strftime('%Y-%m-%d'),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing earnings for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def get_moving_average_data(ticker: str):
        """
        移動平均線データ取得
        """
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if hist.empty or len(hist) < 25:
                return None
            
            # 5日、25日移動平均を計算
            hist['MA5'] = hist['Close'].rolling(window=5).mean()
            hist['MA25'] = hist['Close'].rolling(window=25).mean()
            
            # 最新のデータ
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            # 5日線上抜け判定
            current_price = latest['Close']
            ma5_current = latest['MA5']
            ma5_previous = previous['MA5']
            
            # 前日は5日線下にいて、今日は5日線上にいる
            is_ma5_breakout = (previous['Close'] <= ma5_previous and current_price > ma5_current)
            
            # 出来高急増判定
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1.0
            
            return {
                "current_price": float(current_price),
                "ma5": float(ma5_current) if not pd.isna(ma5_current) else None,
                "ma25": float(latest['MA25']) if not pd.isna(latest['MA25']) else None,
                "is_ma5_breakout": is_ma5_breakout,
                "volume_ratio": float(volume_ratio),
                "ma_break_date": datetime.now().strftime("%Y-%m-%d") if is_ma5_breakout else "該当なし"
            }
            
        except Exception as e:
            return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            earnings_service = SimpleEarningsAnalysisService()
            
            # 主要銘柄でロジックBをテスト
            test_tickers = ["7203", "6501", "4755", "9984", "8306", "6758", "9434", "4063", "6954", "7974"]
            
            results = []
            
            for ticker in test_tickers:
                # 決算データを取得
                earnings_data = earnings_service.get_earnings_data(ticker)
                if not earnings_data:
                    continue
                
                # 移動平均線データを取得
                ma_data = earnings_service.get_moving_average_data(ticker)
                if not ma_data:
                    continue
                
                # ロジックB判定（黒字転換 + その他改善）
                score = 0
                is_candidate = False
                
                # 黒字転換の場合は最高スコア
                if earnings_data['is_black_ink_conversion']:
                    score += 80
                    is_candidate = True
                
                # 大幅な利益改善
                growth_rate = earnings_data.get('growth_rate')
                if growth_rate is not None:
                    if growth_rate > 100:  # 100%以上成長
                        score += 60
                        is_candidate = True
                    elif growth_rate > 50:  # 50%以上成長
                        score += 40
                        is_candidate = True
                    elif growth_rate > 20:  # 20%以上成長
                        score += 20
                        is_candidate = True
                
                # 移動平均線上抜け
                if ma_data['is_ma5_breakout']:
                    score += 20
                
                # 出来高急増
                if ma_data['volume_ratio'] >= 2.0:
                    score += 15
                elif ma_data['volume_ratio'] >= 1.5:
                    score += 10
                
                if is_candidate and score >= 30:
                    # 詳細根拠データ作成
                    logic_b_details = {
                        "score": score,
                        "profitChange": earnings_data['profit_change'],
                        "blackInkDate": earnings_data['latest_year'],
                        "maBreakDate": ma_data['ma_break_date'],
                        "volumeRatio": ma_data['volume_ratio'],
                        "isBlackInkConversion": earnings_data['is_black_ink_conversion'],
                        "growthRate": growth_rate,
                        "realTimePrice": ma_data['current_price'],
                        "ma5": ma_data['ma5'],
                        "ma25": ma_data['ma25']
                    }
                    
                    result = {
                        "code": earnings_data['code'],
                        "name": earnings_data['name'],
                        "score": score,
                        "logicB": logic_b_details
                    }
                    results.append(result)
            
            # スコア順でソート
            results.sort(key=lambda x: x["score"], reverse=True)
            
            response_data = {
                "success": True,
                "results": results[:5],  # 上位5銘柄
                "scan_time": datetime.now().isoformat(),
                "total_scanned": len(test_tickers),
                "matches_found": len(results),
                "data_source": "Yahoo Finance (Real-time)",
                "notice": "実データ版ロジックB - 決算データ・移動平均線・出来高分析"
            }
            
            # CORS ヘッダーを設定
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # JSONレスポンスを送信
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            # エラーレスポンス
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "success": False,
                "error": f"実データ版ロジックBスキャンに失敗しました: {str(e)}",
                "fallback": "モック版を使用してください"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # プリフライトリクエストへの対応
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()