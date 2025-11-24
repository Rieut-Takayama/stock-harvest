"""
データソース基盤デモスクリプト
新しく実装した上場日管理・制限値幅計算・強化版株価取得機能のテスト
"""

import asyncio
import logging
from src.services.listing_data_service import ListingDataService
from src.services.price_limit_service import PriceLimitService
from src.services.stock_data_service_enhanced import StockDataServiceEnhanced

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data_source_demo.log')
    ]
)

logger = logging.getLogger(__name__)


async def demo_listing_data():
    """上場日データ管理のデモ"""
    print("\n" + "="*60)
    print("🏢 上場日データ管理サービス デモ")
    print("="*60)
    
    listing_service = ListingDataService()
    
    try:
        # 1. サンプルデータで上場日データを更新
        print("\n📅 1. 上場日データ更新（サンプルデータ使用）")
        update_result = await listing_service.update_listing_data(use_sample=True)
        print(f"   更新結果: {update_result}")
        
        # 2. スキャン対象銘柄リストを取得
        print("\n🎯 2. スキャン対象銘柄リスト取得（上場2.5-5年以内）")
        target_stocks = await listing_service.get_target_stocks(limit=10)
        print(f"   対象銘柄数: {len(target_stocks)} 件")
        for stock in target_stocks[:3]:
            print(f"   - {stock['code']}: {stock['name']} ({stock['years_since_listing']}年)")
        
        # 3. 上場統計情報を取得
        print("\n📊 3. 上場統計情報")
        stats = await listing_service.get_listing_stats()
        print(f"   総銘柄数: {stats['total_stocks']}")
        print(f"   対象銘柄数: {stats['target_stocks']}")
        print(f"   市場別内訳: {stats['market_breakdown']}")
        
    except Exception as e:
        print(f"   ❌ エラー: {str(e)}")


async def demo_price_limits():
    """制限値幅計算のデモ"""
    print("\n" + "="*60)
    print("📈 制限値幅計算サービス デモ")
    print("="*60)
    
    price_limit_service = PriceLimitService()
    
    try:
        # 1. 様々な価格での制限値幅計算
        print("\n💰 1. 制限値幅計算テスト")
        test_prices = [100, 500, 1000, 5000, 10000, 50000]
        
        for price in test_prices:
            limits = price_limit_service.calculate_price_limits(price)
            print(f"   {price:,}円 → 上限: {limits['upper_limit']:,}円, 下限: {limits['lower_limit']:,}円")
        
        # 2. 銘柄別制限値幅更新
        print("\n📝 2. 銘柄制限値幅更新テスト")
        test_stocks = [
            ("7203", 2900),  # トヨタ
            ("4477", 420),   # BASE
            ("6758", 13000)  # ソニー
        ]
        
        for code, price in test_stocks:
            result = await price_limit_service.update_stock_price_limits(code, price)
            print(f"   {code}: {result['action']} - {result['limits']['lower_limit']:.0f}～{result['limits']['upper_limit']:.0f}")
        
        # 3. 価格アラートチェック
        print("\n🚨 3. 価格アラートチェック")
        alert_result = await price_limit_service.check_price_alerts("7203", 3300)  # ストップ高に接近
        if alert_result.get('alerts_available'):
            print(f"   7203 (3,300円): 上限接近: {alert_result['near_upper_limit']}")
            print(f"   上限まで: {alert_result['upper_distance_percent']}%")
        
        # 4. 制限値幅統計
        print("\n📊 4. 制限値幅統計")
        price_stats = await price_limit_service.get_price_limit_stats()
        print(f"   登録銘柄数: {price_stats['total_stocks']}")
        print(f"   平均価格: {price_stats['avg_price']:,.0f}円")
        
    except Exception as e:
        print(f"   ❌ エラー: {str(e)}")


async def demo_enhanced_stock_data():
    """強化版株価データ取得のデモ"""
    print("\n" + "="*60)
    print("📊 強化版株価データ取得サービス デモ")
    print("="*60)
    
    stock_service = StockDataServiceEnhanced()
    
    try:
        # 1. 個別銘柄データ取得
        print("\n💹 1. 個別銘柄データ取得テスト")
        test_codes = ["7203", "4477", "6758"]
        
        for code in test_codes:
            data = await stock_service.fetch_stock_data(code, f"銘柄{code}")
            if data:
                print(f"   {data['code']}: {data['price']:,.0f}円 ({data['changeRate']:+.2f}%)")
                print(f"     データソース: {data.get('data_source', 'unknown')}")
        
        # 2. 並行取得テスト
        print("\n⚡ 2. 複数銘柄並行取得テスト")
        stock_list = [
            {"code": "7203", "name": "トヨタ自動車"},
            {"code": "6758", "name": "ソニーグループ"},
            {"code": "4477", "name": "BASE"},
            {"code": "4490", "name": "ビザスク"}
        ]
        
        batch_results = await stock_service.batch_fetch_stock_data(stock_list, max_concurrent=3)
        print(f"   取得成功: {len(batch_results)}/{len(stock_list)} 件")
        
        # 3. キャッシュテスト（同じデータを再取得）
        print("\n💾 3. キャッシュ機能テスト")
        cache_test_data = await stock_service.fetch_stock_data("7203", "トヨタ自動車", use_cache=True)
        if cache_test_data.get('cached'):
            print(f"   ✅ キャッシュからデータを取得: {cache_test_data['cache_time']}")
        else:
            print(f"   🔄 新規データを取得: {cache_test_data.get('data_source', 'unknown')}")
        
        # 4. 統計情報
        print("\n📈 4. データ取得統計")
        stats = stock_service.get_fetch_statistics()
        print(f"   総リクエスト数: {stats['total_requests']}")
        print(f"   キャッシュヒット率: {stats['cache_hit_rate']:.1f}%")
        print(f"   フォールバック利用率: {stats['fallback_rate']:.1f}%")
        print(f"   成功率: {stats['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"   ❌ エラー: {str(e)}")


async def demo_integration_test():
    """統合テスト - 全機能を組み合わせた実用例"""
    print("\n" + "="*60)
    print("🔗 統合テスト - 実用例デモ")
    print("="*60)
    
    listing_service = ListingDataService()
    price_limit_service = PriceLimitService()
    stock_service = StockDataServiceEnhanced()
    
    try:
        print("\n🎯 シナリオ: スキャン対象銘柄の価格アラートチェック")
        
        # 1. スキャン対象銘柄を取得
        target_stocks = await listing_service.get_target_stocks(limit=5)
        print(f"   対象銘柄: {len(target_stocks)} 件")
        
        # 2. 各銘柄の現在価格を取得
        for stock in target_stocks[:3]:  # 最初の3件をテスト
            code = stock['code']
            name = stock['name']
            
            # 株価データ取得
            stock_data = await stock_service.fetch_stock_data(code, name)
            if not stock_data:
                continue
            
            current_price = stock_data['price']
            
            # 制限値幅を更新
            await price_limit_service.update_stock_price_limits(code, current_price)
            
            # 価格アラートをチェック
            alerts = await price_limit_service.check_price_alerts(code, current_price)
            
            print(f"\n   📊 {code} ({name})")
            print(f"      現在価格: {current_price:,.0f}円 ({stock_data['changeRate']:+.2f}%)")
            print(f"      上場経過: {stock['years_since_listing']}年")
            
            if alerts.get('alerts_available'):
                if alerts['near_upper_limit']:
                    print(f"      ⚠️  ストップ高接近! (残り{alerts['upper_distance_percent']:.1f}%)")
                elif alerts['near_lower_limit']:
                    print(f"      ⚠️  ストップ安接近! (残り{alerts['lower_distance_percent']:.1f}%)")
                else:
                    print(f"      ✅ 正常範囲内")
        
        print(f"\n🎉 統合テスト完了!")
        
    except Exception as e:
        print(f"   ❌ エラー: {str(e)}")


async def main():
    """メイン実行関数"""
    print("🚀 Stock Harvest AI - データソース基盤デモ開始")
    print("=" * 80)
    
    # データベース接続テスト
    try:
        from src.database.config import connect_db, disconnect_db
        
        print("🔌 データベース接続テスト...")
        if await connect_db():
            print("✅ データベース接続成功")
            
            # 各機能のデモ実行
            await demo_listing_data()
            await demo_price_limits()
            await demo_enhanced_stock_data()
            await demo_integration_test()
            
            await disconnect_db()
            print("🔌 データベース切断完了")
        else:
            print("❌ データベース接続失敗")
            return
            
    except Exception as e:
        print(f"❌ 実行エラー: {str(e)}")
        logger.error(f"Demo execution error: {str(e)}")
    
    print("\n🎯 データソース基盤デモ完了!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())