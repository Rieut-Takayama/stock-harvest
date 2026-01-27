"""
ストップ高銘柄スクレイピングサービス
kabu.hayauma.netから実際のストップ高銘柄リストを取得
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from ..lib.logger import logger


class StopHighScraperService:
    """ストップ高銘柄取得サービス"""

    def __init__(self):
        self.base_url = "https://kabu.hayauma.net/ranking/stop-high/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    async def fetch_stop_high_stocks(self, date: Optional[str] = None) -> List[Dict]:
        """
        指定日のストップ高銘柄リストを取得

        Args:
            date: 日付（YYYY-MM-DD形式）。Noneの場合は最新

        Returns:
            ストップ高銘柄リスト [{'code': '1234', 'name': '銘柄名', 'market': '東証GRT'}]
        """
        try:
            # URLを構築（日付指定がある場合）
            url = self.base_url
            if date:
                url = f"{self.base_url}?date={date}"

            logger.info(f"ストップ高銘柄取得開始: {url}")

            # HTTPリクエスト（SSL検証スキップ）
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"HTTP エラー: {response.status}")
                        return []

                    html = await response.text()

            # HTMLをパース
            soup = BeautifulSoup(html, 'html.parser')

            # テーブルから銘柄情報を抽出
            stocks = []
            table = soup.find('table')

            if not table:
                logger.warning("ストップ高銘柄テーブルが見つかりません")
                return []

            rows = table.find_all('tr')[1:]  # ヘッダー行をスキップ

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    code = cols[0].text.strip()
                    name = cols[1].text.strip()
                    market = cols[2].text.strip() if len(cols) > 2 else ''

                    stocks.append({
                        'code': code,
                        'name': name,
                        'market': market
                    })

            logger.info(f"✅ ストップ高銘柄 {len(stocks)}件を取得")
            return stocks

        except asyncio.TimeoutError:
            logger.error("タイムアウト: ストップ高銘柄の取得に時間がかかりすぎました")
            return []
        except Exception as e:
            logger.error(f"ストップ高銘柄取得エラー: {str(e)}", exc_info=True)
            return []

    async def fetch_with_ohlc(self, date: Optional[str] = None) -> List[Dict]:
        """
        ストップ高銘柄のOHLC情報を取得（yfinance使用）

        Args:
            date: 日付（YYYY-MM-DD形式）

        Returns:
            OHLC情報付きストップ高銘柄リスト
        """
        import yfinance as yf

        # ストップ高銘柄リストを取得
        stop_high_stocks = await self.fetch_stop_high_stocks(date)

        if not stop_high_stocks:
            return []

        logger.info(f"📊 {len(stop_high_stocks)}銘柄のOHLC情報取得開始")

        # 各銘柄のOHLC情報を取得
        enriched_stocks = []

        for stock in stop_high_stocks:
            try:
                # yfinanceで詳細データ取得
                ticker = yf.Ticker(f"{stock['code']}.T")
                hist = ticker.history(period='5d')

                if hist.empty:
                    logger.warning(f"銘柄 {stock['code']} のデータ取得失敗")
                    continue

                # 最新日のデータを取得
                latest = hist.iloc[-1]

                stock_with_ohlc = {
                    **stock,
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'close': float(latest['Close']),
                    'volume': int(latest['Volume']),
                    'date': latest.name.strftime('%Y-%m-%d')
                }

                enriched_stocks.append(stock_with_ohlc)

                # レート制限対策
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.warning(f"銘柄 {stock['code']} のOHLC取得エラー: {str(e)}")
                continue

        logger.info(f"✅ OHLC情報取得完了: {len(enriched_stocks)}件")
        return enriched_stocks

    def filter_sticking_stocks(self, stocks: List[Dict]) -> List[Dict]:
        """
        「終値＝始値」（張り付き）の銘柄を抽出

        Args:
            stocks: OHLC情報付き銘柄リスト

        Returns:
            張り付き銘柄リスト
        """
        sticking_stocks = []

        for stock in stocks:
            open_price = stock.get('open', 0)
            close_price = stock.get('close', 0)

            # 終値 = 始値（誤差0.1%以内）
            if open_price > 0 and abs(close_price - open_price) / open_price < 0.001:
                sticking_stocks.append({
                    **stock,
                    'is_sticking': True,
                    'price_diff': close_price - open_price
                })

        logger.info(f"🎯 張り付き銘柄: {len(sticking_stocks)}/{len(stocks)}件")
        return sticking_stocks


# テスト用
async def test_scraper():
    """スクレイパーのテスト"""
    scraper = StopHighScraperService()

    # 1. ストップ高銘柄リスト取得
    print("=== ストップ高銘柄リスト取得 ===")
    stocks = await scraper.fetch_stop_high_stocks()
    print(f"取得件数: {len(stocks)}")
    for stock in stocks[:5]:
        print(f"  {stock['code']} {stock['name']} ({stock['market']})")

    # 2. OHLC情報付きで取得
    print("\n=== OHLC情報付き取得 ===")
    stocks_with_ohlc = await scraper.fetch_with_ohlc()
    print(f"取得件数: {len(stocks_with_ohlc)}")
    for stock in stocks_with_ohlc[:3]:
        print(f"  {stock['code']} {stock['name']}")
        print(f"    始値: {stock['open']}, 終値: {stock['close']}")

    # 3. 張り付き銘柄抽出
    print("\n=== 張り付き銘柄抽出 ===")
    sticking = scraper.filter_sticking_stocks(stocks_with_ohlc)
    print(f"張り付き銘柄: {len(sticking)}件")
    for stock in sticking:
        print(f"  {stock['code']} {stock['name']}: 始値={stock['open']}, 終値={stock['close']}")


if __name__ == "__main__":
    asyncio.run(test_scraper())
