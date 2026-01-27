"""
ロジックA Phase 1実装
上場5年以内 × ストップ高張り付き × 出来高フィルタ
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from .stop_high_scraper_service import StopHighScraperService
from .listing_age_filter_service import ListingAgeFilterService
from ..lib.logger import logger
import yfinance as yf


class LogicAPhase1Service:
    """ロジックA Phase 1 検出サービス"""

    def __init__(self):
        self.scraper = StopHighScraperService()
        self.listing_filter = ListingAgeFilterService()

        # Phase 1の検出条件（馬場さんノウハウ完全準拠）
        self.config = {
            'max_listing_years': 5.0,           # 上場5年以内
            'sticking_tolerance': 0.001,        # 張り付き判定の誤差（0.1%）
            'min_daily_volume': 1000,           # 最低日次出来高（株）※1日でも1000株以下があったら除外
            'max_market_cap': 50000000000,      # 時価総額500億円以下
            'max_stock_price': 5000,            # 株価5000円以下
            'volume_check_days': 20,            # 直近20営業日をチェック
            'scan_days_mid': list(range(8, 18)), # 毎月中旬（8-17日）
            'scan_days_end': list(range(28, 32)) # 毎月下旬（28-31日）
        }

    def should_scan_today(self) -> bool:
        """
        今日スキャンを実行すべきかチェック

        実行日：毎月8-17日、28-31日のみ

        Returns:
            True: スキャン実行すべき, False: スキップ
        """
        today = datetime.now()
        day = today.day

        is_scan_day = (day in self.config['scan_days_mid'] or
                      day in self.config['scan_days_end'])

        if not is_scan_day:
            logger.info(f"📅 今日は{day}日 - スキャン対象日ではありません（8-17日、28-31日のみ実行）")
        else:
            logger.info(f"📅 今日は{day}日 - スキャン対象日です")

        return is_scan_day

    async def scan_logic_a_phase1(self, target_date: Optional[str] = None, force: bool = False) -> List[Dict]:
        """
        ロジックA Phase 1スキャン実行

        手順：
        1. 日付チェック（8-17日、28-31日のみ）
        2. ストップ高銘柄リスト取得（kabu.hayauma.net）
        3. OHLC情報取得 → 張り付き判定
        4. 株価5000円以下フィルタ
        5. 上場5年以内フィルタ
        6. 時価総額500億円以下フィルタ
        7. 出来高フィルタ（直近1ヶ月で日々1000株以上）

        Args:
            target_date: スキャン対象日（YYYY-MM-DD）。Noneの場合は最新
            force: Trueの場合、日付チェックをスキップして強制実行

        Returns:
            検出された銘柄リスト
        """
        try:
            logger.info("=" * 60)
            logger.info("ロジックA Phase 1 スキャン開始")
            logger.info("=" * 60)

            # 日付チェック
            if not force and not self.should_scan_today():
                logger.info("スキャンをスキップします")
                return []

            # Step 1: ストップ高銘柄のOHLC情報取得
            logger.info("Step 1: ストップ高銘柄のOHLC情報取得")
            stop_high_stocks = await self.scraper.fetch_with_ohlc(target_date)
            logger.info(f"ストップ高銘柄: {len(stop_high_stocks)}件")

            if not stop_high_stocks:
                logger.info("ストップ高銘柄が0件のため終了")
                return []

            # Step 2: 張り付き判定
            logger.info("\nStep 2: 張り付き判定（終値＝始値 OR 安値 < 終値×0.01）")
            sticking_stocks = self._filter_sticking_enhanced(stop_high_stocks)
            logger.info(f"張り付き銘柄: {len(sticking_stocks)}件")

            if not sticking_stocks:
                logger.info("張り付き銘柄が0件のため終了")
                return []

            # Step 3: 株価5000円以下フィルタ
            logger.info("\nStep 3: 株価5000円以下フィルタ")
            price_filtered = self._filter_by_price(sticking_stocks)
            logger.info(f"株価5000円以下: {len(price_filtered)}件")

            if not price_filtered:
                logger.info("株価5000円以下の銘柄が0件のため終了")
                return []

            # Step 4: 上場5年以内フィルタ
            logger.info("\nStep 4: 上場5年以内フィルタ")
            listing_filtered = await self._filter_by_listing_age(price_filtered)
            logger.info(f"上場5年以内: {len(listing_filtered)}件")

            if not listing_filtered:
                logger.info("上場5年以内の銘柄が0件のため終了")
                return []

            # Step 5: 時価総額500億円以下フィルタ
            logger.info("\nStep 5: 時価総額500億円以下フィルタ")
            marketcap_filtered = await self._filter_by_market_cap(listing_filtered)
            logger.info(f"時価総額500億円以下: {len(marketcap_filtered)}件")

            if not marketcap_filtered:
                logger.info("時価総額500億円以下の銘柄が0件のため終了")
                return []

            # Step 6: 出来高フィルタ（直近1ヶ月で日々1000株以上）
            logger.info("\nStep 6: 出来高フィルタ（直近20営業日で日々1000株以上）")
            volume_filtered = await self._filter_by_volume(marketcap_filtered)
            logger.info(f"出来高条件クリア: {len(volume_filtered)}件")

            # 結果サマリー
            logger.info("\n" + "=" * 60)
            logger.info(f"🎯 ロジックA Phase 1 検出結果: {len(volume_filtered)}件")
            logger.info("=" * 60)

            for stock in volume_filtered:
                logger.info(f"  {stock['code']} {stock['name']}")
                logger.info(f"    市場: {stock['market']}, 上場: {stock['years_since_listing']}年")
                logger.info(f"    始値: {stock['open']}, 終値: {stock['close']}, 安値: {stock['low']}")
                logger.info(f"    平均出来高: {stock['avg_volume']:,.0f}株/日")

            return volume_filtered

        except Exception as e:
            logger.error(f"ロジックA Phase 1 スキャンエラー: {str(e)}", exc_info=True)
            return []

    def _filter_by_price(self, stocks: List[Dict]) -> List[Dict]:
        """
        株価5000円以下にフィルタリング

        Args:
            stocks: 銘柄リスト

        Returns:
            株価5000円以下の銘柄リスト
        """
        filtered = []

        for stock in stocks:
            close_price = stock.get('close', 0)

            if close_price <= self.config['max_stock_price']:
                filtered.append(stock)
                logger.info(f"  ✅ {stock['code']}: 株価{close_price}円 - 対象")
            else:
                logger.info(f"  ❌ {stock['code']}: 株価{close_price}円 > 5000円 - 除外")

        return filtered

    def _filter_sticking_enhanced(self, stocks: List[Dict]) -> List[Dict]:
        """
        張り付き判定（強化版）

        条件:
        - 終値 = 始値（誤差0.1%以内）
        - OR 安値 < 終値 × 0.01（1%未満）

        Args:
            stocks: OHLC情報付き銘柄リスト

        Returns:
            張り付き銘柄リスト
        """
        sticking_stocks = []

        for stock in stocks:
            open_price = stock.get('open', 0)
            close_price = stock.get('close', 0)
            low_price = stock.get('low', 0)

            # 条件1: 終値 = 始値（誤差0.1%以内）
            is_equal_close_open = False
            if open_price > 0:
                diff_ratio = abs(close_price - open_price) / open_price
                is_equal_close_open = diff_ratio < self.config['sticking_tolerance']

            # 条件2: 安値 < 終値 × 0.01（1%未満の差）
            is_low_near_close = False
            if close_price > 0:
                low_diff_ratio = abs(close_price - low_price) / close_price
                is_low_near_close = low_diff_ratio < 0.01

            # どちらかの条件を満たせば張り付き
            if is_equal_close_open or is_low_near_close:
                stock['is_sticking'] = True
                stock['sticking_reason'] = []
                if is_equal_close_open:
                    stock['sticking_reason'].append('終値=始値')
                if is_low_near_close:
                    stock['sticking_reason'].append('安値<終値×0.01')

                sticking_stocks.append(stock)
                logger.info(f"  ✅ {stock['code']} {stock['name']}: {', '.join(stock['sticking_reason'])}")

        return sticking_stocks

    async def _filter_by_listing_age(self, stocks: List[Dict]) -> List[Dict]:
        """
        上場5年以内にフィルタリング

        Args:
            stocks: 銘柄リスト

        Returns:
            上場5年以内の銘柄リスト
        """
        filtered = []

        for stock in stocks:
            code = stock['code']

            # 上場日を取得
            listing_date = await self.listing_filter.get_listing_date(code)

            if not listing_date:
                logger.warning(f"  ❌ {code}: 上場日取得失敗")
                continue

            years = self.listing_filter.calculate_years_since_listing(listing_date)

            if years <= self.config['max_listing_years']:
                stock['listing_date'] = listing_date
                stock['years_since_listing'] = years
                filtered.append(stock)
                logger.info(f"  ✅ {code}: 上場{years}年 - 対象")
            else:
                logger.info(f"  ❌ {code}: 上場{years}年 - 除外")

            # レート制限対策
            await asyncio.sleep(0.5)

        return filtered

    async def _filter_by_market_cap(self, stocks: List[Dict]) -> List[Dict]:
        """
        時価総額500億円以下にフィルタリング

        Args:
            stocks: 銘柄リスト

        Returns:
            時価総額500億円以下の銘柄リスト
        """
        filtered = []

        for stock in stocks:
            code = stock['code']

            try:
                # yfinanceで時価総額を取得
                ticker = yf.Ticker(f"{code}.T")
                info = ticker.info

                # 時価総額（円）を取得
                market_cap = info.get('marketCap', 0)

                # 時価総額が取得できない場合はスキップ
                if market_cap == 0:
                    logger.warning(f"  ❌ {code}: 時価総額データ取得失敗")
                    continue

                # 500億円以下のみ
                if market_cap <= self.config['max_market_cap']:
                    stock['market_cap'] = market_cap
                    market_cap_billion = market_cap / 1000000000
                    filtered.append(stock)
                    logger.info(f"  ✅ {code}: 時価総額{market_cap_billion:.1f}億円 - 対象")
                else:
                    market_cap_billion = market_cap / 1000000000
                    logger.info(f"  ❌ {code}: 時価総額{market_cap_billion:.1f}億円 > 500億円 - 除外")

                # レート制限対策
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.warning(f"  ❌ {code}: 時価総額チェックエラー: {str(e)}")
                continue

        return filtered

    async def _filter_by_volume(self, stocks: List[Dict]) -> List[Dict]:
        """
        出来高フィルタ（直近1ヶ月で日々3000株以上）

        Args:
            stocks: 銘柄リスト

        Returns:
            出来高条件をクリアした銘柄リスト
        """
        filtered = []

        for stock in stocks:
            code = stock['code']

            try:
                # yfinanceで直近1ヶ月のデータ取得
                ticker = yf.Ticker(f"{code}.T")
                hist = ticker.history(period='1mo')

                if hist.empty:
                    logger.warning(f"  ❌ {code}: 出来高データ取得失敗")
                    continue

                # 日次出来高の平均を計算
                avg_volume = hist['Volume'].mean()

                # 最低日次出来高チェック（全営業日で3000株以上）
                min_volume = hist['Volume'].min()

                if min_volume >= self.config['min_daily_volume']:
                    stock['avg_volume'] = avg_volume
                    stock['min_volume'] = min_volume
                    filtered.append(stock)
                    logger.info(f"  ✅ {code}: 平均{avg_volume:,.0f}株/日, 最低{min_volume:,.0f}株/日")
                else:
                    logger.info(f"  ❌ {code}: 最低{min_volume:,.0f}株/日 < 3000株/日")

                # レート制限対策
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.warning(f"  ❌ {code}: 出来高チェックエラー: {str(e)}")
                continue

        return filtered


# テスト実行
async def test_logic_a_phase1():
    """ロジックA Phase 1のテスト"""
    service = LogicAPhase1Service()

    print("\n" + "=" * 60)
    print("ロジックA Phase 1 テスト実行（強制実行）")
    print("=" * 60)

    # force=Trueで日付チェックをスキップ
    results = await service.scan_logic_a_phase1(force=True)

    print(f"\n最終結果: {len(results)}件の銘柄が検出されました")


if __name__ == "__main__":
    asyncio.run(test_logic_a_phase1())
