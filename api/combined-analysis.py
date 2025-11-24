"""
Vercel Functions用 総合判断API
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
            
            # ロジックA結果を生成
            logic_a_results = {}
            for stock in MOCK_STOCKS:
                listing_date = datetime.strptime(stock["listing_date"], "%Y-%m-%d")
                years_since_listing = (datetime.now() - listing_date).days / 365.25
                
                if years_since_listing <= 5.0:
                    score = 50
                    if years_since_listing <= 2.5:
                        score += 10
                    
                    prev_price = stock["price"] - int(stock["price"] * 0.1)
                    
                    logic_a_results[stock["code"]] = {
                        "code": stock["code"],
                        "name": stock["name"],
                        "score": score,
                        "logicA": {
                            "score": score,
                            "listingDate": stock["listing_date"],
                            "earningsDate": stock["earnings_date"],
                            "stopHighDate": (datetime.strptime(stock["earnings_date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
                            "prevPrice": prev_price,
                            "stopHighPrice": stock["price"],
                            "isFirstTime": True,
                            "noConsecutive": True,
                            "noLongTail": True
                        }
                    }
            
            # ロジックB結果を生成
            logic_b_results = {}
            for stock in MOCK_STOCKS:
                if "前年" in stock["profit_change"] and "今期" in stock["profit_change"]:
                    score = 50
                    volume_ratio = round(random.uniform(1.5, 3.0), 1)
                    if volume_ratio >= 2.0:
                        score += 10
                    
                    ma_break_date = (datetime.strptime(stock["earnings_date"], "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
                    
                    logic_b_results[stock["code"]] = {
                        "code": stock["code"],
                        "name": stock["name"],
                        "score": score,
                        "logicB": {
                            "score": score,
                            "profitChange": stock["profit_change"],
                            "blackInkDate": stock["earnings_date"],
                            "maBreakDate": ma_break_date,
                            "volumeRatio": volume_ratio
                        }
                    }
            
            # 総合判断結果を生成
            results = []
            all_codes = set(logic_a_results.keys()) | set(logic_b_results.keys())
            
            for code in all_codes:
                logic_a = logic_a_results.get(code)
                logic_b = logic_b_results.get(code)
                
                total_score = 0
                result = {
                    "code": code,
                    "name": logic_a["name"] if logic_a else logic_b["name"],
                    "score": 0
                }
                
                if logic_a:
                    result["logicA"] = logic_a["logicA"]
                    total_score += logic_a["score"]
                
                if logic_b:
                    result["logicB"] = logic_b["logicB"]
                    total_score += logic_b["score"]
                
                # 両方該当の場合はボーナス
                if logic_a and logic_b:
                    total_score += 20  # 両方該当ボーナス
                
                result["score"] = total_score
                results.append(result)
            
            # 総合スコア順でソート
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
                "error": f"総合判断スキャンに失敗しました: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # プリフライトリクエストへの対応
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()