"""
上場年数フィルタリングサービス
上場5年以内の銘柄のみを抽出
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
from ..lib.logger import logger


class ListingAgeFilterService:
    """上場年数フィルタリング専門サービス"""

    def __init__(self):
        self.max_listing_years = 5.0  # 上場5年以内

    def calculate_years_since_listing(self, listing_date: datetime) -> float:
        """
        上場日から現在までの年数を計算

        Args:
            listing_date: 上場日

        Returns:
            経過年数（float）
        """
        # タイムゾーンを削除（offset-naive に統一）
        if listing_date.tzinfo is not None:
            listing_date = listing_date.replace(tzinfo=None)

        now = datetime.now()
        delta = now - listing_date
        years = delta.days / 365.25
        return round(years, 2)

    async def get_listing_date(self, stock_code: str) -> Optional[datetime]:
        """
        銘柄の上場日を取得（yfinance使用）

        Args:
            stock_code: 銘柄コード

        Returns:
            上場日（datetime）、取得失敗時はNone
        """
        try:
            ticker = yf.Ticker(f"{stock_code}.T")

            # 方法1: info から取得
            try:
                info = ticker.info
                if 'firstTradeDateEpochUtc' in info and info['firstTradeDateEpochUtc']:
                    listing_date = datetime.fromtimestamp(info['firstTradeDateEpochUtc'])
                    logger.debug(f"銘柄 {stock_code} 上場日（info）: {listing_date.strftime('%Y-%m-%d')}")
                    return listing_date
            except:
                pass

            # 方法2: 履歴データの最古日付から推定
            try:
                # 最大期間のデータを取得
                hist = ticker.history(period='max')
                if not hist.empty:
                    listing_date = hist.index[0].to_pydatetime()
                    logger.debug(f"銘柄 {stock_code} 上場日（履歴）: {listing_date.strftime('%Y-%m-%d')}")
                    return listing_date
            except:
                pass

            logger.warning(f"銘柄 {stock_code} の上場日取得失敗")
            return None

        except Exception as e:
            logger.warning(f"銘柄 {stock_code} の上場日取得エラー: {str(e)}")
            return None

    async def filter_by_listing_age(self, stock_codes: List[str]) -> List[Dict]:
        """
        上場5年以内の銘柄を抽出

        Args:
            stock_codes: 銘柄コードリスト

        Returns:
            上場5年以内の銘柄リスト [{'code': '1234', 'listing_date': datetime, 'years': 3.5}]
        """
        filtered_stocks = []

        logger.info(f"上場年数フィルタ開始: {len(stock_codes)}銘柄")

        for i, code in enumerate(stock_codes):
            try:
                listing_date = await self.get_listing_date(code)

                if not listing_date:
                    continue

                years_since_listing = self.calculate_years_since_listing(listing_date)

                # 上場5年以内のみ
                if years_since_listing <= self.max_listing_years:
                    filtered_stocks.append({
                        'code': code,
                        'listing_date': listing_date,
                        'years_since_listing': years_since_listing
                    })
                    logger.info(f"✅ {code}: 上場{years_since_listing}年 - 対象")
                else:
                    logger.debug(f"❌ {code}: 上場{years_since_listing}年 - 除外")

                # API制限対策（10銘柄ごとに1秒待機）
                if (i + 1) % 10 == 0:
                    await asyncio.sleep(1)
                    logger.info(f"進捗: {i+1}/{len(stock_codes)}銘柄処理完了")

            except Exception as e:
                logger.warning(f"銘柄 {code} の処理エラー: {str(e)}")
                continue

        logger.info(f"✅ 上場5年以内の銘柄: {len(filtered_stocks)}/{len(stock_codes)}件")
        return filtered_stocks

    async def get_recent_5year_listings(self, stock_codes: List[str]) -> List[str]:
        """
        上場5年以内の銘柄コードのみを返す（シンプル版）

        Args:
            stock_codes: 銘柄コードリスト

        Returns:
            上場5年以内の銘柄コードリスト
        """
        filtered = await self.filter_by_listing_age(stock_codes)
        return [stock['code'] for stock in filtered]


# テスト用
async def test_listing_filter():
    """上場年数フィルタのテスト"""
    service = ListingAgeFilterService()

    # テスト銘柄（上場年数がバラバラ）
    test_codes = [
        '7203',  # トヨタ（古い）
        '4477',  # BASE（新しい）
        '4490',  # ビザスク（新しい）
        '6758',  # ソニー（古い）
    ]

    print("=== 上場年数フィルタテスト ===")
    filtered = await service.filter_by_listing_age(test_codes)

    print(f"\n上場5年以内の銘柄: {len(filtered)}件")
    for stock in filtered:
        print(f"  {stock['code']}: 上場{stock['years_since_listing']}年 ({stock['listing_date'].strftime('%Y-%m-%d')})")


if __name__ == "__main__":
    asyncio.run(test_listing_filter())
