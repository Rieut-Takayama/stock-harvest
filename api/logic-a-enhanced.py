"""
Vercel Functions用 ロジックA強化版API
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import random
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # モックデータ
            MOCK_STOCKS = [
                {
                    "code": "7203",
                    "name": "トヨタ自動車", 
                    "price": 3135,
                    "listing_date": "2022-04-15",
                    "earnings_date": "2024-11-20",
                    "profit_change": "前年-120億→今期+340億"
                },
                {
                    "code": "6501",
                    "name": "日立製作所",
                    "price": 4200,
                    "listing_date": "2021-10-01", 
                    "earnings_date": "2024-11-19",
                    "profit_change": "既に黒字継続中"
                },
                {
                    "code": "4755",
                    "name": "楽天グループ",
                    "price": 1890,
                    "listing_date": "2023-03-10",
                    "earnings_date": "2024-11-21", 
                    "profit_change": "前年-85億→今期+15億"
                }
            ]
            
            results = []
            
            # ロジックA該当銘柄を検出
            for stock in MOCK_STOCKS:
                # 上場2年半以内の条件をチェック
                listing_date = datetime.strptime(stock["listing_date"], "%Y-%m-%d")
                years_since_listing = (datetime.now() - listing_date).days / 365.25
                
                if years_since_listing <= 5.0:  # 上場5年以内
                    # ロジックAスコア計算
                    score = 50
                    if years_since_listing <= 2.5:
                        score += 10  # 上場2.5年以内ボーナス
                    
                    # 詳細根拠データ作成
                    prev_price = stock["price"] - int(stock["price"] * 0.1)
                    stop_high_price = stock["price"]
                    
                    logic_a_details = {
                        "score": score,
                        "listingDate": stock["listing_date"],
                        "earningsDate": stock["earnings_date"],
                        "stopHighDate": (datetime.strptime(stock["earnings_date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
                        "prevPrice": prev_price,
                        "stopHighPrice": stop_high_price,
                        "isFirstTime": True,
                        "noConsecutive": True,
                        "noLongTail": True
                    }
                    
                    result = {
                        "code": stock["code"],
                        "name": stock["name"],
                        "score": score,
                        "logicA": logic_a_details
                    }
                    results.append(result)
            
            # スコア順でソート
            results.sort(key=lambda x: x["score"], reverse=True)
            
            response_data = {
                "success": True,
                "results": results,
                "scan_time": datetime.now().isoformat(),
                "total_scanned": 3800,
                "matches_found": len(results)
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
                "error": f"ロジックAスキャンに失敗しました: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # プリフライトリクエストへの対応
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()