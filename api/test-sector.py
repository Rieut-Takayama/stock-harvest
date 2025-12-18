"""
セクター別API動作テスト
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # テスト用の簡易結果
            test_results = [
                {
                    "code": "7203",
                    "name": "トヨタ自動車",
                    "score": 85,
                    "bonuses": ["テストボーナス", "高スコア"],
                    "sector": "テスト",
                    "priority_level": "優先",
                    "analysis_summary": {
                        "logic_a_score": 45,
                        "logic_b_score": 40,
                        "total_conditions_met": 2
                    },
                    "logicA": {
                        "score": 45,
                        "listingDate": "テスト上場",
                        "earningsDate": "2024-11-20",
                        "stopHighDate": "2024-11-25",
                        "prevPrice": 2800,
                        "stopHighPrice": 3100,
                        "isFirstTime": True,
                        "noConsecutive": True,
                        "noLongTail": True
                    }
                },
                {
                    "code": "6501",
                    "name": "日立製作所",
                    "score": 70,
                    "bonuses": ["テストボーナス"],
                    "sector": "テスト",
                    "priority_level": "注目",
                    "analysis_summary": {
                        "logic_a_score": 35,
                        "logic_b_score": 35,
                        "total_conditions_met": 1
                    },
                    "logicB": {
                        "score": 35,
                        "profitChange": "前年100億円→今期150億円(テスト成長)",
                        "blackInkDate": "2024-11-20",
                        "maBreakDate": "2024-11-25",
                        "volumeRatio": 1.5
                    }
                }
            ]
            
            response_data = {
                "success": True,
                "results": test_results,
                "scan_time": datetime.now().isoformat(),
                "sector": "テストセクター",
                "total_scanned": 10,
                "matches_found": len(test_results),
                "data_source": "Test Data",
                "analysis_method": "テスト用簡易分析",
                "notice": "API動作確認用テストデータ",
                "coverage": "テスト用データ"
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
                "error": f"テストAPIエラー: {str(e)}",
                "fallback": "テスト失敗"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()