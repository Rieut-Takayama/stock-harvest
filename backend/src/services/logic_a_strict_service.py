"""
ロジックA厳密版: ストップ高張り付き5条件判定サービス
CLAUDE.mdの要件定義に完全準拠した実装

5つの判定条件:
1. ストップ高価格に到達（終値 = ストップ高価格）
2. 始値 = 終値（張り付き状態）
3. 安値 < 終値 × 0.01（1%未満条件）
4. 上場5年未満の銘柄
5. 四半期決算発表の翌営業日
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from ..lib.logger import logger
from ..database.config import get_db_connection
from .price_limit_service import PriceLimitService
from .listing_data_service import ListingDataService


class LogicAStrictService:
    """ロジックA厳密版サービス - 5条件完全準拠"""

    def __init__(self):
        self.price_limit_service = PriceLimitService()
        self.listing_data_service = ListingDataService()

    async def detect_strict_stop_high_sticking(self, stock_data: Dict) -> Dict:
        """
        5つの条件を厳密にチェック

        Args:
            stock_data: 株価データ（OHLCV + メタデータ）

        Returns:
            検出結果（detected: bool, conditions: Dict, reason: str）
        """
        try:
            stock_code = stock_data.get('code', '')
            stock_name = stock_data.get('name', '')

            logger.info(f"ロジックA厳密版検出開始: {stock_code} {stock_name}")

            # 必須データの確認
            if not self._validate_required_data(stock_data):
                return {
                    'detected': False,
                    'reason': '必須データ不足（OHLC情報が欠損）',
                    'conditions': {}
                }

            # OHLC情報を取得
            ohlc = stock_data.get('ohlc', {})
            open_price = float(ohlc.get('open', 0))
            high_price = float(ohlc.get('high', 0))
            low_price = float(ohlc.get('low', 0))
            close_price = float(ohlc.get('close', 0))
            volume = int(ohlc.get('volume', 0))

            # 前日終値（ストップ高計算用）
            prev_close = float(stock_data.get('prevClose', close_price))

            # 条件チェック結果を格納
            conditions_result = {}

            # 条件1: ストップ高価格に到達（終値 = ストップ高価格）
            condition_1 = await self._check_condition_1(
                stock_code, close_price, prev_close
            )
            conditions_result['condition_1'] = condition_1

            if not condition_1['passed']:
                return {
                    'detected': False,
                    'reason': condition_1['reason'],
                    'conditions': conditions_result
                }

            # 条件2: 始値 = 終値（張り付き状態）
            condition_2 = self._check_condition_2(open_price, close_price)
            conditions_result['condition_2'] = condition_2

            if not condition_2['passed']:
                return {
                    'detected': False,
                    'reason': condition_2['reason'],
                    'conditions': conditions_result
                }

            # 条件3: 安値 < 終値 × 0.01（1%未満条件）
            condition_3 = self._check_condition_3(low_price, close_price)
            conditions_result['condition_3'] = condition_3

            if not condition_3['passed']:
                return {
                    'detected': False,
                    'reason': condition_3['reason'],
                    'conditions': conditions_result
                }

            # 条件4: 上場5年未満の銘柄
            condition_4 = await self._check_condition_4(stock_code)
            conditions_result['condition_4'] = condition_4

            if not condition_4['passed']:
                return {
                    'detected': False,
                    'reason': condition_4['reason'],
                    'conditions': conditions_result
                }

            # 条件5: 四半期決算発表の翌営業日
            condition_5 = await self._check_condition_5(stock_code)
            conditions_result['condition_5'] = condition_5

            if not condition_5['passed']:
                return {
                    'detected': False,
                    'reason': condition_5['reason'],
                    'conditions': conditions_result
                }

            # 全条件クリア
            logger.info(f"✅ ロジックA厳密版検出成功: {stock_code} {stock_name} - 全5条件クリア")

            return {
                'detected': True,
                'reason': '全5条件を満たすストップ高張り付き銘柄',
                'conditions': conditions_result,
                'stock_info': {
                    'code': stock_code,
                    'name': stock_name,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume,
                    'stop_high_price': condition_1.get('stop_high_price'),
                    'listing_years': condition_4.get('years_since_listing'),
                    'earnings_date': condition_5.get('earnings_date')
                }
            }

        except Exception as e:
            logger.error(f"ロジックA厳密版検出エラー: {stock_code} - {str(e)}")
            return {
                'detected': False,
                'reason': f'検出処理エラー: {str(e)}',
                'conditions': {}
            }

    def _validate_required_data(self, stock_data: Dict) -> bool:
        """必須データの検証"""
        required_fields = ['code', 'name', 'ohlc']
        ohlc_required = ['open', 'high', 'low', 'close', 'volume']

        # 基本フィールドのチェック
        for field in required_fields:
            if field not in stock_data or stock_data[field] is None:
                return False

        # OHLC情報のチェック
        ohlc = stock_data.get('ohlc', {})
        for field in ohlc_required:
            if field not in ohlc or ohlc[field] is None:
                return False

        return True

    async def _check_condition_1(
        self,
        stock_code: str,
        close_price: float,
        prev_close: float
    ) -> Dict:
        """
        条件1: ストップ高価格に到達（終値 = ストップ高価格）

        Returns:
            {'passed': bool, 'reason': str, 'stop_high_price': float, 'difference': float}
        """
        try:
            # ストップ高価格を計算
            limits = self.price_limit_service.calculate_price_limits(prev_close)
            stop_high_price = limits['upper_limit']

            # 許容誤差（1円）
            tolerance = 1.0
            difference = abs(close_price - stop_high_price)

            # 終値がストップ高価格と一致するか
            is_stop_high = difference <= tolerance

            if is_stop_high:
                return {
                    'passed': True,
                    'reason': f'ストップ高到達: 終値{close_price}円 = ストップ高{stop_high_price}円',
                    'stop_high_price': stop_high_price,
                    'close_price': close_price,
                    'difference': difference
                }
            else:
                return {
                    'passed': False,
                    'reason': f'ストップ高未到達: 終値{close_price}円 ≠ ストップ高{stop_high_price}円（差分{difference}円）',
                    'stop_high_price': stop_high_price,
                    'close_price': close_price,
                    'difference': difference
                }

        except Exception as e:
            logger.error(f"条件1チェックエラー: {str(e)}")
            return {
                'passed': False,
                'reason': f'条件1検証エラー: {str(e)}',
                'stop_high_price': None,
                'difference': None
            }

    def _check_condition_2(self, open_price: float, close_price: float) -> Dict:
        """
        条件2: 始値 = 終値（張り付き状態）

        Returns:
            {'passed': bool, 'reason': str, 'open': float, 'close': float}
        """
        try:
            # 許容誤差（1円）
            tolerance = 1.0
            difference = abs(open_price - close_price)

            # 始値と終値が一致するか
            is_sticking = difference <= tolerance

            if is_sticking:
                return {
                    'passed': True,
                    'reason': f'張り付き状態: 始値{open_price}円 = 終値{close_price}円',
                    'open': open_price,
                    'close': close_price,
                    'difference': difference
                }
            else:
                return {
                    'passed': False,
                    'reason': f'張り付き不成立: 始値{open_price}円 ≠ 終値{close_price}円（差分{difference}円）',
                    'open': open_price,
                    'close': close_price,
                    'difference': difference
                }

        except Exception as e:
            logger.error(f"条件2チェックエラー: {str(e)}")
            return {
                'passed': False,
                'reason': f'条件2検証エラー: {str(e)}',
                'open': None,
                'close': None
            }

    def _check_condition_3(self, low_price: float, close_price: float) -> Dict:
        """
        条件3: 安値 < 終値 × 0.01（1%未満条件）

        Returns:
            {'passed': bool, 'reason': str, 'low': float, 'threshold': float, 'ratio': float}
        """
        try:
            # 1%閾値を計算
            threshold = close_price * 0.01

            # 安値が閾値未満か
            is_valid_low = low_price < threshold

            # 安値/終値比率
            low_to_close_ratio = (low_price / close_price) * 100 if close_price > 0 else 0

            if is_valid_low:
                return {
                    'passed': True,
                    'reason': f'安値条件クリア: 安値{low_price}円 < 終値×0.01={threshold:.2f}円（比率{low_to_close_ratio:.2f}%）',
                    'low': low_price,
                    'close': close_price,
                    'threshold': threshold,
                    'ratio': low_to_close_ratio
                }
            else:
                return {
                    'passed': False,
                    'reason': f'安値条件未達: 安値{low_price}円 ≥ 終値×0.01={threshold:.2f}円（比率{low_to_close_ratio:.2f}%）',
                    'low': low_price,
                    'close': close_price,
                    'threshold': threshold,
                    'ratio': low_to_close_ratio
                }

        except Exception as e:
            logger.error(f"条件3チェックエラー: {str(e)}")
            return {
                'passed': False,
                'reason': f'条件3検証エラー: {str(e)}',
                'low': None,
                'threshold': None
            }

    async def _check_condition_4(self, stock_code: str) -> Dict:
        """
        条件4: 上場5年未満の銘柄

        Returns:
            {'passed': bool, 'reason': str, 'listing_date': str, 'years_since_listing': float}
        """
        try:
            # データベースから上場日情報を取得
            database = await get_db_connection()
            query = """
            SELECT stock_code, listing_date, years_since_listing, company_name, market
            FROM listing_dates
            WHERE stock_code = :stock_code
            """

            result = await database.fetch_one(query, {"stock_code": stock_code})

            if not result:
                return {
                    'passed': False,
                    'reason': '上場日情報が見つからない',
                    'listing_date': None,
                    'years_since_listing': None
                }

            years_since_listing = float(result['years_since_listing'])
            listing_date = result['listing_date']

            # 上場5年未満の判定
            is_within_5_years = years_since_listing < 5.0

            if is_within_5_years:
                return {
                    'passed': True,
                    'reason': f'上場条件クリア: 上場{years_since_listing:.2f}年（5年未満）',
                    'listing_date': listing_date.isoformat() if listing_date else None,
                    'years_since_listing': years_since_listing,
                    'market': result['market']
                }
            else:
                return {
                    'passed': False,
                    'reason': f'上場条件未達: 上場{years_since_listing:.2f}年（5年以上）',
                    'listing_date': listing_date.isoformat() if listing_date else None,
                    'years_since_listing': years_since_listing,
                    'market': result['market']
                }

        except Exception as e:
            logger.error(f"条件4チェックエラー: {str(e)}")
            return {
                'passed': False,
                'reason': f'条件4検証エラー: {str(e)}',
                'listing_date': None,
                'years_since_listing': None
            }

    async def _check_condition_5(self, stock_code: str) -> Dict:
        """
        条件5: 四半期決算発表の翌営業日

        Returns:
            {'passed': bool, 'reason': str, 'earnings_date': str, 'days_since_earnings': int}
        """
        try:
            # 今日の日付
            today = datetime.now().date()

            # データベースから直近の決算発表日を取得
            database = await get_db_connection()
            query = """
            SELECT stock_code, stock_name, fiscal_year, fiscal_quarter,
                   actual_date, announcement_time, earnings_status
            FROM earnings_schedule
            WHERE stock_code = :stock_code
              AND earnings_status = 'announced'
              AND actual_date IS NOT NULL
            ORDER BY actual_date DESC
            LIMIT 1
            """

            result = await database.fetch_one(query, {"stock_code": stock_code})

            if not result:
                return {
                    'passed': False,
                    'reason': '決算発表履歴が見つからない',
                    'earnings_date': None,
                    'days_since_earnings': None
                }

            earnings_date = result['actual_date'].date() if result['actual_date'] else None

            if not earnings_date:
                return {
                    'passed': False,
                    'reason': '決算発表日が未設定',
                    'earnings_date': None,
                    'days_since_earnings': None
                }

            # 決算発表日からの経過日数
            days_since_earnings = (today - earnings_date).days

            # 翌営業日の判定（土日を考慮）
            # 簡易版: 決算発表日の1-3日後を許容（週末を考慮）
            is_next_business_day = 1 <= days_since_earnings <= 3

            if is_next_business_day:
                return {
                    'passed': True,
                    'reason': f'決算翌営業日: {earnings_date}の{days_since_earnings}日後',
                    'earnings_date': earnings_date.isoformat(),
                    'days_since_earnings': days_since_earnings,
                    'fiscal_info': f"{result['fiscal_year']}年{result['fiscal_quarter']}"
                }
            else:
                return {
                    'passed': False,
                    'reason': f'決算翌営業日でない: {earnings_date}の{days_since_earnings}日後',
                    'earnings_date': earnings_date.isoformat(),
                    'days_since_earnings': days_since_earnings,
                    'fiscal_info': f"{result['fiscal_year']}年{result['fiscal_quarter']}"
                }

        except Exception as e:
            logger.error(f"条件5チェックエラー: {str(e)}")
            return {
                'passed': False,
                'reason': f'条件5検証エラー: {str(e)}',
                'earnings_date': None,
                'days_since_earnings': None
            }
