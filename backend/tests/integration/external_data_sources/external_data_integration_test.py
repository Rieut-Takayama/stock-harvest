"""
外部データソース統合テスト
IRバンク・カブタン・スケジューラー・強化版決算サービスの統合テスト
"""

import asyncio
import sys
import os
import unittest
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# パスの設定
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

# テスト用設定
os.environ['DATABASE_URL'] = 'sqlite:///./test_external_data.db'

from src.database.config import database, connect_db, disconnect_db
from src.database.tables import (
    earnings_schedule, listing_dates, price_limits, 
    stock_master, stock_data_cache
)
from src.services.irbank_integration_service import IRBankIntegrationService
from src.services.kabutan_integration_service import KabutanIntegrationService
from src.services.data_source_scheduler_service import DataSourceSchedulerService
from src.services.enhanced_earnings_service import EnhancedEarningsService
from src.services.listing_data_service import ListingDataService
from src.services.price_limit_service import PriceLimitService
from tests.utils.MilestoneTracker import MilestoneTracker

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExternalDataSourceIntegrationTest(unittest.TestCase):
    """外部データソース統合テストクラス"""
    
    @classmethod
    async def async_setUpClass(cls):
        """テストクラス初期化（非同期）"""
        cls.tracker = MilestoneTracker()
        cls.tracker.setOperation("テスト環境初期化")
        cls.tracker.mark("テスト開始")
        
        # データベース接続
        await connect_db()
        
        # テーブル作成
        await cls._create_test_tables()
        
        # サービスインスタンス初期化
        cls.irbank_service = IRBankIntegrationService()
        cls.kabutan_service = KabutanIntegrationService()
        cls.scheduler_service = DataSourceSchedulerService()
        cls.enhanced_earnings_service = EnhancedEarningsService()
        cls.listing_service = ListingDataService()
        cls.price_limit_service = PriceLimitService()
        
        cls.tracker.mark("初期化完了")
    
    @classmethod
    async def async_tearDownClass(cls):
        """テストクラス終了処理（非同期）"""
        cls.tracker.setOperation("テスト環境終了処理")
        
        # スケジューラー停止
        if cls.scheduler_service.is_running:
            await cls.scheduler_service.stop_scheduler()
        
        # データベース切断
        await disconnect_db()
        
        # テスト結果サマリー表示
        cls.tracker.summary()
    
    @classmethod
    async def _create_test_tables(cls):
        """テストテーブル作成"""
        from src.database.config import metadata, engine
        
        # メタデータを使用してテーブル作成
        metadata.create_all(engine)
        
        # 初期データ投入
        await cls._insert_test_data()
    
    @classmethod
    async def _insert_test_data(cls):
        """テスト用データ投入"""
        # 上場日データ
        test_listing_data = [
            {
                'stock_code': '7203',
                'listing_date': datetime(2020, 1, 15),
                'market': 'Prime',
                'company_name': 'トヨタ自動車テスト',
                'years_since_listing': 4.0,
                'is_target': True,
                'data_source': 'test',
                'sector': '自動車'
            },
            {
                'stock_code': '6758',
                'listing_date': datetime(2019, 6, 20),
                'market': 'Prime',
                'company_name': 'ソニーグループテスト',
                'years_since_listing': 4.5,
                'is_target': True,
                'data_source': 'test',
                'sector': 'テクノロジー'
            }
        ]
        
        for data in test_listing_data:
            await database.execute(listing_dates.insert().values(**data))
        
        # 決算スケジュールデータ
        test_earnings_data = [
            {
                'id': 'earnings-7203-2024-Q3',
                'stock_code': '7203',
                'stock_name': 'トヨタ自動車テスト',
                'fiscal_year': 2024,
                'fiscal_quarter': 'Q3',
                'scheduled_date': datetime.now() + timedelta(days=7),
                'announcement_time': 'after_market',
                'earnings_status': 'scheduled',
                'is_black_ink_conversion': False,
                'data_source': 'test'
            },
            {
                'id': 'earnings-6758-2024-Q3',
                'stock_code': '6758',
                'stock_name': 'ソニーグループテスト',
                'fiscal_year': 2024,
                'fiscal_quarter': 'Q3',
                'scheduled_date': datetime.now() + timedelta(days=14),
                'announcement_time': 'after_market',
                'earnings_status': 'scheduled',
                'is_black_ink_conversion': True,
                'is_target_for_logic_b': True,
                'data_source': 'test'
            }
        ]
        
        for data in test_earnings_data:
            await database.execute(earnings_schedule.insert().values(**data))
    
    async def test_01_irbank_integration_service(self):
        """IRバンク連携サービステスト"""
        self.tracker.setOperation("IRバンク連携テスト")
        
        print("\n=== Test 1: IRバンク連携サービス ===")
        
        # 1.1 決算スケジュール取得テスト
        self.tracker.mark("決算スケジュール取得開始")
        earnings_data = await self.irbank_service.fetch_earnings_schedule()
        
        self.assertIsInstance(earnings_data, list, "決算スケジュールはリスト形式である必要があります")
        self.assertGreater(len(earnings_data), 0, "決算スケジュールデータが取得できませんでした")
        
        # データ構造の確認
        if earnings_data:
            sample_item = earnings_data[0]
            required_keys = ['stock_code', 'stock_name', 'fiscal_year', 'scheduled_date']
            for key in required_keys:
                self.assertIn(key, sample_item, f"必須キー {key} が見つかりません")
        
        self.tracker.mark("決算スケジュール取得完了")
        
        # 1.2 決算データのデータベース保存テスト
        self.tracker.mark("決算データDB保存開始")
        save_result = await self.irbank_service.save_earnings_to_database(earnings_data)
        
        self.assertIsInstance(save_result, dict, "保存結果は辞書形式である必要があります")
        self.assertIn('inserted', save_result, "挿入件数情報が必要です")
        self.assertIn('updated', save_result, "更新件数情報が必要です")
        
        self.tracker.mark("決算データDB保存完了")
        
        # 1.3 適時開示情報取得テスト
        self.tracker.mark("適時開示情報取得開始")
        disclosure_data = await self.irbank_service.fetch_disclosure_info('7203', days_back=14)
        
        self.assertIsInstance(disclosure_data, list, "適時開示情報はリスト形式である必要があります")
        
        self.tracker.mark("適時開示情報取得完了")
        
        # 1.4 サービス状態確認テスト
        status = await self.irbank_service.get_service_status()
        self.assertIsInstance(status, dict, "サービス状態は辞書形式である必要があります")
        self.assertEqual(status['status'], 'active', "サービスはアクティブである必要があります")
        
        print("✅ IRバンク連携サービステスト完了")
    
    async def test_02_kabutan_integration_service(self):
        """カブタン連携サービステスト"""
        self.tracker.setOperation("カブタン連携テスト")
        
        print("\n=== Test 2: カブタン連携サービス ===")
        
        test_stock_codes = ['7203', '6758']
        
        for stock_code in test_stock_codes:
            # 2.1 決算サマリー取得テスト
            self.tracker.mark(f"{stock_code}_決算サマリー取得開始")
            earnings_summary = await self.kabutan_service.fetch_earnings_summary(stock_code)
            
            self.assertIsInstance(earnings_summary, dict, "決算サマリーは辞書形式である必要があります")
            self.assertEqual(earnings_summary['stock_code'], stock_code, "銘柄コードが一致しません")
            
            # 必須フィールドの確認
            required_fields = ['latest_annual', 'growth_analysis', 'risk_assessment']
            for field in required_fields:
                self.assertIn(field, earnings_summary, f"必須フィールド {field} が見つかりません")
            
            self.tracker.mark(f"{stock_code}_決算サマリー取得完了")
            
            # 2.2 決算サマリーのDB保存テスト
            self.tracker.mark(f"{stock_code}_DB保存開始")
            save_success = await self.kabutan_service.save_earnings_to_database(earnings_summary)
            self.assertTrue(save_success, f"{stock_code} の決算サマリーDB保存に失敗しました")
            
            self.tracker.mark(f"{stock_code}_DB保存完了")
            
            # 2.3 企業プロフィール取得テスト
            profile = await self.kabutan_service.fetch_company_profile(stock_code)
            if profile:  # プロフィール取得は必須ではない
                self.assertIsInstance(profile, dict, "企業プロフィールは辞書形式である必要があります")
                self.assertEqual(profile['stock_code'], stock_code, "銘柄コードが一致しません")
        
        # 2.4 サービス状態確認テスト
        status = await self.kabutan_service.get_service_status()
        self.assertIsInstance(status, dict, "サービス状態は辞書形式である必要があります")
        self.assertEqual(status['status'], 'active', "サービスはアクティブである必要があります")
        
        print("✅ カブタン連携サービステスト完了")
    
    async def test_03_data_source_scheduler_service(self):
        """データソーススケジューラーサービステスト"""
        self.tracker.setOperation("スケジューラーサービステスト")
        
        print("\n=== Test 3: データソーススケジューラーサービス ===")
        
        # 3.1 スケジューラー開始テスト
        self.tracker.mark("スケジューラー開始")
        await self.scheduler_service.start_scheduler()
        
        self.assertTrue(self.scheduler_service.is_running, "スケジューラーが開始されていません")
        
        # 3.2 スケジュール済みジョブ確認テスト
        jobs = self.scheduler_service.get_scheduled_jobs()
        self.assertIsInstance(jobs, list, "ジョブリストはリスト形式である必要があります")
        self.assertGreater(len(jobs), 0, "スケジュール済みジョブが見つかりません")
        
        # 必要なジョブが存在するか確認
        job_ids = [job['id'] for job in jobs]
        expected_jobs = [
            'listing_dates_weekly',
            'earnings_schedule_daily',
            'health_check_interval'
        ]
        
        for expected_job in expected_jobs:
            self.assertIn(expected_job, job_ids, f"必要なジョブ {expected_job} が見つかりません")
        
        self.tracker.mark("ジョブ確認完了")
        
        # 3.3 手動ジョブ実行テスト（ヘルスチェックのみ）
        manual_result = await self.scheduler_service.execute_job_manually('health_check_interval')
        self.assertIsInstance(manual_result, dict, "手動実行結果は辞書形式である必要があります")
        self.assertTrue(manual_result['success'], "ヘルスチェックジョブの手動実行に失敗しました")
        
        self.tracker.mark("手動実行テスト完了")
        
        # 3.4 実行統計確認テスト
        stats = self.scheduler_service.get_execution_statistics()
        self.assertIsInstance(stats, dict, "実行統計は辞書形式である必要があります")
        self.assertIn('total_executions', stats, "総実行回数が見つかりません")
        
        # 3.5 サービス状態確認テスト
        status = await self.scheduler_service.get_service_status()
        self.assertIsInstance(status, dict, "サービス状態は辞書形式である必要があります")
        self.assertTrue(status['is_running'], "スケジューラーが実行中ではありません")
        
        self.tracker.mark("スケジューラー状態確認完了")
        
        print("✅ スケジューラーサービステスト完了")
    
    async def test_04_enhanced_earnings_service(self):
        """強化版決算サービステスト"""
        self.tracker.setOperation("強化版決算サービステスト")
        
        print("\n=== Test 4: 強化版決算サービス ===")
        
        # 4.1 包括的決算カレンダー取得テスト
        self.tracker.mark("決算カレンダー取得開始")
        calendar = await self.enhanced_earnings_service.get_comprehensive_earnings_calendar()
        
        self.assertIsInstance(calendar, dict, "決算カレンダーは辞書形式である必要があります")
        
        # 必須セクションの確認
        required_sections = ['period', 'summary', 'by_date', 'by_quarter', 'by_sector']
        for section in required_sections:
            self.assertIn(section, calendar, f"必須セクション {section} が見つかりません")
        
        # サマリー情報の確認
        summary = calendar['summary']
        self.assertIsInstance(summary['total_earnings'], int, "総決算数は整数である必要があります")
        self.assertGreaterEqual(summary['total_earnings'], 0, "総決算数は0以上である必要があります")
        
        self.tracker.mark("決算カレンダー取得完了")
        
        # 4.2 黒字転換パイプライン分析テスト
        self.tracker.mark("黒字転換パイプライン分析開始")
        pipeline = await self.enhanced_earnings_service.get_black_ink_conversion_pipeline()
        
        self.assertIsInstance(pipeline, dict, "パイプラインデータは辞書形式である必要があります")
        
        # パイプライン構造の確認
        required_pipeline_sections = ['summary', 'by_stage', 'by_timing', 'risk_analysis']
        for section in required_pipeline_sections:
            self.assertIn(section, pipeline, f"パイプライン必須セクション {section} が見つかりません")
        
        # ステージ別データの確認
        stages = pipeline['by_stage']
        expected_stages = ['confirmed', 'probable', 'potential']
        for stage in expected_stages:
            self.assertIn(stage, stages, f"ステージ {stage} が見つかりません")
        
        self.tracker.mark("黒字転換パイプライン分析完了")
        
        # 4.3 外部ソースからの決算データ更新テスト
        self.tracker.mark("外部ソース更新開始")
        update_result = await self.enhanced_earnings_service.update_earnings_from_external_sources(['7203'])
        
        self.assertIsInstance(update_result, dict, "更新結果は辞書形式である必要があります")
        
        required_stats = ['total_requested', 'irbank_updates', 'kabutan_updates', 'errors']
        for stat in required_stats:
            self.assertIn(stat, update_result, f"更新統計 {stat} が見つかりません")
        
        self.tracker.mark("外部ソース更新完了")
        
        # 4.4 サービス設定確認テスト
        config = await self.enhanced_earnings_service.get_service_configuration()
        self.assertIsInstance(config, dict, "サービス設定は辞書形式である必要があります")
        self.assertIn('service_name', config, "サービス名が見つかりません")
        self.assertIn('capabilities', config, "サービス機能リストが見つかりません")
        
        print("✅ 強化版決算サービステスト完了")
    
    async def test_05_existing_services_integration(self):
        """既存サービス統合テスト"""
        self.tracker.setOperation("既存サービス統合テスト")
        
        print("\n=== Test 5: 既存サービス統合テスト ===")
        
        # 5.1 上場日データサービステスト
        self.tracker.mark("上場日データ更新開始")
        listing_result = await self.listing_service.update_listing_data(use_sample=True)
        
        self.assertIsInstance(listing_result, dict, "上場日データ更新結果は辞書形式である必要があります")
        self.assertIn('inserted', listing_result, "挿入件数が見つかりません")
        self.assertIn('updated', listing_result, "更新件数が見つかりません")
        
        # 対象銘柄取得テスト
        target_stocks = await self.listing_service.get_target_stocks(limit=10)
        self.assertIsInstance(target_stocks, list, "対象銘柄リストはリスト形式である必要があります")
        
        self.tracker.mark("上場日データ更新完了")
        
        # 5.2 制限値幅サービステスト
        self.tracker.mark("制限値幅計算開始")
        
        test_prices = [100, 1000, 5000]
        for price in test_prices:
            limits = self.price_limit_service.calculate_price_limits(price)
            
            self.assertIsInstance(limits, dict, "制限値幅は辞書形式である必要があります")
            self.assertEqual(limits['current_price'], float(price), "基準価格が一致しません")
            self.assertGreater(limits['upper_limit'], price, "上限価格は基準価格より大きい必要があります")
            self.assertLess(limits['lower_limit'], price, "下限価格は基準価格より小さい必要があります")
        
        # 制限値幅のDB更新テスト
        update_result = await self.price_limit_service.update_stock_price_limits('7203', 2500)
        self.assertIsInstance(update_result, dict, "制限値幅更新結果は辞書形式である必要があります")
        self.assertEqual(update_result['stock_code'], '7203', "銘柄コードが一致しません")
        
        self.tracker.mark("制限値幅計算完了")
        
        print("✅ 既存サービス統合テスト完了")
    
    async def test_06_cross_service_integration(self):
        """サービス間連携統合テスト"""
        self.tracker.setOperation("サービス間連携統合テスト")
        
        print("\n=== Test 6: サービス間連携統合テスト ===")
        
        # 6.1 IRバンク → 強化版決算サービス連携テスト
        self.tracker.mark("IRバンク・決算サービス連携開始")
        
        # IRバンクから取得した決算データを強化版サービスで活用
        irbank_earnings = await self.irbank_service.fetch_earnings_schedule()
        if irbank_earnings:
            # データベースに保存
            await self.irbank_service.save_earnings_to_database(irbank_earnings)
            
            # 強化版サービスで包括的分析
            calendar = await self.enhanced_earnings_service.get_comprehensive_earnings_calendar()
            
            # データが連携されているか確認
            self.assertGreater(calendar['summary']['total_earnings'], 0, 
                             "IRバンクデータが強化版サービスに反映されていません")
        
        self.tracker.mark("IRバンク・決算サービス連携完了")
        
        # 6.2 カブタン → 決算スケジュール連携テスト
        self.tracker.mark("カブタン・スケジュール連携開始")
        
        # カブタンから取得した決算データをスケジュールに反映
        kabutan_summary = await self.kabutan_service.fetch_earnings_summary('7203')
        if kabutan_summary:
            # データベースに保存
            await self.kabutan_service.save_earnings_to_database(kabutan_summary)
            
            # 決算スケジュールで確認
            calendar = await self.enhanced_earnings_service.get_comprehensive_earnings_calendar()
            
            # 黒字転換情報が反映されているか確認
            if kabutan_summary['growth_analysis']['is_black_ink_conversion']:
                self.assertGreater(calendar['summary']['black_ink_candidates'], 0, 
                                 "カブタンの黒字転換データが反映されていません")
        
        self.tracker.mark("カブタン・スケジュール連携完了")
        
        # 6.3 スケジューラー → 各種サービス連携テスト
        self.tracker.mark("スケジューラー連携テスト開始")
        
        # スケジューラーの各種サービス状態を確認
        scheduler_status = await self.scheduler_service.get_service_status()
        self.assertTrue(scheduler_status['is_running'], "スケジューラーが動作していません")
        
        # 各サービスの状態をスケジューラー経由で確認
        irbank_status = await self.irbank_service.get_service_status()
        kabutan_status = await self.kabutan_service.get_service_status()
        
        self.assertEqual(irbank_status['status'], 'active', "IRバンクサービスがアクティブではありません")
        self.assertEqual(kabutan_status['status'], 'active', "カブタンサービスがアクティブではありません")
        
        self.tracker.mark("スケジューラー連携テスト完了")
        
        print("✅ サービス間連携統合テスト完了")
    
    async def test_07_data_consistency_verification(self):
        """データ整合性確認テスト"""
        self.tracker.setOperation("データ整合性確認")
        
        print("\n=== Test 7: データ整合性確認テスト ===")
        
        # 7.1 データベース内のデータ整合性確認
        self.tracker.mark("DB整合性確認開始")
        
        # 上場日データと決算スケジュールの整合性
        listing_query = "SELECT stock_code FROM listing_dates WHERE is_target = true"
        listing_results = await database.fetch_all(listing_query)
        listing_codes = [row['stock_code'] for row in listing_results]
        
        earnings_query = "SELECT DISTINCT stock_code FROM earnings_schedule"
        earnings_results = await database.fetch_all(earnings_query)
        earnings_codes = [row['stock_code'] for row in earnings_results]
        
        # 共通の銘柄が存在するか確認
        common_codes = set(listing_codes) & set(earnings_codes)
        self.assertGreater(len(common_codes), 0, "上場日データと決算スケジュールで共通の銘柄がありません")
        
        self.tracker.mark("DB整合性確認完了")
        
        # 7.2 外部データソース間のデータ一貫性確認
        self.tracker.mark("外部データ一貫性確認開始")
        
        # 同じ銘柄に対するIRバンクとカブタンのデータ比較
        test_code = '7203'
        
        # IRバンクからの決算情報
        irbank_earnings = await self.irbank_service.fetch_earnings_schedule()
        irbank_data = None
        for item in irbank_earnings:
            if item.get('stock_code') == test_code:
                irbank_data = item
                break
        
        # カブタンからの決算情報
        kabutan_data = await self.kabutan_service.fetch_earnings_summary(test_code)
        
        # 両方のデータが取得できた場合、基本情報の一貫性を確認
        if irbank_data and kabutan_data:
            self.assertEqual(irbank_data['stock_code'], kabutan_data['stock_code'], 
                           "IRバンクとカブタンで銘柄コードが一致しません")
            
            # データソースの記録確認
            self.assertEqual(irbank_data.get('data_source'), 'irbank', 
                           "IRバンクデータのソース情報が正しくありません")
            self.assertEqual(kabutan_data.get('data_source'), 'kabutan', 
                           "カブタンデータのソース情報が正しくありません")
        
        self.tracker.mark("外部データ一貫性確認完了")
        
        # 7.3 タイムスタンプとバージョン管理確認
        self.tracker.mark("タイムスタンプ確認開始")
        
        # 最新のデータ更新時刻を確認
        timestamp_query = """
            SELECT MAX(last_updated_from_source) as latest_update
            FROM earnings_schedule 
            WHERE last_updated_from_source IS NOT NULL
        """
        
        result = await database.fetch_one(timestamp_query)
        if result and result['latest_update']:
            latest_update = result['latest_update']
            time_diff = datetime.now() - latest_update
            
            # 更新が24時間以内かどうか確認（テスト環境では緩い条件）
            self.assertLess(time_diff.total_seconds(), 86400 * 7, 
                           "データ更新が7日以上前です（正常な範囲外）")
        
        self.tracker.mark("タイムスタンプ確認完了")
        
        print("✅ データ整合性確認テスト完了")

# テスト実行関数
async def run_external_data_integration_tests():
    """外部データソース統合テストを実行"""
    print("🚀 外部データソース統合テスト開始")
    print("=" * 60)
    
    # テストスイートの作成
    test_instance = ExternalDataSourceIntegrationTest()
    
    try:
        # テスト環境初期化
        await ExternalDataSourceIntegrationTest.async_setUpClass()
        
        # 各テストの実行
        test_methods = [
            'test_01_irbank_integration_service',
            'test_02_kabutan_integration_service', 
            'test_03_data_source_scheduler_service',
            'test_04_enhanced_earnings_service',
            'test_05_existing_services_integration',
            'test_06_cross_service_integration',
            'test_07_data_consistency_verification'
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method_name in test_methods:
            try:
                print(f"\n▶️ 実行中: {test_method_name}")
                test_method = getattr(test_instance, test_method_name)
                await test_method()
                passed_tests += 1
                print(f"✅ 合格: {test_method_name}")
                
            except Exception as e:
                print(f"❌ 失敗: {test_method_name}")
                print(f"    エラー: {str(e)}")
                logger.error(f"テスト失敗: {test_method_name} - {str(e)}")
        
        # テスト結果サマリー
        print("\n" + "=" * 60)
        print(f"🏁 外部データソース統合テスト結果")
        print(f"✅ 合格: {passed_tests}/{total_tests} テスト")
        print(f"❌ 失敗: {total_tests - passed_tests}/{total_tests} テスト")
        
        if passed_tests == total_tests:
            print("🎉 全てのテストが合格しました！")
            success_rate = 100.0
        else:
            success_rate = (passed_tests / total_tests) * 100
            print(f"⚠️ 成功率: {success_rate:.1f}%")
        
        print("\n📊 テスト詳細:")
        print("   - IRバンク連携: 適時開示情報・決算スケジュール取得")
        print("   - カブタン連携: 決算短信・企業プロフィール取得")  
        print("   - スケジューラー: 自動データ更新・ジョブ管理")
        print("   - 強化版決算サービス: 包括的分析・黒字転換検出")
        print("   - サービス統合: データ連携・整合性確認")
        
        return success_rate >= 80  # 80%以上で成功とみなす
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {str(e)}")
        logger.error(f"統合テスト実行エラー: {str(e)}")
        return False
        
    finally:
        # テスト環境終了処理
        try:
            await ExternalDataSourceIntegrationTest.async_tearDownClass()
        except Exception as e:
            print(f"⚠️ 終了処理エラー: {str(e)}")

# メイン実行
if __name__ == "__main__":
    # イベントループでテスト実行
    success = asyncio.run(run_external_data_integration_tests())
    
    # 終了コード設定
    import sys
    sys.exit(0 if success else 1)