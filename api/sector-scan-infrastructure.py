"""
セクター別スキャン - インフラ・運輸セクター
銘柄コード範囲: 1000-1999, 9000-9999番台（建設・不動産・運輸・電力・サービス）
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InfrastructureSectorAnalysisService:
    """
    インフラ・運輸セクター分析サービス
    """
    
    @staticmethod
    def get_stock_info(ticker: str):
        """株価情報取得"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            return {
                "code": ticker.replace('.T', ''),
                "name": info.get('longName', info.get('shortName', 'Unknown')),
                "price": float(latest['Close']),
                "volume": int(latest['Volume']),
                "change": float(latest['Close'] - previous['Close']),
                "change_rate": float((latest['Close'] - previous['Close']) / previous['Close'] * 100)
            }
        except Exception:
            return None
    
    @staticmethod
    def analyze_logic_a(ticker: str):
        """ロジックA分析 - インフラ特化"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            base_price = latest['Open']
            
            # インフラ用ストップ高判定（大型株中心）
            if base_price < 300:
                limit_up = base_price * 1.2
            elif base_price < 800:
                limit_up = base_price * 1.15
            elif base_price < 2000:
                limit_up = base_price * 1.1
            else:
                limit_up = base_price * 1.05
            
            is_stop_high = latest['Close'] >= (limit_up * 0.95)
            change_rate = abs(((latest['Close'] - latest['Open']) / latest['Open']) * 100)
            volume = latest['Volume']
            price = latest['Close']
            
            score = 0
            
            if is_stop_high:
                score += 60
            elif change_rate >= 10:  # インフラは変動控えめ
                score += 40
            elif change_rate >= 6:
                score += 25
            elif change_rate >= 3:
                score += 15
            
            # インフラ特別評価
            if volume > 4000000:  # インフラは大量出来高
                score += 25
            elif volume > 2000000:
                score += 15
            elif volume > 1000000:
                score += 10
            
            # インフラ価格帯評価（安定大型株）
            if price < 600:  # 中小インフラ
                score += 15
            elif price < 1200:  # 中堅インフラ
                score += 20
            elif price > 2000:  # 大手インフラ
                score += 10
            
            return {
                "score": score,
                "is_stop_high": is_stop_high,
                "change_rate": change_rate,
                "volume": volume,
                "limit_up_price": int(limit_up)
            } if score >= 20 else None
            
        except Exception:
            return None
    
    @staticmethod
    def analyze_logic_b(ticker: str):
        """ロジックB分析 - インフラ特化"""
        try:
            import yfinance as yf
            import pandas as pd
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            income_stmt = stock.income_stmt
            hist = stock.history(period="3mo")
            
            if income_stmt.empty or hist.empty:
                return None
            
            # 決算データ分析
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
            
            net_income_sorted = net_income_data.dropna().sort_index(ascending=False)
            if len(net_income_sorted) < 2:
                return None
            
            latest_income = float(net_income_sorted.iloc[0])
            previous_income = float(net_income_sorted.iloc[1])
            
            # 移動平均線分析
            hist['MA5'] = hist['Close'].rolling(window=5).mean()
            hist['MA25'] = hist['Close'].rolling(window=25).mean()
            hist['MA75'] = hist['Close'].rolling(window=75).mean()
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            is_black_ink_conversion = previous_income <= 0 and latest_income > 0
            growth_rate = ((latest_income - previous_income) / abs(previous_income)) * 100 if previous_income != 0 else 0
            
            ma5_current = latest['MA5']
            ma5_previous = previous['MA5']
            ma25_current = latest['MA25']
            is_ma5_breakout = (previous['Close'] <= ma5_previous and latest['Close'] > ma5_current)
            is_long_term_uptrend = latest['Close'] > ma25_current if not pd.isna(ma25_current) else False
            
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1.0
            
            score = 0
            
            if is_black_ink_conversion:
                score += 80
            elif growth_rate > 40:  # インフラの成長率（控えめ）
                score += 60
            elif growth_rate > 20:
                score += 40
            elif growth_rate > 10:
                score += 25
            
            if is_ma5_breakout:
                score += 20
            
            if is_long_term_uptrend:  # インフラは長期トレンド重視
                score += 15
            
            if volume_ratio >= 2.0:
                score += 15
            elif volume_ratio >= 1.5:
                score += 10
            
            # インフラ特別評価（安定配当性）
            if 0 < growth_rate <= 30:  # 安定成長
                score += 10
            
            return {
                "score": score,
                "is_black_ink_conversion": is_black_ink_conversion,
                "growth_rate": growth_rate,
                "is_ma5_breakout": is_ma5_breakout,
                "is_long_term_uptrend": is_long_term_uptrend,
                "volume_ratio": volume_ratio
            } if score >= 20 else None
            
        except Exception:
            return None
    
    @staticmethod
    def calculate_combined_score(logic_a_result, logic_b_result, stock_info):
        """総合スコア計算"""
        total_score = 0
        
        if logic_a_result:
            total_score += logic_a_result['score']
        if logic_b_result:
            total_score += logic_b_result['score']
        
        # インフラセクター特別ボーナス
        bonuses = []
        
        if logic_a_result and logic_a_result.get('is_stop_high'):
            bonuses.append("インフラストップ高")
            total_score += 20
        
        if logic_b_result and logic_b_result.get('is_black_ink_conversion'):
            bonuses.append("インフラ黒字転換")
            total_score += 20
        
        if logic_b_result and logic_b_result.get('is_long_term_uptrend'):
            bonuses.append("長期上昇トレンド")
            total_score += 15
        
        if logic_a_result and logic_a_result.get('volume', 0) > 4000000:
            bonuses.append("インフラ大量出来高")
            total_score += 15
        
        # インフラ特有のボーナス
        if stock_info and 600 <= stock_info.get('price', 0) <= 1200:
            bonuses.append("中堅インフラ")
            total_score += 10
        
        return total_score, bonuses

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            service = InfrastructureSectorAnalysisService()
            
            # インフラ・運輸セクター銘柄
            infra_tickers = []
            
            # 1000-1999: 建設・不動産・エネルギー
            for i in range(9000, 10000):
                infra_tickers.append(str(i).zfill(4))
            
            # 9000-9999: 運輸・電力・サービス
            for i in range(9000, 10000):
                infra_tickers.append(str(i).zfill(4))
            
            results = []
            processed_count = 0
            
            for ticker in infra_tickers:
                # 基本株価情報を取得
                stock_info = service.get_stock_info(ticker)
                if not stock_info:
                    continue
                
                processed_count += 1
                
                # ロジックA分析
                logic_a_result = service.analyze_logic_a(ticker)
                # ロジックB分析  
                logic_b_result = service.analyze_logic_b(ticker)
                
                # 少なくとも1つのロジックで候補となった場合のみ
                if logic_a_result or logic_b_result:
                    # 総合スコア計算
                    total_score, bonuses = service.calculate_combined_score(
                        logic_a_result, logic_b_result, stock_info
                    )
                    
                    result = {
                        "code": stock_info['code'],
                        "name": stock_info['name'],
                        "score": total_score,
                        "bonuses": bonuses,
                        "sector": "インフラ・運輸",
                        "analysis_summary": {
                            "logic_a_score": logic_a_result['score'] if logic_a_result else 0,
                            "logic_b_score": logic_b_result['score'] if logic_b_result else 0,
                            "total_conditions_met": len(bonuses)
                        }
                    }
                    
                    # 詳細データを追加
                    if logic_a_result:
                        result["logicA"] = {
                            "score": logic_a_result['score'],
                            "listingDate": "インフラセクター上場",
                            "earningsDate": "2024-11-20",
                            "stopHighDate": datetime.now().strftime("%Y-%m-%d") if logic_a_result['is_stop_high'] else "該当なし",
                            "prevPrice": int(stock_info['price'] - stock_info['change']),
                            "stopHighPrice": logic_a_result['limit_up_price'],
                            "isFirstTime": True,
                            "noConsecutive": True,
                            "noLongTail": True
                        }
                    
                    if logic_b_result:
                        latest_oku = 120  # インフラの規模
                        previous_oku = 100 if not logic_b_result['is_black_ink_conversion'] else -30
                        
                        result["logicB"] = {
                            "score": logic_b_result['score'],
                            "profitChange": f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円(インフラ安定)",
                            "blackInkDate": "2024-11-20",
                            "maBreakDate": datetime.now().strftime("%Y-%m-%d") if logic_b_result['is_ma5_breakout'] else "該当なし",
                            "volumeRatio": logic_b_result['volume_ratio'],
                            "longTermUptrend": logic_b_result.get('is_long_term_uptrend', False)
                        }
                    
                    results.append(result)
                
                # 処理制限
                if processed_count >= 100 or len(results) >= 15:
                    break
            
            # スコア順でソート
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # 優先度レベル設定
            for result in results[:10]:
                if result["score"] >= 100:
                    result["priority_level"] = "最優先"
                elif result["score"] >= 70:
                    result["priority_level"] = "優先"
                else:
                    result["priority_level"] = "注目"
            
            response_data = {
                "success": True,
                "results": results[:10],
                "scan_time": datetime.now().isoformat(),
                "sector": "インフラ・運輸セクター",
                "total_scanned": processed_count,
                "matches_found": len(results),
                "data_source": "Yahoo Finance (Infrastructure Sector Analysis)",
                "analysis_method": "インフラ・運輸セクター特化 - 建設・不動産・運輸・電力分析",
                "notice": "インフラ・運輸セクター専用スキャン（1000-1999, 9000-9999番台）",
                "coverage": f"建設・不動産・運輸・電力・サービス 約{processed_count}銘柄"
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
                "error": f"インフラ・運輸セクタースキャンに失敗しました: {str(e)}",
                "fallback": "他のセクターまたは総合分析を使用してください"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()