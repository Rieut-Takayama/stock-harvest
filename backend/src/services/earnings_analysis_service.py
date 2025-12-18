"""
決算データ分析サービス
Yahoo Finance APIを使用した黒字転換判定
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EarningsAnalysisService:
    """
    Yahoo Finance APIを使用した決算データ分析
    黒字転換銘柄の検出に特化
    """
    
    def __init__(self):
        self.cache = {}
        
    def get_earnings_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        決算データを取得・分析
        
        Args:
            ticker: 銘柄コード (例: "7203.T")
        
        Returns:
            決算分析結果の辞書
        """
        try:
            # 日本株の場合は .T を付与
            if not ticker.endswith('.T') and ticker.isdigit():
                ticker = f"{ticker}.T"
            
            # キャッシュチェック
            cache_key = f"earnings_{ticker}"
            if cache_key in self.cache:
                cached_time = self.cache[cache_key].get('timestamp', 0)
                if datetime.now().timestamp() - cached_time < 3600:  # 1時間のキャッシュ
                    return self.cache[cache_key]['data']
            
            stock = yf.Ticker(ticker)
            
            # 年次決算データ取得
            income_stmt = stock.income_stmt
            quarterly_income = stock.quarterly_income_stmt
            
            if income_stmt.empty:
                logger.warning(f"No income statement data for {ticker}")
                return None
            
            # 純利益の取得
            net_income_data = None
            operating_income_data = None
            
            # 純利益の検索（複数の可能性のある項目名）
            possible_net_income_names = [
                'Net Income',
                'Net Income Common Stockholders', 
                'Net Income From Continuing Operation Net Minority Interest',
                'Net Income Including Noncontrolling Interests'
            ]
            
            for name in possible_net_income_names:
                if name in income_stmt.index:
                    net_income_data = income_stmt.loc[name]
                    break
            
            # 営業利益の検索
            possible_operating_names = [
                'Operating Income',
                'EBIT',
                'Operating Revenue'
            ]
            
            for name in possible_operating_names:
                if name in income_stmt.index:
                    operating_income_data = income_stmt.loc[name]
                    break
            
            if net_income_data is None:
                logger.warning(f"No net income data found for {ticker}")
                return None
            
            # データの分析
            analysis_result = self._analyze_earnings_trend(
                ticker, net_income_data, operating_income_data
            )
            
            # 四半期データがある場合の追加分析
            if not quarterly_income.empty:
                quarterly_analysis = self._analyze_quarterly_trends(
                    ticker, quarterly_income
                )
                analysis_result['quarterly'] = quarterly_analysis
            
            # キャッシュに保存
            self.cache[cache_key] = {
                'data': analysis_result,
                'timestamp': datetime.now().timestamp()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing earnings for {ticker}: {str(e)}")
            return None
    
    def _analyze_earnings_trend(self, ticker: str, net_income: pd.Series, operating_income: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        決算トレンドを分析
        
        Args:
            ticker: 銘柄コード
            net_income: 純利益データ
            operating_income: 営業利益データ（オプション）
        
        Returns:
            分析結果
        """
        try:
            # データを日付順にソート（新しい順）
            net_income_sorted = net_income.dropna().sort_index(ascending=False)
            
            if len(net_income_sorted) < 2:
                return {"error": "Insufficient data for trend analysis"}
            
            # 最新年度と前年度の比較
            latest_year = net_income_sorted.index[0]
            previous_year = net_income_sorted.index[1]
            
            latest_income = float(net_income_sorted.iloc[0])
            previous_income = float(net_income_sorted.iloc[1])
            
            # 黒字転換の判定
            is_black_ink_conversion = False
            conversion_type = "none"
            
            if previous_income <= 0 and latest_income > 0:
                is_black_ink_conversion = True
                conversion_type = "loss_to_profit"
            elif previous_income > 0 and latest_income > previous_income * 2:
                # 利益倍増も注目
                conversion_type = "profit_surge"
            elif previous_income < 0 and latest_income < 0 and latest_income > previous_income:
                # 赤字縮小も候補
                conversion_type = "loss_reduction"
            
            # 利益成長率の計算
            growth_rate = None
            if previous_income != 0:
                growth_rate = ((latest_income - previous_income) / abs(previous_income)) * 100
            
            # 過去3年の傾向分析
            trend_analysis = self._analyze_multi_year_trend(net_income_sorted)
            
            result = {
                "ticker": ticker.replace('.T', ''),
                "latest_year": latest_year.strftime('%Y-%m-%d'),
                "previous_year": previous_year.strftime('%Y-%m-%d'),
                "latest_net_income": latest_income,
                "previous_net_income": previous_income,
                "is_black_ink_conversion": is_black_ink_conversion,
                "conversion_type": conversion_type,
                "growth_rate": growth_rate,
                "trend_analysis": trend_analysis,
                "profit_change_description": self._create_profit_change_description(
                    latest_income, previous_income
                ),
                "analysis_date": datetime.now().isoformat()
            }
            
            # 営業利益データがある場合の追加分析
            if operating_income is not None:
                operating_sorted = operating_income.dropna().sort_index(ascending=False)
                if len(operating_sorted) >= 2:
                    latest_op = float(operating_sorted.iloc[0])
                    previous_op = float(operating_sorted.iloc[1])
                    
                    result["operating_income"] = {
                        "latest": latest_op,
                        "previous": previous_op,
                        "is_operating_conversion": previous_op <= 0 and latest_op > 0
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in trend analysis for {ticker}: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_multi_year_trend(self, income_data: pd.Series) -> Dict[str, Any]:
        """
        複数年の傾向分析
        """
        try:
            years_data = income_data.head(5)  # 最新5年
            
            # 連続成長年数
            consecutive_growth = 0
            for i in range(len(years_data) - 1):
                if years_data.iloc[i] > years_data.iloc[i+1]:
                    consecutive_growth += 1
                else:
                    break
            
            # 過去の最高益との比較
            max_income = years_data.max()
            latest_income = years_data.iloc[0]
            is_record_high = latest_income >= max_income
            
            # 平均成長率
            avg_growth_rate = None
            if len(years_data) >= 3:
                first_year = years_data.iloc[-1]
                last_year = years_data.iloc[0]
                years = len(years_data) - 1
                if first_year != 0 and years > 0:
                    avg_growth_rate = ((last_year / first_year) ** (1/years) - 1) * 100
            
            return {
                "consecutive_growth_years": consecutive_growth,
                "is_record_high": is_record_high,
                "data_years_available": len(years_data),
                "average_growth_rate": avg_growth_rate,
                "max_income_in_period": float(max_income),
                "volatility": "high" if years_data.std() / years_data.mean() > 0.5 else "low"
            }
            
        except Exception as e:
            return {"error": f"Multi-year analysis error: {str(e)}"}
    
    def _analyze_quarterly_trends(self, ticker: str, quarterly_data: pd.DataFrame) -> Dict[str, Any]:
        """
        四半期データの分析
        """
        try:
            # 純利益の四半期データを取得
            net_income_keys = [
                'Net Income',
                'Net Income Common Stockholders',
                'Net Income From Continuing Operation Net Minority Interest'
            ]
            
            quarterly_net_income = None
            for key in net_income_keys:
                if key in quarterly_data.index:
                    quarterly_net_income = quarterly_data.loc[key].dropna()
                    break
            
            if quarterly_net_income is None or len(quarterly_net_income) < 2:
                return {"error": "Insufficient quarterly data"}
            
            # 最新四半期と前四半期の比較
            sorted_quarterly = quarterly_net_income.sort_index(ascending=False)
            latest_q = float(sorted_quarterly.iloc[0])
            previous_q = float(sorted_quarterly.iloc[1])
            
            # 前年同四半期との比較（4四半期前）
            yoy_comparison = None
            if len(sorted_quarterly) >= 5:  # 5四半期以上のデータがある場合
                same_quarter_last_year = float(sorted_quarterly.iloc[4])
                yoy_growth = ((latest_q - same_quarter_last_year) / abs(same_quarter_last_year)) * 100
                yoy_comparison = {
                    "same_quarter_last_year": same_quarter_last_year,
                    "yoy_growth_rate": yoy_growth,
                    "is_yoy_positive": latest_q > same_quarter_last_year
                }
            
            return {
                "latest_quarter": sorted_quarterly.index[0].strftime('%Y-%m-%d'),
                "latest_quarter_income": latest_q,
                "previous_quarter_income": previous_q,
                "qoq_growth_rate": ((latest_q - previous_q) / abs(previous_q)) * 100 if previous_q != 0 else None,
                "quarters_available": len(sorted_quarterly),
                "yoy_comparison": yoy_comparison
            }
            
        except Exception as e:
            return {"error": f"Quarterly analysis error: {str(e)}"}
    
    def _create_profit_change_description(self, latest: float, previous: float) -> str:
        """
        利益変動の説明文を生成
        """
        try:
            # 億円単位に変換（日本円想定）
            latest_oku = latest / 100_000_000
            previous_oku = previous / 100_000_000
            
            if previous <= 0 and latest > 0:
                return f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円(黒字転換)"
            elif previous > 0 and latest <= 0:
                return f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円(赤字転落)"
            elif previous > 0 and latest > 0:
                change_oku = latest_oku - previous_oku
                return f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({change_oku:+.0f}億円)"
            else:
                change_oku = latest_oku - previous_oku
                return f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({change_oku:+.0f}億円改善)" if change_oku > 0 else f"前年{previous_oku:.0f}億円→今期{latest_oku:.0f}億円({abs(change_oku):.0f}億円悪化)"
                
        except Exception:
            return f"前年{previous:,.0f}→今期{latest:,.0f}"

    def scan_for_black_ink_conversions(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        黒字転換銘柄をスキャン
        
        Args:
            tickers: 検査対象の銘柄コードリスト
        
        Returns:
            黒字転換銘柄のリスト
        """
        results = []
        
        for ticker in tickers:
            earnings_data = self.get_earnings_data(ticker)
            if not earnings_data or 'error' in earnings_data:
                continue
            
            # 黒字転換またはその他注目すべき条件をチェック
            if (earnings_data.get('is_black_ink_conversion') or 
                earnings_data.get('conversion_type') in ['profit_surge', 'loss_reduction']):
                
                results.append({
                    "ticker": earnings_data['ticker'],
                    "earnings_analysis": earnings_data,
                    "priority_score": self._calculate_priority_score(earnings_data)
                })
        
        # 優先度順でソート
        results.sort(key=lambda x: x['priority_score'], reverse=True)
        return results
    
    def _calculate_priority_score(self, earnings_data: Dict[str, Any]) -> float:
        """
        優先度スコアを計算
        """
        score = 0.0
        
        # 黒字転換の場合は高スコア
        if earnings_data.get('is_black_ink_conversion'):
            score += 100.0
        
        # 成長率によるスコア
        growth_rate = earnings_data.get('growth_rate')
        if growth_rate is not None:
            if growth_rate > 100:  # 100%以上成長
                score += 50.0
            elif growth_rate > 50:  # 50%以上成長
                score += 30.0
            elif growth_rate > 0:  # プラス成長
                score += 20.0
        
        # 連続成長年数
        trend = earnings_data.get('trend_analysis', {})
        consecutive_growth = trend.get('consecutive_growth_years', 0)
        score += consecutive_growth * 10.0
        
        # 過去最高益の場合
        if trend.get('is_record_high'):
            score += 25.0
        
        return score

# テスト用関数
def test_earnings_analysis():
    """
    決算分析サービスのテスト
    """
    service = EarningsAnalysisService()
    
    test_tickers = ["7203", "6501", "4755"]  # トヨタ、日立、楽天
    
    logger.info("=== Individual Earnings Analysis ===")
    for ticker in test_tickers:
        logger.info(f"Analyzing {ticker}...")
        result = service.get_earnings_data(ticker)
        if result and 'error' not in result:
            logger.info(f"Company: {result['ticker']}")
            logger.info(f"Profit change: {result['profit_change_description']}")
            logger.info(f"Black ink conversion: {result['is_black_ink_conversion']}")
            logger.info(f"Growth rate: {result.get('growth_rate', 'N/A'):.1f}%" if result.get('growth_rate') else "Growth rate: N/A")
            logger.info(f"Conversion type: {result.get('conversion_type', 'none')}")
        else:
            logger.warning(f"Failed to analyze {ticker}: {result}")
    
    logger.info("=== Black Ink Conversion Scan ===")
    conversions = service.scan_for_black_ink_conversions(test_tickers)
    for conversion in conversions:
        logger.info(f"{conversion['ticker']}: Priority Score = {conversion['priority_score']:.1f}")
        logger.info(f"  {conversion['earnings_analysis']['profit_change_description']}")

if __name__ == "__main__":
    test_earnings_analysis()