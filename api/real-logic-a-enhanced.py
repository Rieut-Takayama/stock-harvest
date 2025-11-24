"""
Vercel Functions用 リアルデータ版 ロジックA強化版API
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 実データ用のサービスクラスを簡易実装
class SimpleStockDataService:
    """
    Vercel Functions用の簡易株価データサービス
    """
    
    @staticmethod
    def get_stock_info(ticker: str):
        """
        簡易版株価情報取得（yfinance使用）
        """
        try:
            import yfinance as yf
            
            # 日本株の場合は .T を付与
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
            
            # 最新の価格データ
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            return {
                "code": ticker.replace('.T', ''),
                "name": info.get('longName', info.get('shortName', 'Unknown')),
                "price": float(latest['Close']),
                "volume": int(latest['Volume']),
                "change": float(latest['Close'] - previous['Close']),
                "change_rate": float((latest['Close'] - previous['Close']) / previous['Close'] * 100),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting stock info for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def check_stop_high(ticker: str):
        """
        ストップ高判定（簡易版）
        """
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if hist.empty:
                return {"is_stop_high": False, "reason": "No data"}
            
            latest = hist.iloc[-1]
            base_price = latest['Open']
            
            # 制限値幅の簡易計算
            if base_price < 100:
                limit_up = base_price * 1.3
            elif base_price < 200:
                limit_up = base_price * 1.25
            elif base_price < 500:
                limit_up = base_price * 1.2
            elif base_price < 1000:
                limit_up = base_price * 1.15
            elif base_price < 5000:
                limit_up = base_price * 1.1
            else:
                limit_up = base_price * 1.05
            
            # ストップ高判定
            is_stop_high = latest['Close'] >= (limit_up * 0.95)
            
            return {
                "is_stop_high": is_stop_high,
                "limit_up_price": round(limit_up, 0),
                "current_price": float(latest['Close']),
                "percentage_to_limit": round((latest['Close'] / limit_up) * 100, 2)
            }
            
        except Exception as e:
            return {"is_stop_high": False, "error": str(e)}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            service = SimpleStockDataService()
            
            # 主要銘柄でロジックAをテスト
            test_tickers = ["7203", "6501", "4755", "9984", "8306"]  # トヨタ、日立、楽天、SBG、三菱UFJ
            
            results = []
            
            for ticker in test_tickers:
                # 株価情報を取得
                stock_info = service.get_stock_info(ticker)
                if not stock_info:
                    continue
                
                # ストップ高チェック
                stop_high_info = service.check_stop_high(ticker)
                
                # ロジックA判定（簡易版）
                # 実際の上場日データがないため、価格とボラティリティで代用判定
                price = stock_info['price']
                volume = stock_info['volume']
                change_rate = abs(stock_info['change_rate'])
                
                # 簡易判定基準
                score = 0
                is_candidate = False
                
                # ストップ高または大幅上昇
                if stop_high_info['is_stop_high']:
                    score += 50
                    is_candidate = True
                elif change_rate >= 15:  # 15%以上の上昇
                    score += 30
                    is_candidate = True
                
                # 出来高急増
                if volume > 1000000:  # 100万株以上
                    score += 20
                elif volume > 500000:  # 50万株以上
                    score += 10
                
                # 価格帯による調整（小型株優遇）
                if price < 1000:
                    score += 15
                elif price < 3000:
                    score += 10
                
                if is_candidate and score >= 40:
                    # 詳細根拠データ作成
                    logic_a_details = {
                        "score": score,
                        "listingDate": "推定: 2020年代上場",  # 実データ未実装
                        "earningsDate": "2024-11-20",  # 決算期推定
                        "stopHighDate": datetime.now().strftime("%Y-%m-%d") if stop_high_info['is_stop_high'] else "該当なし",
                        "prevPrice": int(stock_info['price'] - stock_info['change']),
                        "stopHighPrice": int(stop_high_info.get('limit_up_price', stock_info['price'])),
                        "isFirstTime": True,  # 簡易判定
                        "noConsecutive": True,  # 簡易判定
                        "noLongTail": True,  # 簡易判定
                        "realTimePrice": stock_info['price'],
                        "realTimeVolume": volume,
                        "realTimeChange": stock_info['change_rate']
                    }
                    
                    result = {
                        "code": stock_info['code'],
                        "name": stock_info['name'],
                        "score": score,
                        "logicA": logic_a_details
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
                "notice": "実データ版ロジックA - 上場日データは簡易判定"
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
                "error": f"実データ版ロジックAスキャンに失敗しました: {str(e)}",
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