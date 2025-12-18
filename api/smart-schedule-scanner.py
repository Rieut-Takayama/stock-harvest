"""
決算時期特化型スキャンAPI
ロジックホルダー指定の時期のみ全銘柄スキャンを実行
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SmartScheduleScanner:
    """決算時期特化型スキャン制御"""
    
    def __init__(self):
        self.target_periods = {
            "mid_month": {"start": 8, "end": 17},  # 毎月中旬
            "end_month": {"start": 28, "end": 31}  # 毎月下旬
        }
    
    def is_target_period(self):
        """現在が対象期間かどうか判定"""
        today = datetime.now()
        day = today.day
        
        # 中旬期間チェック
        if self.target_periods["mid_month"]["start"] <= day <= self.target_periods["mid_month"]["end"]:
            return True, "mid_month", "決算発表集中期間（中旬）"
        
        # 下旬期間チェック（月末日を考慮）
        if day >= self.target_periods["end_month"]["start"]:
            return True, "end_month", "決算発表集中期間（下旬）"
        
        return False, None, "決算発表期間外"
    
    def get_next_target_date(self):
        """次の対象期間開始日を取得"""
        today = datetime.now()
        day = today.day
        month = today.month
        year = today.year
        
        # 今月中旬がまだの場合
        if day < 8:
            return f"{year}-{month:02d}-08", "中旬期間"
        # 今月下旬がまだの場合
        elif day < 28:
            return f"{year}-{month:02d}-28", "下旬期間"
        # 来月中旬
        else:
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            return f"{next_year}-{next_month:02d}-08", "来月中旬期間"
    
    def calculate_api_efficiency(self):
        """API効率の計算"""
        # 年間対象日数: 12ヶ月 × (10日 + 4日) = 168日
        total_target_days = 168
        total_days_year = 365
        
        # 効率化率
        efficiency_rate = 1 - (total_target_days / total_days_year)
        
        # 月間スキャン回数（対象期間のみ）
        monthly_target_days = 14  # 平均
        
        return {
            "efficiency_rate": round(efficiency_rate * 100, 1),
            "annual_target_days": total_target_days,
            "monthly_avg_days": monthly_target_days,
            "api_savings": f"年間{round(efficiency_rate * 100, 1)}%のAPI節約"
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            scanner = SmartScheduleScanner()
            
            # 現在の状況チェック
            is_target, period_type, period_name = scanner.is_target_period()
            next_date, next_period = scanner.get_next_target_date()
            efficiency = scanner.calculate_api_efficiency()
            
            if is_target:
                # 対象期間内：全銘柄スキャン推奨
                response_data = {
                    "success": True,
                    "scan_recommended": True,
                    "current_status": {
                        "period": period_name,
                        "period_type": period_type,
                        "today": datetime.now().strftime("%Y-%m-%d"),
                        "message": "🎯 決算発表集中期間です。全銘柄スキャンを推奨します。"
                    },
                    "scan_actions": {
                        "logic_a": "/api/real-logic-a-enhanced",
                        "logic_b": "/api/real-logic-b-enhanced",
                        "batch_controller": "/api/scan-batch-controller",
                        "recommended_frequency": "1日1回のスキャン推奨"
                    },
                    "efficiency_info": efficiency,
                    "business_logic": {
                        "rationale": "決算発表後の翌日ストップ高や黒字転換銘柄が出現する可能性が最も高い期間",
                        "expected_detection": "通常期間の5-10倍の候補銘柄検出が期待される",
                        "api_value": "限られたAPI枠を最も効果的に活用"
                    }
                }
            else:
                # 対象期間外：スキャン非推奨
                response_data = {
                    "success": True,
                    "scan_recommended": False,
                    "current_status": {
                        "period": period_name,
                        "today": datetime.now().strftime("%Y-%m-%d"),
                        "message": "📅 決算発表期間外です。API温存のためスキャン休止を推奨します。"
                    },
                    "next_target": {
                        "date": next_date,
                        "period": next_period,
                        "days_until": (datetime.strptime(next_date, "%Y-%m-%d") - datetime.now()).days
                    },
                    "efficiency_info": efficiency,
                    "alternative_actions": {
                        "portfolio_review": "既存ポートフォリオの見直し",
                        "market_research": "業界動向・企業分析",
                        "strategy_planning": "次回決算期間の戦略立案"
                    },
                    "emergency_scan": {
                        "available": True,
                        "note": "特別な市況変化時のみ手動実行",
                        "endpoints": {
                            "logic_a": "/api/real-logic-a-enhanced",
                            "logic_b": "/api/real-logic-b-enhanced"
                        }
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
                "error": f"スマートスケジュールエラー: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()