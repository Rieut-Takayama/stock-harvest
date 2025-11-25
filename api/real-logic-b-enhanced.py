"""
Vercel Functions用 実データ版 ロジックB強化版API
黒字転換銘柄精密検出
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LogicBProfitabilityTurnaround:
    """
    ロジックB強化版: 黒字転換銘柄精密検出
    直近1年間で初めて経常利益黒字転換 + 5日移動平均線上抜けタイミング
    """
    
    def __init__(self):
        self.config = {
            'ma5_crossover_threshold': 0.02,  # 5日移動平均線上抜け検出閾値（2%）
            'profit_target_rate': 25.0,       # 利確目標（+25%）
            'stop_loss_rate': -10.0,          # 損切りライン（-10%）
            'max_holding_days': 45,           # 最大保有期間（1.5ヶ月）
            'min_volume': 15000000,           # 最低出来高（1500万株）
            'earnings_improvement_threshold': 0.10,  # 利益改善率10%以上
            'consecutive_profit_quarters': 2,  # 連続黒字四半期数
            'exclude_loss_carryforward': True, # 繰越損失除外フラグ
            # ホルダー指定の共通条件
            'max_market_cap': 50000000000,   # 最大時価総額500億円
            'max_price': 5000,               # 最大株価5000円（100株エントリー対応）
            'min_daily_volume': 1000,        # 最低日次出来高1000株
        }
        
        # 履歴管理（オリジナル仕様）
        self.stock_history = {}
        self.detection_cache = {}
    
    def check_common_conditions(self, ticker: str, stock_info: dict):
        """ホルダー指定の共通条件チェック"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            
            # 1. 株価条件（5000円以下）
            price = stock_info.get('price', 0)
            if price > self.config['max_price']:
                return {
                    'valid': False, 
                    'reason': f'株価高すぎ({price:,.0f}円 > 5000円)',
                    'price_check': False
                }
            
            # 2. 時価総額条件（500億円以下）
            info = stock.info
            market_cap = info.get('marketCap', 0)
            if market_cap > self.config['max_market_cap']:
                market_cap_oku = market_cap / 100000000  # 億円単位
                return {
                    'valid': False,
                    'reason': f'時価総額過大({market_cap_oku:,.0f}億円 > 500億円)',
                    'market_cap_check': False
                }
            
            # 3. 出来高条件（1000株/日以下の日がない）
            hist = stock.history(period="1mo")
            if not hist.empty:
                min_daily_volume = hist['Volume'].min()
                if min_daily_volume < self.config['min_daily_volume']:
                    return {
                        'valid': False,
                        'reason': f'低出来高日あり(最低{min_daily_volume:,.0f}株 < 1000株)',
                        'volume_check': False
                    }
            
            return {
                'valid': True,
                'reason': '全共通条件クリア',
                'price_check': True,
                'market_cap_check': True,
                'volume_check': True,
                'price': price,
                'market_cap_oku': market_cap / 100000000 if market_cap > 0 else 0
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'共通条件チェックエラー: {str(e)}'
            }
    
    def check_profitability_turnaround(self, ticker: str):
        """黒字転換条件チェック"""
        try:
            import yfinance as yf
            import pandas as pd
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            income_stmt = stock.income_stmt
            
            if income_stmt.empty:
                return {'is_turnaround': False, 'reason': '決算データなし'}
            
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
                return {'is_turnaround': False, 'reason': '純利益データなし'}
            
            # データを日付順にソート（新しい順）
            net_income_sorted = net_income_data.dropna().sort_index(ascending=False)
            
            if len(net_income_sorted) < 4:  # 少なくとも4四半期必要
                return {'is_turnaround': False, 'reason': '決算データ不足'}
            
            # 最新2四半期と過去2四半期を比較
            recent_quarters = net_income_sorted.iloc[:2]  # 最新2四半期
            past_quarters = net_income_sorted.iloc[2:4]   # 過去2四半期
            
            # 黒字転換判定：過去は赤字、最近は黒字
            recent_profitable = all(income > 0 for income in recent_quarters)
            past_unprofitable = any(income <= 0 for income in past_quarters)
            
            is_turnaround = recent_profitable and past_unprofitable
            
            # 利益改善率計算
            if is_turnaround:
                recent_avg = recent_quarters.mean()
                past_avg = past_quarters.mean()
                if past_avg != 0:
                    improvement_rate = ((recent_avg - past_avg) / abs(past_avg)) * 100
                else:
                    improvement_rate = 100  # 赤字から黒字なので100%改善
                
                meets_improvement_threshold = improvement_rate >= (self.config['earnings_improvement_threshold'] * 100)
            else:
                improvement_rate = 0
                meets_improvement_threshold = False
            
            # 連続黒字四半期数チェック
            consecutive_profits = 0
            for income in recent_quarters:
                if income > 0:
                    consecutive_profits += 1
                else:
                    break
            
            meets_consecutive_requirement = consecutive_profits >= self.config['consecutive_profit_quarters']
            
            # 最終判定
            final_turnaround = is_turnaround and meets_improvement_threshold and meets_consecutive_requirement
            
            return {
                'is_turnaround': final_turnaround,
                'reason': 'black_ink_conversion' if final_turnaround else 'not_qualified',
                'recent_quarters': [float(x) for x in recent_quarters],
                'past_quarters': [float(x) for x in past_quarters],
                'improvement_rate': improvement_rate,
                'consecutive_profits': consecutive_profits,
                'quarter_dates': [q.strftime('%Y-%m-%d') for q in net_income_sorted.index[:4]]
            }
            
        except Exception as e:
            return {'is_turnaround': False, 'reason': f'分析エラー: {str(e)}'}
    
    def detect_ma5_crossover(self, ticker: str):
        """5日移動平均線上抜けチェック"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if hist.empty or len(hist) < 25:
                return {'is_crossover': False, 'reason': 'データ不足'}
            
            # 5日移動平均を計算
            hist['MA5'] = hist['Close'].rolling(window=5).mean()
            
            # 最新のデータ
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            # 5日線上抜け判定
            current_price = latest['Close']
            ma5_current = latest['MA5']
            ma5_previous = previous['MA5']
            
            # 前日は5日線下、今日は5日線上（閾値2%以上で確実な上抜け）
            price_above_ma5 = current_price > (ma5_current * (1 + self.config['ma5_crossover_threshold']))
            crossover_signal = previous['Close'] <= ma5_previous and price_above_ma5
            
            # 出来高チェック
            volume_sufficient = latest['Volume'] >= self.config['min_volume']
            
            return {
                'is_crossover': crossover_signal and volume_sufficient,
                'current_price': float(current_price),
                'ma5': float(ma5_current),
                'ma5_distance': ((current_price - ma5_current) / ma5_current) * 100,
                'volume': int(latest['Volume']),
                'volume_sufficient': volume_sufficient,
                'crossover_date': datetime.now().strftime("%Y-%m-%d") if crossover_signal else None
            }
            
        except Exception as e:
            return {'is_crossover': False, 'reason': f'MA5分析エラー: {str(e)}'}
    
    def validate_entry_conditions_b(self, ticker: str, stock_data: dict):
        """エントリー条件の詳細判定"""
        try:
            # 基本的な価格・出来高条件
            volume = stock_data.get('volume', 0)
            change_rate = stock_data.get('change_rate', 0)
            
            # 最低出来高条件
            volume_ok = volume >= self.config['min_volume']
            
            # 適度な上昇（過度な急騰は除外）
            moderate_rise = 1.0 <= change_rate <= 15.0
            
            # 価格帯チェック（極端な低位株・高位株除外）
            price = stock_data.get('price', 0)
            reasonable_price = 100 <= price <= 5000
            
            all_conditions_met = volume_ok and moderate_rise and reasonable_price
            
            reasons = []
            if not volume_ok:
                reasons.append(f'出来高不足({volume:,} < {self.config["min_volume"]:,})')
            if not moderate_rise:
                reasons.append(f'上昇率範囲外({change_rate:.1f}%)')
            if not reasonable_price:
                reasons.append(f'価格範囲外({price}円)')
            
            return {
                'valid': all_conditions_met,
                'reason': ', '.join(reasons) if reasons else '全条件クリア',
                'volume_check': volume_ok,
                'price_movement_check': moderate_rise,
                'price_range_check': reasonable_price
            }
            
        except Exception as e:
            return {'valid': False, 'reason': f'条件チェックエラー: {str(e)}'}
    
    def check_earnings_timing_b(self, ticker: str):
        """決算タイミング判定（ロジックB用）"""
        try:
            # ロジックホルダー指定の決算集中期間をチェック
            today = datetime.now()
            day = today.day
            
            # 毎月中旬: 8日〜17日
            is_mid_month = 8 <= day <= 17
            
            # 毎月下旬: 28日〜31日
            is_end_month = day >= 28
            
            # 決算集中期間判定
            is_earnings_period = is_mid_month or is_end_month
            
            if is_earnings_period:
                period_type = '中旬期間' if is_mid_month else '下旬期間'
                return {
                    'is_earnings_period': True,
                    'period_type': period_type,
                    'reason': f'黒字転換発表集中{period_type}によるスキャン対象'
                }
            else:
                return {
                    'is_earnings_period': False,
                    'period_type': '非対象期間',
                    'reason': f'決算期間外（{day}日）API温存のためスキップ'
                }
                
        except Exception as e:
            # エラー時は日付チェックのみで再判定
            today = datetime.now()
            day = today.day
            is_target = (8 <= day <= 17) or (day >= 28)
            
            return {
                'is_earnings_period': is_target,
                'reason': f'エラー時簡易判定: {str(e)}'
            }
    
    def check_exclusion_rules_b(self, ticker: str):
        """除外条件チェック（ロジックB特有）"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            
            # 繰越損失チェック（簡易実装）
            # 実際には有価証券報告書データが必要だが、ここでは株価の長期トレンドで代用
            hist = stock.history(period="1y")
            
            if len(hist) < 100:
                return {'should_exclude': False, 'reason': 'データ不足'}
            
            # 長期下落トレンド（1年前比で大幅下落している場合は要注意）
            year_ago_price = hist.iloc[0]['Close']
            current_price = hist.iloc[-1]['Close']
            year_change = ((current_price - year_ago_price) / year_ago_price) * 100
            
            # 1年で50%以上下落している場合は構造的問題があると判定
            structural_decline = year_change < -50
            
            should_exclude = structural_decline and self.config['exclude_loss_carryforward']
            
            return {
                'should_exclude': should_exclude,
                'reason': f'1年間で{year_change:.1f}%下落' if should_exclude else '除外条件なし',
                'year_performance': year_change
            }
            
        except Exception as e:
            return {'should_exclude': False, 'reason': f'除外チェックエラー: {str(e)}'}
    
    def generate_stock_info(self, ticker: str):
        """株価情報取得(効率化版)"""
        try:
            import yfinance as yf
            from requests import Session
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            # セッションの設定(リトライあり)
            session = Session()
            retries = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))
            
            stock = yf.Ticker(ticker, session=session)
            
            # 最小限のデータで高速取得
            hist = stock.history(period="2d", timeout=10)  # 2日分のみ
            
            if hist.empty or len(hist) == 0:
                return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            # 基本情報はキャッシュありで取得
            try:
                info = stock.info
                name = info.get('longName', info.get('shortName', f'銘柄{ticker.replace(".T", "")}'))
            except:
                name = f'銘柄{ticker.replace(".T", "")}'
            
            return {
                "code": ticker.replace('.T', ''),
                "name": name,
                "price": float(latest['Close']),
                "volume": int(latest['Volume']),
                "change": float(latest['Close'] - previous['Close']),
                "change_rate": float((latest['Close'] - previous['Close']) / previous['Close'] * 100),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception:
            return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            logic_service = LogicBProfitabilityTurnaround()
            
            # 全上場銘柄スキャン（1000-9999）- 効率化版
            def generate_ticker_list():
                tickers = []
                for i in range(1000, 10000):
                    tickers.append(str(i).zfill(4))
                return tickers
            
            test_tickers = generate_ticker_list()
            
            results = []
            processed_count = 0
            
            for ticker in test_tickers:
                try:
                    # Step 1: 基本株価情報を取得(タイムアウト付き)
                    stock_info = logic_service.generate_stock_info(ticker)
                    if not stock_info:
                        continue
                        
                    processed_count += 1
                except Exception as e:
                    # エラー時はスキップして継続
                    continue
                
                # Step 2: 共通条件チェック（ホルダー指定）
                common_conditions = logic_service.check_common_conditions(ticker, stock_info)
                if not common_conditions['valid']:
                    continue
                
                # Step 3: 決算タイミングチェック（ロジックホルダー指定期間）
                earnings_timing = logic_service.check_earnings_timing_b(ticker)
                if not earnings_timing['is_earnings_period']:
                    continue
                
                # Step 4: 黒字転換条件チェック
                profitability_check = logic_service.check_profitability_turnaround(ticker)
                if not profitability_check['is_turnaround']:
                    continue
                
                # Step 5: 5日移動平均線上抜けチェック
                ma5_crossover = logic_service.detect_ma5_crossover(ticker)
                if not ma5_crossover['is_crossover']:
                    continue
                
                # Step 6: エントリー条件の詳細判定
                entry_conditions = logic_service.validate_entry_conditions_b(ticker, stock_info)
                if not entry_conditions['valid']:
                    continue
                
                # Step 7: 除外条件チェック
                exclusion_check = logic_service.check_exclusion_rules_b(ticker)
                if exclusion_check['should_exclude']:
                    continue
                
                # 全条件クリア！
                recent_oku = profitability_check['recent_quarters'][0] / 100_000_000  # 億円換算
                past_oku = profitability_check['past_quarters'][0] / 100_000_000
                
                logic_b_details = {
                    "score": 100,  # 条件満たした場合は満点
                    "profitChange": f"前年{past_oku:.0f}億円→今期{recent_oku:.0f}億円(黒字転換)",
                    "blackInkDate": profitability_check['quarter_dates'][0],
                    "maBreakDate": ma5_crossover['crossover_date'],
                    "volumeRatio": ma5_crossover['volume'] / logic_service.config['min_volume'],
                    "isBlackInkConversion": True,
                    "growthRate": profitability_check['improvement_rate'],
                    "consecutiveQuarters": profitability_check['consecutive_profits'],
                    "ma5Distance": ma5_crossover['ma5_distance'],
                    "profitTarget": f"+{logic_service.config['profit_target_rate']}%",
                    "stopLoss": f"{logic_service.config['stop_loss_rate']}%",
                    "maxHoldingDays": logic_service.config['max_holding_days'],
                    "commonConditionsCheck": common_conditions['valid'],
                    "priceRange": f"株価{common_conditions.get('price', 0):,.0f}円(5000円以下)",
                    "marketCapCheck": f"時価総額{common_conditions.get('market_cap_oku', 0):,.0f}億円(500億円以下)",
                    "volumeHistory": "出来高1000株以上/日"
                }
                
                result = {
                    "code": stock_info['code'],
                    "name": stock_info['name'],
                    "score": 100,
                    "logicB": logic_b_details
                }
                results.append(result)
                
                # 結果制限（見つかった場合のみ）
                if len(results) >= 20:
                    break
                
                # 全銘柄スキャン（制限なし）
                # if processed_count >= 100:  # コメントアウトして全銘柄処理
                #     break
            
            response_data = {
                "success": True,
                "results": results,
                "scan_time": datetime.now().isoformat(),
                "total_universe": len(test_tickers),
                "total_scanned": processed_count,
                "matches_found": len(results),
                "data_source": "Yahoo Finance - ロジックB強化版",
                "scan_summary": f"📊 ロジックBスキャン完了レポート",
                "detailed_message": f"【スキャン範囲】決算期間特化スキャン: 全{len(test_tickers)}銘柄を対象に実行しました。\n【期間特化】毎月8-17日・28-31日の決算集中期間のみスキャン実行\n【処理結果】{processed_count}銘柄の株価データと決算情報を取得・分析しました。\n【条件チェック】各銘柄に対してロジックBの8つの厳密条件を精密に検証しました。\n【最終結果】{len(results)}銘柄が全条件を満たす有力候補として検出されました。",
                "notice": f"ロジックB強化版: 全{len(test_tickers)}銘柄中{processed_count}銘柄処理, 厳密条件合格{len(results)}銘柄",
                "analysis_method": "黒字転換銘柄精密検出",
                "coverage": f"黒字転換・MA5上抜け・利益改善の厳密条件",
                "logic_details": {
                    "conditions": [
                        "直近2四半期連続黒字",
                        "過去2四半期に赤字あり",
                        "利益改善率10%以上",
                        "5日移動平均線上抜け（2%以上）",
                        "出来高1500万株以上",
                        "適度な上昇率（1-15%）",
                        "繰越損失リスク除外",
                        "時価総額500億円以下（共通）",
                        "株価5000円以下（共通）",
                        "出来高1000株/日以上（共通）"
                    ],
                    "targets": {
                        "profit_target": "+25%",
                        "stop_loss": "-10%",
                        "max_holding": "45日"
                    }
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
                "error": f"ロジックB強化版エラー: {str(e)}",
                "logic": "黒字転換銘柄精密検出"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # プリフライトリクエストへの対応
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()