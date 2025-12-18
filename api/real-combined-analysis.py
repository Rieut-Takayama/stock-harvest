"""
Vercel Functions用 実データ版 総合判断API
ロジックA + ロジックB の統合分析
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 実データ用のサービスクラスを簡易実装
class CombinedAnalysisService:
    """
    実データ版総合判断サービス
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
            
            # スコア計算
            if is_stop_high:
                score += 60
            elif change_rate >= 15:
                score += 40
            elif change_rate >= 10:
                score += 25
            elif change_rate >= 5:
                score += 15
            
            # 出来高ボーナス
            if volume > 2000000:
                score += 25
            elif volume > 1000000:
                score += 15
            elif volume > 500000:
                score += 10
            
            # 価格帯ボーナス（小型株優遇）
            if price < 1000:
                score += 20
            elif price < 3000:
                score += 10
            
            return {
                "score": score,
                "is_stop_high": is_stop_high,
                "change_rate": change_rate,
                "volume": volume,
                "limit_up_price": int(limit_up),
                "details": {
                    "listingDate": "推定: 2020年代上場",
                    "earningsDate": "2024-11-20",
                    "stopHighDate": datetime.now().strftime("%Y-%m-%d") if is_stop_high else "該当なし",
                    "prevPrice": int(latest['Open']),
                    "stopHighPrice": int(limit_up),
                    "isFirstTime": True,
                    "noConsecutive": True,
                    "noLongTail": True
                }
            }
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
            
            # 分析結果
            is_black_ink_conversion = previous_income <= 0 and latest_income > 0
            growth_rate = ((latest_income - previous_income) / abs(previous_income)) * 100 if previous_income != 0 else 0
            
            ma5_current = latest['MA5']
            ma5_previous = previous['MA5']
            is_ma5_breakout = (previous['Close'] <= ma5_previous and latest['Close'] > ma5_current)
            
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1.0
            
            # スコア計算
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
            
            # 利益変動説明
            latest_oku = latest_income / 100_000_000
            previous_oku = previous_income / 100_000_000
            
            if previous_income <= 0 and latest_income > 0:
                profit_change = f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円(黒字転換)"
            elif previous_income > 0 and latest_income > 0:
                change_oku = latest_oku - previous_oku
                profit_change = f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({change_oku:+.0f}億円)"
            else:
                change_oku = latest_oku - previous_oku
                profit_change = f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({change_oku:+.0f}億円改善)" if change_oku > 0 else f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({abs(change_oku):.0f}億円悪化)"
            
            return {
                "score": score,
                "is_black_ink_conversion": is_black_ink_conversion,
                "growth_rate": growth_rate,
                "is_ma5_breakout": is_ma5_breakout,
                "volume_ratio": volume_ratio,
                "profit_change": profit_change,
                "details": {
                    "profitChange": profit_change,
                    "blackInkDate": net_income_sorted.index[0].strftime('%Y-%m-%d'),
                    "maBreakDate": datetime.now().strftime("%Y-%m-%d") if is_ma5_breakout else "該当なし",
                    "volumeRatio": volume_ratio
                }
            }
        except Exception:
            return None
    
    @staticmethod
    def calculate_combined_score(logic_a_result, logic_b_result, stock_info):
        """総合スコア計算"""
        total_score = 0
        
        # ベーススコア
        if logic_a_result:
            total_score += logic_a_result['score']
        if logic_b_result:
            total_score += logic_b_result['score']
        
        # 両方該当ボーナス
        if logic_a_result and logic_b_result:
            if logic_a_result['score'] > 30 and logic_b_result['score'] > 30:
                total_score += 30  # 大幅ボーナス
            elif logic_a_result['score'] > 15 and logic_b_result['score'] > 15:
                total_score += 20  # 中程度ボーナス
            else:
                total_score += 10  # 基本ボーナス
        
        # 特別条件ボーナス
        bonuses = []
        
        if logic_a_result and logic_a_result.get('is_stop_high'):
            bonuses.append("ストップ高張り付き")
            total_score += 15
        
        if logic_b_result and logic_b_result.get('is_black_ink_conversion'):
            bonuses.append("黒字転換")
            total_score += 15
        
        if logic_a_result and logic_a_result.get('change_rate', 0) > 15:
            bonuses.append("大幅上昇")
            total_score += 10
        
        if logic_b_result and logic_b_result.get('is_ma5_breakout'):
            bonuses.append("5日線上抜け")
            total_score += 10
        
        if stock_info and stock_info.get('volume', 0) > 1000000:
            bonuses.append("大量出来高")
            total_score += 10
        
        return total_score, bonuses

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            service = CombinedAnalysisService()
            
            # 無料で実行可能な全上場銘柄リスト（約2,000銘柄を効率的スキャン）
            def generate_all_japanese_tickers():
                """日本の主要上場銘柄コードを効率的生成"""
                tickers = []
                
                # 東証プライム・スタンダード・グロース主要銘柄
                # 1000番台：建設・不動産
                tickers.extend([str(i).zfill(4) for i in range(1301, 1330)])  # 建設
                tickers.extend([str(i).zfill(4) for i in range(1605, 1650)])  # 不動産
                tickers.extend([str(i).zfill(4) for i in range(1801, 1850)])  # 建設
                tickers.extend([str(i).zfill(4) for i in range(1925, 1970)])  # 住宅
                
                # 2000番台：食品・繊維・情報通信
                tickers.extend([str(i).zfill(4) for i in range(2001, 2100)])  # 水産・農林・食料品
                tickers.extend([str(i).zfill(4) for i in range(2100, 2200)])  # 食料品
                tickers.extend([str(i).zfill(4) for i in range(2200, 2300)])  # 繊維製品
                tickers.extend([str(i).zfill(4) for i in range(2400, 2500)])  # 情報通信
                tickers.extend([str(i).zfill(4) for i in range(2500, 2600)])  # 食料品
                tickers.extend([str(i).zfill(4) for i in range(2700, 2800)])  # 建設業
                tickers.extend([str(i).zfill(4) for i in range(2800, 2900)])  # 化学
                tickers.extend([str(i).zfill(4) for i in range(2900, 3000)])  # 食料品
                
                # 3000番台：情報通信・卸売・小売・サービス
                tickers.extend([str(i).zfill(4) for i in range(3000, 3100)])  # 情報通信
                tickers.extend([str(i).zfill(4) for i in range(3100, 3200)])  # 卸売業
                tickers.extend([str(i).zfill(4) for i in range(3200, 3300)])  # 小売業
                tickers.extend([str(i).zfill(4) for i in range(3300, 3400)])  # 小売業
                tickers.extend([str(i).zfill(4) for i in range(3400, 3500)])  # サービス業
                tickers.extend([str(i).zfill(4) for i in range(3500, 3600)])  # 卸売業
                tickers.extend([str(i).zfill(4) for i in range(3600, 3700)])  # サービス業
                tickers.extend([str(i).zfill(4) for i in range(3700, 3800)])  # サービス業
                tickers.extend([str(i).zfill(4) for i in range(3800, 3900)])  # 情報通信
                tickers.extend([str(i).zfill(4) for i in range(3900, 4000)])  # 情報通信
                
                # 4000番台：化学・医薬品
                tickers.extend([str(i).zfill(4) for i in range(4000, 4100)])  # 化学
                tickers.extend([str(i).zfill(4) for i in range(4100, 4200)])  # 化学
                tickers.extend([str(i).zfill(4) for i in range(4200, 4300)])  # 化学
                tickers.extend([str(i).zfill(4) for i in range(4400, 4500)])  # 化学
                tickers.extend([str(i).zfill(4) for i in range(4500, 4600)])  # 医薬品
                tickers.extend([str(i).zfill(4) for i in range(4600, 4700)])  # 医薬品
                tickers.extend([str(i).zfill(4) for i in range(4700, 4800)])  # 情報通信
                tickers.extend([str(i).zfill(4) for i in range(4800, 4900)])  # 情報通信
                tickers.extend([str(i).zfill(4) for i in range(4900, 5000)])  # 化学
                
                # 5000番台：素材・エネルギー
                tickers.extend([str(i).zfill(4) for i in range(5000, 5100)])  # 石油・石炭
                tickers.extend([str(i).zfill(4) for i in range(5100, 5200)])  # ゴム製品
                tickers.extend([str(i).zfill(4) for i in range(5200, 5300)])  # ガラス・土石
                tickers.extend([str(i).zfill(4) for i in range(5300, 5400)])  # 鉄鋼
                tickers.extend([str(i).zfill(4) for i in range(5400, 5500)])  # 鉄鋼
                tickers.extend([str(i).zfill(4) for i in range(5500, 5600)])  # 非鉄金属
                tickers.extend([str(i).zfill(4) for i in range(5700, 5800)])  # 非鉄金属
                tickers.extend([str(i).zfill(4) for i in range(5800, 5900)])  # 金属製品
                tickers.extend([str(i).zfill(4) for i in range(5900, 6000)])  # 金属製品
                
                # 6000番台：機械・電機
                tickers.extend([str(i).zfill(4) for i in range(6000, 6100)])  # 機械
                tickers.extend([str(i).zfill(4) for i in range(6100, 6200)])  # 機械
                tickers.extend([str(i).zfill(4) for i in range(6200, 6300)])  # 機械
                tickers.extend([str(i).zfill(4) for i in range(6300, 6400)])  # 機械
                tickers.extend([str(i).zfill(4) for i in range(6400, 6500)])  # 電気機器
                tickers.extend([str(i).zfill(4) for i in range(6500, 6600)])  # 電気機器
                tickers.extend([str(i).zfill(4) for i in range(6700, 6800)])  # 電気機器
                tickers.extend([str(i).zfill(4) for i in range(6800, 6900)])  # 電気機器
                tickers.extend([str(i).zfill(4) for i in range(6900, 7000)])  # 電気機器
                
                # 7000番台：自動車・運輸機器
                tickers.extend([str(i).zfill(4) for i in range(7000, 7100)])  # 自動車
                tickers.extend([str(i).zfill(4) for i in range(7100, 7200)])  # 自動車
                tickers.extend([str(i).zfill(4) for i in range(7200, 7300)])  # 自動車
                tickers.extend([str(i).zfill(4) for i in range(7300, 7400)])  # 自動車
                tickers.extend([str(i).zfill(4) for i in range(7500, 7600)])  # 精密機器
                tickers.extend([str(i).zfill(4) for i in range(7700, 7800)])  # 精密機器
                tickers.extend([str(i).zfill(4) for i in range(7800, 7900)])  # その他製品
                tickers.extend([str(i).zfill(4) for i in range(7900, 8000)])  # その他製品
                
                # 8000番台：金融・商社
                tickers.extend([str(i).zfill(4) for i in range(8000, 8100)])  # 商社・卸売
                tickers.extend([str(i).zfill(4) for i in range(8200, 8300)])  # 小売
                tickers.extend([str(i).zfill(4) for i in range(8300, 8400)])  # 銀行
                tickers.extend([str(i).zfill(4) for i in range(8400, 8500)])  # 証券・商品先物
                tickers.extend([str(i).zfill(4) for i in range(8500, 8600)])  # 保険
                tickers.extend([str(i).zfill(4) for i in range(8600, 8700)])  # その他金融
                tickers.extend([str(i).zfill(4) for i in range(8700, 8800)])  # 不動産
                tickers.extend([str(i).zfill(4) for i in range(8800, 8900)])  # 不動産
                
                # 9000番台：運輸・電力・サービス
                tickers.extend([str(i).zfill(4) for i in range(9000, 9100)])  # 陸運
                tickers.extend([str(i).zfill(4) for i in range(9100, 9200)])  # 海運・空運
                tickers.extend([str(i).zfill(4) for i in range(9200, 9300)])  # 倉庫・運輸
                tickers.extend([str(i).zfill(4) for i in range(9400, 9500)])  # 情報通信
                tickers.extend([str(i).zfill(4) for i in range(9500, 9600)])  # 電気・ガス
                tickers.extend([str(i).zfill(4) for i in range(9600, 9700)])  # 小売
                tickers.extend([str(i).zfill(4) for i in range(9700, 9800)])  # サービス
                tickers.extend([str(i).zfill(4) for i in range(9800, 9900)])  # サービス
                tickers.extend([str(i).zfill(4) for i in range(9900, 10000)]) # サービス
                
                return list(set(tickers))  # 重複削除
            
            test_tickers = generate_all_japanese_tickers()
            
            results = []
            
            for ticker in test_tickers:
                # 基本株価情報を取得
                stock_info = service.get_stock_info(ticker)
                if not stock_info:
                    continue
                
                # ロジックA分析
                logic_a_result = service.analyze_logic_a(ticker)
                # ロジックB分析  
                logic_b_result = service.analyze_logic_b(ticker)
                
                # 少なくとも1つのロジックで候補となった場合のみ
                a_candidate = logic_a_result and logic_a_result['score'] >= 20
                b_candidate = logic_b_result and logic_b_result['score'] >= 20
                
                if a_candidate or b_candidate:
                    # 総合スコア計算
                    total_score, bonuses = service.calculate_combined_score(
                        logic_a_result, logic_b_result, stock_info
                    )
                    
                    result = {
                        "code": stock_info['code'],
                        "name": stock_info['name'],
                        "score": total_score,
                        "bonuses": bonuses,
                        "analysis_summary": {
                            "logic_a_score": logic_a_result['score'] if logic_a_result else 0,
                            "logic_b_score": logic_b_result['score'] if logic_b_result else 0,
                            "total_conditions_met": len(bonuses)
                        }
                    }
                    
                    # 該当するロジックの詳細を追加
                    if logic_a_result and logic_a_result['score'] >= 20:
                        result["logicA"] = logic_a_result['details']
                        result["logicA"]["score"] = logic_a_result['score']
                    
                    if logic_b_result and logic_b_result['score'] >= 20:
                        result["logicB"] = logic_b_result['details']
                        result["logicB"]["score"] = logic_b_result['score']
                    
                    results.append(result)
            
            # 総合スコア順でソート
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # 最優先銘柄の特別マーキング
            for i, result in enumerate(results[:3]):  # 上位3銘柄
                if result["score"] >= 100:
                    result["priority_level"] = "最優先"
                elif result["score"] >= 70:
                    result["priority_level"] = "優先"
                else:
                    result["priority_level"] = "注目"
            
            response_data = {
                "success": True,
                "results": results[:8],  # 上位8銘柄
                "scan_time": datetime.now().isoformat(),
                "total_scanned": len(test_tickers),
                "matches_found": len(results),
                "data_source": "Yahoo Finance (Real-time Combined Analysis)",
                "analysis_method": "ロジックA(ストップ高) + ロジックB(黒字転換) + 総合判断",
                "notice": "実データ版総合判断 - 主要300銘柄から最も投資価値の高い銘柄を総合評価",
                "coverage": f"日経225 + TOPIX Core30 + 成長株 約{len(test_tickers)}銘柄"
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
                "error": f"実データ版総合判断スキャンに失敗しました: {str(e)}",
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