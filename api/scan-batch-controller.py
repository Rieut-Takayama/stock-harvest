"""
バッチ制御API - Vercel制限回避版
全銘柄を複数回に分割してスキャン
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BatchController:
    """バッチスキャン制御"""
    
    def __init__(self):
        self.batch_size = 500  # 1回あたり500銘柄
        self.total_stocks = 9000
        self.total_batches = 18  # 9000 ÷ 500 = 18回
        
    def get_batch_range(self, batch_number: int):
        """バッチ番号から銘柄範囲を取得"""
        start = 1000 + (batch_number * self.batch_size)
        end = min(start + self.batch_size, 10000)
        return start, end
    
    def generate_batch_tickers(self, batch_number: int):
        """指定バッチの銘柄リスト生成"""
        start, end = self.get_batch_range(batch_number)
        tickers = []
        for i in range(start, end):
            tickers.append(str(i).zfill(4))
        return tickers

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # URLパラメータ解析
            from urllib.parse import urlparse, parse_qs
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            batch_number = int(query_params.get('batch', [0])[0])
            logic_type = query_params.get('logic', ['A'])[0]
            
            controller = BatchController()
            
            if batch_number >= controller.total_batches:
                # 全バッチ完了
                response_data = {
                    "success": True,
                    "message": "全バッチスキャン完了",
                    "total_batches": controller.total_batches,
                    "completed_batches": controller.total_batches,
                    "progress": 100.0,
                    "next_action": "aggregate_results"
                }
            else:
                # バッチ情報提供
                start, end = controller.get_batch_range(batch_number)
                batch_tickers = controller.generate_batch_tickers(batch_number)
                
                response_data = {
                    "success": True,
                    "batch_info": {
                        "batch_number": batch_number,
                        "total_batches": controller.total_batches,
                        "range": f"{start}-{end-1}",
                        "stock_count": len(batch_tickers),
                        "tickers": batch_tickers[:10],  # サンプル表示
                        "progress": round((batch_number / controller.total_batches) * 100, 1)
                    },
                    "api_endpoints": {
                        "logic_a": f"/api/scan-batch-logic-a?batch={batch_number}",
                        "logic_b": f"/api/scan-batch-logic-b?batch={batch_number}"
                    },
                    "instructions": {
                        "step1": f"上記エンドポイントを呼び出してバッチ{batch_number}をスキャン",
                        "step2": f"完了後、batch={batch_number+1}で次のバッチを実行",
                        "step3": "全18バッチ完了で全銘柄スキャン終了"
                    },
                    "timing": {
                        "estimated_time_per_batch": "30秒",
                        "total_estimated_time": "9分",
                        "vercel_limit_safe": True
                    }
                }
            
            # CORS対応
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "success": False,
                "error": f"バッチ制御エラー: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()