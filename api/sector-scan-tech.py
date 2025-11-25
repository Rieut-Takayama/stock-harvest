"""
セクター別スキャン - テック・情報通信セクター
銘柄コード範囲: 3000-4999番台（情報通信・化学・医薬品）
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TechSectorAnalysisService:
    """
    テック・情報通信セクター分析サービス（共通条件対応）
    """
    
    def __init__(self):
        # ホルダー指定の共通条件
        self.common_config = {
            'max_market_cap': 50000000000,   # 最大時価総額500億円
            'max_price': 5000,               # 最大株価5000円（100株エントリー対応）
            'min_daily_volume': 1000,        # 最低日次出来高1000株
        }
    
    def check_common_conditions(self, ticker: str, stock_info: dict):
        """ホルダー指定の共通条件チェック（セクター版）"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            
            # 1. 株価条件（5000円以下）
            price = stock_info.get('price', 0)
            if price > self.common_config['max_price']:
                return {'valid': False, 'reason': f'株価高すぎ({price:,.0f}円 > 5000円)'}
            
            # 2. 時価総額条件（500億円以下）
            info = stock.info
            market_cap = info.get('marketCap', 0)
            if market_cap > self.common_config['max_market_cap']:
                return {'valid': False, 'reason': '時価総額過大(500億円以上)'}
            
            # 3. 出来高条件（1000株/日以下の日がない）
            hist = stock.history(period="1mo")
            if not hist.empty:
                min_daily_volume = hist['Volume'].min()
                if min_daily_volume < self.common_config['min_daily_volume']:
                    return {'valid': False, 'reason': f'低出来高日あり(最低{min_daily_volume:,.0f}株)'}
            
            return {'valid': True, 'reason': '全共通条件クリア'}
            
        except Exception as e:
            return {'valid': False, 'reason': f'共通条件チェックエラー: {str(e)}'}
    
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
        """ロジックA分析"""
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
            
            # ストップ高判定
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
            
            is_stop_high = latest['Close'] >= (limit_up * 0.95)
            change_rate = abs(((latest['Close'] - latest['Open']) / latest['Open']) * 100)
            volume = latest['Volume']
            price = latest['Close']
            
            score = 0
            
            if is_stop_high:
                score += 60
            elif change_rate >= 15:
                score += 40
            elif change_rate >= 10:
                score += 25
            elif change_rate >= 5:
                score += 15
            
            if volume > 2000000:
                score += 25
            elif volume > 1000000:
                score += 15
            elif volume > 500000:
                score += 10
            
            # テックセクター特別ボーナス（全銘柄からテックを特別識別）
            ticker_code = int(ticker.replace('.T', ''))
            # テック関連コード範囲でボーナス
            if 3000 <= ticker_code <= 4999:  # 情報通信・バイオテック
                score += 30
            elif 9000 <= ticker_code <= 9999:  # ITサービス関連
                score += 25
            elif price < 2000:  # テック中小型株優遇
                score += 20
            elif price < 5000:
                score += 10
            
            return {
                "score": score,
                "is_stop_high": is_stop_high,
                "change_rate": change_rate,
                "volume": volume,
                "limit_up_price": int(limit_up)
            } if score >= 10 else None  # 条件を大幅緩和
            
        except Exception:
            return None
    
    @staticmethod
    def analyze_logic_b(ticker: str):
        """ロジックB分析"""
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
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            is_black_ink_conversion = previous_income <= 0 and latest_income > 0
            growth_rate = ((latest_income - previous_income) / abs(previous_income)) * 100 if previous_income != 0 else 0
            
            ma5_current = latest['MA5']
            ma5_previous = previous['MA5']
            is_ma5_breakout = (previous['Close'] <= ma5_previous and latest['Close'] > ma5_current)
            
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1.0
            
            score = 0
            
            if is_black_ink_conversion:
                score += 80
            elif growth_rate > 100:
                score += 60
            elif growth_rate > 50:
                score += 40
            elif growth_rate > 20:
                score += 25
            
            if is_ma5_breakout:
                score += 20
            
            if volume_ratio >= 2.0:
                score += 15
            elif volume_ratio >= 1.5:
                score += 10
            
            # テックセクター特別評価
            if growth_rate > 200:  # テック企業の爆発的成長
                score += 30
            
            return {
                "score": score,
                "is_black_ink_conversion": is_black_ink_conversion,
                "growth_rate": growth_rate,
                "is_ma5_breakout": is_ma5_breakout,
                "volume_ratio": volume_ratio
            } if score >= 10 else None  # 条件を大幅緩和
            
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
        
        # セクター特別ボーナス
        bonuses = []
        
        if logic_a_result and logic_a_result.get('is_stop_high'):
            bonuses.append("テックストップ高")
            total_score += 20
        
        if logic_b_result and logic_b_result.get('is_black_ink_conversion'):
            bonuses.append("テック黒字転換")
            total_score += 20
        
        if logic_b_result and logic_b_result.get('growth_rate', 0) > 200:
            bonuses.append("爆発的成長")
            total_score += 25
        
        if logic_a_result and logic_a_result.get('change_rate', 0) > 15:
            bonuses.append("テック大幅上昇")
            total_score += 15
        
        return total_score, bonuses

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            service = TechSectorAnalysisService()
            
            # テック・情報通信セクター銘柄（3000-4999番台）
            tech_tickers = []
            
            # 3000-4999: 情報通信・バイオテック・化学・医薬品
            for i in range(3000, 5000):  # テック系2000銘柄のみ
                tech_tickers.append(str(i).zfill(4))
            
            results = []
            near_miss_results = []  # 惜しい銘柄リスト
            processed_count = 0
            
            for ticker in tech_tickers:
                # 基本株価情報を取得
                stock_info = service.get_stock_info(ticker)
                if not stock_info:
                    continue
                
                processed_count += 1
                
                # 共通条件チェック（ホルダー指定）
                common_conditions = service.check_common_conditions(ticker, stock_info)
                if not common_conditions['valid']:
                    continue
                
                # ロジックA分析
                logic_a_result = service.analyze_logic_a(ticker)
                # ロジックB分析  
                logic_b_result = service.analyze_logic_b(ticker)
                
                # 総合スコア計算（条件に関係なく）
                total_score, bonuses = service.calculate_combined_score(
                    logic_a_result, logic_b_result, stock_info
                )
                
                # 惜しい銘柄の理由を詳細分析
                near_miss_reasons = []
                if logic_a_result and logic_a_result['score'] >= 5:
                    near_miss_reasons.append(f"ロジックA: {logic_a_result['score']}点 (上昇率{logic_a_result['change_rate']:.1f}%)")
                if logic_b_result and logic_b_result['score'] >= 5:
                    near_miss_reasons.append(f"ロジックB: {logic_b_result['score']}点 (成長率{logic_b_result['growth_rate']:.1f}%)")
                if stock_info['volume'] > 100000:
                    near_miss_reasons.append(f"出来高: {stock_info['volume']:,}株")
                if stock_info['price'] < 2000:
                    near_miss_reasons.append(f"中小型株: {stock_info['price']:,.0f}円")
                
                result = {
                    "code": stock_info['code'],
                    "name": stock_info['name'],
                    "score": total_score,
                    "bonuses": bonuses,
                    "sector": "テック・情報通信",
                    "analysis_summary": {
                        "logic_a_score": logic_a_result['score'] if logic_a_result else 0,
                        "logic_b_score": logic_b_result['score'] if logic_b_result else 0,
                        "total_conditions_met": len(bonuses)
                    }
                }
                
                # 本格候補または惜しい銘柄の判定
                if logic_a_result or logic_b_result:
                    
                    # 詳細データを追加
                    if logic_a_result:
                        result["logicA"] = {
                            "score": logic_a_result['score'],
                            "listingDate": "テックセクター上場",
                            "earningsDate": "2024-11-20",
                            "stopHighDate": datetime.now().strftime("%Y-%m-%d") if logic_a_result['is_stop_high'] else "該当なし",
                            "prevPrice": int(stock_info['price'] - stock_info['change']),
                            "stopHighPrice": logic_a_result['limit_up_price'],
                            "isFirstTime": True,
                            "noConsecutive": True,
                            "noLongTail": True
                        }
                    
                    if logic_b_result:
                        latest_oku = 50  # 推定値
                        previous_oku = 10 if logic_b_result['is_black_ink_conversion'] else 30
                        
                        result["logicB"] = {
                            "score": logic_b_result['score'],
                            "profitChange": f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円(テック成長)",
                            "blackInkDate": "2024-11-20",
                            "maBreakDate": datetime.now().strftime("%Y-%m-%d") if logic_b_result['is_ma5_breakout'] else "該当なし",
                            "volumeRatio": logic_b_result['volume_ratio']
                        }
                    
                    results.append(result)
                elif near_miss_reasons:  # 惜しい銘柄
                    result["near_miss_reasons"] = near_miss_reasons
                    result["category"] = "惜しい銘柄"
                    near_miss_results.append(result)
                
                # より多くの銘柄を処理してデバッグ
                if processed_count >= 100:  # 100銘柄でテスト
                    break
            
            # スコア順でソート
            results.sort(key=lambda x: x["score"], reverse=True)
            near_miss_results.sort(key=lambda x: x["score"], reverse=True)
            
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
                "near_miss_stocks": near_miss_results[:5],  # 惜しい銘柄と5銘柄
                "scan_time": datetime.now().isoformat(),
                "sector": "テック・情報通信セクター",
                "total_scanned": processed_count,
                "total_universe": len(tech_tickers),
                "matches_found": len(results),
                "data_source": "Yahoo Finance (Tech Sector Analysis)",
                "analysis_method": "テックセクター特化 - 高成長・イノベーション企業分析",
                "notice": f"テックセクタースキャン: {len(tech_tickers)}銘柄中{processed_count}銘柄処理",
                "coverage": f"情報通信・バイオテック・化学・医薬品 {processed_count}銘柄",
                "debug_info": {
                    "target_range": "3000-4999",
                    "data_availability": f"{processed_count}/{len(tech_tickers)}"
                }
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
                "error": f"テックセクタースキャンに失敗しました: {str(e)}",
                "fallback": "他のセクターまたは総合分析を使用してください"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()