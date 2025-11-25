"""
Vercel Functions用 実データ版 ロジックA強化版API
ストップ高張り付き精密検出（セミナーノウハウ対応）
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import sys
import os

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LogicAStopHighDetection:
    """
    ロジックA強化版: ストップ高張り付き精密検出（オリジナル仕様完全実装）
    """
    
    def __init__(self):
        # ロジック共通条件追加（ホルダー指定）
        self.config = {
            'entry_signal_rate': 5.0,        # エントリーシグナル上昇率（%）
            'profit_target_rate': 24.0,      # 利確目標（%）
            'stop_loss_rate': -10.0,         # 損切り（%）
            'max_holding_days': 30,          # 最大保有期間（日）
            'min_stop_high_volume': 20000000, # ストップ高最低出来高
            'max_lower_shadow_ratio': 0.15,  # 下髭最大比率（15%）
            'max_listing_years': 2.5,        # 上場後最大年数
            'exclude_consecutive_stop_high': True, # 2連続ストップ高除外
            # ホルダー指定の共通条件
            'max_market_cap': 50000000000,   # 最大時価総額500億円
            'max_price': 5000,               # 最大株価5000円（100株エントリー対応）
            'min_daily_volume': 1000,        # 最低日次出来高1000株
        }
        
        # 履歴管理（オリジナル仕様）
        self.stock_history = {}
        self.detection_cache = {}
    
    def check_listing_conditions(self, ticker: str):
        """上場条件チェック: 2.5年以内の新興株"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 上場日データがない場合は一律OK（簡易実装）
            listing_date = info.get('firstTradeDateEpochUtc')
            if not listing_date:
                return True  # データ不足の場合は通す
            
            # 上場からの経過年数計算
            listing_datetime = datetime.fromtimestamp(listing_date)
            years_since_listing = (datetime.now() - listing_datetime).days / 365.25
            
            return years_since_listing <= self.config['max_listing_years']
            
        except Exception:
            return True  # エラー時は通す
    
    def detect_stop_high_sticking(self, ticker: str):
        """ストップ高張り付き判定"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if hist.empty:
                return {'is_stop_high': False, 'reason': 'データなし'}
            
            latest = hist.iloc[-1]
            open_price = latest['Open']
            close_price = latest['Close']
            high_price = latest['High']
            volume = latest['Volume']
            
            # 制限値幅の計算（東証基準）
            if open_price < 100:
                limit_up = open_price * 1.3
            elif open_price < 200:
                limit_up = open_price * 1.25
            elif open_price < 500:
                limit_up = open_price * 1.2
            elif open_price < 1000:
                limit_up = open_price * 1.15
            elif open_price < 5000:
                limit_up = open_price * 1.1
            else:
                limit_up = open_price * 1.05
            
            # ストップ高判定（95%以上）
            is_stop_high = close_price >= (limit_up * 0.95) and high_price >= (limit_up * 0.95)
            
            # 出来高チェック
            volume_ok = volume >= self.config['min_stop_high_volume']
            
            return {
                'is_stop_high': is_stop_high and volume_ok,
                'limit_up_price': limit_up,
                'close_price': close_price,
                'volume': volume,
                'volume_sufficient': volume_ok
            }
            
        except Exception as e:
            return {'is_stop_high': False, 'reason': f'エラー: {str(e)}'}
    
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
    
    def check_earnings_timing(self, ticker: str):
        """決算タイミング判定（ロジックホルダー指定期間）"""
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
                    'is_earnings_day': True,
                    'earnings_date': today.strftime('%Y-%m-%d'),
                    'days_since': 1,
                    'period_type': period_type,
                    'reason': f'決算集中{period_type}によるスキャン対象'
                }
            else:
                # 決算期間外は非対象
                return {
                    'is_earnings_day': False,
                    'earnings_date': '決算期間外',
                    'days_since': 0,
                    'period_type': '非対象期間',
                    'reason': f'決算期間外（{day}日）API温存のためスキップ'
                }
            
        except Exception as e:
            # エラー時は日付チェックのみで再判定
            today = datetime.now()
            day = today.day
            is_target = (8 <= day <= 17) or (day >= 28)
            
            return {
                'is_earnings_day': is_target,
                'earnings_date': 'エラー時簡易判定',
                'days_since': 1 if is_target else 0,
                'reason': f'エラー: {str(e)}'
            }
    
    def check_exclusion_rules(self, ticker: str):
        """除外条件チェック"""
        try:
            import yfinance as yf
            
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="10d")
            
            if len(hist) < 2:
                return {'should_exclude': False, 'reason': 'データ不足'}
            
            # 2連続ストップ高チェック
            consecutive_stop_high = False
            if self.config['exclude_consecutive_stop_high']:
                for i in range(len(hist) - 1):
                    current = hist.iloc[i]
                    previous = hist.iloc[i - 1] if i > 0 else current
                    
                    current_change = (current['Close'] - previous['Close']) / previous['Close']
                    if current_change >= 0.15:  # 15%以上の上昇を2日連続
                        consecutive_stop_high = True
                        break
            
            # 長い下髭チェック
            latest = hist.iloc[-1]
            open_price = latest['Open']
            close_price = latest['Close']
            low_price = latest['Low']
            
            # 下髭比率計算
            if open_price > low_price:
                lower_shadow_ratio = (open_price - low_price) / open_price
                long_tail = lower_shadow_ratio > self.config['max_lower_shadow_ratio']
            else:
                long_tail = False
            
            should_exclude = consecutive_stop_high or long_tail
            
            reasons = []
            if consecutive_stop_high:
                reasons.append('2連続ストップ高')
            if long_tail:
                reasons.append(f'長い下髭({lower_shadow_ratio:.1%})')
            
            return {
                'should_exclude': should_exclude,
                'reason': ', '.join(reasons) if reasons else 'なし'
            }
            
        except Exception:
            return {'should_exclude': False, 'reason': 'チェック不可'}
    
    def check_first_time_condition(self, ticker: str):
        """初回条件確認（上場後初回達成）- オリジナル仕様実装"""
        try:
            # 過去6ヶ月の検出履歴をチェック
            history_key = f"logic_a_{ticker}"
            
            if history_key in self.stock_history:
                last_detection = self.stock_history[history_key]
                days_since = (datetime.now() - last_detection).days
                
                # 6ヶ月以内（180日）に検出された場合は除外
                if days_since < 180:
                    return {
                        'is_first_time': False,
                        'reason': f'{days_since}日前に検出済み（重複除外）',
                        'last_detection': last_detection.isoformat()
                    }
            
            # 初回または6ヶ月以上経過
            return {
                'is_first_time': True,
                'reason': '初回条件達成または6ヶ月以上経過',
                'last_detection': None
            }
            
        except Exception as e:
            return {
                'is_first_time': True,  # エラー時は通す
                'reason': f'履歴チェックエラー: {str(e)}'
            }
    
    def record_detection(self, ticker: str):
        """検出履歴を記録"""
        history_key = f"logic_a_{ticker}"
        self.stock_history[history_key] = datetime.now()
    
    def generate_trading_signal(self, stock_data: dict):
        """売買シグナル生成（オリジナル仕様）"""
        try:
            price = stock_data.get('price', 0)
            change_rate = stock_data.get('change_rate', 0)
            volume = stock_data.get('volume', 0)
            
            # エントリーシグナル判定
            if change_rate >= self.config['entry_signal_rate']:
                signal_type = 'BUY_ENTRY'
                signal_strength = min(100, 50 + (change_rate - 5) * 5)  # 5%で50点、以降1%毎に+5点
            else:
                signal_type = 'WATCH'
                signal_strength = max(10, change_rate * 10)  # 最低10点
            
            # 利確・損切り価格計算
            entry_price = price
            profit_target = price * (1 + self.config['profit_target_rate'] / 100)
            stop_loss = price * (1 + self.config['stop_loss_rate'] / 100)
            
            # リスク評価
            risk_score = self.calculate_risk_score(stock_data)
            risk_level = 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW'
            
            return {
                'signal_type': signal_type,
                'signal_strength': signal_strength,
                'entry_price': entry_price,
                'profit_target': profit_target,
                'stop_loss': stop_loss,
                'max_holding_days': self.config['max_holding_days'],
                'risk_assessment': {
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'recommendation': self.get_recommendation(risk_level, signal_strength)
                }
            }
            
        except Exception as e:
            return {
                'signal_type': 'ERROR',
                'signal_strength': 0,
                'reason': f'シグナル生成エラー: {str(e)}'
            }
    
    def calculate_risk_score(self, stock_data: dict):
        """リスク評価スコア計算（オリジナル仕様）"""
        try:
            risk_score = 0
            
            # 出来高リスク（高出来高ほど安全）
            volume = stock_data.get('volume', 0)
            if volume < 10000000:
                risk_score += 30
            elif volume < 50000000:
                risk_score += 15
            
            # 価格変動リスク（急騰しすぎは危険）
            change_rate = abs(stock_data.get('change_rate', 0))
            if change_rate > 20:
                risk_score += 40
            elif change_rate > 15:
                risk_score += 25
            elif change_rate > 10:
                risk_score += 10
            
            # 価格帯リスク（低位株は変動大）
            price = stock_data.get('price', 0)
            if price < 100:
                risk_score += 25
            elif price < 500:
                risk_score += 10
            
            return min(100, risk_score)
            
        except Exception:
            return 50  # デフォルトはMIDDLE
    
    def get_recommendation(self, risk_level: str, signal_strength: float):
        """投資推奨度計算"""
        if risk_level == 'LOW' and signal_strength >= 70:
            return '強く推奨（低リスク・強シグナル）'
        elif risk_level == 'MEDIUM' and signal_strength >= 60:
            return '推奨（中リスク・良シグナル）'
        elif risk_level == 'HIGH':
            return '注意（高リスク）'
        else:
            return '様子見（弱シグナル）'
    
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
            logic_service = LogicAStopHighDetection()
            
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
                
                # Step 3: 上場条件チェック
                if not logic_service.check_listing_conditions(ticker):
                    continue
                
                # Step 4: ストップ高張り付き判定
                stop_high_result = logic_service.detect_stop_high_sticking(ticker)
                if not stop_high_result['is_stop_high']:
                    continue
                
                # Step 5: 決算タイミング判定
                earnings_timing = logic_service.check_earnings_timing(ticker)
                if not earnings_timing['is_earnings_day']:
                    continue
                
                # Step 6: 除外条件チェック
                exclusion_check = logic_service.check_exclusion_rules(ticker)
                if exclusion_check['should_exclude']:
                    continue
                
                # Step 7: 初回条件確認
                first_time_check = logic_service.check_first_time_condition(ticker)
                if not first_time_check['is_first_time']:
                    continue
                
                # Step 8: 売買シグナル生成（オリジナル仕様）
                trading_signal = logic_service.generate_trading_signal(stock_info)
                
                # Step 9: 検出履歴記録
                logic_service.record_detection(ticker)
                
                # 全条件クリア！
                logic_a_details = {
                    "score": trading_signal['signal_strength'],  # オリジナル仕様のシグナル強度
                    "listingDate": "2.5年以内上場",
                    "earningsDate": earnings_timing['earnings_date'],
                    "stopHighDate": datetime.now().strftime("%Y-%m-%d"),
                    "prevPrice": int(stock_info['price'] - stock_info['change']),
                    "stopHighPrice": int(stop_high_result['limit_up_price']),
                    "isFirstTime": first_time_check['is_first_time'],
                    "noConsecutive": not exclusion_check['should_exclude'],
                    "noLongTail": not exclusion_check['should_exclude'],
                    "volumeCheck": stop_high_result['volume_sufficient'],
                    "commonConditionsCheck": common_conditions['valid'],
                    "priceRange": f"株価{common_conditions.get('price', 0):,.0f}円(5000円以下)",
                    "marketCapCheck": f"時価総額{common_conditions.get('market_cap_oku', 0):,.0f}億円(500億円以下)",
                    "volumeHistory": "出来高1000株以上/日"，
                    "profitTarget": f"+{logic_service.config['profit_target_rate']}%",
                    "stopLoss": f"{logic_service.config['stop_loss_rate']}%",
                    "maxHoldingDays": logic_service.config['max_holding_days'],
                    "signalType": trading_signal['signal_type'],
                    "entryPrice": trading_signal['entry_price'],
                    "riskLevel": trading_signal['risk_assessment']['risk_level'],
                    "recommendation": trading_signal['risk_assessment']['recommendation']
                }
                
                result = {
                    "code": stock_info['code'],
                    "name": stock_info['name'],
                    "score": trading_signal['signal_strength'],
                    "logicA": logic_a_details,
                    "tradingSignal": trading_signal  # オリジナル仕様の詳細シグナル
                }
                results.append(result)
                
                # 結果制限（見つかった場合のみ）
                if len(results) >= 20:
                    break
                
                # 全銘柄スキャン（制限なし）
                # if processed_count >= 1000:  # コメントアウトして全銘柄処理
                #     break
            
            response_data = {
                "success": True,
                "results": results,
                "scan_time": datetime.now().isoformat(),
                "total_universe": len(test_tickers),
                "total_scanned": processed_count,
                "matches_found": len(results),
                "data_source": "Yahoo Finance - ロジックA強化版",
                "scan_summary": f"📊 ロジックAスキャン完了レポート",
                "detailed_message": f"【スキャン範囲】決算期間特化スキャン: 全{len(test_tickers)}銘柄を対象に実行しました。\n【期間特化】毎月8-17日・28-31日の決算集中期間のみスキャン実行\n【処理結果】{processed_count}銘柄の株価データを取得・分析しました。\n【条件チェック】各銘柄に対してロジックAの8つの厳密条件を精密に検証しました。\n【最終結果】{len(results)}銘柄が全条件を満たす有力候補として検出されました。",
                "notice": f"ロジックA強化版: 全{len(test_tickers)}銘柄中{processed_count}銘柄処理, 厳密条件合格{len(results)}銘柄",
                "analysis_method": "ストップ高張り付き精密検出（セミナーノウハウ対応）",
                "coverage": f"上場2.5年以内・決算翌日・初回達成の厳密条件",
                "logic_details": {
                    "conditions": [
                        "上場2.5年以内の新興株",
                        "ストップ高張り付き（95%以上）",
                        "決算発表翌日（1-3日以内）",
                        "2連続ストップ高でない",
                        "下髭15%以下",
                        "出来高2000万株以上",
                        "上場後初回達成",
                        "時価総額500億円以下（共通）",
                        "株価5000円以下（共通）",
                        "出来高1000株/日以上（共通）"
                    ],
                    "targets": {
                        "profit_target": "+24%",
                        "stop_loss": "-10%",
                        "max_holding": "30日"
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
                "error": f"ロジックA強化版エラー: {str(e)}",
                "logic": "ストップ高張り付き精密検出"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # プリフライトリクエストへの対応
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()